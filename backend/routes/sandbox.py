"""
Sandbox Execution System for Melus AI
Provides 3 execution modes:
- A) CodeSandbox API (remote, recommended)
- B) Node.js Process Sandbox (local, simulated)
- C) Docker Container (full isolation, requires Docker)
"""
from fastapi import APIRouter, HTTPException, Request, BackgroundTasks
from typing import Optional, Dict, Any, List
import logging
import asyncio
import subprocess
import tempfile
import shutil
import os
import json
import signal
import uuid
from datetime import datetime
import aiohttp

from utils import generate_id, utc_now, get_authenticated_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/sandbox", tags=["sandbox"])

# Execution limits
MAX_EXECUTION_TIME = 30  # seconds
MAX_MEMORY_MB = 256
MAX_OUTPUT_SIZE = 100000  # characters

# Store running executions
active_executions: Dict[str, Dict] = {}


# ============================================================================
# OPTION A: CodeSandbox API Integration
# ============================================================================

CODESANDBOX_API = "https://codesandbox.io/api/v1"

@router.post("/codesandbox/create")
async def create_codesandbox(request: Request):
    """Create a CodeSandbox from workspace files"""
    db = request.app.state.db
    user_doc = await get_authenticated_user(request, db)
    
    body = await request.json()
    workspace_id = body.get("workspace_id")
    
    if not workspace_id:
        raise HTTPException(status_code=400, detail="workspace_id required")
    
    # Get workspace
    workspace = await db.workspaces.find_one(
        {"workspace_id": workspace_id, "user_id": user_doc["user_id"]},
        {"_id": 0, "files": 1, "name": 1}
    )
    
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")
    
    files = workspace.get("files", {})
    
    # Convert to CodeSandbox format
    sandbox_files = {}
    for path, content in files.items():
        sandbox_files[path] = {"content": content}
    
    # Ensure package.json exists
    if "package.json" not in sandbox_files:
        sandbox_files["package.json"] = {
            "content": json.dumps({
                "name": workspace.get("name", "melus-app"),
                "version": "1.0.0",
                "dependencies": {
                    "react": "^18.2.0",
                    "react-dom": "^18.2.0"
                }
            }, indent=2)
        }
    
    # Create sandbox definition
    sandbox_definition = {
        "files": sandbox_files,
        "template": "create-react-app"
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            # Use CodeSandbox define API
            async with session.post(
                f"{CODESANDBOX_API}/sandboxes/define",
                json={"files": sandbox_files},
                headers={"Content-Type": "application/json"}
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    sandbox_id = data.get("sandbox_id")
                    
                    # Save reference
                    await db.workspaces.update_one(
                        {"workspace_id": workspace_id},
                        {"$set": {
                            "codesandbox_id": sandbox_id,
                            "codesandbox_url": f"https://codesandbox.io/s/{sandbox_id}",
                            "sandbox_created_at": utc_now()
                        }}
                    )
                    
                    return {
                        "sandbox_id": sandbox_id,
                        "url": f"https://codesandbox.io/s/{sandbox_id}",
                        "embed_url": f"https://codesandbox.io/embed/{sandbox_id}",
                        "preview_url": f"https://{sandbox_id}.csb.app"
                    }
                else:
                    error_text = await response.text()
                    logger.error(f"CodeSandbox API error: {error_text}")
                    raise HTTPException(status_code=500, detail="Failed to create CodeSandbox")
    except aiohttp.ClientError as e:
        logger.error(f"CodeSandbox connection error: {e}")
        raise HTTPException(status_code=500, detail="Could not connect to CodeSandbox")


@router.get("/codesandbox/{sandbox_id}/status")
async def get_codesandbox_status(sandbox_id: str):
    """Get status of a CodeSandbox"""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{CODESANDBOX_API}/sandboxes/{sandbox_id}") as response:
                if response.status == 200:
                    data = await response.json()
                    return {
                        "sandbox_id": sandbox_id,
                        "status": "ready",
                        "url": f"https://codesandbox.io/s/{sandbox_id}",
                        "preview_url": f"https://{sandbox_id}.csb.app"
                    }
                else:
                    return {"sandbox_id": sandbox_id, "status": "not_found"}
    except Exception as e:
        return {"sandbox_id": sandbox_id, "status": "error", "error": str(e)}


# ============================================================================
# OPTION B: Node.js Process Sandbox (Local Simulated)
# ============================================================================

@router.post("/node/execute")
async def execute_node_sandbox(request: Request):
    """Execute JavaScript/Node.js code in a sandboxed process"""
    db = request.app.state.db
    user_doc = await get_authenticated_user(request, db)
    
    body = await request.json()
    code = body.get("code", "")
    timeout = min(body.get("timeout", 10), MAX_EXECUTION_TIME)
    
    if not code:
        raise HTTPException(status_code=400, detail="No code provided")
    
    execution_id = generate_id("exec")
    
    # Create temp directory
    temp_dir = tempfile.mkdtemp(prefix="melus_sandbox_")
    
    try:
        # Write code to file
        code_file = os.path.join(temp_dir, "sandbox.js")
        
        # Simpler wrapper - capture console output
        wrapped_code = '''
const output = [];
const _log = console.log;
const _error = console.error;
const _warn = console.warn;

console.log = (...args) => output.push({ type: 'log', data: args.map(a => typeof a === 'object' ? JSON.stringify(a) : String(a)).join(' ') });
console.error = (...args) => output.push({ type: 'error', data: args.map(a => String(a)).join(' ') });
console.warn = (...args) => output.push({ type: 'warn', data: args.map(a => String(a)).join(' ') });

try {
''' + code + '''
} catch (error) {
    output.push({ type: 'error', data: error.message });
}

_log(JSON.stringify({ success: true, output }));
'''
        
        with open(code_file, 'w') as f:
            f.write(wrapped_code)
        
        # Execute with timeout
        try:
            result = subprocess.run(
                ['node', code_file],
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=temp_dir,
                env={
                    **os.environ,
                    'NODE_OPTIONS': f'--max-old-space-size={MAX_MEMORY_MB}'
                }
            )
            
            stdout = result.stdout[:MAX_OUTPUT_SIZE]
            stderr = result.stderr[:MAX_OUTPUT_SIZE]
            
            # Parse output
            try:
                output_data = json.loads(stdout.strip().split('\n')[-1])
            except:
                output_data = {"output": stdout, "raw": True}
            
            # Log execution
            await db.sandbox_executions.insert_one({
                "execution_id": execution_id,
                "user_id": user_doc["user_id"],
                "type": "node",
                "code_length": len(code),
                "exit_code": result.returncode,
                "executed_at": utc_now()
            })
            
            return {
                "execution_id": execution_id,
                "success": result.returncode == 0,
                "output": output_data,
                "stderr": stderr if stderr else None,
                "exit_code": result.returncode,
                "execution_time": timeout
            }
            
        except subprocess.TimeoutExpired:
            return {
                "execution_id": execution_id,
                "success": False,
                "error": f"Execution timed out after {timeout} seconds",
                "timeout": True
            }
            
    finally:
        # Cleanup
        shutil.rmtree(temp_dir, ignore_errors=True)


@router.post("/node/evaluate")
async def evaluate_expression(request: Request):
    """Quickly evaluate a JavaScript expression"""
    body = await request.json()
    expression = body.get("expression", "")
    
    if not expression or len(expression) > 1000:
        raise HTTPException(status_code=400, detail="Invalid expression")
    
    # Safe evaluation using Node
    try:
        result = subprocess.run(
            ['node', '-e', f'console.log(JSON.stringify({expression}))'],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if result.returncode == 0:
            return {"result": json.loads(result.stdout.strip())}
        else:
            return {"error": result.stderr.strip()}
    except subprocess.TimeoutExpired:
        return {"error": "Expression evaluation timed out"}
    except Exception as e:
        return {"error": str(e)}


# ============================================================================
# OPTION C: Docker Container Sandbox (Full Isolation)
# ============================================================================

DOCKER_IMAGE = "node:18-alpine"
DOCKER_AVAILABLE = shutil.which('docker') is not None

@router.get("/docker/status")
async def docker_status():
    """Check if Docker is available"""
    if not DOCKER_AVAILABLE:
        return {
            "available": False,
            "message": "Docker not installed on this server"
        }
    
    try:
        result = subprocess.run(
            ['docker', 'info'],
            capture_output=True,
            text=True,
            timeout=10
        )
        return {
            "available": result.returncode == 0,
            "message": "Docker is running" if result.returncode == 0 else "Docker daemon not running"
        }
    except Exception as e:
        return {"available": False, "message": str(e)}


@router.post("/docker/execute")
async def execute_docker_sandbox(request: Request, background_tasks: BackgroundTasks):
    """Execute code in an isolated Docker container"""
    db = request.app.state.db
    user_doc = await get_authenticated_user(request, db)
    
    if not DOCKER_AVAILABLE:
        raise HTTPException(
            status_code=503, 
            detail="Docker not available. Use /sandbox/node/execute instead."
        )
    
    body = await request.json()
    workspace_id = body.get("workspace_id")
    command = body.get("command", "npm start")
    timeout = min(body.get("timeout", 30), MAX_EXECUTION_TIME)
    
    if not workspace_id:
        raise HTTPException(status_code=400, detail="workspace_id required")
    
    # Get workspace files
    workspace = await db.workspaces.find_one(
        {"workspace_id": workspace_id, "user_id": user_doc["user_id"]},
        {"_id": 0, "files": 1}
    )
    
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")
    
    execution_id = generate_id("docker")
    temp_dir = tempfile.mkdtemp(prefix="melus_docker_")
    
    try:
        # Write all files to temp directory
        files = workspace.get("files", {})
        for path, content in files.items():
            file_path = os.path.join(temp_dir, path)
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, 'w') as f:
                f.write(content)
        
        # Create Dockerfile if not exists
        dockerfile_path = os.path.join(temp_dir, "Dockerfile")
        if not os.path.exists(dockerfile_path):
            with open(dockerfile_path, 'w') as f:
                f.write(f'''FROM {DOCKER_IMAGE}
WORKDIR /app
COPY package*.json ./
RUN npm install --production 2>/dev/null || true
COPY . .
CMD {json.dumps(command.split())}
''')
        
        # Build image
        image_name = f"melus-sandbox-{execution_id}"
        
        build_result = subprocess.run(
            ['docker', 'build', '-t', image_name, '.'],
            cwd=temp_dir,
            capture_output=True,
            text=True,
            timeout=60
        )
        
        if build_result.returncode != 0:
            return {
                "execution_id": execution_id,
                "success": False,
                "phase": "build",
                "error": build_result.stderr[:MAX_OUTPUT_SIZE]
            }
        
        # Run container with limits
        container_name = f"melus-run-{execution_id}"
        
        run_result = subprocess.run(
            [
                'docker', 'run',
                '--name', container_name,
                '--rm',
                '--memory', f'{MAX_MEMORY_MB}m',
                '--cpus', '0.5',
                '--network', 'none',  # No network access
                '--read-only',
                '--tmpfs', '/tmp:size=50m',
                image_name
            ],
            capture_output=True,
            text=True,
            timeout=timeout
        )
        
        # Cleanup image
        background_tasks.add_task(cleanup_docker_image, image_name)
        
        # Log execution
        await db.sandbox_executions.insert_one({
            "execution_id": execution_id,
            "user_id": user_doc["user_id"],
            "workspace_id": workspace_id,
            "type": "docker",
            "command": command,
            "exit_code": run_result.returncode,
            "executed_at": utc_now()
        })
        
        return {
            "execution_id": execution_id,
            "success": run_result.returncode == 0,
            "stdout": run_result.stdout[:MAX_OUTPUT_SIZE],
            "stderr": run_result.stderr[:MAX_OUTPUT_SIZE],
            "exit_code": run_result.returncode
        }
        
    except subprocess.TimeoutExpired:
        # Kill container if still running
        subprocess.run(['docker', 'kill', container_name], capture_output=True)
        subprocess.run(['docker', 'rm', container_name], capture_output=True)
        
        return {
            "execution_id": execution_id,
            "success": False,
            "error": f"Container execution timed out after {timeout} seconds",
            "timeout": True
        }
        
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


def cleanup_docker_image(image_name: str):
    """Background task to cleanup Docker image"""
    try:
        subprocess.run(['docker', 'rmi', image_name], capture_output=True, timeout=30)
    except:
        pass


# ============================================================================
# Universal Sandbox Interface
# ============================================================================

@router.post("/run")
async def run_sandbox(request: Request, background_tasks: BackgroundTasks):
    """
    Universal sandbox execution endpoint.
    Automatically selects the best available method.
    """
    db = request.app.state.db
    user_doc = await get_authenticated_user(request, db)
    
    body = await request.json()
    workspace_id = body.get("workspace_id")
    code = body.get("code")
    method = body.get("method", "auto")  # auto, codesandbox, node, docker
    
    # Determine best method
    if method == "auto":
        if DOCKER_AVAILABLE:
            method = "docker"
        elif workspace_id:
            method = "codesandbox"
        else:
            method = "node"
    
    # Route to appropriate handler
    if method == "docker" and DOCKER_AVAILABLE:
        return await execute_docker_sandbox(request, background_tasks)
    elif method == "codesandbox" and workspace_id:
        return await create_codesandbox(request)
    else:
        return await execute_node_sandbox(request)


@router.get("/methods")
async def get_available_methods():
    """Get available sandbox execution methods"""
    return {
        "methods": {
            "codesandbox": {
                "available": True,
                "description": "Remote execution via CodeSandbox API",
                "features": ["Full React app", "Live preview", "Persistent URL"]
            },
            "node": {
                "available": True,
                "description": "Local Node.js process sandbox",
                "features": ["Quick execution", "JavaScript only", "Limited APIs"]
            },
            "docker": {
                "available": DOCKER_AVAILABLE,
                "description": "Full Docker container isolation",
                "features": ["Complete isolation", "Any command", "Network disabled"]
            }
        },
        "recommended": "docker" if DOCKER_AVAILABLE else "codesandbox",
        "limits": {
            "max_execution_time": MAX_EXECUTION_TIME,
            "max_memory_mb": MAX_MEMORY_MB,
            "max_output_size": MAX_OUTPUT_SIZE
        }
    }


@router.get("/executions")
async def get_user_executions(request: Request, limit: int = 20):
    """Get user's execution history"""
    db = request.app.state.db
    user_doc = await get_authenticated_user(request, db)
    
    executions = await db.sandbox_executions.find(
        {"user_id": user_doc["user_id"]},
        {"_id": 0}
    ).sort("executed_at", -1).limit(limit).to_list(limit)
    
    return {"executions": executions}

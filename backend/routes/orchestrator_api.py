"""
MelusAI - Multi-Agent Orchestrator API Routes
Full code generation engine for web apps, 2D/3D games, and mobile applications
"""
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import FileResponse, HTMLResponse
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
import uuid
import os
import asyncio
import json
import logging
from pathlib import Path

from orchestrator_models import (
    Objective, ObjectiveCreate, ObjectiveStatus, ObjectiveType,
    Task, TaskStatus, AgentRole
)
from code_generator import ProjectGenerator, get_full_app_prompt, get_enhancement_prompt, PROJECTS_DIR

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/orchestrator", tags=["orchestrator"])

# ============= LLM INTEGRATION =============

async def call_llm(prompt: str, system_message: str, model: str = "gpt-4o") -> Dict[str, Any]:
    """Call LLM using emergent integrations"""
    try:
        from emergentintegrations.llm.chat import LlmChat, UserMessage
        
        api_key = os.environ.get('EMERGENT_LLM_KEY')
        if not api_key:
            raise ValueError("EMERGENT_LLM_KEY not configured")
        
        chat = LlmChat(
            api_key=api_key,
            session_id=f"task_{uuid.uuid4().hex[:8]}",
            system_message=system_message
        ).with_model("openai", model)
        
        user_message = UserMessage(text=prompt)
        response = await chat.send_message(user_message)
        
        return {
            "success": True,
            "response": response,
            "tokens_used": len(prompt.split()) + len(response.split()) * 2,
            "cost": 0.01
        }
    except Exception as e:
        logger.error(f"LLM call failed: {e}")
        return {
            "success": False,
            "error": str(e),
            "response": None
        }

# ============= CODE AGENT PROMPT =============

CODE_AGENT_PROMPT = """You are the Code Agent for MelusAI - an advanced AI code generation platform.
You write production-quality, complete applications.

CRITICAL RULES:
1. Write COMPLETE, WORKING code - no placeholders, no TODOs, no "// add code here"
2. Every file must be fully functional and ready to run
3. Include ALL imports, dependencies, and configurations
4. Add proper error handling
5. Use modern best practices and clean code principles
6. Make visually appealing UIs with modern design

OUTPUT FORMAT - Always respond with valid JSON:
{
    "files": [
        {"path": "relative/path/to/file.ext", "content": "COMPLETE file content here"}
    ],
    "summary": "Brief description of what was generated"
}

You generate:
- Full-stack web applications (React, Vue, FastAPI, Node.js)
- 2D games (Phaser 3, PixiJS, Canvas)
- 3D games (Three.js, Babylon.js)
- Mobile-first web apps
- Landing pages and marketing sites
- Complete with styling, animations, and interactivity"""

# ============= DEFAULT AGENTS =============

DEFAULT_AGENTS = [
    {"id": "agent_planner", "role": "planner", "name": "Strategic Planner", "model": "gpt-4o", "status": "active", "color": "#0ea5e9"},
    {"id": "agent_research", "role": "research", "name": "Research Agent", "model": "gpt-4o", "status": "active", "color": "#f97316"},
    {"id": "agent_reasoning", "role": "reasoning", "name": "Architecture Agent", "model": "gpt-4o", "status": "active", "color": "#eab308"},
    {"id": "agent_content", "role": "content", "name": "Content Creator", "model": "gpt-4o", "status": "active", "color": "#22c55e"},
    {"id": "agent_code", "role": "code", "name": "Code Agent", "model": "gpt-4o", "status": "active", "color": "#6366f1"},
    {"id": "agent_automation", "role": "automation", "name": "Automation Agent", "model": "gpt-4o", "status": "active", "color": "#0ea5e9"},
    {"id": "agent_qa", "role": "qa", "name": "QA Agent", "model": "gpt-4o", "status": "active", "color": "#10b981"},
    {"id": "agent_security", "role": "security", "name": "Security Agent", "model": "gpt-4o", "status": "active", "color": "#ef4444"},
    {"id": "agent_optimization", "role": "optimization", "name": "Optimization Agent", "model": "gpt-4o", "status": "active", "color": "#06b6d4"},
    {"id": "agent_cost_control", "role": "cost_control", "name": "Cost Controller", "model": "gpt-4o", "status": "active", "color": "#84cc16"},
]

# ============= DATABASE HELPERS =============

def get_db(request: Request):
    """Get database from request state"""
    return request.app.state.db

async def ensure_indexes(db):
    """Ensure MongoDB indexes exist"""
    await db.orchestrator_objectives.create_index("id", unique=True)
    await db.orchestrator_objectives.create_index("user_id")
    await db.orchestrator_objectives.create_index("status")
    await db.orchestrator_tasks.create_index("id", unique=True)
    await db.orchestrator_tasks.create_index("objective_id")
    await db.orchestrator_agents.create_index("id", unique=True)

async def init_agents_if_empty(db):
    """Initialize default agents if none exist"""
    count = await db.orchestrator_agents.count_documents({})
    if count == 0:
        for agent in DEFAULT_AGENTS:
            agent_doc = {
                **agent,
                "tasks_completed": 0,
                "success_rate": 100,
                "avg_cost": 0,
                "reputation_score": 100,
                "created_at": datetime.now(timezone.utc).isoformat()
            }
            await db.orchestrator_agents.insert_one(agent_doc)

# ============= PROJECT TYPE DETECTION =============

def detect_project_type(description: str) -> str:
    """Detect the type of project from description"""
    desc_lower = description.lower()
    
    if any(word in desc_lower for word in ["3d", "three.js", "babylon", "webgl", "3d game"]):
        return "game_3d"
    elif any(word in desc_lower for word in ["2d game", "phaser", "pixi", "canvas game", "platformer", "shooter", "arcade"]):
        return "game_2d"
    elif any(word in desc_lower for word in ["mobile", "react native", "flutter", "ios", "android", "app store"]):
        return "mobile_app"
    elif any(word in desc_lower for word in ["landing", "landing page", "marketing", "portfolio", "one page"]):
        return "landing_page"
    else:
        return "web_app"

# ============= OBJECTIVES ENDPOINTS =============

@router.post("/objectives")
async def create_objective(data: ObjectiveCreate, request: Request):
    """Create a new objective/project"""
    db = get_db(request)
    await ensure_indexes(db)
    await init_agents_if_empty(db)
    
    obj_id = f"obj_{uuid.uuid4().hex[:12]}"
    project_type = detect_project_type(data.description)
    
    objective = {
        "id": obj_id,
        "title": data.title,
        "description": data.description,
        "type": data.type.value,
        "project_type": project_type,
        "priority": data.priority,
        "status": "pending",
        "cost_budget": data.cost_budget,
        "cost_used": 0,
        "auto_mode": data.auto_mode,
        "quality_score": None,
        "project_path": None,
        "generated_files": [],
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat()
    }
    
    await db.orchestrator_objectives.insert_one(objective)
    objective.pop("_id", None)
    return objective

@router.get("/objectives")
async def get_objectives(request: Request):
    """Get all objectives"""
    db = get_db(request)
    objectives = await db.orchestrator_objectives.find({}, {"_id": 0}).to_list(100)
    return objectives

@router.get("/objectives/{objective_id}")
async def get_objective(objective_id: str, request: Request):
    """Get a specific objective with its tasks"""
    db = get_db(request)
    
    objective = await db.orchestrator_objectives.find_one({"id": objective_id}, {"_id": 0})
    if not objective:
        raise HTTPException(status_code=404, detail="Objective not found")
    
    tasks = await db.orchestrator_tasks.find({"objective_id": objective_id}, {"_id": 0}).to_list(100)
    
    return {
        "objective": objective,
        "tasks": tasks,
        "task_count": len(tasks),
        "completed_tasks": len([t for t in tasks if t.get("status") == "completed"])
    }

@router.post("/objectives/{objective_id}/start")
async def start_objective(objective_id: str, request: Request):
    """Start processing an objective - generates the complete application"""
    db = get_db(request)
    
    objective = await db.orchestrator_objectives.find_one({"id": objective_id})
    if not objective:
        raise HTTPException(status_code=404, detail="Objective not found")
    
    # Update status to running
    await db.orchestrator_objectives.update_one(
        {"id": objective_id},
        {"$set": {"status": "in_progress", "updated_at": datetime.now(timezone.utc).isoformat()}}
    )
    
    # Initialize project generator
    generator = ProjectGenerator(db)
    
    # Create project directory and initialize structure
    init_result = await generator.initialize_project_structure(
        objective_id,
        objective.get("project_type", "web_app"),
        objective["title"]
    )
    
    # Create the main generation task
    task_id = f"task_{uuid.uuid4().hex[:12]}"
    task = {
        "id": task_id,
        "objective_id": objective_id,
        "title": "Generate Complete Application",
        "agent_role": "code",
        "agent_id": "agent_code",
        "phase": 1,
        "status": "queued",
        "progress": 0,
        "input_data": {
            "objective_title": objective["title"],
            "objective_description": objective["description"],
            "project_type": objective.get("project_type", "web_app"),
            "project_path": init_result["project_dir"]
        },
        "output_data": None,
        "generated_files": [],
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    await db.orchestrator_tasks.insert_one(task)
    
    # Start generation in background
    asyncio.create_task(generate_complete_application(db, objective_id, task_id, generator))
    
    return {
        "status": "started",
        "objective_id": objective_id,
        "project_type": objective.get("project_type"),
        "project_path": init_result["project_dir"],
        "message": "Generation started. Check the Tasks tab for progress."
    }

async def generate_complete_application(db, objective_id: str, task_id: str, generator: ProjectGenerator):
    """Generate the complete application using LLM"""
    try:
        # Get objective details
        objective = await db.orchestrator_objectives.find_one({"id": objective_id})
        if not objective:
            return
        
        # Update task status
        await db.orchestrator_tasks.update_one(
            {"id": task_id},
            {"$set": {"status": "running", "started_at": datetime.now(timezone.utc).isoformat()}}
        )
        
        # Generate the application
        project_type = objective.get("project_type", "web_app")
        prompt = get_full_app_prompt(project_type, objective["description"], objective["title"])
        
        result = await call_llm(prompt, CODE_AGENT_PROMPT)
        
        if result["success"]:
            response = result["response"]
            
            # Parse generated files
            files = parse_generated_files(response)
            
            # Save all files to project directory
            saved_files = []
            for file in files:
                if file.get("path") and file.get("content"):
                    success = await generator.save_generated_file(
                        objective_id,
                        file["path"],
                        file["content"]
                    )
                    if success:
                        saved_files.append(file)
            
            # Update task
            await db.orchestrator_tasks.update_one(
                {"id": task_id},
                {"$set": {
                    "status": "completed",
                    "output_data": {"response": response[:10000], "files_count": len(saved_files)},
                    "generated_files": [{"path": f["path"]} for f in saved_files],
                    "completed_at": datetime.now(timezone.utc).isoformat()
                }}
            )
            
            # Update objective
            await db.orchestrator_objectives.update_one(
                {"id": objective_id},
                {"$set": {
                    "status": "completed",
                    "generated_files": [{"path": f["path"]} for f in saved_files],
                    "completed_at": datetime.now(timezone.utc).isoformat()
                }}
            )
            
            logger.info(f"Generated {len(saved_files)} files for objective {objective_id}")
            
        else:
            await db.orchestrator_tasks.update_one(
                {"id": task_id},
                {"$set": {
                    "status": "failed",
                    "error_message": result.get("error", "Unknown error"),
                    "completed_at": datetime.now(timezone.utc).isoformat()
                }}
            )
            
            await db.orchestrator_objectives.update_one(
                {"id": objective_id},
                {"$set": {"status": "failed"}}
            )
            
    except Exception as e:
        logger.error(f"Error generating application: {e}")
        await db.orchestrator_objectives.update_one(
            {"id": objective_id},
            {"$set": {"status": "failed", "error": str(e)}}
        )

def parse_generated_files(response: str) -> List[Dict[str, str]]:
    """Parse generated files from LLM response"""
    files = []
    
    try:
        # Try to find JSON in response
        import re
        
        # Look for JSON object with files array
        json_patterns = [
            r'\{[^{}]*"files"\s*:\s*\[.*?\][^{}]*\}',
            r'```json\s*(\{.*?\})\s*```',
            r'```\s*(\{.*?"files".*?\})\s*```'
        ]
        
        for pattern in json_patterns:
            matches = re.findall(pattern, response, re.DOTALL)
            for match in matches:
                try:
                    data = json.loads(match if isinstance(match, str) else match)
                    if "files" in data:
                        files.extend(data["files"])
                        break
                except json.JSONDecodeError:
                    continue
            if files:
                break
        
        # If no JSON found, try to extract code blocks with file paths
        if not files:
            # Pattern: ```language // filepath or # filepath
            code_block_pattern = r'```(\w+)?\s*(?://|#|<!--)\s*([^\n]+?)\s*(?:-->)?\n(.*?)```'
            blocks = re.findall(code_block_pattern, response, re.DOTALL)
            
            for lang, path, content in blocks:
                path = path.strip()
                if path and not path.startswith('http'):
                    files.append({
                        "path": path,
                        "content": content.strip()
                    })
        
        # Also check for file content markers
        if not files:
            # Pattern: File: path/to/file.ext followed by code
            file_marker_pattern = r'(?:File|Path|Filename):\s*[`"]?([^\n`"]+)[`"]?\s*\n```\w*\n(.*?)```'
            markers = re.findall(file_marker_pattern, response, re.DOTALL)
            
            for path, content in markers:
                files.append({
                    "path": path.strip(),
                    "content": content.strip()
                })
                
    except Exception as e:
        logger.error(f"Error parsing files: {e}")
    
    return files

@router.post("/objectives/{objective_id}/pause")
async def pause_objective(objective_id: str, request: Request):
    """Pause an objective"""
    db = get_db(request)
    
    result = await db.orchestrator_objectives.update_one(
        {"id": objective_id},
        {"$set": {"status": "paused", "updated_at": datetime.now(timezone.utc).isoformat()}}
    )
    
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Objective not found")
    
    return {"status": "paused"}

# ============= TASKS ENDPOINTS =============

@router.get("/tasks")
async def get_tasks(request: Request, objective_id: Optional[str] = None):
    """Get tasks, optionally filtered by objective"""
    db = get_db(request)
    
    query = {}
    if objective_id:
        query["objective_id"] = objective_id
    
    tasks = await db.orchestrator_tasks.find(query, {"_id": 0}).to_list(100)
    return tasks

@router.get("/tasks/{task_id}")
async def get_task(task_id: str, request: Request):
    """Get a specific task"""
    db = get_db(request)
    
    task = await db.orchestrator_tasks.find_one({"id": task_id}, {"_id": 0})
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return task

@router.post("/tasks/{task_id}/execute")
async def execute_single_task(task_id: str, request: Request):
    """Manually execute a single task"""
    db = get_db(request)
    
    task = await db.orchestrator_tasks.find_one({"id": task_id})
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    objective = await db.orchestrator_objectives.find_one({"id": task["objective_id"]})
    if not objective:
        raise HTTPException(status_code=404, detail="Objective not found")
    
    # Update status
    await db.orchestrator_tasks.update_one(
        {"id": task_id},
        {"$set": {"status": "running", "started_at": datetime.now(timezone.utc).isoformat()}}
    )
    
    generator = ProjectGenerator(db)
    
    # Generate using full app prompt
    project_type = objective.get("project_type", "web_app")
    prompt = get_full_app_prompt(project_type, objective["description"], objective["title"])
    
    result = await call_llm(prompt, CODE_AGENT_PROMPT)
    
    if result["success"]:
        files = parse_generated_files(result["response"])
        
        saved_files = []
        for file in files:
            if file.get("path") and file.get("content"):
                success = await generator.save_generated_file(
                    task["objective_id"],
                    file["path"],
                    file["content"]
                )
                if success:
                    saved_files.append(file)
        
        await db.orchestrator_tasks.update_one(
            {"id": task_id},
            {"$set": {
                "status": "completed",
                "output_data": {"response": result["response"][:10000], "files_count": len(saved_files)},
                "generated_files": saved_files,
                "completed_at": datetime.now(timezone.utc).isoformat()
            }}
        )
        
        task["status"] = "completed"
        task["generated_files"] = saved_files
    else:
        await db.orchestrator_tasks.update_one(
            {"id": task_id},
            {"$set": {"status": "failed", "error_message": result.get("error")}}
        )
        task["status"] = "failed"
        task["error_message"] = result.get("error")
    
    task.pop("_id", None)
    return task

# ============= AGENTS ENDPOINTS =============

@router.get("/agents")
async def get_agents(request: Request):
    """Get all agents"""
    db = get_db(request)
    await init_agents_if_empty(db)
    
    agents = await db.orchestrator_agents.find({}, {"_id": 0}).to_list(20)
    return agents

@router.post("/agents/{agent_id}/toggle")
async def toggle_agent(agent_id: str, request: Request):
    """Toggle agent active status"""
    db = get_db(request)
    
    agent = await db.orchestrator_agents.find_one({"id": agent_id})
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    new_status = "inactive" if agent["status"] == "active" else "active"
    
    await db.orchestrator_agents.update_one(
        {"id": agent_id},
        {"$set": {"status": new_status}}
    )
    
    agent["status"] = new_status
    agent.pop("_id", None)
    return agent

# ============= PROJECT FILES & PREVIEW =============

@router.get("/objectives/{objective_id}/files")
async def get_project_files(objective_id: str, request: Request):
    """Get all files in the project directory"""
    db = get_db(request)
    
    generator = ProjectGenerator(db)
    files = await generator.get_project_files(objective_id)
    
    return {"files": files, "count": len(files)}

@router.get("/objectives/{objective_id}/download")
async def download_project(objective_id: str, request: Request):
    """Download project as ZIP"""
    db = get_db(request)
    
    generator = ProjectGenerator(db)
    zip_path = await generator.create_zip(objective_id)
    
    if not zip_path or not Path(zip_path).exists():
        raise HTTPException(status_code=404, detail="Project not found or empty")
    
    return FileResponse(
        zip_path,
        media_type="application/zip",
        filename=f"project_{objective_id[:8]}.zip"
    )

@router.get("/preview/{objective_id}")
async def preview_project(objective_id: str, request: Request):
    """Preview the generated project (serves index.html)"""
    db = get_db(request)
    
    objective = await db.orchestrator_objectives.find_one({"id": objective_id})
    if not objective or not objective.get("project_path"):
        raise HTTPException(status_code=404, detail="Project not found")
    
    project_dir = Path(objective["project_path"])
    index_path = project_dir / "index.html"
    
    if not index_path.exists():
        raise HTTPException(status_code=404, detail="No index.html found")
    
    with open(index_path, 'r') as f:
        content = f.read()
    
    return HTMLResponse(content=content)

@router.get("/preview/{objective_id}/{path:path}")
async def serve_project_file(objective_id: str, path: str, request: Request):
    """Serve static files from the project"""
    db = get_db(request)
    
    objective = await db.orchestrator_objectives.find_one({"id": objective_id})
    if not objective or not objective.get("project_path"):
        raise HTTPException(status_code=404, detail="Project not found")
    
    project_dir = Path(objective["project_path"])
    file_path = project_dir / path
    
    if not file_path.exists() or not file_path.is_file():
        raise HTTPException(status_code=404, detail="File not found")
    
    # Determine content type
    suffix = file_path.suffix.lower()
    content_types = {
        ".html": "text/html",
        ".css": "text/css",
        ".js": "application/javascript",
        ".json": "application/json",
        ".png": "image/png",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".gif": "image/gif",
        ".svg": "image/svg+xml",
        ".ico": "image/x-icon"
    }
    
    return FileResponse(file_path, media_type=content_types.get(suffix, "text/plain"))

# ============= DASHBOARD STATS =============

@router.get("/stats")
async def get_dashboard_stats(request: Request):
    """Get dashboard statistics"""
    db = get_db(request)
    await init_agents_if_empty(db)
    
    total_objectives = await db.orchestrator_objectives.count_documents({})
    active_objectives = await db.orchestrator_objectives.count_documents({"status": "in_progress"})
    completed_objectives = await db.orchestrator_objectives.count_documents({"status": "completed"})
    
    total_tasks = await db.orchestrator_tasks.count_documents({})
    completed_tasks = await db.orchestrator_tasks.count_documents({"status": "completed"})
    running_tasks = await db.orchestrator_tasks.count_documents({"status": "running"})
    
    agents = await db.orchestrator_agents.find({}, {"_id": 0}).to_list(20)
    active_agents = len([a for a in agents if a.get("status") == "active"])
    
    pipeline = [{"$group": {"_id": None, "total": {"$sum": "$cost_used"}}}]
    cost_result = await db.orchestrator_objectives.aggregate(pipeline).to_list(1)
    total_cost = cost_result[0]["total"] if cost_result else 0
    
    return {
        "objectives": {
            "total": total_objectives,
            "active": active_objectives,
            "completed": completed_objectives
        },
        "tasks": {
            "total": total_tasks,
            "completed": completed_tasks,
            "running": running_tasks,
            "queued": total_tasks - completed_tasks - running_tasks
        },
        "agents": {
            "total": len(agents),
            "active": active_agents,
            "list": agents
        },
        "cost": {
            "total": total_cost,
            "average_per_objective": total_cost / total_objectives if total_objectives > 0 else 0
        },
        "performance": {
            "avg_quality_score": 0.85,
            "tasks_per_hour": 12,
            "success_rate": 95
        }
    }

@router.get("/activity")
async def get_recent_activity(request: Request):
    """Get recent activity log"""
    db = get_db(request)
    
    activities = []
    
    tasks = await db.orchestrator_tasks.find({}, {"_id": 0}).sort("created_at", -1).to_list(15)
    for task in tasks:
        activities.append({
            "type": "task",
            "action": task.get("status"),
            "title": task.get("title"),
            "agent": task.get("agent_role"),
            "timestamp": task.get("created_at")
        })
    
    objectives = await db.orchestrator_objectives.find({}, {"_id": 0}).sort("created_at", -1).to_list(5)
    for obj in objectives:
        activities.append({
            "type": "objective",
            "action": obj.get("status"),
            "title": obj.get("title"),
            "timestamp": obj.get("created_at")
        })
    
    activities.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
    
    return activities[:15]

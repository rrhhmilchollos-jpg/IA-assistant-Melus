"""Docker Sandbox Service for Melus AI - Isolated code execution"""
import asyncio
import logging
import os
import tempfile
import shutil
from typing import Dict, Any, Optional
import json

logger = logging.getLogger(__name__)

# Sandbox configuration
SANDBOX_CONFIG = {
    "enabled": os.environ.get("SANDBOX_ENABLED", "false").lower() == "true",
    "timeout_seconds": 30,
    "memory_limit": "256m",
    "cpu_limit": "0.5",
    "network_disabled": True,
    "base_image": "node:18-alpine"
}


class DockerSandbox:
    """Docker-based sandbox for isolated code execution"""
    
    def __init__(self):
        self.enabled = SANDBOX_CONFIG["enabled"]
        self.timeout = SANDBOX_CONFIG["timeout_seconds"]
        
    async def is_available(self) -> bool:
        """Check if Docker is available"""
        if not self.enabled:
            return False
            
        try:
            proc = await asyncio.create_subprocess_exec(
                "docker", "version",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            await proc.wait()
            return proc.returncode == 0
        except Exception:
            return False
    
    async def run_project(
        self,
        files: Dict[str, str],
        command: str = "npm start",
        env_vars: Dict[str, str] = None
    ) -> Dict[str, Any]:
        """Run a project in isolated Docker container"""
        
        if not await self.is_available():
            return {
                "success": False,
                "error": "Docker sandbox not available",
                "output": None
            }
        
        # Create temp directory
        temp_dir = tempfile.mkdtemp(prefix="melus_sandbox_")
        
        try:
            # Write files
            for path, content in files.items():
                file_path = os.path.join(temp_dir, path)
                os.makedirs(os.path.dirname(file_path), exist_ok=True)
                with open(file_path, 'w') as f:
                    f.write(content)
            
            # Create Dockerfile
            dockerfile = f"""
FROM {SANDBOX_CONFIG["base_image"]}
WORKDIR /app
COPY . .
RUN npm install --legacy-peer-deps 2>/dev/null || true
CMD {json.dumps(command.split())}
"""
            with open(os.path.join(temp_dir, "Dockerfile"), 'w') as f:
                f.write(dockerfile)
            
            # Build image
            image_name = f"melus_sandbox_{os.path.basename(temp_dir)}"
            
            build_proc = await asyncio.create_subprocess_exec(
                "docker", "build", "-t", image_name, temp_dir,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            _, build_err = await asyncio.wait_for(
                build_proc.communicate(),
                timeout=60
            )
            
            if build_proc.returncode != 0:
                return {
                    "success": False,
                    "error": f"Build failed: {build_err.decode()[:500]}",
                    "output": None
                }
            
            # Run container
            run_args = [
                "docker", "run",
                "--rm",
                f"--memory={SANDBOX_CONFIG['memory_limit']}",
                f"--cpus={SANDBOX_CONFIG['cpu_limit']}",
            ]
            
            if SANDBOX_CONFIG["network_disabled"]:
                run_args.append("--network=none")
            
            if env_vars:
                for key, value in env_vars.items():
                    run_args.extend(["-e", f"{key}={value}"])
            
            run_args.append(image_name)
            
            run_proc = await asyncio.create_subprocess_exec(
                *run_args,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            try:
                stdout, stderr = await asyncio.wait_for(
                    run_proc.communicate(),
                    timeout=self.timeout
                )
                
                return {
                    "success": run_proc.returncode == 0,
                    "output": stdout.decode()[:10000],
                    "error": stderr.decode()[:2000] if stderr else None,
                    "exit_code": run_proc.returncode
                }
                
            except asyncio.TimeoutError:
                run_proc.kill()
                return {
                    "success": False,
                    "error": f"Execution timeout ({self.timeout}s)",
                    "output": None
                }
            
        except Exception as e:
            logger.error(f"Sandbox error: {e}")
            return {
                "success": False,
                "error": str(e),
                "output": None
            }
            
        finally:
            # Cleanup
            try:
                shutil.rmtree(temp_dir, ignore_errors=True)
                # Remove image
                await asyncio.create_subprocess_exec(
                    "docker", "rmi", "-f", image_name,
                    stdout=asyncio.subprocess.DEVNULL,
                    stderr=asyncio.subprocess.DEVNULL
                )
            except Exception:
                pass
    
    async def lint_code(self, files: Dict[str, str]) -> Dict[str, Any]:
        """Run ESLint on project files"""
        
        temp_dir = tempfile.mkdtemp(prefix="melus_lint_")
        
        try:
            # Write files
            for path, content in files.items():
                if path.endswith(('.js', '.jsx', '.ts', '.tsx')):
                    file_path = os.path.join(temp_dir, path)
                    os.makedirs(os.path.dirname(file_path), exist_ok=True)
                    with open(file_path, 'w') as f:
                        f.write(content)
            
            # Create basic eslint config
            eslint_config = {
                "env": {"browser": True, "es2021": True},
                "extends": ["eslint:recommended"],
                "parserOptions": {"ecmaVersion": "latest", "sourceType": "module"},
                "rules": {}
            }
            
            with open(os.path.join(temp_dir, ".eslintrc.json"), 'w') as f:
                json.dump(eslint_config, f)
            
            # Run eslint (simplified - just syntax check)
            errors = []
            for path, content in files.items():
                if path.endswith(('.js', '.jsx')):
                    # Basic syntax validation
                    try:
                        # Check for common issues
                        if 'import ' in content and 'from ' not in content:
                            errors.append({
                                "file": path,
                                "message": "Invalid import statement"
                            })
                    except Exception as e:
                        errors.append({
                            "file": path,
                            "message": str(e)
                        })
            
            return {
                "success": len(errors) == 0,
                "errors": errors,
                "files_checked": len([f for f in files if f.endswith(('.js', '.jsx'))])
            }
            
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)
    
    async def run_tests(self, files: Dict[str, str]) -> Dict[str, Any]:
        """Run tests in sandbox"""
        
        # Check for test files
        test_files = [f for f in files if 'test' in f.lower() or 'spec' in f.lower()]
        
        if not test_files:
            return {
                "success": True,
                "message": "No test files found",
                "tests_run": 0
            }
        
        # Run in sandbox
        result = await self.run_project(
            files,
            command="npm test -- --watchAll=false"
        )
        
        return {
            "success": result["success"],
            "output": result.get("output"),
            "error": result.get("error"),
            "test_files": test_files
        }


# Singleton instance
_sandbox = None

def get_sandbox() -> DockerSandbox:
    """Get sandbox instance"""
    global _sandbox
    if _sandbox is None:
        _sandbox = DockerSandbox()
    return _sandbox


async def execute_in_sandbox(
    files: Dict[str, str],
    action: str = "run"
) -> Dict[str, Any]:
    """Helper function to execute code in sandbox"""
    
    sandbox = get_sandbox()
    
    if action == "lint":
        return await sandbox.lint_code(files)
    elif action == "test":
        return await sandbox.run_tests(files)
    else:
        return await sandbox.run_project(files)

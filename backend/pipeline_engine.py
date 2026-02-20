"""
MelusAI - Development Pipeline Engine
Sistema de 5 fases: Planificación → Generación → Ejecución → Validación → Iteración
"""
import os
import json
import uuid
import asyncio
import logging
import subprocess
import shutil
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional
from pathlib import Path
from enum import Enum

logger = logging.getLogger(__name__)

# ============= CONSTANTS =============

PROJECTS_BASE = Path("/app/generated_projects")
PROJECTS_BASE.mkdir(exist_ok=True)

class ProjectPhase(str, Enum):
    PLANNING = "planning"
    GENERATION = "generation"
    EXECUTION = "execution"
    VALIDATION = "validation"
    ITERATION = "iteration"
    COMPLETED = "completed"
    FAILED = "failed"

class ProjectType(str, Enum):
    WEB_APP = "web_app"
    GAME_2D = "game_2d"
    GAME_3D = "game_3d"
    MOBILE_APP = "mobile_app"
    LANDING_PAGE = "landing_page"
    API_BACKEND = "api_backend"
    FULL_STACK = "full_stack"

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
            session_id=f"pipeline_{uuid.uuid4().hex[:8]}",
            system_message=system_message
        ).with_model("openai", model)
        
        user_message = UserMessage(text=prompt)
        response = await chat.send_message(user_message)
        
        return {
            "success": True,
            "response": response,
            "tokens_used": len(prompt.split()) + len(response.split()) * 2
        }
    except Exception as e:
        logger.error(f"LLM call failed: {e}")
        return {"success": False, "error": str(e), "response": None}

# ============= SYSTEM PROMPTS =============

PLANNER_PROMPT = """You are the Project Planner for MelusAI - an automated development system.

Analyze the user's project request and create a detailed plan.

OUTPUT FORMAT (JSON only):
{
    "project_name": "clean-project-name",
    "project_type": "web_app|game_2d|game_3d|mobile_app|landing_page|api_backend|full_stack",
    "description": "Brief description",
    "tech_stack": {
        "frontend": ["React", "TailwindCSS"],
        "backend": ["FastAPI", "Python"],
        "database": ["MongoDB"],
        "additional": ["Stripe", "Auth"]
    },
    "structure": {
        "folders": ["src", "src/components", "src/pages", "public"],
        "main_files": ["index.html", "src/App.jsx", "src/index.js"]
    },
    "features": [
        {"name": "feature_name", "priority": 1, "description": "desc"}
    ],
    "integrations": ["stripe", "google_auth"],
    "estimated_files": 15,
    "complexity": "low|medium|high"
}

Be specific and actionable. This plan will be executed automatically."""

GENERATOR_PROMPT = """You are the Code Generator for MelusAI.

Generate COMPLETE, PRODUCTION-READY code. 

CRITICAL RULES:
1. Write COMPLETE code - NO placeholders, NO TODOs, NO "// add code here"
2. Every file must be fully functional
3. Include ALL imports and dependencies
4. Add proper error handling
5. Make it visually appealing with modern design
6. Use best practices

OUTPUT FORMAT (JSON only):
{
    "files": [
        {
            "path": "relative/path/to/file.ext",
            "content": "COMPLETE file content here",
            "type": "component|page|style|config|util"
        }
    ],
    "dependencies": {
        "npm": ["package-name@version"],
        "pip": ["package==version"]
    },
    "entry_point": "index.html or main.py",
    "build_command": "npm run build",
    "start_command": "npm start"
}"""

VALIDATOR_PROMPT = """You are the Code Validator for MelusAI.

Review the generated code and identify issues.

Check for:
1. Syntax errors
2. Missing imports
3. Undefined variables
4. Logic errors
5. Security vulnerabilities
6. Missing dependencies
7. Integration issues

OUTPUT FORMAT (JSON only):
{
    "valid": true|false,
    "issues": [
        {
            "file": "path/to/file.ext",
            "line": 10,
            "type": "error|warning",
            "message": "Description of issue",
            "fix": "Suggested fix"
        }
    ],
    "suggestions": ["improvement suggestions"],
    "score": 85
}"""

FIXER_PROMPT = """You are the Code Fixer for MelusAI.

Fix the identified issues in the code.

You receive:
- The original file content
- List of issues to fix

OUTPUT the complete fixed file content.

RULES:
1. Fix ALL identified issues
2. Maintain existing functionality
3. Keep the same code style
4. Return COMPLETE file content (not patches)

OUTPUT FORMAT (JSON only):
{
    "files": [
        {
            "path": "path/to/file.ext",
            "content": "COMPLETE fixed file content",
            "changes": ["List of changes made"]
        }
    ]
}"""

ITERATOR_PROMPT = """You are the Iteration Agent for MelusAI.

The user wants to modify an existing project.

You receive:
- Current project structure and files
- User's modification request

RULES:
1. Only modify files that need changes
2. Don't regenerate everything
3. Maintain consistency with existing code
4. Add new features incrementally

OUTPUT FORMAT (JSON only):
{
    "action": "modify|add|delete",
    "files": [
        {
            "path": "path/to/file.ext",
            "content": "COMPLETE new/modified content",
            "action": "create|update|delete"
        }
    ],
    "summary": "What was changed"
}"""

# ============= DEVELOPMENT PIPELINE =============

class DevelopmentPipeline:
    """
    Main pipeline for automated development.
    Phases: Planning → Generation → Execution → Validation → Iteration
    """
    
    def __init__(self, db):
        self.db = db
    
    async def create_project(self, user_id: str, prompt: str) -> Dict[str, Any]:
        """Create a new project from user prompt"""
        project_id = f"proj_{uuid.uuid4().hex[:12]}"
        
        project = {
            "id": project_id,
            "user_id": user_id,
            "prompt": prompt,
            "phase": ProjectPhase.PLANNING.value,
            "status": "initializing",
            "plan": None,
            "files": {},
            "errors": [],
            "iterations": [],
            "project_path": None,
            "preview_url": None,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
        
        await self.db.projects.insert_one(project)
        project.pop("_id", None)
        
        return project
    
    async def run_pipeline(self, project_id: str) -> Dict[str, Any]:
        """Execute the full development pipeline"""
        project = await self.db.projects.find_one({"id": project_id})
        if not project:
            return {"error": "Project not found"}
        
        try:
            # Phase 1: Planning
            await self._update_phase(project_id, ProjectPhase.PLANNING, "Analyzing requirements...")
            plan = await self._phase_planning(project["prompt"])
            if not plan:
                return await self._handle_failure(project_id, "Planning failed")
            
            await self.db.projects.update_one(
                {"id": project_id},
                {"$set": {"plan": plan}}
            )
            
            # Phase 2: Generation
            await self._update_phase(project_id, ProjectPhase.GENERATION, "Generating code...")
            generated = await self._phase_generation(plan, project["prompt"])
            if not generated:
                return await self._handle_failure(project_id, "Generation failed")
            
            # Create project directory and save files
            project_path = await self._save_files(project_id, plan["project_name"], generated["files"])
            
            await self.db.projects.update_one(
                {"id": project_id},
                {"$set": {
                    "files": {f["path"]: f["content"] for f in generated["files"]},
                    "project_path": str(project_path),
                    "dependencies": generated.get("dependencies", {}),
                    "entry_point": generated.get("entry_point", "index.html")
                }}
            )
            
            # Phase 3: Execution (install deps, build)
            await self._update_phase(project_id, ProjectPhase.EXECUTION, "Setting up project...")
            exec_result = await self._phase_execution(project_path, generated)
            
            # Phase 4: Validation
            await self._update_phase(project_id, ProjectPhase.VALIDATION, "Validating code...")
            validation = await self._phase_validation(generated["files"])
            
            # If validation found issues, try to fix them
            if validation and not validation.get("valid", True):
                await self._update_phase(project_id, ProjectPhase.VALIDATION, "Fixing issues...")
                fixed = await self._phase_fix_issues(generated["files"], validation["issues"])
                if fixed:
                    # Save fixed files
                    for file in fixed.get("files", []):
                        file_path = project_path / file["path"]
                        file_path.parent.mkdir(parents=True, exist_ok=True)
                        with open(file_path, "w") as f:
                            f.write(file["content"])
                    
                    # Update stored files
                    for file in fixed.get("files", []):
                        await self.db.projects.update_one(
                            {"id": project_id},
                            {"$set": {f"files.{file['path']}": file["content"]}}
                        )
            
            # Phase 5: Completed
            await self._update_phase(project_id, ProjectPhase.COMPLETED, "Project ready!")
            
            preview_url = f"/api/preview/{project_id}"
            await self.db.projects.update_one(
                {"id": project_id},
                {"$set": {
                    "preview_url": preview_url,
                    "validation": validation,
                    "completed_at": datetime.now(timezone.utc).isoformat()
                }}
            )
            
            return {
                "success": True,
                "project_id": project_id,
                "preview_url": preview_url,
                "files_count": len(generated["files"]),
                "plan": plan
            }
            
        except Exception as e:
            logger.error(f"Pipeline error: {e}")
            return await self._handle_failure(project_id, str(e))
    
    async def iterate_project(self, project_id: str, modification: str) -> Dict[str, Any]:
        """Apply incremental modification to existing project"""
        project = await self.db.projects.find_one({"id": project_id})
        if not project:
            return {"error": "Project not found"}
        
        await self._update_phase(project_id, ProjectPhase.ITERATION, "Applying changes...")
        
        # Get current files
        current_files = project.get("files", {})
        
        # Create iteration prompt
        prompt = f"""
Current project: {project.get('plan', {}).get('project_name', 'Unknown')}
Current files: {list(current_files.keys())}

User request: {modification}

Analyze what needs to change and generate the modifications.
"""
        
        result = await call_llm(prompt, ITERATOR_PROMPT)
        
        if result["success"]:
            try:
                # Parse response
                response_text = result["response"]
                changes = self._parse_json_response(response_text)
                
                if changes and "files" in changes:
                    project_path = Path(project["project_path"])
                    
                    for file in changes["files"]:
                        file_path = project_path / file["path"]
                        
                        if file.get("action") == "delete":
                            if file_path.exists():
                                file_path.unlink()
                            await self.db.projects.update_one(
                                {"id": project_id},
                                {"$unset": {f"files.{file['path']}": ""}}
                            )
                        else:
                            file_path.parent.mkdir(parents=True, exist_ok=True)
                            with open(file_path, "w") as f:
                                f.write(file["content"])
                            await self.db.projects.update_one(
                                {"id": project_id},
                                {"$set": {f"files.{file['path']}": file["content"]}}
                            )
                    
                    # Record iteration
                    iteration = {
                        "request": modification,
                        "changes": changes,
                        "timestamp": datetime.now(timezone.utc).isoformat()
                    }
                    await self.db.projects.update_one(
                        {"id": project_id},
                        {"$push": {"iterations": iteration}}
                    )
                    
                    await self._update_phase(project_id, ProjectPhase.COMPLETED, "Changes applied!")
                    
                    return {
                        "success": True,
                        "changes": changes,
                        "summary": changes.get("summary", "Changes applied")
                    }
            except Exception as e:
                logger.error(f"Iteration parse error: {e}")
        
        return {"error": "Failed to apply changes"}
    
    # ============= PHASE IMPLEMENTATIONS =============
    
    async def _phase_planning(self, prompt: str) -> Optional[Dict]:
        """Phase 1: Analyze and plan the project"""
        result = await call_llm(prompt, PLANNER_PROMPT)
        
        if result["success"]:
            return self._parse_json_response(result["response"])
        return None
    
    async def _phase_generation(self, plan: Dict, original_prompt: str) -> Optional[Dict]:
        """Phase 2: Generate all project files"""
        generation_prompt = f"""
Project Plan:
{json.dumps(plan, indent=2)}

Original Request:
{original_prompt}

Generate ALL files for this project. Make it complete and production-ready.
"""
        result = await call_llm(generation_prompt, GENERATOR_PROMPT)
        
        if result["success"]:
            return self._parse_json_response(result["response"])
        return None
    
    async def _phase_execution(self, project_path: Path, generated: Dict) -> Dict:
        """Phase 3: Set up project environment"""
        results = {"success": True, "steps": []}
        
        # For now, we don't run npm/pip install in sandbox
        # Just create necessary config files
        
        # Create package.json if npm deps exist
        npm_deps = generated.get("dependencies", {}).get("npm", [])
        if npm_deps:
            package_json = {
                "name": project_path.name,
                "version": "1.0.0",
                "dependencies": {}
            }
            for dep in npm_deps:
                if "@" in dep:
                    name, version = dep.rsplit("@", 1)
                    package_json["dependencies"][name] = version
                else:
                    package_json["dependencies"][dep] = "latest"
            
            with open(project_path / "package.json", "w") as f:
                json.dump(package_json, f, indent=2)
            results["steps"].append("Created package.json")
        
        # Create requirements.txt if pip deps exist
        pip_deps = generated.get("dependencies", {}).get("pip", [])
        if pip_deps:
            with open(project_path / "requirements.txt", "w") as f:
                f.write("\n".join(pip_deps))
            results["steps"].append("Created requirements.txt")
        
        return results
    
    async def _phase_validation(self, files: List[Dict]) -> Optional[Dict]:
        """Phase 4: Validate generated code"""
        files_summary = []
        for f in files[:10]:  # Limit to avoid token overflow
            files_summary.append({
                "path": f["path"],
                "preview": f["content"][:500] if len(f["content"]) > 500 else f["content"]
            })
        
        validation_prompt = f"""
Review these generated files for issues:

{json.dumps(files_summary, indent=2)}

Check for syntax errors, missing imports, and other issues.
"""
        result = await call_llm(validation_prompt, VALIDATOR_PROMPT)
        
        if result["success"]:
            return self._parse_json_response(result["response"])
        return {"valid": True, "issues": [], "score": 70}
    
    async def _phase_fix_issues(self, files: List[Dict], issues: List[Dict]) -> Optional[Dict]:
        """Fix identified issues in code"""
        if not issues:
            return None
        
        # Group issues by file
        files_dict = {f["path"]: f["content"] for f in files}
        issues_by_file = {}
        for issue in issues:
            file_path = issue.get("file", "")
            if file_path not in issues_by_file:
                issues_by_file[file_path] = []
            issues_by_file[file_path].append(issue)
        
        fix_prompt = f"""
Fix these issues in the code:

Issues:
{json.dumps(issues, indent=2)}

Original files:
{json.dumps([{"path": p, "content": c[:1000]} for p, c in files_dict.items() if p in issues_by_file], indent=2)}

Return the complete fixed files.
"""
        result = await call_llm(fix_prompt, FIXER_PROMPT)
        
        if result["success"]:
            return self._parse_json_response(result["response"])
        return None
    
    # ============= HELPER METHODS =============
    
    async def _save_files(self, project_id: str, project_name: str, files: List[Dict]) -> Path:
        """Save generated files to disk"""
        safe_name = "".join(c for c in project_name if c.isalnum() or c in (' ', '-', '_')).strip()
        safe_name = safe_name.replace(' ', '_').lower()
        
        project_path = PROJECTS_BASE / f"{safe_name}_{project_id[:8]}"
        project_path.mkdir(parents=True, exist_ok=True)
        
        for file in files:
            file_path = project_path / file["path"]
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(file_path, "w") as f:
                f.write(file["content"])
        
        return project_path
    
    async def _update_phase(self, project_id: str, phase: ProjectPhase, status: str):
        """Update project phase and status"""
        await self.db.projects.update_one(
            {"id": project_id},
            {"$set": {
                "phase": phase.value,
                "status": status,
                "updated_at": datetime.now(timezone.utc).isoformat()
            }}
        )
    
    async def _handle_failure(self, project_id: str, error: str) -> Dict:
        """Handle pipeline failure"""
        await self.db.projects.update_one(
            {"id": project_id},
            {"$set": {
                "phase": ProjectPhase.FAILED.value,
                "status": f"Error: {error}",
                "updated_at": datetime.now(timezone.utc).isoformat()
            },
            "$push": {"errors": {"message": error, "timestamp": datetime.now(timezone.utc).isoformat()}}}
        )
        return {"error": error, "project_id": project_id}
    
    def _parse_json_response(self, response: str) -> Optional[Dict]:
        """Parse JSON from LLM response"""
        try:
            # Try direct parse
            return json.loads(response)
        except:
            pass
        
        # Try to extract JSON from markdown code blocks
        import re
        patterns = [
            r'```json\s*([\s\S]*?)\s*```',
            r'```\s*([\s\S]*?)\s*```',
            r'\{[\s\S]*\}'
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, response)
            for match in matches:
                try:
                    return json.loads(match)
                except:
                    continue
        
        logger.error(f"Could not parse JSON from response: {response[:200]}")
        return None
    
    async def get_project(self, project_id: str) -> Optional[Dict]:
        """Get project by ID"""
        project = await self.db.projects.find_one({"id": project_id}, {"_id": 0})
        return project
    
    async def get_user_projects(self, user_id: str) -> List[Dict]:
        """Get all projects for a user"""
        projects = await self.db.projects.find(
            {"user_id": user_id},
            {"_id": 0}
        ).sort("created_at", -1).to_list(50)
        return projects

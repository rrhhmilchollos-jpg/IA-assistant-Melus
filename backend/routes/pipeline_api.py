"""
MelusAI - Pipeline API Routes
Handles project creation, generation, and iteration
"""
from fastapi import APIRouter, HTTPException, Request, BackgroundTasks
from fastapi.responses import FileResponse, HTMLResponse
from pydantic import BaseModel
from typing import Optional, List
from pathlib import Path
import asyncio
import os

from pipeline_engine import DevelopmentPipeline, ProjectPhase

router = APIRouter(prefix="/api/pipeline", tags=["pipeline"])

# ============= REQUEST MODELS =============

class CreateProjectRequest(BaseModel):
    prompt: str
    mode: str = "e1"  # e1, e1.5, e2

class IterateProjectRequest(BaseModel):
    modification: str

class ChatMessage(BaseModel):
    content: str
    role: str = "user"

class RegenerateFileRequest(BaseModel):
    file_path: str
    instruction: str = ""

# ============= HELPER FUNCTIONS =============

def get_db(request: Request):
    return request.app.state.db

async def get_user_id(request: Request) -> str:
    """Get user ID from session token - validates against DB"""
    token = request.headers.get("X-Session-Token")
    if not token:
        return "anonymous"
    
    db = get_db(request)
    user = await db.users.find_one({"session_token": token}, {"user_id": 1})
    
    if user:
        return user["user_id"]
    
    # Fallback to token itself for testing
    return token or "anonymous"

# ============= PROJECT ENDPOINTS =============

@router.post("/projects")
async def create_project(
    data: CreateProjectRequest,
    request: Request,
    background_tasks: BackgroundTasks
):
    """
    Create a new project from user prompt.
    Starts the development pipeline in background.
    """
    db = get_db(request)
    user_id = await get_user_id(request)
    
    pipeline = DevelopmentPipeline(db)
    
    # Create project record
    project = await pipeline.create_project(user_id, data.prompt)
    
    # Start pipeline in background
    background_tasks.add_task(pipeline.run_pipeline, project["id"])
    
    return {
        "project_id": project["id"],
        "status": "started",
        "message": "Project creation started. Check status for updates."
    }

@router.get("/projects")
async def get_user_projects(request: Request):
    """Get all projects for current user"""
    db = get_db(request)
    user_id = await get_user_id(request)
    
    pipeline = DevelopmentPipeline(db)
    projects = await pipeline.get_user_projects(user_id)
    
    # Return summary info only - filter out invalid projects
    result = []
    for p in projects:
        if not p.get("id"):
            continue
        result.append({
            "id": p["id"],
            "prompt": p.get("prompt", "")[:100] + "..." if len(p.get("prompt", "")) > 100 else p.get("prompt", ""),
            "phase": p.get("phase", "unknown"),
            "status": p.get("status", "unknown"),
            "plan": p.get("plan", {}),
            "preview_url": p.get("preview_url"),
            "files_count": len(p.get("files", {})),
            "created_at": p.get("created_at")
        })
    return result

@router.get("/projects/{project_id}")
async def get_project(project_id: str, request: Request):
    """Get full project details"""
    db = get_db(request)
    
    pipeline = DevelopmentPipeline(db)
    project = await pipeline.get_project(project_id)
    
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    return project

@router.get("/projects/{project_id}/status")
async def get_project_status(project_id: str, request: Request):
    """Get project status (for polling during generation)"""
    db = get_db(request)
    
    project = await db.projects.find_one(
        {"id": project_id},
        {"_id": 0, "id": 1, "phase": 1, "status": 1, "preview_url": 1, "errors": 1}
    )
    
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    return project

@router.post("/projects/{project_id}/iterate")
async def iterate_project(
    project_id: str,
    data: IterateProjectRequest,
    request: Request,
    background_tasks: BackgroundTasks
):
    """
    Apply modification to existing project.
    Only changes what's necessary.
    """
    db = get_db(request)
    
    pipeline = DevelopmentPipeline(db)
    project = await pipeline.get_project(project_id)
    
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    if project["phase"] not in [ProjectPhase.COMPLETED.value, ProjectPhase.ITERATION.value]:
        raise HTTPException(
            status_code=400,
            detail="Project must be completed before iteration"
        )
    
    # Run iteration in background
    background_tasks.add_task(pipeline.iterate_project, project_id, data.modification)
    
    return {
        "status": "iterating",
        "message": "Applying changes..."
    }

@router.post("/projects/{project_id}/regenerate-file")
async def regenerate_single_file(project_id: str, data: RegenerateFileRequest, request: Request):
    """Regenerate a single file in the project"""
    db = get_db(request)
    
    project = await db.projects.find_one({"id": project_id})
    
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    files = project.get("files", {})
    
    if data.file_path not in files:
        raise HTTPException(status_code=404, detail="File not found")
    
    current_content = files[data.file_path]
    project_plan = project.get("plan", {})
    
    # Build regeneration prompt
    from emergentintegrations.llm.chat import LlmChat, UserMessage
    
    api_key = os.environ.get('EMERGENT_LLM_KEY')
    if not api_key:
        raise HTTPException(status_code=500, detail="LLM key not configured")
    
    chat = LlmChat(
        api_key=api_key,
        session_id=f"regen_{project_id}_{data.file_path}",
        system_message="""You are an expert code generator. 
Regenerate the given file following the instructions.
Return ONLY the new file content, no explanations or markdown code blocks.
Keep the same file structure and purpose but improve based on the instruction."""
    ).with_model("openai", "gpt-4o")
    
    prompt = f"""Project: {project_plan.get('project_name', 'Web App')}
Project Type: {project_plan.get('project_type', 'web_app')}

File to regenerate: {data.file_path}

Current content:
```
{current_content}
```

Instruction: {data.instruction if data.instruction else 'Improve this file, fix any issues, and make it better.'}

Generate the improved version of this file. Return ONLY the code, no explanations."""

    try:
        response = await chat.send_message(UserMessage(text=prompt))
        
        # Clean the response
        new_content = response.strip()
        
        # Remove markdown code blocks if present
        if new_content.startswith("```"):
            lines = new_content.split("\n")
            # Find first and last ``` lines
            start_idx = 0
            end_idx = len(lines)
            for i, line in enumerate(lines):
                if line.startswith("```") and i == 0:
                    start_idx = 1
                elif line.strip() == "```" and i > 0:
                    end_idx = i
                    break
            new_content = "\n".join(lines[start_idx:end_idx])
        
        # Save to disk and database
        project_path = Path(project.get("project_path", ""))
        if project_path.exists():
            file_path = project_path / data.file_path
            file_path.parent.mkdir(parents=True, exist_ok=True)
            with open(file_path, "w") as f:
                f.write(new_content)
        
        # Update database
        await db.projects.update_one(
            {"id": project_id},
            {"$set": {f"files.{data.file_path}": new_content}}
        )
        
        return {
            "success": True,
            "file_path": data.file_path,
            "content": new_content,
            "summary": f"Regenerated {data.file_path} successfully"
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

@router.get("/projects/{project_id}/files")
async def get_project_files(project_id: str, request: Request):
    """Get all files in a project"""
    db = get_db(request)
    
    project = await db.projects.find_one({"id": project_id}, {"_id": 0, "files": 1, "project_path": 1})
    
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    files = project.get("files", {})
    
    return {
        "files": [
            {
                "path": path,
                "content": content,
                "size": len(content)
            }
            for path, content in files.items()
        ],
        "count": len(files)
    }

@router.get("/projects/{project_id}/download")
async def download_project(project_id: str, request: Request, background_tasks: BackgroundTasks):
    """Download project as ZIP and record feedback"""
    db = get_db(request)
    
    project = await db.projects.find_one({"id": project_id})
    if not project or not project.get("project_path"):
        raise HTTPException(status_code=404, detail="Project not found")
    
    import zipfile
    from pathlib import Path
    
    project_path = Path(project["project_path"])
    if not project_path.exists():
        raise HTTPException(status_code=404, detail="Project files not found")
    
    zip_path = project_path.parent / f"{project_path.name}.zip"
    
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for file_path in project_path.rglob("*"):
            if file_path.is_file():
                arcname = file_path.relative_to(project_path)
                zipf.write(file_path, arcname)
    
    # Record download as positive feedback (in background)
    async def record_download_feedback():
        try:
            from learning.feedback_system import FeedbackSystem
            user_id = await get_user_id(request)
            feedback_system = FeedbackSystem(db)
            await feedback_system.record_download(project_id, user_id)
        except Exception as e:
            pass  # Non-critical, don't fail download
    
    background_tasks.add_task(record_download_feedback)
    
    return FileResponse(
        zip_path,
        media_type="application/zip",
        filename=f"{project_path.name}.zip"
    )

# ============= PREVIEW ENDPOINTS =============

@router.get("/preview/{project_id}")
async def preview_project(project_id: str, request: Request):
    """Serve project preview (index.html)"""
    db = get_db(request)
    
    project = await db.projects.find_one({"id": project_id})
    if not project or not project.get("project_path"):
        raise HTTPException(status_code=404, detail="Project not found")
    
    project_path = Path(project["project_path"])
    entry_point = project.get("entry_point", "index.html")
    index_path = project_path / entry_point
    
    if not index_path.exists():
        # Try to find any HTML file
        html_files = list(project_path.glob("**/*.html"))
        if html_files:
            index_path = html_files[0]
        else:
            raise HTTPException(status_code=404, detail="No preview available")
    
    with open(index_path, 'r') as f:
        content = f.read()
    
    return HTMLResponse(content=content)

@router.get("/preview/{project_id}/{path:path}")
async def serve_project_file(project_id: str, path: str, request: Request):
    """Serve static files from project"""
    db = get_db(request)
    
    project = await db.projects.find_one({"id": project_id})
    if not project or not project.get("project_path"):
        raise HTTPException(status_code=404, detail="Project not found")
    
    project_path = Path(project["project_path"])
    file_path = project_path / path
    
    if not file_path.exists() or not file_path.is_file():
        raise HTTPException(status_code=404, detail="File not found")
    
    # Security check - ensure file is within project
    try:
        file_path.relative_to(project_path)
    except ValueError:
        raise HTTPException(status_code=403, detail="Access denied")
    
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
        ".ico": "image/x-icon",
        ".woff": "font/woff",
        ".woff2": "font/woff2",
        ".ttf": "font/ttf"
    }
    
    return FileResponse(file_path, media_type=content_types.get(suffix, "text/plain"))

# ============= CHAT INTERFACE =============

@router.post("/projects/{project_id}/chat")
async def project_chat(
    project_id: str,
    message: ChatMessage,
    request: Request,
    background_tasks: BackgroundTasks
):
    """
    Chat interface for project control.
    Interprets user messages as project commands.
    """
    db = get_db(request)
    
    pipeline = DevelopmentPipeline(db)
    project = await pipeline.get_project(project_id)
    
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    content = message.content.lower()
    
    # Command detection
    if any(word in content for word in ["add", "añade", "agrega", "include"]):
        # Iteration command
        background_tasks.add_task(pipeline.iterate_project, project_id, message.content)
        return {
            "type": "iteration",
            "message": "Applying changes to your project...",
            "status": "processing"
        }
    
    elif any(word in content for word in ["fix", "corrige", "arregla", "repair"]):
        # Fix command
        background_tasks.add_task(pipeline.iterate_project, project_id, f"Fix: {message.content}")
        return {
            "type": "fix",
            "message": "Fixing the issue...",
            "status": "processing"
        }
    
    elif any(word in content for word in ["change", "cambia", "modify", "modifica"]):
        # Modify command
        background_tasks.add_task(pipeline.iterate_project, project_id, message.content)
        return {
            "type": "modification",
            "message": "Modifying your project...",
            "status": "processing"
        }
    
    elif any(word in content for word in ["status", "estado", "progress"]):
        # Status query
        return {
            "type": "status",
            "message": f"Project is {project['status']}",
            "phase": project["phase"],
            "files_count": len(project.get("files", {}))
        }
    
    else:
        # General iteration
        background_tasks.add_task(pipeline.iterate_project, project_id, message.content)
        return {
            "type": "command",
            "message": "Processing your request...",
            "status": "processing"
        }

# ============= QUICK ACTIONS =============

@router.post("/projects/{project_id}/regenerate")
async def regenerate_project(
    project_id: str,
    request: Request,
    background_tasks: BackgroundTasks
):
    """Regenerate entire project from original prompt"""
    db = get_db(request)
    
    project = await db.projects.find_one({"id": project_id})
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Reset project
    await db.projects.update_one(
        {"id": project_id},
        {"$set": {
            "phase": ProjectPhase.PLANNING.value,
            "status": "Regenerating...",
            "files": {},
            "errors": []
        }}
    )
    
    pipeline = DevelopmentPipeline(db)
    background_tasks.add_task(pipeline.run_pipeline, project_id)
    
    return {"status": "regenerating", "message": "Project regeneration started"}

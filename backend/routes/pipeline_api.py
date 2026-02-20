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
    user_id = get_user_id(request)
    
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
    user_id = get_user_id(request)
    
    pipeline = DevelopmentPipeline(db)
    projects = await pipeline.get_user_projects(user_id)
    
    # Return summary info only
    return [{
        "id": p["id"],
        "prompt": p["prompt"][:100] + "..." if len(p["prompt"]) > 100 else p["prompt"],
        "phase": p["phase"],
        "status": p["status"],
        "plan": p.get("plan", {}),
        "preview_url": p.get("preview_url"),
        "files_count": len(p.get("files", {})),
        "created_at": p["created_at"]
    } for p in projects]

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
async def download_project(project_id: str, request: Request):
    """Download project as ZIP"""
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

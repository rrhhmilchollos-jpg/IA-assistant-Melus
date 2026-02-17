"""Projects routes for Assistant Melus"""
from fastapi import APIRouter, HTTPException, Request
from typing import List, Optional
import logging

from models import ProjectCreate, ProjectResponse
from utils import generate_id, utc_now, get_authenticated_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/projects", tags=["projects"])


@router.get("", response_model=List[ProjectResponse])
async def get_projects(request: Request):
    """Get all user projects"""
    db = request.app.state.db
    user_doc = await get_authenticated_user(request, db)
    user_id = user_doc["user_id"]
    
    projects = await db.projects.find(
        {"user_id": user_id},
        {"_id": 0}
    ).sort("created_at", -1).to_list(100)
    
    return [ProjectResponse(**p) for p in projects]


@router.post("", response_model=ProjectResponse)
async def create_project(request: Request, project_data: ProjectCreate):
    """Create a new project"""
    db = request.app.state.db
    user_doc = await get_authenticated_user(request, db)
    user_id = user_doc["user_id"]
    
    project = {
        "project_id": generate_id("proj"),
        "user_id": user_id,
        "name": project_data.name,
        "description": project_data.description,
        "status": "draft",
        "agent_results": [],
        "files": [],
        "total_credits_used": 0,
        "created_at": utc_now(),
        "updated_at": utc_now()
    }
    
    await db.projects.insert_one(project)
    
    return ProjectResponse(**project)


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(request: Request, project_id: str):
    """Get a specific project"""
    db = request.app.state.db
    user_doc = await get_authenticated_user(request, db)
    user_id = user_doc["user_id"]
    
    project = await db.projects.find_one(
        {"project_id": project_id, "user_id": user_id},
        {"_id": 0}
    )
    
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    return ProjectResponse(**project)


@router.put("/{project_id}")
async def update_project(request: Request, project_id: str, update_data: dict):
    """Update a project"""
    db = request.app.state.db
    user_doc = await get_authenticated_user(request, db)
    user_id = user_doc["user_id"]
    
    # Find project
    project = await db.projects.find_one(
        {"project_id": project_id, "user_id": user_id}
    )
    
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Update allowed fields
    allowed = ["name", "description", "status"]
    update = {k: v for k, v in update_data.items() if k in allowed}
    update["updated_at"] = utc_now()
    
    await db.projects.update_one(
        {"project_id": project_id},
        {"$set": update}
    )
    
    updated = await db.projects.find_one(
        {"project_id": project_id},
        {"_id": 0}
    )
    
    return ProjectResponse(**updated)


@router.delete("/{project_id}")
async def delete_project(request: Request, project_id: str):
    """Delete a project"""
    db = request.app.state.db
    user_doc = await get_authenticated_user(request, db)
    user_id = user_doc["user_id"]
    
    result = await db.projects.delete_one(
        {"project_id": project_id, "user_id": user_id}
    )
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Project not found")
    
    return {"message": "Project deleted"}


@router.get("/{project_id}/files")
async def get_project_files(request: Request, project_id: str):
    """Get generated files for a project"""
    db = request.app.state.db
    user_doc = await get_authenticated_user(request, db)
    user_id = user_doc["user_id"]
    
    project = await db.projects.find_one(
        {"project_id": project_id, "user_id": user_id},
        {"_id": 0}
    )
    
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Extract files from agent results
    files = []
    for result in project.get("agent_results", []):
        agent_result = result.get("result", {})
        if "files" in agent_result:
            for f in agent_result["files"]:
                files.append({
                    "path": f.get("path", "unknown"),
                    "content": f.get("content", ""),
                    "agent": result.get("agent", "unknown")
                })
    
    return {"files": files, "total": len(files)}


@router.post("/{project_id}/download")
async def prepare_download(request: Request, project_id: str):
    """Prepare project for download as ZIP"""
    db = request.app.state.db
    user_doc = await get_authenticated_user(request, db)
    user_id = user_doc["user_id"]
    
    project = await db.projects.find_one(
        {"project_id": project_id, "user_id": user_id},
        {"_id": 0}
    )
    
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Collect all files
    files = []
    for result in project.get("agent_results", []):
        agent_result = result.get("result", {})
        if "files" in agent_result:
            files.extend(agent_result["files"])
    
    return {
        "project_name": project.get("name", "project"),
        "files": files,
        "ready": True
    }

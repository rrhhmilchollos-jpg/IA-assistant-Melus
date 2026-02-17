"""Workspace Management - Virtual File System & Live Preview for Assistant Melus"""
from fastapi import APIRouter, HTTPException, Request, WebSocket, WebSocketDisconnect
from typing import List, Optional, Dict, Any
import logging
import os
import json
import asyncio
from datetime import datetime

from utils import generate_id, utc_now, get_authenticated_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/workspace", tags=["workspace"])

# Active WebSocket connections per project
active_connections: Dict[str, List[WebSocket]] = {}


class ConnectionManager:
    """Manages WebSocket connections for real-time updates"""
    
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}
    
    async def connect(self, websocket: WebSocket, project_id: str):
        await websocket.accept()
        if project_id not in self.active_connections:
            self.active_connections[project_id] = []
        self.active_connections[project_id].append(websocket)
    
    def disconnect(self, websocket: WebSocket, project_id: str):
        if project_id in self.active_connections:
            if websocket in self.active_connections[project_id]:
                self.active_connections[project_id].remove(websocket)
    
    async def broadcast(self, project_id: str, message: dict):
        if project_id in self.active_connections:
            for connection in self.active_connections[project_id]:
                try:
                    await connection.send_json(message)
                except:
                    pass


manager = ConnectionManager()


# Default project templates
TEMPLATES = {
    "react-vite": {
        "package.json": """{
  "name": "generated-app",
  "private": true,
  "version": "0.0.1",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview"
  },
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0"
  },
  "devDependencies": {
    "@vitejs/plugin-react": "^4.0.0",
    "vite": "^4.4.0"
  }
}""",
        "vite.config.js": """import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
})""",
        "index.html": """<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Generated App</title>
    <script src="https://cdn.tailwindcss.com"></script>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.jsx"></script>
  </body>
</html>""",
        "src/main.jsx": """import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App'
import './index.css'

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)""",
        "src/index.css": """@tailwind base;
@tailwind components;
@tailwind utilities;

body {
  margin: 0;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen',
    'Ubuntu', 'Cantarell', 'Fira Sans', 'Droid Sans', 'Helvetica Neue',
    sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}""",
        "src/App.jsx": """import React from 'react'

function App() {
  return (
    <div className="min-h-screen bg-gray-900 text-white flex items-center justify-center">
      <div className="text-center">
        <h1 className="text-4xl font-bold mb-4">Welcome to Your App</h1>
        <p className="text-gray-400">Start building something amazing!</p>
      </div>
    </div>
  )
}

export default App"""
    }
}


@router.post("/create")
async def create_workspace(request: Request):
    """Create a new workspace/project with virtual file system"""
    db = request.app.state.db
    user_doc = await get_authenticated_user(request, db)
    user_id = user_doc["user_id"]
    
    body = await request.json()
    name = body.get("name", "My App")
    description = body.get("description", "")
    template = body.get("template", "react-vite")
    
    # Get template files
    template_files = TEMPLATES.get(template, TEMPLATES["react-vite"])
    
    # Create workspace
    workspace_id = generate_id("ws")
    workspace = {
        "workspace_id": workspace_id,
        "user_id": user_id,
        "name": name,
        "description": description,
        "template": template,
        "files": template_files,
        "versions": [{
            "version": 1,
            "files": template_files,
            "created_at": utc_now(),
            "message": "Initial template"
        }],
        "current_version": 1,
        "status": "active",
        "build_status": "idle",
        "build_logs": [],
        "created_at": utc_now(),
        "updated_at": utc_now()
    }
    
    await db.workspaces.insert_one(workspace)
    
    return {
        "workspace_id": workspace_id,
        "name": name,
        "files": template_files,
        "current_version": 1
    }


@router.get("/{workspace_id}")
async def get_workspace(request: Request, workspace_id: str):
    """Get workspace with all files"""
    db = request.app.state.db
    user_doc = await get_authenticated_user(request, db)
    user_id = user_doc["user_id"]
    
    workspace = await db.workspaces.find_one(
        {"workspace_id": workspace_id, "user_id": user_id},
        {"_id": 0}
    )
    
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")
    
    return workspace


@router.put("/{workspace_id}/files")
async def update_files(request: Request, workspace_id: str):
    """Update files in workspace"""
    db = request.app.state.db
    user_doc = await get_authenticated_user(request, db)
    user_id = user_doc["user_id"]
    
    body = await request.json()
    files = body.get("files", {})
    message = body.get("message", "File update")
    
    workspace = await db.workspaces.find_one(
        {"workspace_id": workspace_id, "user_id": user_id}
    )
    
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")
    
    # Merge files
    current_files = workspace.get("files", {})
    current_files.update(files)
    
    # Create new version
    new_version = workspace.get("current_version", 0) + 1
    
    await db.workspaces.update_one(
        {"workspace_id": workspace_id},
        {
            "$set": {
                "files": current_files,
                "current_version": new_version,
                "updated_at": utc_now()
            },
            "$push": {
                "versions": {
                    "version": new_version,
                    "files": current_files,
                    "created_at": utc_now(),
                    "message": message
                }
            }
        }
    )
    
    # Broadcast update
    await manager.broadcast(workspace_id, {
        "type": "files_updated",
        "files": current_files,
        "version": new_version
    })
    
    return {
        "files": current_files,
        "version": new_version
    }


@router.post("/{workspace_id}/file")
async def create_or_update_file(request: Request, workspace_id: str):
    """Create or update a single file"""
    db = request.app.state.db
    user_doc = await get_authenticated_user(request, db)
    user_id = user_doc["user_id"]
    
    body = await request.json()
    path = body.get("path")
    content = body.get("content", "")
    
    if not path:
        raise HTTPException(status_code=400, detail="File path required")
    
    workspace = await db.workspaces.find_one(
        {"workspace_id": workspace_id, "user_id": user_id}
    )
    
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")
    
    # Update single file
    await db.workspaces.update_one(
        {"workspace_id": workspace_id},
        {
            "$set": {
                f"files.{path}": content,
                "updated_at": utc_now()
            }
        }
    )
    
    # Broadcast file update
    await manager.broadcast(workspace_id, {
        "type": "file_updated",
        "path": path,
        "content": content
    })
    
    return {"path": path, "status": "updated"}


@router.delete("/{workspace_id}/file")
async def delete_file(request: Request, workspace_id: str):
    """Delete a file from workspace"""
    db = request.app.state.db
    user_doc = await get_authenticated_user(request, db)
    user_id = user_doc["user_id"]
    
    body = await request.json()
    path = body.get("path")
    
    if not path:
        raise HTTPException(status_code=400, detail="File path required")
    
    await db.workspaces.update_one(
        {"workspace_id": workspace_id, "user_id": user_id},
        {
            "$unset": {f"files.{path}": ""},
            "$set": {"updated_at": utc_now()}
        }
    )
    
    # Broadcast deletion
    await manager.broadcast(workspace_id, {
        "type": "file_deleted",
        "path": path
    })
    
    return {"path": path, "status": "deleted"}


@router.get("/{workspace_id}/versions")
async def get_versions(request: Request, workspace_id: str):
    """Get all versions of a workspace"""
    db = request.app.state.db
    user_doc = await get_authenticated_user(request, db)
    user_id = user_doc["user_id"]
    
    workspace = await db.workspaces.find_one(
        {"workspace_id": workspace_id, "user_id": user_id},
        {"versions": 1, "current_version": 1}
    )
    
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")
    
    return {
        "versions": workspace.get("versions", []),
        "current_version": workspace.get("current_version", 1)
    }


@router.post("/{workspace_id}/rollback/{version}")
async def rollback_version(request: Request, workspace_id: str, version: int):
    """Rollback workspace to a specific version"""
    db = request.app.state.db
    user_doc = await get_authenticated_user(request, db)
    user_id = user_doc["user_id"]
    
    workspace = await db.workspaces.find_one(
        {"workspace_id": workspace_id, "user_id": user_id}
    )
    
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")
    
    # Find version
    target_version = None
    for v in workspace.get("versions", []):
        if v.get("version") == version:
            target_version = v
            break
    
    if not target_version:
        raise HTTPException(status_code=404, detail="Version not found")
    
    # Rollback
    new_version_num = workspace.get("current_version", 0) + 1
    
    await db.workspaces.update_one(
        {"workspace_id": workspace_id},
        {
            "$set": {
                "files": target_version["files"],
                "current_version": new_version_num,
                "updated_at": utc_now()
            },
            "$push": {
                "versions": {
                    "version": new_version_num,
                    "files": target_version["files"],
                    "created_at": utc_now(),
                    "message": f"Rollback to version {version}"
                }
            }
        }
    )
    
    # Broadcast rollback
    await manager.broadcast(workspace_id, {
        "type": "rollback",
        "files": target_version["files"],
        "version": new_version_num
    })
    
    return {
        "files": target_version["files"],
        "version": new_version_num,
        "rolled_back_to": version
    }


@router.post("/{workspace_id}/log")
async def add_build_log(request: Request, workspace_id: str):
    """Add a build log entry"""
    db = request.app.state.db
    
    body = await request.json()
    log_type = body.get("type", "info")
    message = body.get("message", "")
    agent = body.get("agent", "system")
    data = body.get("data")
    
    log_entry = {
        "id": generate_id("log"),
        "type": log_type,
        "agent": agent,
        "message": message,
        "data": data,
        "timestamp": utc_now().isoformat()
    }
    
    await db.workspaces.update_one(
        {"workspace_id": workspace_id},
        {
            "$push": {"build_logs": log_entry},
            "$set": {"updated_at": utc_now()}
        }
    )
    
    # Broadcast log
    await manager.broadcast(workspace_id, {
        "type": "log",
        "log": log_entry
    })
    
    return log_entry


@router.websocket("/ws/{workspace_id}")
async def websocket_endpoint(websocket: WebSocket, workspace_id: str):
    """WebSocket endpoint for real-time updates"""
    await manager.connect(websocket, workspace_id)
    try:
        while True:
            data = await websocket.receive_text()
            # Handle incoming messages if needed
            message = json.loads(data)
            
            if message.get("type") == "ping":
                await websocket.send_json({"type": "pong"})
            
    except WebSocketDisconnect:
        manager.disconnect(websocket, workspace_id)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(websocket, workspace_id)


# Export manager for use in other modules
def get_connection_manager():
    return manager

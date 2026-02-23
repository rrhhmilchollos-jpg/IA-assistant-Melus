"""
MelusAI - Live Preview System
Serves generated projects for live preview
"""
from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import HTMLResponse, FileResponse, Response
from pathlib import Path
import mimetypes
import os

router = APIRouter(prefix="/api/preview", tags=["preview"])

PROJECTS_BASE = Path("/app/generated_projects")


@router.get("/{project_id}")
async def get_preview(project_id: str, request: Request):
    """Get project preview - serves index.html"""
    db = request.app.state.db
    
    # Find project
    project = await db.projects.find_one({"id": project_id})
    if not project:
        project = await db.projects.find_one({"project_id": project_id})
    
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Check for files in DB
    files = project.get("files", {})
    
    # Look for index.html
    index_content = files.get("index.html")
    if not index_content:
        # Try to find any HTML file
        for path, content in files.items():
            if path.endswith(".html"):
                index_content = content
                break
    
    if index_content:
        # Inject base tag for relative paths
        if "<head>" in index_content:
            base_tag = f'<base href="/api/preview/{project_id}/">'
            index_content = index_content.replace("<head>", f"<head>\n{base_tag}")
        
        return HTMLResponse(content=index_content)
    
    # Generate preview HTML if no index.html
    preview_html = generate_preview_html(project_id, files)
    return HTMLResponse(content=preview_html)


@router.get("/{project_id}/{path:path}")
async def get_preview_file(project_id: str, path: str, request: Request):
    """Get a specific file from the project"""
    db = request.app.state.db
    
    project = await db.projects.find_one({"id": project_id})
    if not project:
        project = await db.projects.find_one({"project_id": project_id})
    
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    files = project.get("files", {})
    
    # Normalize path
    normalized_path = path.lstrip("/")
    
    # Try to find the file
    content = files.get(normalized_path)
    if not content:
        content = files.get(f"src/{normalized_path}")
    if not content:
        content = files.get(path)
    
    if not content:
        raise HTTPException(status_code=404, detail=f"File not found: {path}")
    
    # Determine content type
    mime_type, _ = mimetypes.guess_type(path)
    if not mime_type:
        if path.endswith(".jsx") or path.endswith(".js"):
            mime_type = "application/javascript"
        elif path.endswith(".css"):
            mime_type = "text/css"
        elif path.endswith(".html"):
            mime_type = "text/html"
        else:
            mime_type = "text/plain"
    
    return Response(content=content, media_type=mime_type)


def generate_preview_html(project_id: str, files: dict) -> str:
    """Generate a preview HTML that includes all project files"""
    
    # Find JSX/JS files
    jsx_files = []
    css_content = ""
    
    for path, content in files.items():
        if path.endswith(".jsx") or path.endswith(".js"):
            jsx_files.append({"path": path, "content": content})
        elif path.endswith(".css"):
            css_content += content + "\n"
    
    # Build preview HTML
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Preview - {project_id}</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://unpkg.com/react@18/umd/react.development.js"></script>
    <script src="https://unpkg.com/react-dom@18/umd/react-dom.development.js"></script>
    <script src="https://unpkg.com/@babel/standalone/babel.min.js"></script>
    <style>
        {css_content}
    </style>
</head>
<body>
    <div id="root"></div>
"""
    
    # Add each JSX file
    for jsx in jsx_files:
        html += f"""
    <script type="text/babel">
    {jsx['content']}
    </script>
"""
    
    # Add render call
    html += """
    <script type="text/babel">
        if (typeof App !== 'undefined') {
            ReactDOM.createRoot(document.getElementById('root')).render(<App />);
        }
    </script>
</body>
</html>"""
    
    return html


@router.get("/{project_id}/files")
async def list_preview_files(project_id: str, request: Request):
    """List all files in a project"""
    db = request.app.state.db
    
    project = await db.projects.find_one({"id": project_id})
    if not project:
        project = await db.projects.find_one({"project_id": project_id})
    
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    files = project.get("files", {})
    
    return {
        "project_id": project_id,
        "files": list(files.keys()),
        "file_count": len(files)
    }

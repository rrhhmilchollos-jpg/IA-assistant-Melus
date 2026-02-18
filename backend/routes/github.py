"""GitHub Integration routes for Assistant Melus"""
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import RedirectResponse
from typing import Optional, List
import logging
import os
import secrets
import httpx
from github import Github, GithubException
from github.Auth import Token

from utils import generate_id, utc_now, get_authenticated_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/github", tags=["github"])

# GitHub OAuth Configuration - Users need to provide these
GITHUB_CLIENT_ID = os.environ.get('GITHUB_CLIENT_ID', '')
GITHUB_CLIENT_SECRET = os.environ.get('GITHUB_CLIENT_SECRET', '')

# Store OAuth states temporarily (in production use Redis/cache)
oauth_states = {}


class GitHubManager:
    """Manages GitHub repository operations"""
    
    def __init__(self, access_token: str):
        self.auth = Token(access_token)
        self.gh = Github(auth=self.auth)
    
    def get_user_info(self) -> dict:
        """Get authenticated user info"""
        user = self.gh.get_user()
        return {
            "login": user.login,
            "name": user.name,
            "email": user.email,
            "avatar_url": user.avatar_url,
            "public_repos": user.public_repos,
            "html_url": user.html_url
        }
    
    def list_repositories(self) -> List[dict]:
        """List user's repositories"""
        user = self.gh.get_user()
        repos = user.get_repos()
        return [
            {
                "name": repo.name,
                "full_name": repo.full_name,
                "url": repo.html_url,
                "clone_url": repo.clone_url,
                "private": repo.private,
                "description": repo.description,
                "stars": repo.stargazers_count,
                "language": repo.language,
                "updated_at": repo.updated_at.isoformat() if repo.updated_at else None
            }
            for repo in repos
        ]
    
    def create_repository(
        self,
        name: str,
        description: Optional[str] = None,
        private: bool = False,
        auto_init: bool = True
    ) -> dict:
        """Create a new repository"""
        try:
            user = self.gh.get_user()
            repo = user.create_repo(
                name=name,
                description=description,
                private=private,
                auto_init=auto_init
            )
            return {
                "id": repo.id,
                "name": repo.name,
                "full_name": repo.full_name,
                "url": repo.html_url,
                "clone_url": repo.clone_url,
                "ssh_url": repo.ssh_url,
                "private": repo.private
            }
        except GithubException as e:
            raise Exception(f"Failed to create repository: {str(e)}")
    
    def push_files(
        self,
        repo_name: str,
        files: List[dict],
        commit_message: str = "Initial commit from Assistant Melus",
        branch: str = "main"
    ) -> dict:
        """Push multiple files to a repository"""
        try:
            user = self.gh.get_user()
            repo = user.get_repo(repo_name)
            
            commits = []
            for file_info in files:
                file_path = file_info.get("path", "")
                content = file_info.get("content", "")
                
                if not file_path:
                    continue
                
                try:
                    # Try to get existing file
                    existing = repo.get_contents(file_path, ref=branch)
                    result = repo.update_file(
                        path=file_path,
                        message=f"Update {file_path}",
                        content=content,
                        sha=existing.sha,
                        branch=branch
                    )
                except:
                    # File doesn't exist, create new
                    result = repo.create_file(
                        path=file_path,
                        message=f"Add {file_path}",
                        content=content,
                        branch=branch
                    )
                
                commits.append({
                    "file": file_path,
                    "sha": result["commit"].sha
                })
            
            return {
                "success": True,
                "commits": commits,
                "total_files": len(commits),
                "branch": branch,
                "repo_url": repo.html_url
            }
        except GithubException as e:
            raise Exception(f"Failed to push files: {str(e)}")


def generate_oauth_state() -> str:
    """Generate cryptographically secure state parameter"""
    return secrets.token_urlsafe(32)


@router.get("/auth/login")
async def github_login(request: Request):
    """Initiate GitHub OAuth login"""
    db = request.app.state.db
    user_doc = await get_authenticated_user(request, db)
    user_id = user_doc["user_id"]
    
    if not GITHUB_CLIENT_ID:
        raise HTTPException(
            status_code=400, 
            detail="GitHub integration not configured. Please add GITHUB_CLIENT_ID to environment."
        )
    
    state = generate_oauth_state()
    oauth_states[state] = {
        "user_id": user_id,
        "created_at": utc_now().isoformat()
    }
    
    # Use external URL for callback (from environment or hardcoded)
    external_url = os.environ.get('EXTERNAL_URL', 'https://agent-labs.preview.emergentagent.com')
    redirect_uri = f"{external_url}/api/github/auth/callback"
    
    auth_url = (
        f"https://github.com/login/oauth/authorize?"
        f"client_id={GITHUB_CLIENT_ID}&"
        f"redirect_uri={redirect_uri}&"
        f"scope=repo,user&"
        f"state={state}"
    )
    
    return {"auth_url": auth_url, "state": state}


@router.get("/auth/callback")
async def github_callback(request: Request, code: str, state: str):
    """Handle GitHub OAuth callback"""
    db = request.app.state.db
    
    # Validate state
    if state not in oauth_states:
        raise HTTPException(status_code=400, detail="Invalid state parameter")
    
    state_data = oauth_states.pop(state)
    user_id = state_data["user_id"]
    
    if not GITHUB_CLIENT_SECRET:
        raise HTTPException(
            status_code=400,
            detail="GitHub integration not configured. Please add GITHUB_CLIENT_SECRET."
        )
    
    # Exchange code for access token
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://github.com/login/oauth/access_token",
            data={
                "client_id": GITHUB_CLIENT_ID,
                "client_secret": GITHUB_CLIENT_SECRET,
                "code": code
            },
            headers={"Accept": "application/json"}
        )
        
        if response.status_code != 200:
            raise HTTPException(status_code=400, detail="Failed to exchange code for token")
        
        token_data = response.json()
        access_token = token_data.get("access_token")
        
        if not access_token:
            error = token_data.get("error_description", "Unknown error")
            raise HTTPException(status_code=400, detail=f"GitHub OAuth error: {error}")
    
    # Get GitHub user info
    manager = GitHubManager(access_token)
    github_user = manager.get_user_info()
    
    # Store GitHub connection
    await db.github_connections.update_one(
        {"user_id": user_id},
        {
            "$set": {
                "user_id": user_id,
                "github_token": access_token,
                "github_username": github_user["login"],
                "github_avatar": github_user["avatar_url"],
                "connected_at": utc_now()
            }
        },
        upsert=True
    )
    
    # Redirect to frontend with success
    frontend_url = os.environ.get('FRONTEND_URL', 'https://agent-labs.preview.emergentagent.com')
    return RedirectResponse(url=f"{frontend_url}/dashboard?github=connected")


@router.get("/status")
async def github_status(request: Request):
    """Check GitHub connection status"""
    db = request.app.state.db
    user_doc = await get_authenticated_user(request, db)
    user_id = user_doc["user_id"]
    
    connection = await db.github_connections.find_one(
        {"user_id": user_id},
        {"_id": 0, "github_token": 0}  # Don't expose token
    )
    
    if not connection:
        return {
            "connected": False,
            "message": "GitHub no conectado"
        }
    
    return {
        "connected": True,
        "username": connection.get("github_username"),
        "avatar": connection.get("github_avatar"),
        "connected_at": connection.get("connected_at")
    }


@router.post("/disconnect")
async def disconnect_github(request: Request):
    """Disconnect GitHub account"""
    db = request.app.state.db
    user_doc = await get_authenticated_user(request, db)
    user_id = user_doc["user_id"]
    
    await db.github_connections.delete_one({"user_id": user_id})
    
    return {"message": "GitHub desconectado exitosamente"}


@router.get("/repos")
async def list_github_repos(request: Request):
    """List user's GitHub repositories"""
    db = request.app.state.db
    user_doc = await get_authenticated_user(request, db)
    user_id = user_doc["user_id"]
    
    connection = await db.github_connections.find_one({"user_id": user_id})
    if not connection:
        raise HTTPException(status_code=400, detail="GitHub no conectado")
    
    try:
        manager = GitHubManager(connection["github_token"])
        repos = manager.list_repositories()
        return {"repositories": repos}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/repos/create")
async def create_github_repo(request: Request):
    """Create a new GitHub repository"""
    db = request.app.state.db
    user_doc = await get_authenticated_user(request, db)
    user_id = user_doc["user_id"]
    
    connection = await db.github_connections.find_one({"user_id": user_id})
    if not connection:
        raise HTTPException(status_code=400, detail="GitHub no conectado")
    
    body = await request.json()
    name = body.get("name")
    description = body.get("description", "")
    private = body.get("private", False)
    
    if not name:
        raise HTTPException(status_code=400, detail="Repository name required")
    
    try:
        manager = GitHubManager(connection["github_token"])
        repo = manager.create_repository(
            name=name,
            description=description,
            private=private
        )
        return repo
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/push-project")
async def push_project_to_github(request: Request):
    """Push a generated project to GitHub"""
    db = request.app.state.db
    user_doc = await get_authenticated_user(request, db)
    user_id = user_doc["user_id"]
    
    # Check credits (pushing costs 100 credits)
    PUSH_COST = 100
    if user_doc["credits"] < PUSH_COST:
        raise HTTPException(status_code=402, detail="Créditos insuficientes")
    
    connection = await db.github_connections.find_one({"user_id": user_id})
    if not connection:
        raise HTTPException(status_code=400, detail="GitHub no conectado")
    
    body = await request.json()
    project_id = body.get("project_id")
    repo_name = body.get("repo_name")
    create_new = body.get("create_new", True)
    private = body.get("private", False)
    
    if not project_id:
        raise HTTPException(status_code=400, detail="project_id required")
    
    # Get project
    project = await db.projects.find_one(
        {"project_id": project_id, "user_id": user_id},
        {"_id": 0}
    )
    
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Collect all files from agent results
    files = []
    for result in project.get("agent_results", []):
        agent_result = result.get("result", {})
        if "files" in agent_result:
            for f in agent_result["files"]:
                files.append({
                    "path": f.get("path", ""),
                    "content": f.get("content", "")
                })
    
    # Add README
    readme_content = f"""# {project.get('name', 'Generated App')}

## Description
{project.get('description', 'Generated by Assistant Melus')}

## Generated with Assistant Melus
This project was generated using AI-powered multi-agent architecture.

### Agents Used
- Orchestrator: Project analysis and planning
- Design: UI/UX design
- Frontend: React code generation
- Backend: FastAPI code generation
- Database: Database schema design
- Deploy: Deployment configuration

## Setup
1. Install dependencies
2. Configure environment variables
3. Run the application

---
Generated on {utc_now().strftime('%Y-%m-%d %H:%M:%S')} by [Assistant Melus](https://agent-labs.preview.emergentagent.com)
"""
    files.append({"path": "README.md", "content": readme_content})
    
    try:
        manager = GitHubManager(connection["github_token"])
        
        # Create repository if requested
        final_repo_name = repo_name or project.get("name", "generated-app").lower().replace(" ", "-")
        
        if create_new:
            repo_info = manager.create_repository(
                name=final_repo_name,
                description=project.get("description", ""),
                private=private
            )
        
        # Push files
        push_result = manager.push_files(
            repo_name=final_repo_name,
            files=files,
            commit_message=f"Initial commit: {project.get('name', 'Generated App')}"
        )
        
        # Deduct credits
        new_credits = user_doc["credits"] - PUSH_COST
        await db.users.update_one(
            {"user_id": user_id},
            {
                "$set": {"credits": new_credits},
                "$inc": {"credits_used": PUSH_COST}
            }
        )
        
        # Log usage
        await db.agent_usage.insert_one({
            "usage_id": generate_id("usage"),
            "user_id": user_id,
            "agent_type": "github_push",
            "credits_used": PUSH_COST,
            "project_id": project_id,
            "created_at": utc_now()
        })
        
        # Update project with GitHub info
        await db.projects.update_one(
            {"project_id": project_id},
            {
                "$set": {
                    "github_repo": final_repo_name,
                    "github_url": push_result.get("repo_url"),
                    "pushed_to_github": True,
                    "github_pushed_at": utc_now()
                }
            }
        )
        
        return {
            "success": True,
            "repo_name": final_repo_name,
            "repo_url": push_result.get("repo_url"),
            "files_pushed": push_result.get("total_files"),
            "credits_used": PUSH_COST,
            "credits_remaining": new_credits
        }
        
    except Exception as e:
        logger.error(f"GitHub push error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/push-conversation")
async def push_conversation_code_to_github(request: Request):
    """Push code from a conversation to GitHub"""
    import re
    
    db = request.app.state.db
    user_doc = await get_authenticated_user(request, db)
    user_id = user_doc["user_id"]
    
    PUSH_COST = 50
    if user_doc["credits"] < PUSH_COST:
        raise HTTPException(status_code=402, detail="Créditos insuficientes")
    
    connection = await db.github_connections.find_one({"user_id": user_id})
    if not connection:
        raise HTTPException(status_code=400, detail="GitHub no conectado")
    
    body = await request.json()
    conversation_id = body.get("conversation_id")
    repo_name = body.get("repo_name")
    private = body.get("private", False)
    
    if not conversation_id:
        raise HTTPException(status_code=400, detail="conversation_id required")
    
    # Get conversation and extract code
    conv = await db.conversations.find_one(
        {"conversation_id": conversation_id, "user_id": user_id}
    )
    
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    messages = await db.messages.find(
        {"conversation_id": conversation_id, "role": "assistant"},
        {"_id": 0}
    ).to_list(100)
    
    # Extract code blocks
    files = []
    for msg in messages:
        content = msg.get("content", "")
        pattern = r'```(\w+)?\n(.*?)```'
        matches = re.findall(pattern, content, re.DOTALL)
        
        for i, (lang, code) in enumerate(matches):
            ext = {
                "python": ".py",
                "javascript": ".js",
                "typescript": ".ts",
                "jsx": ".jsx",
                "tsx": ".tsx",
                "html": ".html",
                "css": ".css",
                "json": ".json",
                "yaml": ".yaml",
                "sql": ".sql",
                "bash": ".sh",
                "shell": ".sh"
            }.get(lang.lower() if lang else "", ".txt")
            
            filename = f"code_{len(files) + 1}{ext}"
            files.append({
                "path": filename,
                "content": code.strip()
            })
    
    if not files:
        raise HTTPException(status_code=400, detail="No code found in conversation")
    
    # Add README
    files.append({
        "path": "README.md",
        "content": f"# {conv.get('title', 'Code from Assistant Melus')}\n\nCode extracted from conversation.\n"
    })
    
    try:
        manager = GitHubManager(connection["github_token"])
        
        final_repo_name = repo_name or f"melus-code-{conversation_id[:8]}"
        
        repo_info = manager.create_repository(
            name=final_repo_name,
            description=f"Code from: {conv.get('title', 'Assistant Melus conversation')}",
            private=private
        )
        
        push_result = manager.push_files(
            repo_name=final_repo_name,
            files=files
        )
        
        # Deduct credits
        new_credits = user_doc["credits"] - PUSH_COST
        await db.users.update_one(
            {"user_id": user_id},
            {
                "$set": {"credits": new_credits},
                "$inc": {"credits_used": PUSH_COST}
            }
        )
        
        return {
            "success": True,
            "repo_name": final_repo_name,
            "repo_url": push_result.get("repo_url"),
            "files_pushed": push_result.get("total_files"),
            "credits_used": PUSH_COST,
            "credits_remaining": new_credits
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

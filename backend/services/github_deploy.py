"""
MelusAI - GitHub Deployment Service
Servicio para desplegar proyectos a GitHub desde el perfil del usuario
"""
import os
import base64
import aiohttp
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class GitHubRepo:
    name: str
    full_name: str
    html_url: str
    clone_url: str
    created_at: str


@dataclass
class DeployResult:
    success: bool
    repo_url: Optional[str]
    message: str
    files_pushed: int
    commit_sha: Optional[str]


class GitHubDeployService:
    """Servicio para crear repos y subir código a GitHub"""
    
    def __init__(self, access_token: str):
        self.token = access_token
        self.api_base = "https://api.github.com"
        self.headers = {
            "Authorization": f"token {access_token}",
            "Accept": "application/vnd.github.v3+json",
            "X-GitHub-Api-Version": "2022-11-28"
        }
    
    async def get_user(self) -> Dict[str, Any]:
        """Obtiene información del usuario autenticado"""
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{self.api_base}/user",
                headers=self.headers
            ) as response:
                if response.status == 200:
                    return await response.json()
                raise Exception(f"Error getting user: {response.status}")
    
    async def create_repository(
        self,
        name: str,
        description: str = "",
        private: bool = False,
        auto_init: bool = True
    ) -> GitHubRepo:
        """Crea un nuevo repositorio en GitHub"""
        async with aiohttp.ClientSession() as session:
            payload = {
                "name": name,
                "description": description,
                "private": private,
                "auto_init": auto_init,
                "has_issues": True,
                "has_projects": False,
                "has_wiki": False
            }
            
            async with session.post(
                f"{self.api_base}/user/repos",
                headers=self.headers,
                json=payload
            ) as response:
                if response.status == 201:
                    data = await response.json()
                    return GitHubRepo(
                        name=data["name"],
                        full_name=data["full_name"],
                        html_url=data["html_url"],
                        clone_url=data["clone_url"],
                        created_at=data["created_at"]
                    )
                elif response.status == 422:
                    error = await response.json()
                    raise Exception(f"Repository already exists or invalid name: {error}")
                else:
                    error = await response.text()
                    raise Exception(f"Error creating repository: {error}")
    
    async def check_repo_exists(self, owner: str, repo: str) -> bool:
        """Verifica si un repositorio existe"""
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{self.api_base}/repos/{owner}/{repo}",
                headers=self.headers
            ) as response:
                return response.status == 200
    
    async def get_default_branch(self, owner: str, repo: str) -> str:
        """Obtiene la rama por defecto del repositorio"""
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{self.api_base}/repos/{owner}/{repo}",
                headers=self.headers
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get("default_branch", "main")
                return "main"
    
    async def get_latest_commit_sha(self, owner: str, repo: str, branch: str = "main") -> Optional[str]:
        """Obtiene el SHA del último commit"""
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{self.api_base}/repos/{owner}/{repo}/git/ref/heads/{branch}",
                headers=self.headers
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    return data["object"]["sha"]
                return None
    
    async def create_blob(self, owner: str, repo: str, content: str) -> str:
        """Crea un blob con el contenido del archivo"""
        async with aiohttp.ClientSession() as session:
            # Encode content to base64
            encoded_content = base64.b64encode(content.encode('utf-8')).decode('utf-8')
            
            async with session.post(
                f"{self.api_base}/repos/{owner}/{repo}/git/blobs",
                headers=self.headers,
                json={
                    "content": encoded_content,
                    "encoding": "base64"
                }
            ) as response:
                if response.status == 201:
                    data = await response.json()
                    return data["sha"]
                error = await response.text()
                raise Exception(f"Error creating blob: {error}")
    
    async def create_tree(
        self,
        owner: str,
        repo: str,
        files: Dict[str, str],
        base_tree: Optional[str] = None
    ) -> str:
        """Crea un tree con todos los archivos"""
        async with aiohttp.ClientSession() as session:
            tree_items = []
            
            for path, content in files.items():
                blob_sha = await self.create_blob(owner, repo, content)
                tree_items.append({
                    "path": path,
                    "mode": "100644",
                    "type": "blob",
                    "sha": blob_sha
                })
            
            payload = {"tree": tree_items}
            if base_tree:
                payload["base_tree"] = base_tree
            
            async with session.post(
                f"{self.api_base}/repos/{owner}/{repo}/git/trees",
                headers=self.headers,
                json=payload
            ) as response:
                if response.status == 201:
                    data = await response.json()
                    return data["sha"]
                error = await response.text()
                raise Exception(f"Error creating tree: {error}")
    
    async def create_commit(
        self,
        owner: str,
        repo: str,
        message: str,
        tree_sha: str,
        parent_sha: Optional[str] = None
    ) -> str:
        """Crea un commit"""
        async with aiohttp.ClientSession() as session:
            payload = {
                "message": message,
                "tree": tree_sha
            }
            if parent_sha:
                payload["parents"] = [parent_sha]
            
            async with session.post(
                f"{self.api_base}/repos/{owner}/{repo}/git/commits",
                headers=self.headers,
                json=payload
            ) as response:
                if response.status == 201:
                    data = await response.json()
                    return data["sha"]
                error = await response.text()
                raise Exception(f"Error creating commit: {error}")
    
    async def update_ref(
        self,
        owner: str,
        repo: str,
        branch: str,
        commit_sha: str
    ) -> bool:
        """Actualiza la referencia de la rama al nuevo commit"""
        async with aiohttp.ClientSession() as session:
            async with session.patch(
                f"{self.api_base}/repos/{owner}/{repo}/git/refs/heads/{branch}",
                headers=self.headers,
                json={"sha": commit_sha, "force": True}
            ) as response:
                return response.status == 200
    
    async def deploy_project(
        self,
        project_name: str,
        project_description: str,
        files: Dict[str, str],
        private: bool = False,
        commit_message: str = "Initial commit from MelusAI"
    ) -> DeployResult:
        """
        Despliega un proyecto completo a GitHub
        
        Args:
            project_name: Nombre del repositorio
            project_description: Descripción del proyecto
            files: Dict de {ruta: contenido} de todos los archivos
            private: Si el repo debe ser privado
            commit_message: Mensaje del commit
            
        Returns:
            DeployResult con información del deploy
        """
        try:
            # 1. Obtener usuario
            user = await self.get_user()
            username = user["login"]
            
            # 2. Sanitizar nombre del repo
            repo_name = self._sanitize_repo_name(project_name)
            
            # 3. Verificar si existe
            exists = await self.check_repo_exists(username, repo_name)
            
            if exists:
                # Usar repo existente
                logger.info(f"Repository {repo_name} exists, updating...")
                branch = await self.get_default_branch(username, repo_name)
                parent_sha = await self.get_latest_commit_sha(username, repo_name, branch)
            else:
                # Crear nuevo repo
                logger.info(f"Creating new repository: {repo_name}")
                repo = await self.create_repository(
                    name=repo_name,
                    description=project_description,
                    private=private,
                    auto_init=True
                )
                # Esperar un momento para que GitHub procese
                import asyncio
                await asyncio.sleep(2)
                branch = "main"
                parent_sha = await self.get_latest_commit_sha(username, repo_name, branch)
            
            # 4. Agregar README si no existe
            if "README.md" not in files:
                files["README.md"] = self._generate_readme(project_name, project_description)
            
            # 5. Agregar .gitignore si no existe
            if ".gitignore" not in files:
                files[".gitignore"] = self._generate_gitignore()
            
            # 6. Crear tree con todos los archivos
            tree_sha = await self.create_tree(
                username, repo_name, files,
                base_tree=parent_sha
            )
            
            # 7. Crear commit
            commit_sha = await self.create_commit(
                username, repo_name,
                message=commit_message,
                tree_sha=tree_sha,
                parent_sha=parent_sha
            )
            
            # 8. Actualizar rama
            await self.update_ref(username, repo_name, branch, commit_sha)
            
            repo_url = f"https://github.com/{username}/{repo_name}"
            
            return DeployResult(
                success=True,
                repo_url=repo_url,
                message=f"Proyecto desplegado exitosamente en GitHub",
                files_pushed=len(files),
                commit_sha=commit_sha
            )
            
        except Exception as e:
            logger.error(f"Deploy error: {e}")
            return DeployResult(
                success=False,
                repo_url=None,
                message=f"Error al desplegar: {str(e)}",
                files_pushed=0,
                commit_sha=None
            )
    
    def _sanitize_repo_name(self, name: str) -> str:
        """Sanitiza el nombre del repositorio"""
        import re
        # Remover caracteres no válidos
        sanitized = re.sub(r'[^a-zA-Z0-9_-]', '-', name.lower())
        # Remover guiones múltiples
        sanitized = re.sub(r'-+', '-', sanitized)
        # Remover guiones al inicio y final
        sanitized = sanitized.strip('-')
        # Limitar longitud
        return sanitized[:100] or "melusai-project"
    
    def _generate_readme(self, name: str, description: str) -> str:
        """Genera un README.md para el proyecto"""
        return f"""# {name}

{description}

## 🚀 Generado con MelusAI

Este proyecto fue creado automáticamente usando [MelusAI](https://www.melusai.com) - Constructor Universal de Apps con IA.

## 📦 Instalación

```bash
npm install
npm run dev
```

## 🛠️ Tecnologías

- React
- Vite
- TailwindCSS

## 📄 Licencia

MIT

---

Creado con ❤️ por MelusAI
"""
    
    def _generate_gitignore(self) -> str:
        """Genera un .gitignore estándar"""
        return """# Dependencies
node_modules/
.pnp
.pnp.js

# Build
dist/
build/
.next/
out/

# Testing
coverage/

# Misc
.DS_Store
*.pem
.env
.env.local
.env.development.local
.env.test.local
.env.production.local

# Debug
npm-debug.log*
yarn-debug.log*
yarn-error.log*

# IDE
.idea/
.vscode/
*.swp
*.swo

# Python
__pycache__/
*.py[cod]
*$py.class
venv/
.env
"""


# ===========================================
# API Routes for GitHub Deploy
# ===========================================

async def deploy_to_github_handler(
    workspace_id: str,
    user_id: str,
    github_token: str,
    private: bool = False,
    db = None
):
    """
    Handler para desplegar un workspace a GitHub
    
    Args:
        workspace_id: ID del workspace a desplegar
        user_id: ID del usuario
        github_token: Token de acceso de GitHub del usuario
        private: Si el repo debe ser privado
        db: Conexión a la base de datos
    """
    # 1. Obtener workspace
    workspace = await db.workspaces.find_one(
        {"workspace_id": workspace_id, "user_id": user_id},
        {"_id": 0}
    )
    
    if not workspace:
        return {"success": False, "error": "Workspace not found"}
    
    # 2. Preparar archivos
    files = {}
    for file_data in workspace.get("files", []):
        files[file_data["path"]] = file_data["content"]
    
    # 3. Desplegar
    deploy_service = GitHubDeployService(github_token)
    result = await deploy_service.deploy_project(
        project_name=workspace.get("name", "melusai-project"),
        project_description=workspace.get("description", "Proyecto generado con MelusAI"),
        files=files,
        private=private,
        commit_message=f"Deploy from MelusAI - {datetime.utcnow().isoformat()}"
    )
    
    # 4. Actualizar workspace con info de deploy
    if result.success:
        await db.workspaces.update_one(
            {"workspace_id": workspace_id},
            {
                "$set": {
                    "github_repo": result.repo_url,
                    "last_deploy": datetime.utcnow().isoformat(),
                    "deploy_commit": result.commit_sha
                }
            }
        )
    
    return {
        "success": result.success,
        "repo_url": result.repo_url,
        "message": result.message,
        "files_pushed": result.files_pushed,
        "commit_sha": result.commit_sha
    }

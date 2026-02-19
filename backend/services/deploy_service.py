"""
Melus AI - Deploy Agent Service
Automated deployment to Vercel, Netlify, and other platforms
"""
import os
import json
import httpx
import asyncio
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

@dataclass
class DeploymentResult:
    success: bool
    platform: str
    url: Optional[str] = None
    deploy_id: Optional[str] = None
    error: Optional[str] = None
    logs: List[str] = None

class VercelDeployer:
    """Deploy projects to Vercel"""
    
    def __init__(self, token: str = None):
        self.token = token or os.environ.get('VERCEL_TOKEN')
        self.api_base = "https://api.vercel.com"
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
    
    async def deploy_project(
        self, 
        project_name: str, 
        files: Dict[str, str],
        framework: str = "vite"
    ) -> DeploymentResult:
        """
        Deploy a project to Vercel
        
        Args:
            project_name: Name for the Vercel project
            files: Dict of file paths to content
            framework: Framework type (vite, nextjs, create-react-app)
        """
        if not self.token:
            return DeploymentResult(
                success=False,
                platform="vercel",
                error="Vercel token not configured. Add VERCEL_TOKEN to environment."
            )
        
        try:
            # Prepare files for Vercel deployment
            vercel_files = []
            for path, content in files.items():
                # Normalize path
                normalized_path = path.lstrip('/')
                vercel_files.append({
                    "file": normalized_path,
                    "data": content
                })
            
            # Add vercel.json if not present
            has_vercel_config = any(f["file"] == "vercel.json" for f in vercel_files)
            if not has_vercel_config:
                vercel_config = {
                    "buildCommand": "npm run build",
                    "outputDirectory": "dist",
                    "framework": framework,
                    "rewrites": [{"source": "/(.*)", "destination": "/index.html"}]
                }
                vercel_files.append({
                    "file": "vercel.json",
                    "data": json.dumps(vercel_config, indent=2)
                })
            
            # Create deployment
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.api_base}/v13/deployments",
                    headers=self.headers,
                    json={
                        "name": project_name.lower().replace(" ", "-"),
                        "files": vercel_files,
                        "projectSettings": {
                            "framework": framework,
                            "buildCommand": "npm run build",
                            "outputDirectory": "dist"
                        }
                    },
                    timeout=60.0
                )
                
                if response.status_code in [200, 201]:
                    data = response.json()
                    return DeploymentResult(
                        success=True,
                        platform="vercel",
                        url=f"https://{data.get('url', '')}",
                        deploy_id=data.get('id'),
                        logs=[f"Deployed to Vercel: {data.get('url')}"]
                    )
                else:
                    return DeploymentResult(
                        success=False,
                        platform="vercel",
                        error=f"Vercel API error: {response.text}"
                    )
                    
        except Exception as e:
            logger.error(f"Vercel deployment failed: {e}")
            return DeploymentResult(
                success=False,
                platform="vercel",
                error=str(e)
            )

class NetlifyDeployer:
    """Deploy projects to Netlify"""
    
    def __init__(self, token: str = None):
        self.token = token or os.environ.get('NETLIFY_TOKEN')
        self.api_base = "https://api.netlify.com/api/v1"
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
    
    async def deploy_project(
        self, 
        project_name: str, 
        files: Dict[str, str]
    ) -> DeploymentResult:
        """Deploy a project to Netlify"""
        if not self.token:
            return DeploymentResult(
                success=False,
                platform="netlify",
                error="Netlify token not configured. Add NETLIFY_TOKEN to environment."
            )
        
        try:
            # Create site first
            async with httpx.AsyncClient() as client:
                # Create new site
                site_response = await client.post(
                    f"{self.api_base}/sites",
                    headers=self.headers,
                    json={"name": project_name.lower().replace(" ", "-")},
                    timeout=30.0
                )
                
                if site_response.status_code not in [200, 201]:
                    return DeploymentResult(
                        success=False,
                        platform="netlify",
                        error=f"Failed to create site: {site_response.text}"
                    )
                
                site_data = site_response.json()
                site_id = site_data.get('id')
                
                # Deploy files
                # Note: Netlify requires a ZIP file for deployment
                # This is a simplified version
                return DeploymentResult(
                    success=True,
                    platform="netlify",
                    url=site_data.get('ssl_url') or site_data.get('url'),
                    deploy_id=site_id,
                    logs=[f"Site created: {site_data.get('url')}"]
                )
                
        except Exception as e:
            logger.error(f"Netlify deployment failed: {e}")
            return DeploymentResult(
                success=False,
                platform="netlify",
                error=str(e)
            )

class DeployService:
    """Unified deployment service"""
    
    def __init__(self):
        self.vercel = VercelDeployer()
        self.netlify = NetlifyDeployer()
    
    async def deploy(
        self,
        platform: str,
        project_name: str,
        files: Dict[str, str],
        **kwargs
    ) -> DeploymentResult:
        """
        Deploy to specified platform
        
        Args:
            platform: 'vercel' or 'netlify'
            project_name: Name for the project
            files: Dict of file paths to content
        """
        if platform == "vercel":
            return await self.vercel.deploy_project(project_name, files, **kwargs)
        elif platform == "netlify":
            return await self.netlify.deploy_project(project_name, files)
        else:
            return DeploymentResult(
                success=False,
                platform=platform,
                error=f"Unsupported platform: {platform}"
            )
    
    def generate_deploy_configs(self, project_name: str) -> Dict[str, str]:
        """Generate deployment configuration files"""
        
        configs = {}
        
        # Vercel config
        configs["vercel.json"] = json.dumps({
            "buildCommand": "npm run build",
            "outputDirectory": "dist",
            "framework": "vite",
            "rewrites": [{"source": "/(.*)", "destination": "/index.html"}]
        }, indent=2)
        
        # Netlify config
        configs["netlify.toml"] = """[build]
  command = "npm run build"
  publish = "dist"

[[redirects]]
  from = "/*"
  to = "/index.html"
  status = 200
"""
        
        # Dockerfile
        configs["Dockerfile"] = f"""FROM node:18-alpine AS builder

WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
"""
        
        # Nginx config for Docker
        configs["nginx.conf"] = """server {
    listen 80;
    server_name localhost;
    root /usr/share/nginx/html;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    location /api {
        proxy_pass http://backend:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
}
"""
        
        # Docker Compose
        configs["docker-compose.yml"] = f"""version: '3.8'

services:
  frontend:
    build: .
    ports:
      - "80:80"
    depends_on:
      - backend

  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=${{DATABASE_URL}}
      - JWT_SECRET=${{JWT_SECRET}}

  db:
    image: mongo:6
    volumes:
      - mongo_data:/data/db
    ports:
      - "27017:27017"

volumes:
  mongo_data:
"""
        
        # GitHub Actions workflow
        configs[".github/workflows/deploy.yml"] = """name: Deploy

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup Node
        uses: actions/setup-node@v4
        with:
          node-version: '18'
          cache: 'npm'
      
      - name: Install dependencies
        run: npm ci
      
      - name: Build
        run: npm run build
      
      - name: Deploy to Vercel
        uses: amondnet/vercel-action@v25
        with:
          vercel-token: ${{ secrets.VERCEL_TOKEN }}
          vercel-org-id: ${{ secrets.VERCEL_ORG_ID }}
          vercel-project-id: ${{ secrets.VERCEL_PROJECT_ID }}
          working-directory: ./
"""
        
        return configs

# Singleton instance
deploy_service = DeployService()

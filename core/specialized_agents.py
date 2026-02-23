"""
MelusAI Specialized Agents
Agentes especializados por tipo de proyecto: Web, E-commerce, SaaS, Game2D, Game3D
"""
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from abc import ABC, abstractmethod
import asyncio
import logging
import json

logger = logging.getLogger(__name__)


class ProjectType(Enum):
    """Types of specialized projects"""
    WEB = "web"
    ECOMMERCE = "ecommerce"
    SAAS = "saas"
    GAME_2D = "game2d"
    GAME_3D = "game3d"
    MOBILE = "mobile"
    API = "api"


class BuilderType(Enum):
    """Types of builders"""
    FRONTEND = "frontend"
    BACKEND = "backend"
    UI_DESIGNER = "ui_designer"
    DEPLOY = "deploy"
    GAME_ENGINE = "game_engine"
    GAME_LOGIC = "game_logic"
    GAME_ASSETS = "game_assets"
    GAME_BUILD = "game_build"


@dataclass
class BuilderResult:
    """Result from a builder"""
    builder_type: BuilderType
    files: List[Dict] = field(default_factory=list)
    configs: Dict[str, Any] = field(default_factory=dict)
    status: str = "completed"
    error: Optional[str] = None


class BaseBuilder(ABC):
    """Base class for all builders"""
    
    def __init__(self, builder_type: BuilderType, llm_client=None):
        self.builder_type = builder_type
        self.llm_client = llm_client
    
    @abstractmethod
    async def build(self, context: Dict) -> BuilderResult:
        """Execute the build process"""
        pass


class FrontendBuilder(BaseBuilder):
    """Frontend Builder - React/Next.js components"""
    
    def __init__(self, llm_client=None):
        super().__init__(BuilderType.FRONTEND, llm_client)
    
    async def build(self, context: Dict) -> BuilderResult:
        project_type = context.get("project_type", "web")
        prompt = context.get("prompt", "")
        
        # Get appropriate template
        from .code_templates import get_template_for_intent
        files = get_template_for_intent(project_type, prompt)
        
        return BuilderResult(
            builder_type=self.builder_type,
            files=files,
            status="completed"
        )


class BackendBuilder(BaseBuilder):
    """Backend Builder - FastAPI/Node.js APIs"""
    
    def __init__(self, llm_client=None):
        super().__init__(BuilderType.BACKEND, llm_client)
    
    async def build(self, context: Dict) -> BuilderResult:
        project_type = context.get("project_type", "web")
        apis = context.get("apis", [])
        
        files = []
        for api in apis:
            files.append({
                "path": f"backend/routes/{api}.py",
                "content": self._generate_api(api, project_type),
                "type": "api"
            })
        
        return BuilderResult(
            builder_type=self.builder_type,
            files=files,
            status="completed"
        )
    
    def _generate_api(self, api_name: str, project_type: str) -> str:
        """Generate API route based on project type"""
        base_template = f'''"""
{api_name.title()} API Routes - {project_type.upper()} Module
"""
from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional, Dict
from pydantic import BaseModel
from datetime import datetime

router = APIRouter(prefix="/api/{api_name}", tags=["{api_name}"])


class {api_name.title()}Item(BaseModel):
    id: Optional[str] = None
    name: str
    data: Dict = {{}}
    created_at: Optional[datetime] = None


@router.get("/", response_model=List[{api_name.title()}Item])
async def get_all():
    """Get all {api_name}"""
    return []


@router.get("/{{item_id}}", response_model={api_name.title()}Item)
async def get_by_id(item_id: str):
    """Get {api_name} by ID"""
    return {api_name.title()}Item(id=item_id, name="Sample")


@router.post("/", response_model={api_name.title()}Item)
async def create(item: {api_name.title()}Item):
    """Create new {api_name}"""
    item.id = f"{api_name}_" + str(datetime.now().timestamp())[:10]
    item.created_at = datetime.now()
    return item


@router.put("/{{item_id}}", response_model={api_name.title()}Item)
async def update(item_id: str, item: {api_name.title()}Item):
    """Update {api_name}"""
    item.id = item_id
    return item


@router.delete("/{{item_id}}")
async def delete(item_id: str):
    """Delete {api_name}"""
    return {{"deleted": True, "id": item_id}}
'''
        return base_template


class UIDesignerBuilder(BaseBuilder):
    """UI/UX Designer Builder - Styles, themes, animations"""
    
    def __init__(self, llm_client=None):
        super().__init__(BuilderType.UI_DESIGNER, llm_client)
    
    async def build(self, context: Dict) -> BuilderResult:
        project_type = context.get("project_type", "web")
        theme = context.get("theme", "modern")
        
        files = [
            {
                "path": "styles/theme.css",
                "content": self._generate_theme(project_type, theme),
                "type": "style"
            },
            {
                "path": "styles/animations.css",
                "content": self._generate_animations(),
                "type": "style"
            }
        ]
        
        return BuilderResult(
            builder_type=self.builder_type,
            files=files,
            status="completed"
        )
    
    def _generate_theme(self, project_type: str, theme: str) -> str:
        themes = {
            "modern": {
                "primary": "#6366f1",
                "secondary": "#ec4899",
                "background": "#0f172a",
                "surface": "#1e293b",
                "text": "#f8fafc"
            },
            "light": {
                "primary": "#3b82f6",
                "secondary": "#8b5cf6",
                "background": "#ffffff",
                "surface": "#f1f5f9",
                "text": "#0f172a"
            },
            "dark": {
                "primary": "#22d3ee",
                "secondary": "#f472b6",
                "background": "#09090b",
                "surface": "#18181b",
                "text": "#fafafa"
            }
        }
        
        colors = themes.get(theme, themes["modern"])
        
        return f''':root {{
  --color-primary: {colors["primary"]};
  --color-secondary: {colors["secondary"]};
  --color-background: {colors["background"]};
  --color-surface: {colors["surface"]};
  --color-text: {colors["text"]};
  
  --font-sans: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
  --font-mono: 'JetBrains Mono', monospace;
  
  --radius-sm: 0.375rem;
  --radius-md: 0.5rem;
  --radius-lg: 0.75rem;
  --radius-xl: 1rem;
  
  --shadow-sm: 0 1px 2px rgba(0, 0, 0, 0.05);
  --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
  --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
  --shadow-xl: 0 20px 25px -5px rgba(0, 0, 0, 0.1);
}}

* {{
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}}

body {{
  font-family: var(--font-sans);
  background-color: var(--color-background);
  color: var(--color-text);
  line-height: 1.6;
}}

.btn-primary {{
  background: linear-gradient(135deg, var(--color-primary), var(--color-secondary));
  color: white;
  padding: 0.75rem 1.5rem;
  border-radius: var(--radius-lg);
  border: none;
  cursor: pointer;
  font-weight: 600;
  transition: all 0.2s ease;
}}

.btn-primary:hover {{
  transform: translateY(-2px);
  box-shadow: var(--shadow-lg);
}}

.card {{
  background: var(--color-surface);
  border-radius: var(--radius-xl);
  padding: 1.5rem;
  box-shadow: var(--shadow-md);
}}
'''
    
    def _generate_animations(self) -> str:
        return '''/* Animations */
@keyframes fadeIn {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}

@keyframes slideIn {
  from { opacity: 0; transform: translateX(-20px); }
  to { opacity: 1; transform: translateX(0); }
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

@keyframes bounce {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-10px); }
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.animate-fadeIn { animation: fadeIn 0.5s ease-out forwards; }
.animate-slideIn { animation: slideIn 0.3s ease-out forwards; }
.animate-pulse { animation: pulse 2s infinite; }
.animate-bounce { animation: bounce 1s infinite; }
.animate-spin { animation: spin 1s linear infinite; }

/* Stagger animations */
.stagger > *:nth-child(1) { animation-delay: 0.1s; }
.stagger > *:nth-child(2) { animation-delay: 0.2s; }
.stagger > *:nth-child(3) { animation-delay: 0.3s; }
.stagger > *:nth-child(4) { animation-delay: 0.4s; }
.stagger > *:nth-child(5) { animation-delay: 0.5s; }
'''


class DeployBuilder(BaseBuilder):
    """Deploy & CI/CD Builder - Docker, configs"""
    
    def __init__(self, llm_client=None):
        super().__init__(BuilderType.DEPLOY, llm_client)
    
    async def build(self, context: Dict) -> BuilderResult:
        project_type = context.get("project_type", "web")
        
        files = [
            {
                "path": "Dockerfile",
                "content": self._generate_dockerfile(project_type),
                "type": "config"
            },
            {
                "path": "docker-compose.yml",
                "content": self._generate_compose(project_type),
                "type": "config"
            },
            {
                "path": ".env.example",
                "content": self._generate_env(project_type),
                "type": "config"
            },
            {
                "path": ".github/workflows/deploy.yml",
                "content": self._generate_ci_cd(),
                "type": "config"
            }
        ]
        
        return BuilderResult(
            builder_type=self.builder_type,
            files=files,
            status="completed"
        )
    
    def _generate_dockerfile(self, project_type: str) -> str:
        return '''FROM node:18-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM node:18-alpine AS runner
WORKDIR /app
ENV NODE_ENV production

COPY --from=builder /app/next.config.js ./
COPY --from=builder /app/public ./public
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/package.json ./package.json

EXPOSE 3000
CMD ["npm", "start"]
'''
    
    def _generate_compose(self, project_type: str) -> str:
        services = {
            "web": ["frontend", "backend", "db"],
            "ecommerce": ["frontend", "backend", "db", "redis", "stripe-webhook"],
            "saas": ["frontend", "backend", "db", "redis", "worker"],
            "game2d": ["frontend", "backend"],
            "game3d": ["frontend", "backend", "assets-server"]
        }
        
        svc_list = services.get(project_type, services["web"])
        
        compose = '''version: '3.8'

services:
  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    environment:
      - NODE_ENV=production
      - API_URL=http://backend:8000
    depends_on:
      - backend

  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=${DATABASE_URL}
      - REDIS_URL=${REDIS_URL}
    depends_on:
      - db
'''
        
        if "db" in svc_list:
            compose += '''
  db:
    image: postgres:15-alpine
    environment:
      - POSTGRES_USER=${DB_USER}
      - POSTGRES_PASSWORD=${DB_PASSWORD}
      - POSTGRES_DB=${DB_NAME}
    volumes:
      - postgres_data:/var/lib/postgresql/data
'''
        
        if "redis" in svc_list:
            compose += '''
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
'''
        
        compose += '''
volumes:
  postgres_data:
'''
        return compose
    
    def _generate_env(self, project_type: str) -> str:
        base = '''# Database
DATABASE_URL=postgresql://user:password@localhost:5432/dbname
DB_USER=user
DB_PASSWORD=password
DB_NAME=dbname

# API
API_URL=http://localhost:8000
NEXT_PUBLIC_API_URL=http://localhost:8000

# Auth
JWT_SECRET=your-jwt-secret-key
'''
        
        if project_type == "ecommerce":
            base += '''
# Stripe
STRIPE_PUBLIC_KEY=pk_test_xxx
STRIPE_SECRET_KEY=sk_test_xxx
STRIPE_WEBHOOK_SECRET=whsec_xxx
'''
        
        if project_type == "saas":
            base += '''
# Stripe (Subscriptions)
STRIPE_PUBLIC_KEY=pk_test_xxx
STRIPE_SECRET_KEY=sk_test_xxx
STRIPE_PRICE_ID_PRO=price_xxx
STRIPE_PRICE_ID_ENTERPRISE=price_xxx

# Redis
REDIS_URL=redis://localhost:6379
'''
        
        return base
    
    def _generate_ci_cd(self) -> str:
        return '''name: Deploy

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '18'
          cache: 'npm'
      - run: npm ci
      - run: npm test
      - run: npm run build

  deploy:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    steps:
      - uses: actions/checkout@v4
      - name: Deploy to Production
        run: |
          echo "Deploying to production..."
          # Add your deployment commands here
'''


# ================== SPECIALIZED PROJECT AGENTS ==================

class BaseProjectAgent(ABC):
    """Base class for specialized project agents"""
    
    def __init__(self, project_type: ProjectType, llm_client=None):
        self.project_type = project_type
        self.llm_client = llm_client
        self.builders: Dict[BuilderType, BaseBuilder] = {}
    
    @abstractmethod
    def get_required_apis(self) -> List[str]:
        """Get list of required APIs for this project type"""
        pass
    
    async def build_project(self, prompt: str, context: Dict = None) -> Dict:
        """Build the complete project"""
        context = context or {}
        context["project_type"] = self.project_type.value
        context["prompt"] = prompt
        context["apis"] = self.get_required_apis()
        
        results = {
            "project_type": self.project_type.value,
            "files": [],
            "configs": {},
            "builders_used": []
        }
        
        for builder_type, builder in self.builders.items():
            try:
                result = await builder.build(context)
                results["files"].extend(result.files)
                results["configs"].update(result.configs)
                results["builders_used"].append(builder_type.value)
            except Exception as e:
                logger.error(f"Builder {builder_type} error: {e}")
        
        return results


class WebAgent(BaseProjectAgent):
    """Web Application Agent"""
    
    def __init__(self, llm_client=None):
        super().__init__(ProjectType.WEB, llm_client)
        self.builders = {
            BuilderType.FRONTEND: FrontendBuilder(llm_client),
            BuilderType.BACKEND: BackendBuilder(llm_client),
            BuilderType.UI_DESIGNER: UIDesignerBuilder(llm_client),
            BuilderType.DEPLOY: DeployBuilder(llm_client)
        }
    
    def get_required_apis(self) -> List[str]:
        return ["users", "auth", "data"]


class EcommerceAgent(BaseProjectAgent):
    """E-commerce Agent"""
    
    def __init__(self, llm_client=None):
        super().__init__(ProjectType.ECOMMERCE, llm_client)
        self.builders = {
            BuilderType.FRONTEND: FrontendBuilder(llm_client),
            BuilderType.BACKEND: BackendBuilder(llm_client),
            BuilderType.UI_DESIGNER: UIDesignerBuilder(llm_client),
            BuilderType.DEPLOY: DeployBuilder(llm_client)
        }
    
    def get_required_apis(self) -> List[str]:
        return ["products", "cart", "orders", "users", "payments", "reviews", "categories", "inventory", "shipping"]


class SaaSAgent(BaseProjectAgent):
    """SaaS Application Agent"""
    
    def __init__(self, llm_client=None):
        super().__init__(ProjectType.SAAS, llm_client)
        self.builders = {
            BuilderType.FRONTEND: FrontendBuilder(llm_client),
            BuilderType.BACKEND: BackendBuilder(llm_client),
            BuilderType.UI_DESIGNER: UIDesignerBuilder(llm_client),
            BuilderType.DEPLOY: DeployBuilder(llm_client)
        }
    
    def get_required_apis(self) -> List[str]:
        return ["auth", "users", "teams", "projects", "billing", "subscriptions", "api_keys", "webhooks", "analytics"]


class Game2DAgent(BaseProjectAgent):
    """2D Game Agent (Phaser.js)"""
    
    def __init__(self, llm_client=None):
        super().__init__(ProjectType.GAME_2D, llm_client)
        self.builders = {
            BuilderType.FRONTEND: FrontendBuilder(llm_client),
            BuilderType.BACKEND: BackendBuilder(llm_client),
            BuilderType.DEPLOY: DeployBuilder(llm_client)
        }
    
    def get_required_apis(self) -> List[str]:
        return ["scores", "users", "achievements", "leaderboard"]
    
    async def build_project(self, prompt: str, context: Dict = None) -> Dict:
        """Build 2D game project with Phaser.js"""
        from .code_templates import get_game2d_template
        
        context = context or {}
        context["project_type"] = "game2d"
        context["prompt"] = prompt
        
        # Get game template
        game_files = get_game2d_template()
        
        # Get backend APIs
        backend_builder = self.builders[BuilderType.BACKEND]
        context["apis"] = self.get_required_apis()
        backend_result = await backend_builder.build(context)
        
        # Get deploy configs
        deploy_builder = self.builders[BuilderType.DEPLOY]
        deploy_result = await deploy_builder.build(context)
        
        return {
            "project_type": "game2d",
            "engine": "phaser.js",
            "files": game_files + backend_result.files + deploy_result.files,
            "configs": {},
            "builders_used": ["game_engine", "backend", "deploy"]
        }


class Game3DAgent(BaseProjectAgent):
    """3D Game Agent (Three.js)"""
    
    def __init__(self, llm_client=None):
        super().__init__(ProjectType.GAME_3D, llm_client)
        self.builders = {
            BuilderType.FRONTEND: FrontendBuilder(llm_client),
            BuilderType.BACKEND: BackendBuilder(llm_client),
            BuilderType.DEPLOY: DeployBuilder(llm_client)
        }
    
    def get_required_apis(self) -> List[str]:
        return ["scores", "users", "worlds", "multiplayer", "assets"]
    
    async def build_project(self, prompt: str, context: Dict = None) -> Dict:
        """Build 3D game/experience with Three.js"""
        from .code_templates import get_game3d_template
        
        context = context or {}
        context["project_type"] = "game3d"
        context["prompt"] = prompt
        
        # Get game template
        game_files = get_game3d_template()
        
        # Get backend APIs
        backend_builder = self.builders[BuilderType.BACKEND]
        context["apis"] = self.get_required_apis()
        backend_result = await backend_builder.build(context)
        
        # Get deploy configs
        deploy_builder = self.builders[BuilderType.DEPLOY]
        deploy_result = await deploy_builder.build(context)
        
        return {
            "project_type": "game3d",
            "engine": "three.js",
            "files": game_files + backend_result.files + deploy_result.files,
            "configs": {},
            "builders_used": ["game_engine", "backend", "deploy"]
        }


# ================== PROJECT AGENT FACTORY ==================

class ProjectAgentFactory:
    """Factory for creating specialized project agents"""
    
    _agents: Dict[ProjectType, type] = {
        ProjectType.WEB: WebAgent,
        ProjectType.ECOMMERCE: EcommerceAgent,
        ProjectType.SAAS: SaaSAgent,
        ProjectType.GAME_2D: Game2DAgent,
        ProjectType.GAME_3D: Game3DAgent,
    }
    
    @classmethod
    def create_agent(cls, project_type: str, llm_client=None) -> Optional[BaseProjectAgent]:
        """Create an agent for the specified project type"""
        try:
            ptype = ProjectType(project_type.lower())
            agent_class = cls._agents.get(ptype)
            
            if agent_class:
                return agent_class(llm_client)
            
            # Default to WebAgent
            return WebAgent(llm_client)
            
        except ValueError:
            logger.warning(f"Unknown project type: {project_type}, using WebAgent")
            return WebAgent(llm_client)
    
    @classmethod
    def get_available_types(cls) -> List[Dict]:
        """Get list of available project types"""
        return [
            {
                "id": "web",
                "name": "Web Application",
                "description": "Full-stack web application with React + FastAPI",
                "builders": ["frontend", "backend", "ui_designer", "deploy"]
            },
            {
                "id": "ecommerce",
                "name": "E-commerce",
                "description": "Online store with products, cart, payments",
                "builders": ["frontend", "backend", "ui_designer", "deploy"],
                "apis": ["products", "cart", "orders", "payments"]
            },
            {
                "id": "saas",
                "name": "SaaS Platform",
                "description": "Multi-tenant SaaS with subscriptions",
                "builders": ["frontend", "backend", "ui_designer", "deploy"],
                "apis": ["auth", "teams", "billing", "subscriptions"]
            },
            {
                "id": "game2d",
                "name": "2D Game",
                "description": "Browser game with Phaser.js",
                "builders": ["game_engine", "game_logic", "backend", "deploy"],
                "engine": "phaser.js"
            },
            {
                "id": "game3d",
                "name": "3D Experience",
                "description": "3D game/experience with Three.js",
                "builders": ["game_engine", "game_logic", "backend", "deploy"],
                "engine": "three.js"
            }
        ]

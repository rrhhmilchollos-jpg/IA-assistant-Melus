"""
MelusAI Multi-Agent System
Sistema de agentes especializados coordinados por el Orchestrator
Soporta múltiples proveedores: GPT, Claude, Gemini, Sora
"""
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from abc import ABC, abstractmethod
import asyncio
import logging
import json
import os

logger = logging.getLogger(__name__)


class AgentType(Enum):
    """Types of specialized agents"""
    ARCHITECT = "architect"
    CODER = "coder"
    DESIGNER = "designer"
    SECURITY = "security"
    DEPLOYER = "deployer"
    VIDEO = "video"  # New: Sora video agent
    ORCHESTRATOR = "orchestrator"


class AgentStatus(Enum):
    """Agent execution status"""
    IDLE = "idle"
    WORKING = "working"
    COMPLETED = "completed"
    ERROR = "error"
    WAITING = "waiting"


class GenerationPhase(Enum):
    """Phases of code generation"""
    ARCHITECTURE = "architecture"
    BACKEND = "backend"
    FRONTEND = "frontend"
    INTEGRATIONS = "integrations"
    VIDEO = "video"
    DEPLOYMENT = "deployment"


@dataclass
class AgentTask:
    """Task assigned to an agent"""
    task_id: str
    agent_type: AgentType
    phase: GenerationPhase
    description: str
    input_data: Dict[str, Any] = field(default_factory=dict)
    output_data: Dict[str, Any] = field(default_factory=dict)
    status: AgentStatus = AgentStatus.IDLE
    error: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


@dataclass
class AgentMessage:
    """Message between agents"""
    from_agent: AgentType
    to_agent: AgentType
    message_type: str
    content: str
    data: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class BaseAgent(ABC):
    """Base class for all agents"""
    
    def __init__(self, agent_type: AgentType, llm_client=None):
        self.agent_type = agent_type
        self.status = AgentStatus.IDLE
        self.llm_client = llm_client
        self.current_task: Optional[AgentTask] = None
        self.message_queue: List[AgentMessage] = []
    
    @abstractmethod
    async def execute(self, task: AgentTask) -> Dict[str, Any]:
        """Execute the assigned task"""
        pass
    
    async def send_message(self, to_agent: AgentType, message_type: str, content: str, data: Dict = None):
        """Send message to another agent"""
        message = AgentMessage(
            from_agent=self.agent_type,
            to_agent=to_agent,
            message_type=message_type,
            content=content,
            data=data or {}
        )
        self.message_queue.append(message)
        return message
    
    def get_status(self) -> Dict:
        """Get current agent status"""
        return {
            "type": self.agent_type.value,
            "status": self.status.value,
            "current_task": self.current_task.task_id if self.current_task else None,
            "messages_pending": len(self.message_queue)
        }


class ArchitectAgent(BaseAgent):
    """
    🏗 Architect Agent
    Defines project structure, selects technologies, creates architecture plan
    """
    
    def __init__(self, llm_client=None):
        super().__init__(AgentType.ARCHITECT, llm_client)
    
    async def execute(self, task: AgentTask) -> Dict[str, Any]:
        self.status = AgentStatus.WORKING
        self.current_task = task
        task.started_at = datetime.now(timezone.utc)
        
        try:
            prompt = task.input_data.get("prompt", "")
            intent_type = task.input_data.get("intent_type", "web_app")
            features = task.input_data.get("features", [])
            
            # Create architecture plan
            architecture = await self._create_architecture(prompt, intent_type, features)
            
            task.output_data = architecture
            task.status = AgentStatus.COMPLETED
            task.completed_at = datetime.now(timezone.utc)
            self.status = AgentStatus.COMPLETED
            
            return architecture
            
        except Exception as e:
            logger.error(f"Architect error: {e}")
            task.error = str(e)
            task.status = AgentStatus.ERROR
            self.status = AgentStatus.ERROR
            return {"error": str(e)}
    
    async def _create_architecture(self, prompt: str, intent_type: str, features: List[str]) -> Dict:
        """Create architecture plan using LLM if available"""
        
        # Base architecture based on intent type
        architectures = {
            "ecommerce": {
                "type": "ecommerce",
                "frontend": {
                    "framework": "Next.js",
                    "styling": "TailwindCSS",
                    "components": ["ProductCard", "Cart", "Checkout", "ProductGrid", "Header", "Footer"]
                },
                "backend": {
                    "framework": "FastAPI",
                    "database": "PostgreSQL",
                    "cache": "Redis",
                    "apis": ["products", "cart", "orders", "users", "payments"]
                },
                "integrations": ["Stripe", "Email"],
                "features": ["product_catalog", "shopping_cart", "checkout", "user_auth", "order_management"]
            },
            "saas_app": {
                "type": "saas",
                "frontend": {
                    "framework": "Next.js",
                    "styling": "TailwindCSS",
                    "components": ["Dashboard", "Sidebar", "Settings", "Billing", "TeamManagement"]
                },
                "backend": {
                    "framework": "FastAPI",
                    "database": "PostgreSQL",
                    "cache": "Redis",
                    "apis": ["auth", "users", "teams", "billing", "projects"]
                },
                "integrations": ["Stripe", "Email", "Analytics"],
                "features": ["multi_tenant", "subscriptions", "team_management", "billing", "api_keys"]
            },
            "dashboard": {
                "type": "dashboard",
                "frontend": {
                    "framework": "React",
                    "styling": "TailwindCSS",
                    "components": ["StatCards", "Charts", "Tables", "Filters", "Sidebar"]
                },
                "backend": {
                    "framework": "FastAPI",
                    "database": "PostgreSQL",
                    "apis": ["analytics", "reports", "users"]
                },
                "integrations": ["Charts.js", "DataExport"],
                "features": ["real_time_data", "charts", "exports", "filters"]
            },
            "landing_page": {
                "type": "landing",
                "frontend": {
                    "framework": "Next.js",
                    "styling": "TailwindCSS",
                    "components": ["Hero", "Features", "Pricing", "Testimonials", "CTA", "Footer"]
                },
                "backend": {
                    "framework": "FastAPI",
                    "apis": ["contact", "newsletter"]
                },
                "integrations": ["Email", "Analytics"],
                "features": ["seo_optimized", "responsive", "animations", "contact_form"]
            },
            "game2d": {
                "type": "game2d",
                "frontend": {
                    "framework": "Phaser.js",
                    "styling": "CSS",
                    "components": ["GameScene", "UIScene", "MenuScene", "GameOver"]
                },
                "backend": {
                    "framework": "FastAPI",
                    "database": "PostgreSQL",
                    "apis": ["scores", "users", "achievements"]
                },
                "integrations": ["Phaser.js"],
                "features": ["game_loop", "sprites", "physics", "scoring", "leaderboard"]
            },
            "game3d": {
                "type": "game3d",
                "frontend": {
                    "framework": "Three.js",
                    "styling": "CSS",
                    "components": ["Scene", "Camera", "Renderer", "Controls", "UI"]
                },
                "backend": {
                    "framework": "FastAPI",
                    "database": "PostgreSQL",
                    "apis": ["scores", "users", "worlds"]
                },
                "integrations": ["Three.js", "WebGL"],
                "features": ["3d_rendering", "physics", "controls", "multiplayer_ready"]
            }
        }
        
        base_arch = architectures.get(intent_type, architectures["landing_page"])
        
        # Enhance with LLM if available
        if self.llm_client:
            try:
                from emergentintegrations.llm.chat import UserMessage
                
                llm_prompt = f"""Analiza este proyecto y mejora la arquitectura:

Descripción: {prompt}
Tipo base: {intent_type}
Características detectadas: {features}

Arquitectura base:
{json.dumps(base_arch, indent=2)}

Responde SOLO con JSON mejorado con:
1. Componentes específicos para este proyecto
2. APIs necesarias
3. Configuraciones especiales

JSON:"""
                user_message = UserMessage(text=llm_prompt)
                response = await self.llm_client.send_message(user_message)
                
                # Try to parse enhanced architecture
                json_start = response.find('{')
                json_end = response.rfind('}') + 1
                if json_start >= 0 and json_end > json_start:
                    enhanced = json.loads(response[json_start:json_end])
                    # Merge with base
                    base_arch.update(enhanced)
            except Exception as e:
                logger.warning(f"Could not enhance architecture with LLM: {e}")
        
        base_arch["project_description"] = prompt
        base_arch["detected_features"] = features
        
        return base_arch


class CoderAgent(BaseAgent):
    """
    💻 Coder Agent
    Generates actual code based on architecture and templates
    """
    
    def __init__(self, llm_client=None):
        super().__init__(AgentType.CODER, llm_client)
    
    async def execute(self, task: AgentTask) -> Dict[str, Any]:
        self.status = AgentStatus.WORKING
        self.current_task = task
        task.started_at = datetime.now(timezone.utc)
        
        try:
            architecture = task.input_data.get("architecture", {})
            prompt = task.input_data.get("prompt", "")
            phase = task.phase
            
            # Generate code based on phase
            if phase == GenerationPhase.BACKEND:
                code = await self._generate_backend(architecture, prompt)
            elif phase == GenerationPhase.FRONTEND:
                code = await self._generate_frontend(architecture, prompt)
            else:
                code = await self._generate_generic(architecture, prompt)
            
            task.output_data = code
            task.status = AgentStatus.COMPLETED
            task.completed_at = datetime.now(timezone.utc)
            self.status = AgentStatus.COMPLETED
            
            return code
            
        except Exception as e:
            logger.error(f"Coder error: {e}")
            task.error = str(e)
            task.status = AgentStatus.ERROR
            self.status = AgentStatus.ERROR
            return {"error": str(e)}
    
    async def _generate_backend(self, architecture: Dict, prompt: str) -> Dict:
        """Generate backend code"""
        apis = architecture.get("backend", {}).get("apis", [])
        
        files = []
        
        # Generate API routes
        for api in apis:
            files.append({
                "path": f"backend/routes/{api}.py",
                "content": self._get_api_template(api),
                "type": "api"
            })
        
        return {"files": files, "type": "backend"}
    
    async def _generate_frontend(self, architecture: Dict, prompt: str) -> Dict:
        """Generate frontend code"""
        from .code_templates import get_template_for_intent
        
        intent_type = architecture.get("type", "web_app")
        files = get_template_for_intent(intent_type, prompt)
        
        return {"files": files, "type": "frontend"}
    
    async def _generate_generic(self, architecture: Dict, prompt: str) -> Dict:
        """Generate generic code"""
        return {"files": [], "type": "generic"}
    
    def _get_api_template(self, api_name: str) -> str:
        """Get template for API route"""
        return f'''"""
{api_name.title()} API Routes
"""
from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional

router = APIRouter(prefix="/api/{api_name}", tags=["{api_name}"])


@router.get("/")
async def get_all_{api_name}():
    """Get all {api_name}"""
    return {{"items": [], "total": 0}}


@router.get("/{{item_id}}")
async def get_{api_name}_by_id(item_id: str):
    """Get {api_name} by ID"""
    return {{"id": item_id}}


@router.post("/")
async def create_{api_name}(data: dict):
    """Create new {api_name}"""
    return {{"id": "new", "data": data}}


@router.put("/{{item_id}}")
async def update_{api_name}(item_id: str, data: dict):
    """Update {api_name}"""
    return {{"id": item_id, "data": data}}


@router.delete("/{{item_id}}")
async def delete_{api_name}(item_id: str):
    """Delete {api_name}"""
    return {{"deleted": True}}
'''


class DesignerAgent(BaseAgent):
    """
    🎨 Designer Agent
    Applies styling, themes, and visual customizations
    """
    
    def __init__(self, llm_client=None):
        super().__init__(AgentType.DESIGNER, llm_client)
    
    async def execute(self, task: AgentTask) -> Dict[str, Any]:
        self.status = AgentStatus.WORKING
        self.current_task = task
        task.started_at = datetime.now(timezone.utc)
        
        try:
            files = task.input_data.get("files", [])
            prompt = task.input_data.get("prompt", "")
            theme = task.input_data.get("theme", {})
            
            # Apply design customizations
            styled_files = await self._apply_styling(files, prompt, theme)
            
            task.output_data = {"files": styled_files}
            task.status = AgentStatus.COMPLETED
            task.completed_at = datetime.now(timezone.utc)
            self.status = AgentStatus.COMPLETED
            
            return {"files": styled_files}
            
        except Exception as e:
            logger.error(f"Designer error: {e}")
            task.error = str(e)
            task.status = AgentStatus.ERROR
            self.status = AgentStatus.ERROR
            return {"error": str(e)}
    
    async def _apply_styling(self, files: List[Dict], prompt: str, theme: Dict) -> List[Dict]:
        """Apply styling to files using LLM"""
        
        if not self.llm_client or not files:
            return files
        
        styled_files = []
        
        for file in files:
            if file.get("path", "").endswith((".jsx", ".tsx", ".js")):
                # Get customized content
                styled_content = await self._customize_component(file, prompt, theme)
                styled_files.append({
                    **file,
                    "content": styled_content
                })
            else:
                styled_files.append(file)
        
        return styled_files
    
    async def _customize_component(self, file: Dict, prompt: str, theme: Dict) -> str:
        """Customize component based on prompt using LLM"""
        original_content = file.get("content", "")
        
        if not self.llm_client:
            return original_content
        
        try:
            from emergentintegrations.llm.chat import UserMessage
            
            customize_prompt = f"""Personaliza este componente React para el siguiente proyecto:

PROYECTO: {prompt}

TEMA DESEADO: {json.dumps(theme) if theme else 'Moderno y profesional'}

CÓDIGO ORIGINAL:
{original_content[:3000]}

INSTRUCCIONES:
1. Modifica SOLO los textos para que sean relevantes al proyecto (títulos, descripciones, labels)
2. Mantén la estructura del código exactamente igual
3. NO cambies imports, hooks, ni lógica de estado
4. Responde SOLO con el código modificado, sin explicaciones ni markdown"""

            # Use the new LlmChat API
            user_message = UserMessage(text=customize_prompt)
            response = await self.llm_client.send_message(user_message)
            
            # Clean response
            if "```" in response:
                # Extract code from markdown
                code_start = response.find("```") + 3
                if response[code_start:code_start+3] in ["jsx", "js\n", "tsx"]:
                    code_start = response.find("\n", code_start) + 1
                code_end = response.rfind("```")
                if code_end > code_start:
                    return response[code_start:code_end].strip()
            
            # If response looks like valid code, return it
            if "import" in response or "const " in response or "function " in response:
                return response.strip()
            
            return original_content
            
        except Exception as e:
            logger.warning(f"Could not customize component: {e}")
            return original_content


class VideoAgent(BaseAgent):
    """
    🎬 Video Agent
    Generates promotional videos using Sora 2
    """
    
    def __init__(self, llm_client=None):
        super().__init__(AgentType.VIDEO, llm_client)
    
    async def execute(self, task: AgentTask) -> Dict[str, Any]:
        self.status = AgentStatus.WORKING
        self.current_task = task
        task.started_at = datetime.now(timezone.utc)
        
        try:
            prompt = task.input_data.get("prompt", "")
            video_type = task.input_data.get("video_type", "promo")
            duration = task.input_data.get("duration", 4)
            
            # Generate video
            video_result = await self._generate_video(prompt, video_type, duration)
            
            task.output_data = video_result
            task.status = AgentStatus.COMPLETED
            task.completed_at = datetime.now(timezone.utc)
            self.status = AgentStatus.COMPLETED
            
            return video_result
            
        except Exception as e:
            logger.error(f"Video error: {e}")
            task.error = str(e)
            task.status = AgentStatus.ERROR
            self.status = AgentStatus.ERROR
            return {"error": str(e)}
    
    async def _generate_video(self, prompt: str, video_type: str, duration: int) -> Dict:
        """Generate video using Sora 2"""
        try:
            from .llm_manager import get_llm_manager
            
            llm_manager = get_llm_manager()
            
            # Create video-specific prompt
            video_prompts = {
                "promo": f"Professional promotional video: {prompt}. Modern, clean, cinematic style.",
                "demo": f"Product demonstration video: {prompt}. Clear, focused, showing features.",
                "intro": f"Introduction video: {prompt}. Engaging, dynamic, captures attention."
            }
            
            video_prompt = video_prompts.get(video_type, video_prompts["promo"])
            output_path = f"/app/uploads/video_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp4"
            
            result = await llm_manager.generate_video(
                prompt=video_prompt,
                model="sora-2",
                size="1280x720",
                duration=duration,
                output_path=output_path
            )
            
            return {
                "success": result is not None,
                "video_path": output_path if result else None,
                "prompt_used": video_prompt,
                "duration": duration
            }
                
        except Exception as e:
            logger.error(f"Video generation error: {e}")
            return {"success": False, "error": str(e)}


class SecurityAgent(BaseAgent):
    """
    🔐 Security Agent
    Adds validations, sanitization, and security measures
    """
    
    def __init__(self, llm_client=None):
        super().__init__(AgentType.SECURITY, llm_client)
    
    async def execute(self, task: AgentTask) -> Dict[str, Any]:
        self.status = AgentStatus.WORKING
        self.current_task = task
        task.started_at = datetime.now(timezone.utc)
        
        try:
            files = task.input_data.get("files", [])
            architecture = task.input_data.get("architecture", {})
            
            # Add security measures
            secured_files = await self._add_security(files, architecture)
            security_report = self._generate_security_report(architecture)
            
            task.output_data = {
                "files": secured_files,
                "security_report": security_report
            }
            task.status = AgentStatus.COMPLETED
            task.completed_at = datetime.now(timezone.utc)
            self.status = AgentStatus.COMPLETED
            
            return task.output_data
            
        except Exception as e:
            logger.error(f"Security error: {e}")
            task.error = str(e)
            task.status = AgentStatus.ERROR
            self.status = AgentStatus.ERROR
            return {"error": str(e)}
    
    async def _add_security(self, files: List[Dict], architecture: Dict) -> List[Dict]:
        """Add security measures to files"""
        # For now, return files as-is
        # In production, would add input validation, CSRF protection, etc.
        return files
    
    def _generate_security_report(self, architecture: Dict) -> Dict:
        """Generate security recommendations"""
        recommendations = [
            "Use HTTPS for all communications",
            "Implement rate limiting on API endpoints",
            "Sanitize all user inputs",
            "Use parameterized queries for database",
            "Implement proper authentication and authorization"
        ]
        
        if "payments" in str(architecture) or "stripe" in str(architecture).lower():
            recommendations.append("Use Stripe's secure checkout flow")
            recommendations.append("Never log or store full card numbers")
        
        if "auth" in str(architecture).lower():
            recommendations.append("Use bcrypt for password hashing")
            recommendations.append("Implement JWT token expiration")
        
        return {
            "status": "reviewed",
            "recommendations": recommendations,
            "risk_level": "low"
        }


class DeployerAgent(BaseAgent):
    """
    🚀 Deployer Agent
    Prepares deployment configuration, Docker, CI/CD
    """
    
    def __init__(self, llm_client=None):
        super().__init__(AgentType.DEPLOYER, llm_client)
    
    async def execute(self, task: AgentTask) -> Dict[str, Any]:
        self.status = AgentStatus.WORKING
        self.current_task = task
        task.started_at = datetime.now(timezone.utc)
        
        try:
            architecture = task.input_data.get("architecture", {})
            files = task.input_data.get("files", [])
            
            # Generate deployment files
            deploy_files = self._generate_deployment_files(architecture)
            
            task.output_data = {
                "files": files + deploy_files,
                "deployment_ready": True,
                "deploy_commands": self._get_deploy_commands(architecture)
            }
            task.status = AgentStatus.COMPLETED
            task.completed_at = datetime.now(timezone.utc)
            self.status = AgentStatus.COMPLETED
            
            return task.output_data
            
        except Exception as e:
            logger.error(f"Deployer error: {e}")
            task.error = str(e)
            task.status = AgentStatus.ERROR
            self.status = AgentStatus.ERROR
            return {"error": str(e)}
    
    def _generate_deployment_files(self, architecture: Dict) -> List[Dict]:
        """Generate Docker and deployment files"""
        files = []
        
        # Dockerfile
        files.append({
            "path": "Dockerfile",
            "content": self._get_dockerfile(architecture),
            "type": "config"
        })
        
        # docker-compose.yml
        files.append({
            "path": "docker-compose.yml",
            "content": self._get_docker_compose(architecture),
            "type": "config"
        })
        
        # .env.example
        files.append({
            "path": ".env.example",
            "content": self._get_env_example(architecture),
            "type": "config"
        })
        
        return files
    
    def _get_dockerfile(self, architecture: Dict) -> str:
        """Generate Dockerfile"""
        frontend_framework = architecture.get("frontend", {}).get("framework", "React")
        
        if "Next" in frontend_framework:
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
        else:
            return '''FROM node:18-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=builder /app/build /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
'''
    
    def _get_docker_compose(self, architecture: Dict) -> str:
        """Generate docker-compose.yml"""
        return '''version: '3.8'

services:
  frontend:
    build: .
    ports:
      - "3000:3000"
    environment:
      - NODE_ENV=production
    depends_on:
      - backend

  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=${DATABASE_URL}
    depends_on:
      - db

  db:
    image: postgres:15-alpine
    environment:
      - POSTGRES_USER=${DB_USER}
      - POSTGRES_PASSWORD=${DB_PASSWORD}
      - POSTGRES_DB=${DB_NAME}
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
'''
    
    def _get_env_example(self, architecture: Dict) -> str:
        """Generate .env.example"""
        env_vars = [
            "# Database",
            "DATABASE_URL=postgresql://user:password@localhost:5432/dbname",
            "DB_USER=user",
            "DB_PASSWORD=password",
            "DB_NAME=dbname",
            "",
            "# API",
            "API_URL=http://localhost:8000",
            "",
            "# Auth",
            "JWT_SECRET=your-secret-key",
            ""
        ]
        
        if "stripe" in str(architecture).lower():
            env_vars.extend([
                "# Stripe",
                "STRIPE_PUBLIC_KEY=pk_test_xxx",
                "STRIPE_SECRET_KEY=sk_test_xxx",
                ""
            ])
        
        return "\n".join(env_vars)
    
    def _get_deploy_commands(self, architecture: Dict) -> List[str]:
        """Get deployment commands"""
        return [
            "docker-compose build",
            "docker-compose up -d",
            "docker-compose logs -f"
        ]


class Orchestrator:
    """
    🎯 Orchestrator
    Coordinates all agents and manages the generation pipeline
    """
    
    def __init__(self, llm_client=None):
        self.llm_client = llm_client
        self.agents: Dict[AgentType, BaseAgent] = {
            AgentType.ARCHITECT: ArchitectAgent(llm_client),
            AgentType.CODER: CoderAgent(llm_client),
            AgentType.DESIGNER: DesignerAgent(llm_client),
            AgentType.SECURITY: SecurityAgent(llm_client),
            AgentType.DEPLOYER: DeployerAgent(llm_client)
        }
        self.task_queue: List[AgentTask] = []
        self.completed_tasks: List[AgentTask] = []
        self.message_bus: List[AgentMessage] = []
        self.update_callbacks: List[Callable] = []
        self.current_project_id: Optional[str] = None
    
    def on_update(self, callback: Callable):
        """Register callback for updates"""
        self.update_callbacks.append(callback)
    
    async def _notify(self, event_type: str, data: Dict):
        """Notify all callbacks"""
        for callback in self.update_callbacks:
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback(event_type, data)
                else:
                    callback(event_type, data)
            except Exception as e:
                logger.error(f"Callback error: {e}")
    
    async def run_full_pipeline(
        self,
        prompt: str,
        project_id: str,
        intent_type: str,
        features: List[str]
    ) -> Dict[str, Any]:
        """
        Run the complete generation pipeline through all phases
        """
        self.current_project_id = project_id
        results = {
            "project_id": project_id,
            "phases": {},
            "files": [],
            "errors": []
        }
        
        try:
            # Phase 1: Architecture
            await self._notify("phase_started", {"phase": "architecture", "project_id": project_id})
            arch_result = await self._run_architecture_phase(prompt, intent_type, features)
            results["phases"]["architecture"] = arch_result
            results["architecture"] = arch_result
            
            # Phase 2: Backend (if needed)
            if arch_result.get("backend"):
                await self._notify("phase_started", {"phase": "backend", "project_id": project_id})
                backend_result = await self._run_backend_phase(arch_result, prompt)
                results["phases"]["backend"] = backend_result
                results["files"].extend(backend_result.get("files", []))
            
            # Phase 3: Frontend
            await self._notify("phase_started", {"phase": "frontend", "project_id": project_id})
            frontend_result = await self._run_frontend_phase(arch_result, prompt)
            results["phases"]["frontend"] = frontend_result
            results["files"].extend(frontend_result.get("files", []))
            
            # Phase 4: Design/Styling
            await self._notify("phase_started", {"phase": "design", "project_id": project_id})
            design_result = await self._run_design_phase(results["files"], prompt, arch_result)
            results["phases"]["design"] = design_result
            results["files"] = design_result.get("files", results["files"])
            
            # Phase 5: Security
            await self._notify("phase_started", {"phase": "security", "project_id": project_id})
            security_result = await self._run_security_phase(results["files"], arch_result)
            results["phases"]["security"] = security_result
            results["security_report"] = security_result.get("security_report", {})
            
            # Phase 6: Deployment Prep
            await self._notify("phase_started", {"phase": "deployment", "project_id": project_id})
            deploy_result = await self._run_deployment_phase(results["files"], arch_result)
            results["phases"]["deployment"] = deploy_result
            results["files"] = deploy_result.get("files", results["files"])
            results["deploy_commands"] = deploy_result.get("deploy_commands", [])
            
            await self._notify("pipeline_completed", {
                "project_id": project_id,
                "files_count": len(results["files"]),
                "phases_completed": list(results["phases"].keys())
            })
            
        except Exception as e:
            logger.error(f"Pipeline error: {e}")
            results["errors"].append(str(e))
            await self._notify("pipeline_error", {
                "project_id": project_id,
                "error": str(e)
            })
        
        return results
    
    async def _run_architecture_phase(self, prompt: str, intent_type: str, features: List[str]) -> Dict:
        """Run architecture phase"""
        task = AgentTask(
            task_id=f"arch_{self.current_project_id}",
            agent_type=AgentType.ARCHITECT,
            phase=GenerationPhase.ARCHITECTURE,
            description="Create project architecture",
            input_data={
                "prompt": prompt,
                "intent_type": intent_type,
                "features": features
            }
        )
        
        architect = self.agents[AgentType.ARCHITECT]
        result = await architect.execute(task)
        self.completed_tasks.append(task)
        
        return result
    
    async def _run_backend_phase(self, architecture: Dict, prompt: str) -> Dict:
        """Run backend generation phase"""
        task = AgentTask(
            task_id=f"backend_{self.current_project_id}",
            agent_type=AgentType.CODER,
            phase=GenerationPhase.BACKEND,
            description="Generate backend code",
            input_data={
                "architecture": architecture,
                "prompt": prompt
            }
        )
        
        coder = self.agents[AgentType.CODER]
        result = await coder.execute(task)
        self.completed_tasks.append(task)
        
        return result
    
    async def _run_frontend_phase(self, architecture: Dict, prompt: str) -> Dict:
        """Run frontend generation phase"""
        task = AgentTask(
            task_id=f"frontend_{self.current_project_id}",
            agent_type=AgentType.CODER,
            phase=GenerationPhase.FRONTEND,
            description="Generate frontend code",
            input_data={
                "architecture": architecture,
                "prompt": prompt
            }
        )
        
        coder = self.agents[AgentType.CODER]
        result = await coder.execute(task)
        self.completed_tasks.append(task)
        
        return result
    
    async def _run_design_phase(self, files: List[Dict], prompt: str, architecture: Dict) -> Dict:
        """Run design/styling phase"""
        task = AgentTask(
            task_id=f"design_{self.current_project_id}",
            agent_type=AgentType.DESIGNER,
            phase=GenerationPhase.FRONTEND,
            description="Apply design and styling",
            input_data={
                "files": files,
                "prompt": prompt,
                "theme": architecture.get("theme", {})
            }
        )
        
        designer = self.agents[AgentType.DESIGNER]
        result = await designer.execute(task)
        self.completed_tasks.append(task)
        
        return result
    
    async def _run_security_phase(self, files: List[Dict], architecture: Dict) -> Dict:
        """Run security review phase"""
        task = AgentTask(
            task_id=f"security_{self.current_project_id}",
            agent_type=AgentType.SECURITY,
            phase=GenerationPhase.INTEGRATIONS,
            description="Add security measures",
            input_data={
                "files": files,
                "architecture": architecture
            }
        )
        
        security = self.agents[AgentType.SECURITY]
        result = await security.execute(task)
        self.completed_tasks.append(task)
        
        return result
    
    async def _run_deployment_phase(self, files: List[Dict], architecture: Dict) -> Dict:
        """Run deployment preparation phase"""
        task = AgentTask(
            task_id=f"deploy_{self.current_project_id}",
            agent_type=AgentType.DEPLOYER,
            phase=GenerationPhase.DEPLOYMENT,
            description="Prepare deployment",
            input_data={
                "files": files,
                "architecture": architecture
            }
        )
        
        deployer = self.agents[AgentType.DEPLOYER]
        result = await deployer.execute(task)
        self.completed_tasks.append(task)
        
        return result
    
    def get_status(self) -> Dict:
        """Get orchestrator status"""
        return {
            "current_project": self.current_project_id,
            "agents": {
                agent_type.value: agent.get_status()
                for agent_type, agent in self.agents.items()
            },
            "tasks_completed": len(self.completed_tasks),
            "tasks_pending": len(self.task_queue)
        }


# Singleton instance
_orchestrator: Optional[Orchestrator] = None


def get_orchestrator(llm_client=None) -> Orchestrator:
    """Get or create the singleton Orchestrator instance"""
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = Orchestrator(llm_client)
    return _orchestrator

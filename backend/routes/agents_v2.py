"""Complete Multi-Agent System for Melus AI - All Specialized Agents
Motor de Ejecución No Chat - Sistema de agentes especializados
"""
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import StreamingResponse
from typing import List, Optional, Dict, Any
import logging
import os
import json
import re
import asyncio
import io
import zipfile
from datetime import datetime

from utils import generate_id, utc_now, get_authenticated_user
from emergentintegrations.llm.chat import LlmChat, UserMessage
from templates.app_templates import get_template, get_all_templates, TEMPLATES
from services.execution_engine import (
    parse_project_template, 
    detect_execution_mode, 
    build_agent_prompt,
    get_project_template,
    ProjectPlan
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/agents/v2", tags=["agents-v2"])

EMERGENT_LLM_KEY = os.environ.get('EMERGENT_LLM_KEY')

# ============================================
# AGENT COSTS - Sistema de 13 Agentes
# ============================================
AGENT_COSTS = {
    # Core Generation Agents
    "classifier": 25,      # Classifies app type
    "architect": 50,       # Designs structure
    "frontend": 150,       # Generates React code
    "backend": 150,        # Generates API code
    "integrator": 75,      # Connects frontend/backend
    
    # Specialized Agents
    "design": 100,         # UI/UX design decisions
    "database": 100,       # Database schema design
    "testing": 75,         # Generates tests
    "security": 50,        # Security analysis
    "deploy": 50,          # Deployment configs
    
    # Utility Agents
    "debugger": 30,        # Fixes errors (monetization: 30 credits)
    "optimizer": 50,       # Code optimization
    "docs": 25,            # Documentation generation
}

# Ultra mode multiplier
ULTRA_MULTIPLIER = 2

# Execution modes
EXECUTION_MODE = "execution"  # Modo Motor - Sin chat
CHAT_MODE = "chat"            # Modo conversacional

# ============================================
# COMPLETE AGENT PROMPTS
# ============================================
AGENT_PROMPTS = {
    # ===== CLASSIFIER AGENT =====
    "classifier": """You are the Classifier Agent for Melus AI. Analyze the user's app request and classify it comprehensively.

OUTPUT JSON FORMAT:
{
    "app_type": "landing|saas|dashboard|marketplace|api|blog|ecommerce|portfolio|tool|chat|social|crm|booking|analytics",
    "complexity": "simple|medium|complex|enterprise",
    "requires_auth": boolean,
    "requires_database": boolean,
    "requires_payments": boolean,
    "requires_ai": boolean,
    "requires_realtime": boolean,
    "main_features": ["feature1", "feature2", ...],
    "tech_stack": {
        "frontend": "react|next|vue",
        "styling": "tailwind|css|styled-components",
        "backend": "express|fastapi|none",
        "database": "mongodb|postgresql|none",
        "auth": "jwt|oauth|none"
    },
    "estimated_pages": ["page1", "page2", ...],
    "estimated_components": ["component1", "component2", ...],
    "api_endpoints_needed": ["GET /api/users", "POST /api/products", ...],
    "summary": "Brief description of the app"
}

Be thorough in your analysis. Consider all aspects of the application.""",

    # ===== ARCHITECT AGENT =====
    "architect": """You are the Architect Agent for Melus AI. Design the complete file structure and architecture.

OUTPUT JSON FORMAT:
{
    "structure": {
        "src/App.jsx": "Main app component with routing",
        "src/components/Header.jsx": "Navigation header",
        "src/pages/Home.jsx": "Landing/home page",
        "src/context/AuthContext.jsx": "Authentication context",
        "src/hooks/useApi.js": "API hooks",
        "src/utils/helpers.js": "Utility functions",
        ...
    },
    "dependencies": ["react", "react-dom", "react-router-dom", "axios", "lucide-react"],
    "dev_dependencies": ["tailwindcss", "autoprefixer"],
    "routes": [
        {"path": "/", "component": "Home", "protected": false},
        {"path": "/dashboard", "component": "Dashboard", "protected": true},
        {"path": "/login", "component": "Login", "protected": false}
    ],
    "data_models": [
        {"name": "User", "fields": ["id", "email", "name", "createdAt"]},
        {"name": "Product", "fields": ["id", "name", "price", "description"]}
    ],
    "api_structure": {
        "base_url": "/api",
        "endpoints": [
            {"method": "GET", "path": "/users", "description": "Get all users"},
            {"method": "POST", "path": "/auth/login", "description": "User login"}
        ]
    },
    "state_management": "context|redux|zustand",
    "styling_approach": "tailwind-utility|component-based|css-modules"
}

Design a clean, scalable architecture following best practices.""",

    # ===== DESIGN AGENT =====
    "design": """You are the Design Agent for Melus AI. Create UI/UX design specifications and component styles.

OUTPUT JSON FORMAT:
{
    "theme": {
        "mode": "dark|light",
        "primary_color": "#8B5CF6",
        "secondary_color": "#EC4899",
        "background": "#0a0a12",
        "surface": "#1a1a2e",
        "text_primary": "#ffffff",
        "text_secondary": "#9ca3af",
        "accent": "#22c55e",
        "error": "#ef4444",
        "warning": "#f59e0b"
    },
    "typography": {
        "font_family": "Inter, system-ui, sans-serif",
        "heading_sizes": {"h1": "3rem", "h2": "2rem", "h3": "1.5rem"},
        "body_size": "1rem",
        "small_size": "0.875rem"
    },
    "spacing": {
        "xs": "0.25rem",
        "sm": "0.5rem",
        "md": "1rem",
        "lg": "1.5rem",
        "xl": "2rem",
        "2xl": "3rem"
    },
    "components": {
        "button": {
            "primary": "bg-purple-600 hover:bg-purple-700 text-white rounded-lg px-4 py-2",
            "secondary": "bg-gray-700 hover:bg-gray-600 text-white rounded-lg px-4 py-2",
            "ghost": "hover:bg-white/10 text-gray-400 rounded-lg px-4 py-2"
        },
        "card": "bg-[#1a1a2e] border border-purple-500/20 rounded-xl p-6",
        "input": "bg-gray-800 border border-gray-700 rounded-lg px-4 py-2 focus:border-purple-500",
        "badge": "bg-purple-500/20 text-purple-400 px-2 py-1 rounded text-xs"
    },
    "layout": {
        "max_width": "1280px",
        "sidebar_width": "280px",
        "header_height": "64px",
        "grid_columns": 12,
        "gap": "1.5rem"
    },
    "animations": {
        "duration_fast": "150ms",
        "duration_normal": "300ms",
        "duration_slow": "500ms",
        "easing": "cubic-bezier(0.4, 0, 0.2, 1)"
    },
    "responsive_breakpoints": {
        "sm": "640px",
        "md": "768px",
        "lg": "1024px",
        "xl": "1280px"
    }
}

Create a cohesive, modern design system. Focus on dark theme with purple accents.""",

    # ===== FRONTEND AGENT =====
    "frontend": """You are the Frontend Agent for Melus AI. Generate complete, production-ready React code.

CRITICAL RULES:
1. Generate COMPLETE, WORKING code - NO placeholders, NO "// TODO", NO "..."
2. Use React 18 with functional components and hooks
3. Use Tailwind CSS for all styling - DARK THEME (bg-gray-900, text-white)
4. Use React Router v6 syntax: Routes, Route, useNavigate
5. Include proper error handling and loading states
6. Make UI modern, beautiful, and responsive
7. Use lucide-react for icons

AVAILABLE DEPENDENCIES (DO NOT USE ANY OTHER EXTERNAL LIBRARIES):
- react, react-dom
- react-router-dom (v6)
- lucide-react (for icons)
- prop-types (optional)
- Tailwind CSS (via CDN, already included)

DO NOT import from axios, framer-motion, styled-components, or any other library not listed above.

REACT ROUTER V6 SYNTAX:
- Use <Routes> NOT <Switch>
- Use <Route path="/" element={<Component />} />
- Use useNavigate() NOT useHistory()
- Use useParams() for route params

STATE MANAGEMENT:
- Use useState for local state
- Use useContext for global state
- Use useReducer for complex state

OUTPUT JSON FORMAT:
{
    "files": {
        "src/App.jsx": "COMPLETE REACT CODE",
        "src/components/Header.jsx": "COMPLETE COMPONENT CODE",
        "src/pages/Home.jsx": "COMPLETE PAGE CODE",
        "src/context/AppContext.jsx": "COMPLETE CONTEXT CODE",
        "src/hooks/useApi.js": "COMPLETE HOOK CODE"
    }
}

Generate beautiful, production-ready code with proper imports and exports.""",

    # ===== BACKEND AGENT =====
    "backend": """You are the Backend Agent for Melus AI. Generate complete API code.

GENERATE:
- Express.js or FastAPI code
- RESTful API endpoints
- Database models
- Authentication middleware
- Error handling
- Input validation

OUTPUT JSON FORMAT:
{
    "files": {
        "server.js": "COMPLETE EXPRESS SERVER CODE",
        "routes/api.js": "COMPLETE ROUTE HANDLERS",
        "models/User.js": "COMPLETE MONGOOSE MODEL",
        "middleware/auth.js": "COMPLETE AUTH MIDDLEWARE",
        "utils/helpers.js": "UTILITY FUNCTIONS"
    },
    "env_vars": ["DATABASE_URL", "JWT_SECRET", "PORT"],
    "endpoints": [
        {"method": "GET", "path": "/api/users", "auth": true, "description": "Get all users"},
        {"method": "POST", "path": "/api/auth/login", "auth": false, "description": "User login"}
    ],
    "database_setup": "MongoDB connection and schema setup instructions"
}

Generate secure, well-structured backend code.""",

    # ===== DATABASE AGENT =====
    "database": """You are the Database Agent for Melus AI. Design database schemas and queries.

OUTPUT JSON FORMAT:
{
    "database_type": "mongodb|postgresql|mysql",
    "schemas": {
        "users": {
            "fields": {
                "id": {"type": "ObjectId|UUID", "primary": true},
                "email": {"type": "String", "unique": true, "required": true},
                "password": {"type": "String", "required": true},
                "name": {"type": "String"},
                "createdAt": {"type": "Date", "default": "now"}
            },
            "indexes": ["email"],
            "relations": []
        },
        "products": {
            "fields": {
                "id": {"type": "ObjectId|UUID", "primary": true},
                "name": {"type": "String", "required": true},
                "price": {"type": "Number", "required": true},
                "userId": {"type": "ObjectId", "ref": "users"}
            },
            "indexes": ["userId"],
            "relations": [{"field": "userId", "ref": "users", "type": "many-to-one"}]
        }
    },
    "queries": {
        "getUserById": "db.users.findOne({_id: ObjectId(id)})",
        "getProductsByUser": "db.products.find({userId: ObjectId(userId)})"
    },
    "migrations": [
        "CREATE TABLE users (...)",
        "CREATE INDEX idx_users_email ON users(email)"
    ],
    "seed_data": {
        "users": [{"email": "admin@example.com", "name": "Admin"}]
    }
}

Design efficient, normalized database schemas with proper indexing.""",

    # ===== INTEGRATOR AGENT =====
    "integrator": """You are the Integrator Agent for Melus AI. Connect frontend to backend seamlessly.

CHECK AND FIX:
1. API calls match backend endpoints exactly
2. Request/response data formats are correct
3. Error handling is consistent
4. Loading states work properly
5. Authentication tokens are handled correctly
6. CORS is configured properly

OUTPUT JSON FORMAT:
{
    "fixes": {
        "src/services/api.js": "COMPLETE API SERVICE CODE WITH AXIOS",
        "src/hooks/useAuth.js": "COMPLETE AUTH HOOK"
    },
    "api_config": {
        "base_url": "/api",
        "headers": {"Content-Type": "application/json"},
        "interceptors": ["auth_token", "error_handler"]
    },
    "integration_checklist": [
        {"item": "Login endpoint connected", "status": "complete"},
        {"item": "Protected routes working", "status": "complete"}
    ],
    "integration_notes": ["All API calls use axios instance", "Token stored in localStorage"]
}

Ensure seamless integration between all layers.""",

    # ===== TESTING AGENT =====
    "testing": """You are the Testing Agent for Melus AI. Generate comprehensive tests.

GENERATE:
- Unit tests for components
- Integration tests for API
- E2E test scenarios
- Test utilities and mocks

OUTPUT JSON FORMAT:
{
    "files": {
        "tests/components/Header.test.jsx": "COMPLETE JEST TEST",
        "tests/api/auth.test.js": "COMPLETE API TEST",
        "tests/e2e/login.spec.js": "COMPLETE E2E TEST"
    },
    "test_config": {
        "framework": "jest|vitest",
        "coverage_threshold": 80,
        "setup_files": ["tests/setup.js"]
    },
    "test_cases": [
        {"name": "renders header correctly", "type": "unit", "component": "Header"},
        {"name": "login with valid credentials", "type": "integration", "endpoint": "/api/auth/login"}
    ],
    "mocks": {
        "api": "Mock axios responses",
        "router": "Mock react-router"
    }
}

Generate thorough tests with good coverage.""",

    # ===== SECURITY AGENT =====
    "security": """You are the Security Agent for Melus AI. Analyze and fix security issues.

CHECK FOR:
1. XSS vulnerabilities
2. SQL/NoSQL injection
3. CSRF protection
4. Insecure dependencies
5. Hardcoded secrets
6. Improper authentication
7. Missing input validation

OUTPUT JSON FORMAT:
{
    "vulnerabilities": [
        {
            "severity": "high|medium|low",
            "type": "XSS|Injection|Auth|Config",
            "file": "src/components/Form.jsx",
            "line": 42,
            "description": "User input not sanitized",
            "fix": "Use DOMPurify to sanitize"
        }
    ],
    "fixes": {
        "src/components/Form.jsx": "FIXED CODE WITH SANITIZATION"
    },
    "security_headers": {
        "Content-Security-Policy": "default-src 'self'",
        "X-Frame-Options": "DENY",
        "X-Content-Type-Options": "nosniff"
    },
    "recommendations": [
        "Use helmet.js for Express",
        "Implement rate limiting",
        "Add input validation with Joi/Zod"
    ],
    "security_score": 85
}

Identify and fix all security issues.""",

    # ===== DEPLOY AGENT =====
    "deploy": """You are the Deploy Agent for Melus AI. Generate deployment configurations.

GENERATE CONFIGS FOR:
- Docker
- Vercel
- Netlify
- Railway
- AWS/GCP

OUTPUT JSON FORMAT:
{
    "files": {
        "Dockerfile": "COMPLETE DOCKERFILE",
        "docker-compose.yml": "COMPLETE COMPOSE FILE",
        "vercel.json": "VERCEL CONFIG",
        "netlify.toml": "NETLIFY CONFIG",
        ".env.example": "ENVIRONMENT TEMPLATE"
    },
    "deployment_steps": [
        "1. Set environment variables",
        "2. Build the application",
        "3. Deploy to platform"
    ],
    "environment_variables": {
        "required": ["DATABASE_URL", "JWT_SECRET"],
        "optional": ["ANALYTICS_ID", "SENTRY_DSN"]
    },
    "platform_specific": {
        "vercel": {"build_command": "npm run build", "output_dir": "dist"},
        "docker": {"port": 3000, "healthcheck": "/api/health"}
    },
    "ci_cd": {
        "github_actions": "COMPLETE WORKFLOW YAML"
    }
}

Generate production-ready deployment configs.""",

    # ===== DEBUGGER AGENT =====
    "debugger": """You are the Debug Agent (Fixer Agent) for Melus AI. Fix errors in code.

COST: 30 credits per use.

ANALYZE:
1. Error message and stack trace
2. Relevant code context
3. Common React/JavaScript errors

COMMON FIXES:
- "X is not defined" → Add missing import
- "Cannot read property" → Add null checks
- "Invalid hook call" → Fix hook placement
- "JSX syntax error" → Fix JSX structure
- "Module not found" → Fix import path

OUTPUT JSON FORMAT:
{
    "error_analysis": "Clear explanation of the error cause",
    "root_cause": "Specific line or pattern causing the issue",
    "fixes": {
        "path/to/file.jsx": "COMPLETE FIXED FILE CODE"
    },
    "explanation": "Step-by-step explanation of what was fixed",
    "prevention_tips": ["Always check for null", "Use optional chaining"]
}

Output COMPLETE fixed files, not patches. Preserve all functionality.""",

    # ===== OPTIMIZER AGENT =====
    "optimizer": """You are the Optimizer Agent for Melus AI. Optimize code for performance.

OPTIMIZE FOR:
1. Bundle size reduction
2. Render performance
3. Memory usage
4. Load time
5. Code splitting

OUTPUT JSON FORMAT:
{
    "optimizations": [
        {
            "type": "performance|bundle|memory",
            "file": "src/App.jsx",
            "before": "Original code snippet",
            "after": "Optimized code snippet",
            "impact": "30% faster render"
        }
    ],
    "files": {
        "src/App.jsx": "OPTIMIZED COMPLETE CODE"
    },
    "recommendations": [
        "Use React.memo for expensive components",
        "Implement code splitting with lazy()",
        "Use useMemo for computed values"
    ],
    "metrics": {
        "estimated_bundle_reduction": "15%",
        "estimated_load_time_improvement": "20%"
    }
}

Optimize while maintaining code readability.""",

    # ===== DOCS AGENT =====
    "docs": """You are the Documentation Agent for Melus AI. Generate comprehensive documentation.

GENERATE:
- README.md
- API documentation
- Component documentation
- Setup guides
- Code comments

OUTPUT JSON FORMAT:
{
    "files": {
        "README.md": "COMPLETE README WITH BADGES",
        "docs/API.md": "API DOCUMENTATION",
        "docs/COMPONENTS.md": "COMPONENT DOCS",
        "docs/SETUP.md": "SETUP GUIDE",
        "CONTRIBUTING.md": "CONTRIBUTION GUIDE"
    },
    "api_docs": [
        {
            "endpoint": "POST /api/auth/login",
            "description": "Authenticate user",
            "request": {"email": "string", "password": "string"},
            "response": {"token": "string", "user": "object"},
            "errors": ["401 Invalid credentials"]
        }
    ],
    "component_docs": [
        {
            "name": "Button",
            "props": [{"name": "variant", "type": "string", "default": "primary"}],
            "usage": "<Button variant='secondary'>Click me</Button>"
        }
    ]
}

Generate clear, comprehensive documentation."""
}

# ============================================
# AGENT EXECUTION FUNCTION
# ============================================
async def run_agent_v2(
    agent_type: str, 
    task: str, 
    context: dict, 
    db,
    workspace_id: str = None,
    ultra_mode: bool = False
) -> dict:
    """Execute an agent and optionally broadcast progress"""
    from routes.workspace import get_connection_manager
    
    if agent_type not in AGENT_PROMPTS:
        raise ValueError(f"Unknown agent: {agent_type}")
    
    manager = get_connection_manager()
    
    # Broadcast start
    if workspace_id:
        await manager.broadcast(workspace_id, {
            "type": "agent_start",
            "agent": agent_type,
            "task": task[:100],
            "ultra_mode": ultra_mode
        })
    
    try:
        # Ultra mode uses enhanced prompts
        system_prompt = AGENT_PROMPTS[agent_type]
        if ultra_mode:
            system_prompt = f"""[ULTRA MODE - MAXIMUM QUALITY]

{system_prompt}

ULTRA MODE REQUIREMENTS:
- Generate exceptionally high-quality, production-ready code
- Include comprehensive error handling
- Add detailed comments explaining complex logic
- Use best practices and modern patterns
- Ensure accessibility (ARIA labels, semantic HTML)
- Add loading states and smooth animations
- Include form validation where applicable
- Optimize for performance"""
        
        chat = LlmChat(
            api_key=EMERGENT_LLM_KEY,
            session_id=f"agent_{agent_type}_{generate_id('t')}",
            system_message=system_prompt
        )
        
        # Model selection
        model = "gpt-4o" if ultra_mode else "gpt-4o"
        chat.with_model("openai", model)
        
        # Build prompt
        context_str = json.dumps(context, indent=2, default=str) if context else "{}"
        prompt = f"""Task: {task}

Context:
{context_str}

Generate your response as valid JSON."""

        response = await chat.send_message(UserMessage(text=prompt))
        
        # Log raw response for debugging
        logger.info(f"Agent {agent_type} raw response length: {len(response)}")
        
        # Extract JSON from response with better error handling
        result = {}
        try:
            # Try to find JSON in response
            json_match = re.search(r'\{[\s\S]*\}', response)
            if json_match:
                json_str = json_match.group()
                try:
                    result = json.loads(json_str)
                except json.JSONDecodeError:
                    # Try extracting code blocks from the response if JSON fails
                    code_blocks = re.findall(r'```(?:jsx?|javascript|tsx?)?\n([\s\S]*?)```', response)
                    if code_blocks:
                        result = {"files": {"src/App.jsx": code_blocks[0]}}
                    else:
                        result = {"raw_response": response[:5000]}
            else:
                # No JSON found, try to extract code blocks
                code_blocks = re.findall(r'```(?:jsx?|javascript|tsx?)?\n([\s\S]*?)```', response)
                if code_blocks:
                    result = {"files": {"src/App.jsx": code_blocks[0]}}
                else:
                    result = {"raw_response": response[:5000]}
            
            # Post-process: ensure file contents have proper newlines
            if "files" in result:
                processed_files = {}
                for path, content in result["files"].items():
                    if isinstance(content, str):
                        # Convert escaped newlines to real newlines if they're literal strings
                        if '\\n' in content and '\n' not in content:
                            content = content.replace('\\n', '\n')
                        if '\\t' in content:
                            content = content.replace('\\t', '\t')
                        # Remove any remaining escape issues
                        content = content.replace('\\"', '"')
                    processed_files[path] = content
                result["files"] = processed_files
                
        except Exception as parse_error:
            logger.warning(f"JSON parse error in {agent_type}: {parse_error}")
            logger.warning(f"Raw response (first 1000 chars): {response[:1000]}")
            result = {"raw_response": response[:5000], "parse_error": str(parse_error)}
        
        # Broadcast completion
        if workspace_id:
            await manager.broadcast(workspace_id, {
                "type": "agent_complete",
                "agent": agent_type,
                "success": True,
                "ultra_mode": ultra_mode
            })
        
        # Calculate cost with ultra multiplier
        base_cost = AGENT_COSTS.get(agent_type, 50)
        final_cost = base_cost * ULTRA_MULTIPLIER if ultra_mode else base_cost
        
        return {
            "agent": agent_type,
            "result": result,
            "credits_used": final_cost,
            "ultra_mode": ultra_mode,
            "timestamp": utc_now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Agent {agent_type} failed: {e}")
        
        if workspace_id:
            await manager.broadcast(workspace_id, {
                "type": "agent_error",
                "agent": agent_type,
                "error": str(e)
            })
        
        raise


# ============================================
# API ENDPOINTS
# ============================================

@router.get("/costs")
async def get_costs():
    """Get all agent costs"""
    total = sum(AGENT_COSTS.values())
    return {
        "costs": AGENT_COSTS,
        "total": total,
        "ultra_multiplier": ULTRA_MULTIPLIER,
        "categories": {
            "generation": ["classifier", "architect", "frontend", "backend", "integrator"],
            "specialized": ["design", "database", "testing", "security", "deploy"],
            "utility": ["debugger", "optimizer", "docs"]
        },
        "modes": {
            "execution": "Motor No Chat - Ejecución directa de proyectos",
            "chat": "Modo conversacional tradicional"
        }
    }


@router.get("/template")
async def get_template_format():
    """Get the project template format for Motor No Chat mode"""
    return {
        "template": get_project_template(),
        "description": "Plantilla para modo Motor (No Chat). Completa cada sección con las instrucciones para cada agente.",
        "agents": [
            "FRONTEND AGENT - UI y componentes",
            "BACKEND AGENT - APIs y servidor",
            "DATABASE AGENT - Esquemas y datos",
            "INTEGRATION AGENT - Servicios externos",
            "TESTING AGENT - Pruebas automatizadas",
            "SECURITY AGENT - Análisis de seguridad",
            "DEPLOYMENT AGENT - Configuración de despliegue"
        ],
        "tips": [
            "Usa comandos directos: 'Genera...', 'Construye...', 'Implementa...'",
            "Evita preguntas tipo '¿Qué opinas?' o '¿Cómo puedo?'",
            "Especifica frameworks y tecnologías exactas",
            "Incluye todos los detalles de funcionalidad"
        ]
    }


@router.post("/execute-project")
async def execute_project_no_chat(request: Request):
    """
    MODO MOTOR (NO CHAT) - Ejecuta un proyecto completo automáticamente
    
    Este endpoint recibe una plantilla de proyecto y ejecuta TODOS los agentes
    en secuencia sin interacción de chat.
    
    Flujo:
    1. Parsear plantilla de proyecto
    2. Ejecutar agentes en orden: classifier -> architect -> design -> frontend -> backend -> database -> integration -> testing -> security -> deploy
    3. Retornar proyecto completo
    """
    from routes.workspace import get_connection_manager
    
    db = request.app.state.db
    user_doc = await get_authenticated_user(request, db)
    user_id = user_doc["user_id"]
    
    body = await request.json()
    project_template = body.get("template", body.get("description", ""))
    project_name = body.get("name", "Mi Proyecto")
    ultra_mode = body.get("ultra_mode", False)
    
    # Detectar modo de ejecución
    mode = detect_execution_mode(project_template)
    
    if mode == CHAT_MODE:
        # Si detectamos modo chat, sugerir usar el otro endpoint
        return {
            "mode_detected": "chat",
            "message": "Tu prompt parece ser conversacional. Usa /generate para modo chat o reformula tu prompt con comandos directos.",
            "tip": "Usa: 'Genera una app de...' en lugar de '¿Qué opinas de...?'"
        }
    
    # Parsear plantilla si tiene formato estructurado
    project_plan = None
    if '# FRONTEND' in project_template or '# BACKEND' in project_template:
        project_plan = parse_project_template(project_template)
        project_name = project_plan.name or project_name
    
    # Calcular costo total (todos los agentes)
    agents_to_run = ['classifier', 'architect', 'design', 'frontend', 'backend', 'database', 'integrator', 'testing', 'security', 'deploy', 'docs']
    multiplier = ULTRA_MULTIPLIER if ultra_mode else 1
    total_cost = sum(AGENT_COSTS.get(a, 50) for a in agents_to_run) * multiplier
    
    # Check if user has unlimited credits (owner)
    is_unlimited = user_doc.get("unlimited_credits", False) or user_doc.get("is_owner", False)
    
    if not is_unlimited and user_doc["credits"] < total_cost:
        raise HTTPException(
            status_code=402,
            detail=f"Proyecto completo requiere {total_cost} créditos. Tienes {user_doc['credits']}."
        )
    
    manager = get_connection_manager()
    
    # Crear workspace
    workspace_id = generate_id("ws")
    mode_label = "ULTRA MODE" if ultra_mode else "Normal"
    workspace = {
        "workspace_id": workspace_id,
        "user_id": user_id,
        "name": project_name,
        "description": project_template[:500],
        "mode": "execution",
        "ultra_mode": ultra_mode,
        "files": {},
        "versions": [],
        "current_version": 0,
        "status": "generating",
        "agent_results": {},
        "created_at": utc_now(),
        "updated_at": utc_now()
    }
    await db.workspaces.insert_one(workspace)
    
    total_credits_used = 0
    all_files = {}
    agent_results = {}
    
    try:
        await manager.broadcast(workspace_id, {
            "type": "log",
            "log": {
                "agent": "system",
                "type": "info",
                "message": f"[{mode_label}] MODO MOTOR INICIADO - Ejecutando {len(agents_to_run)} agentes",
                "timestamp": utc_now().isoformat()
            }
        })
        
        # ========================================
        # PASO 1: CLASSIFIER - Analizar proyecto
        # ========================================
        await manager.broadcast(workspace_id, {
            "type": "log",
            "log": {
                "agent": "classifier",
                "type": "working",
                "message": "Analizando tipo de aplicación...",
                "timestamp": utc_now().isoformat()
            }
        })
        
        classifier_result = await run_agent_v2(
            "classifier",
            f"Classify this app: {project_template}",
            {"project_name": project_name},
            db, workspace_id, ultra_mode
        )
        total_credits_used += classifier_result["credits_used"]
        classification = classifier_result["result"]
        agent_results["classifier"] = classification
        
        await manager.broadcast(workspace_id, {
            "type": "log",
            "log": {
                "agent": "classifier",
                "type": "success",
                "message": f"Tipo: {classification.get('app_type', 'custom')} | Complejidad: {classification.get('complexity', 'medium')}",
                "timestamp": utc_now().isoformat()
            }
        })
        
        # ========================================
        # PASO 2: ARCHITECT - Diseñar estructura
        # ========================================
        await manager.broadcast(workspace_id, {
            "type": "log",
            "log": {
                "agent": "architect",
                "type": "working",
                "message": "Diseñando arquitectura del proyecto...",
                "timestamp": utc_now().isoformat()
            }
        })
        
        architect_result = await run_agent_v2(
            "architect",
            f"Design complete architecture for: {project_template}",
            {"classification": classification, "project_name": project_name},
            db, workspace_id, ultra_mode
        )
        total_credits_used += architect_result["credits_used"]
        architecture = architect_result["result"]
        agent_results["architect"] = architecture
        
        await manager.broadcast(workspace_id, {
            "type": "log",
            "log": {
                "agent": "architect",
                "type": "success",
                "message": f"Estructura: {len(architecture.get('structure', {}))} archivos planificados",
                "timestamp": utc_now().isoformat()
            }
        })
        
        # ========================================
        # PASO 3: DESIGN - Sistema de diseño
        # ========================================
        await manager.broadcast(workspace_id, {
            "type": "log",
            "log": {
                "agent": "design",
                "type": "working",
                "message": "Creando sistema de diseño UI/UX...",
                "timestamp": utc_now().isoformat()
            }
        })
        
        design_result = await run_agent_v2(
            "design",
            f"Create design system for: {project_template}",
            {"classification": classification, "architecture": architecture},
            db, workspace_id, ultra_mode
        )
        total_credits_used += design_result["credits_used"]
        design_system = design_result["result"]
        agent_results["design"] = design_system
        
        await manager.broadcast(workspace_id, {
            "type": "log",
            "log": {
                "agent": "design",
                "type": "success",
                "message": f"Tema: {design_system.get('theme', {}).get('mode', 'dark')} | Colores definidos",
                "timestamp": utc_now().isoformat()
            }
        })
        
        # ========================================
        # PASO 4: DATABASE - Esquemas de datos
        # ========================================
        if classification.get("requires_database", True):
            await manager.broadcast(workspace_id, {
                "type": "log",
                "log": {
                    "agent": "database",
                    "type": "working",
                    "message": "Diseñando esquemas de base de datos...",
                    "timestamp": utc_now().isoformat()
                }
            })
            
            database_result = await run_agent_v2(
                "database",
                f"Design database schema for: {project_template}",
                {"classification": classification, "architecture": architecture},
                db, workspace_id, ultra_mode
            )
            total_credits_used += database_result["credits_used"]
            database_schema = database_result["result"]
            agent_results["database"] = database_schema
            
            await manager.broadcast(workspace_id, {
                "type": "log",
                "log": {
                    "agent": "database",
                    "type": "success",
                    "message": f"DB: {database_schema.get('database_type', 'mongodb')} | Tablas diseñadas",
                    "timestamp": utc_now().isoformat()
                }
            })
        
        # ========================================
        # PASO 5: FRONTEND - Generar UI
        # ========================================
        await manager.broadcast(workspace_id, {
            "type": "log",
            "log": {
                "agent": "frontend",
                "type": "working",
                "message": "Generando componentes React...",
                "timestamp": utc_now().isoformat()
            }
        })
        
        frontend_context = {
            "classification": classification,
            "architecture": architecture,
            "design": design_system,
            "project_name": project_name
        }
        
        frontend_result = await run_agent_v2(
            "frontend",
            f"Generate complete React frontend for: {project_template}",
            frontend_context,
            db, workspace_id, ultra_mode
        )
        total_credits_used += frontend_result["credits_used"]
        
        frontend_files = frontend_result["result"].get("files", {})
        all_files.update(frontend_files)
        agent_results["frontend"] = {"files_generated": len(frontend_files)}
        
        await manager.broadcast(workspace_id, {
            "type": "log",
            "log": {
                "agent": "frontend",
                "type": "success",
                "message": f"Generados {len(frontend_files)} archivos frontend",
                "timestamp": utc_now().isoformat()
            }
        })
        
        # Broadcast files update
        await manager.broadcast(workspace_id, {
            "type": "files_updated",
            "files": all_files
        })
        
        # ========================================
        # PASO 6: BACKEND - Generar APIs
        # ========================================
        if classification.get("requires_database") or classification.get("requires_auth"):
            await manager.broadcast(workspace_id, {
                "type": "log",
                "log": {
                    "agent": "backend",
                    "type": "working",
                    "message": "Generando APIs y servidor...",
                    "timestamp": utc_now().isoformat()
                }
            })
            
            backend_result = await run_agent_v2(
                "backend",
                f"Generate backend API for: {project_template}",
                {"classification": classification, "database": agent_results.get("database", {})},
                db, workspace_id, ultra_mode
            )
            total_credits_used += backend_result["credits_used"]
            
            backend_files = backend_result["result"].get("files", {})
            for path, content in backend_files.items():
                all_files[f"backend/{path}"] = content
            
            agent_results["backend"] = {"files_generated": len(backend_files)}
            
            await manager.broadcast(workspace_id, {
                "type": "log",
                "log": {
                    "agent": "backend",
                    "type": "success",
                    "message": f"Generados {len(backend_files)} archivos backend",
                    "timestamp": utc_now().isoformat()
                }
            })
        
        # ========================================
        # PASO 7: INTEGRATOR - Conectar todo
        # ========================================
        await manager.broadcast(workspace_id, {
            "type": "log",
            "log": {
                "agent": "integrator",
                "type": "working",
                "message": "Integrando frontend con backend...",
                "timestamp": utc_now().isoformat()
            }
        })
        
        integrator_result = await run_agent_v2(
            "integrator",
            "Integrate and verify all components",
            {"files": all_files, "classification": classification},
            db, workspace_id, ultra_mode
        )
        total_credits_used += integrator_result["credits_used"]
        
        integration_fixes = integrator_result["result"].get("fixes", {})
        all_files.update(integration_fixes)
        
        await manager.broadcast(workspace_id, {
            "type": "log",
            "log": {
                "agent": "integrator",
                "type": "success",
                "message": "Integración completada",
                "timestamp": utc_now().isoformat()
            }
        })
        
        # ========================================
        # PASO 8: TESTING - Generar tests
        # ========================================
        await manager.broadcast(workspace_id, {
            "type": "log",
            "log": {
                "agent": "testing",
                "type": "working",
                "message": "Generando tests automatizados...",
                "timestamp": utc_now().isoformat()
            }
        })
        
        testing_result = await run_agent_v2(
            "testing",
            "Generate tests for all components and APIs",
            {"files": all_files, "classification": classification},
            db, workspace_id, ultra_mode
        )
        total_credits_used += testing_result["credits_used"]
        
        test_files = testing_result["result"].get("files", {})
        for path, content in test_files.items():
            all_files[f"tests/{path}"] = content
        
        await manager.broadcast(workspace_id, {
            "type": "log",
            "log": {
                "agent": "testing",
                "type": "success",
                "message": f"Generados {len(test_files)} archivos de tests",
                "timestamp": utc_now().isoformat()
            }
        })
        
        # ========================================
        # PASO 9: SECURITY - Análisis
        # ========================================
        await manager.broadcast(workspace_id, {
            "type": "log",
            "log": {
                "agent": "security",
                "type": "working",
                "message": "Analizando seguridad...",
                "timestamp": utc_now().isoformat()
            }
        })
        
        security_result = await run_agent_v2(
            "security",
            "Analyze and fix security issues",
            {"files": all_files},
            db, workspace_id, ultra_mode
        )
        total_credits_used += security_result["credits_used"]
        
        security_fixes = security_result["result"].get("fixes", {})
        all_files.update(security_fixes)
        
        vulnerabilities = security_result["result"].get("vulnerabilities", [])
        
        await manager.broadcast(workspace_id, {
            "type": "log",
            "log": {
                "agent": "security",
                "type": "success",
                "message": f"Seguridad: {len(vulnerabilities)} issues encontrados y corregidos",
                "timestamp": utc_now().isoformat()
            }
        })
        
        # ========================================
        # PASO 10: DEPLOY - Configuración
        # ========================================
        await manager.broadcast(workspace_id, {
            "type": "log",
            "log": {
                "agent": "deploy",
                "type": "working",
                "message": "Generando configuración de despliegue...",
                "timestamp": utc_now().isoformat()
            }
        })
        
        deploy_result = await run_agent_v2(
            "deploy",
            "Generate deployment configuration for Vercel and Docker",
            {"files": all_files, "project_name": project_name},
            db, workspace_id, ultra_mode
        )
        total_credits_used += deploy_result["credits_used"]
        
        deploy_files = deploy_result["result"].get("files", {})
        all_files.update(deploy_files)
        
        await manager.broadcast(workspace_id, {
            "type": "log",
            "log": {
                "agent": "deploy",
                "type": "success",
                "message": "Configuración de deploy generada",
                "timestamp": utc_now().isoformat()
            }
        })
        
        # ========================================
        # PASO 11: DOCS - Documentación
        # ========================================
        await manager.broadcast(workspace_id, {
            "type": "log",
            "log": {
                "agent": "docs",
                "type": "working",
                "message": "Generando documentación...",
                "timestamp": utc_now().isoformat()
            }
        })
        
        docs_result = await run_agent_v2(
            "docs",
            f"Generate documentation for {project_name}",
            {"files": all_files, "classification": classification},
            db, workspace_id, ultra_mode
        )
        total_credits_used += docs_result["credits_used"]
        
        docs_files = docs_result["result"].get("files", {})
        all_files.update(docs_files)
        
        await manager.broadcast(workspace_id, {
            "type": "log",
            "log": {
                "agent": "docs",
                "type": "success",
                "message": "Documentación generada",
                "timestamp": utc_now().isoformat()
            }
        })
        
        # ========================================
        # FINALIZAR - Agregar archivos base
        # ========================================
        base_files = {
            "package.json": json.dumps({
                "name": project_name.lower().replace(" ", "-"),
                "private": True,
                "version": "0.0.1",
                "dependencies": {
                    "react": "^18.2.0",
                    "react-dom": "^18.2.0",
                    "react-router-dom": "^6.20.0"
                }
            }, indent=2),
            "public/index.html": f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>{project_name}</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-gray-900">
    <div id="root"></div>
</body>
</html>""",
            "src/index.js": """import React from 'react';
import { createRoot } from 'react-dom/client';
import App from './App';

const root = createRoot(document.getElementById('root'));
root.render(<App />);"""
        }
        
        for path, content in base_files.items():
            if path not in all_files:
                all_files[path] = content
        
        # Guardar en workspace
        await db.workspaces.update_one(
            {"workspace_id": workspace_id},
            {
                "$set": {
                    "files": all_files,
                    "status": "completed",
                    "current_version": 1,
                    "classification": classification,
                    "architecture": architecture,
                    "design_system": design_system,
                    "agent_results": agent_results,
                    "total_credits_used": total_credits_used,
                    "updated_at": utc_now()
                },
                "$push": {
                    "versions": {
                        "version": 1,
                        "files": all_files,
                        "created_at": utc_now(),
                        "message": f"[{mode_label}] MOTOR NO CHAT - Proyecto completo"
                    }
                }
            }
        )
        
        # Deducir créditos (solo si no es usuario ilimitado)
        if not is_unlimited:
            await db.users.update_one(
                {"user_id": user_id},
                {"$inc": {"credits": -total_credits_used, "credits_used": total_credits_used}}
            )
        
        updated_user = await db.users.find_one({"user_id": user_id}, {"credits": 1})
        credits_msg = "GRATIS (Owner)" if is_unlimited else f"{total_credits_used} créditos"
        
        # Broadcast final
        await manager.broadcast(workspace_id, {
            "type": "generation_complete",
            "files": all_files,
            "workspace_id": workspace_id,
            "credits_used": 0 if is_unlimited else total_credits_used
        })
        
        await manager.broadcast(workspace_id, {
            "type": "log",
            "log": {
                "agent": "system",
                "type": "success",
                "message": f"PROYECTO COMPLETO! {len(all_files)} archivos | {credits_msg} | {len(agents_to_run)} agentes ejecutados",
                "timestamp": utc_now().isoformat()
            }
        })
        
        return {
            "mode": "execution",
            "workspace_id": workspace_id,
            "project_name": project_name,
            "files": all_files,
            "files_count": len(all_files),
            "agents_executed": agents_to_run,
            "classification": classification,
            "credits_used": 0 if is_unlimited else total_credits_used,
            "credits_remaining": updated_user.get("credits", 0),
            "ultra_mode": ultra_mode,
            "is_unlimited": is_unlimited
        }
        
    except Exception as e:
        logger.error(f"Motor execution failed: {e}")
        
        await manager.broadcast(workspace_id, {
            "type": "log",
            "log": {
                "agent": "system",
                "type": "error",
                "message": f"Error: {str(e)}",
                "timestamp": utc_now().isoformat()
            }
        })
        
        await db.workspaces.update_one(
            {"workspace_id": workspace_id},
            {"$set": {"status": "failed", "error": str(e)}}
        )
        
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/agents")
async def list_agents():
    """List all available agents with descriptions"""
    agents = [
        {"id": "classifier", "name": "Classifier", "description": "Analiza y clasifica el tipo de aplicación", "cost": 25, "icon": "Cpu"},
        {"id": "architect", "name": "Architect", "description": "Diseña la estructura y arquitectura", "cost": 50, "icon": "FolderTree"},
        {"id": "design", "name": "Design", "description": "Define UI/UX y sistema de diseño", "cost": 100, "icon": "Palette"},
        {"id": "frontend", "name": "Frontend", "description": "Genera código React completo", "cost": 150, "icon": "Code"},
        {"id": "backend", "name": "Backend", "description": "Genera APIs y lógica de servidor", "cost": 150, "icon": "Server"},
        {"id": "database", "name": "Database", "description": "Diseña esquemas y queries", "cost": 100, "icon": "Database"},
        {"id": "integrator", "name": "Integrator", "description": "Conecta frontend con backend", "cost": 75, "icon": "Link"},
        {"id": "testing", "name": "Testing", "description": "Genera tests automatizados", "cost": 75, "icon": "TestTube"},
        {"id": "security", "name": "Security", "description": "Analiza vulnerabilidades", "cost": 50, "icon": "Shield"},
        {"id": "deploy", "name": "Deploy", "description": "Genera configs de despliegue", "cost": 50, "icon": "Rocket"},
        {"id": "debugger", "name": "Debug", "description": "Corrige errores automáticamente", "cost": 30, "icon": "Bug"},
        {"id": "optimizer", "name": "Optimizer", "description": "Optimiza rendimiento", "cost": 50, "icon": "Zap"},
        {"id": "docs", "name": "Docs", "description": "Genera documentación", "cost": 25, "icon": "FileText"},
    ]
    return {"agents": agents}


@router.post("/run-agent")
async def run_single_agent(request: Request):
    """Run a single agent on demand"""
    db = request.app.state.db
    user_doc = await get_authenticated_user(request, db)
    user_id = user_doc["user_id"]
    
    body = await request.json()
    agent_type = body.get("agent")
    task = body.get("task", "")
    context = body.get("context", {})
    workspace_id = body.get("workspace_id")
    ultra_mode = body.get("ultra_mode", False)
    
    if not agent_type or agent_type not in AGENT_COSTS:
        raise HTTPException(status_code=400, detail=f"Invalid agent: {agent_type}")
    
    # Check if user has unlimited credits (owner)
    is_unlimited = user_doc.get("unlimited_credits", False) or user_doc.get("is_owner", False)
    
    # Check credits
    multiplier = ULTRA_MULTIPLIER if ultra_mode else 1
    cost = AGENT_COSTS[agent_type] * multiplier
    
    if not is_unlimited and user_doc["credits"] < cost:
        raise HTTPException(
            status_code=402,
            detail=f"Need {cost} credits, you have {user_doc['credits']}"
        )
    
    # Run agent
    result = await run_agent_v2(
        agent_type, task, context, db, workspace_id, ultra_mode
    )
    
    # Deduct credits (only if not unlimited)
    if not is_unlimited:
        await db.users.update_one(
            {"user_id": user_id},
            {"$inc": {"credits": -cost, "credits_used": cost}}
        )
    
    # Get updated credits
    updated_user = await db.users.find_one({"user_id": user_id}, {"credits": 1})
    
    return {
        **result,
        "credits_remaining": updated_user.get("credits", 0),
        "is_unlimited": is_unlimited
    }


@router.post("/generate")
async def generate_app_v2(request: Request):
    """Generate a complete application with all agents"""
    from routes.workspace import get_connection_manager
    
    db = request.app.state.db
    user_doc = await get_authenticated_user(request, db)
    user_id = user_doc["user_id"]
    
    body = await request.json()
    description = body.get("description", "")
    app_name = body.get("name", "My App")
    workspace_id = body.get("workspace_id")
    ultra_mode = body.get("ultra_mode", False)
    include_agents = body.get("agents", ["classifier", "architect", "design", "frontend", "integrator"])
    
    if not description:
        raise HTTPException(status_code=400, detail="Description required")
    
    # Calculate estimated cost
    multiplier = ULTRA_MULTIPLIER if ultra_mode else 1
    total_cost = sum(AGENT_COSTS.get(a, 50) for a in include_agents) * multiplier
    
    if user_doc["credits"] < total_cost:
        raise HTTPException(
            status_code=402,
            detail=f"Need {total_cost} credits, you have {user_doc['credits']}"
        )
    
    manager = get_connection_manager()
    
    # Create workspace if not provided
    if not workspace_id:
        workspace_id = generate_id("ws")
        workspace = {
            "workspace_id": workspace_id,
            "user_id": user_id,
            "name": app_name,
            "description": description,
            "template": "react-vite",
            "ultra_mode": ultra_mode,
            "files": {},
            "versions": [],
            "current_version": 0,
            "status": "generating",
            "build_logs": [],
            "created_at": utc_now(),
            "updated_at": utc_now()
        }
        await db.workspaces.insert_one(workspace)
    
    total_credits_used = 0
    all_files = {}
    agent_results = {}
    
    try:
        mode_label = "ULTRA MODE" if ultra_mode else "Normal"
        
        # STEP 1: Classifier
        if "classifier" in include_agents:
            await manager.broadcast(workspace_id, {
                "type": "log",
                "log": {
                    "agent": "classifier",
                    "type": "working",
                    "message": f"[{mode_label}] Analizando requisitos...",
                    "timestamp": utc_now().isoformat()
                }
            })
            
            classifier_result = await run_agent_v2(
                "classifier",
                f"Classify this app: {description}",
                {"app_name": app_name, "description": description},
                db, workspace_id, ultra_mode
            )
            total_credits_used += classifier_result["credits_used"]
            classification = classifier_result["result"]
            agent_results["classifier"] = classification
            
            await manager.broadcast(workspace_id, {
                "type": "log",
                "log": {
                    "agent": "classifier",
                    "type": "success",
                    "message": f"Clasificado: {classification.get('app_type', 'app')} ({classification.get('complexity', 'medium')})",
                    "timestamp": utc_now().isoformat()
                }
            })
        else:
            classification = {"app_type": "custom", "complexity": "medium"}
        
        # STEP 2: Architect
        if "architect" in include_agents:
            await manager.broadcast(workspace_id, {
                "type": "log",
                "log": {
                    "agent": "architect",
                    "type": "working",
                    "message": "Diseñando arquitectura...",
                    "timestamp": utc_now().isoformat()
                }
            })
            
            architect_result = await run_agent_v2(
                "architect",
                f"Design architecture for: {description}",
                {"classification": classification},
                db, workspace_id, ultra_mode
            )
            total_credits_used += architect_result["credits_used"]
            architecture = architect_result["result"]
            agent_results["architect"] = architecture
            
            await manager.broadcast(workspace_id, {
                "type": "log",
                "log": {
                    "agent": "architect",
                    "type": "success",
                    "message": f"Arquitectura: {len(architecture.get('structure', {}))} archivos planificados",
                    "timestamp": utc_now().isoformat()
                }
            })
        else:
            architecture = {}
        
        # STEP 3: Design
        if "design" in include_agents:
            await manager.broadcast(workspace_id, {
                "type": "log",
                "log": {
                    "agent": "design",
                    "type": "working",
                    "message": "Creando sistema de diseño...",
                    "timestamp": utc_now().isoformat()
                }
            })
            
            design_result = await run_agent_v2(
                "design",
                f"Create design system for: {description}",
                {"classification": classification, "architecture": architecture},
                db, workspace_id, ultra_mode
            )
            total_credits_used += design_result["credits_used"]
            design_system = design_result["result"]
            agent_results["design"] = design_system
            
            await manager.broadcast(workspace_id, {
                "type": "log",
                "log": {
                    "agent": "design",
                    "type": "success",
                    "message": f"Tema: {design_system.get('theme', {}).get('mode', 'dark')}",
                    "timestamp": utc_now().isoformat()
                }
            })
        else:
            design_system = {}
        
        # STEP 4: Frontend
        if "frontend" in include_agents:
            await manager.broadcast(workspace_id, {
                "type": "log",
                "log": {
                    "agent": "frontend",
                    "type": "working",
                    "message": "Generando componentes React...",
                    "timestamp": utc_now().isoformat()
                }
            })
            
            frontend_result = await run_agent_v2(
                "frontend",
                f"""Generate complete React frontend for: {description}
                
Pages: {json.dumps(classification.get('estimated_pages', []))}
Features: {json.dumps(classification.get('main_features', []))}
Make it beautiful with Tailwind CSS dark theme.""",
                {
                    "classification": classification,
                    "architecture": architecture,
                    "design": design_system,
                    "app_name": app_name
                },
                db, workspace_id, ultra_mode
            )
            total_credits_used += frontend_result["credits_used"]
            
            frontend_files = frontend_result["result"].get("files", {})
            logger.info(f"Frontend files generated: {len(frontend_files)} files - Keys: {list(frontend_files.keys())[:5]}")
            all_files.update(frontend_files)
            
            await manager.broadcast(workspace_id, {
                "type": "log",
                "log": {
                    "agent": "frontend",
                    "type": "success",
                    "message": f"Generados {len(frontend_files)} archivos frontend",
                    "timestamp": utc_now().isoformat()
                }
            })
        
        # Update workspace with files
        await manager.broadcast(workspace_id, {
            "type": "files_updated",
            "files": all_files
        })
        
        # STEP 5: Backend (if needed)
        if "backend" in include_agents and (classification.get("requires_database") or classification.get("requires_auth")):
            await manager.broadcast(workspace_id, {
                "type": "log",
                "log": {
                    "agent": "backend",
                    "type": "working",
                    "message": "Generando APIs...",
                    "timestamp": utc_now().isoformat()
                }
            })
            
            backend_result = await run_agent_v2(
                "backend",
                f"Generate backend API for: {description}",
                {"classification": classification, "architecture": architecture},
                db, workspace_id, ultra_mode
            )
            total_credits_used += backend_result["credits_used"]
            
            backend_files = backend_result["result"].get("files", {})
            for path, content in backend_files.items():
                all_files[f"backend/{path}"] = content
            
            await manager.broadcast(workspace_id, {
                "type": "log",
                "log": {
                    "agent": "backend",
                    "type": "success",
                    "message": f"Generados {len(backend_files)} archivos backend",
                    "timestamp": utc_now().isoformat()
                }
            })
        
        # STEP 6: Integration
        if "integrator" in include_agents:
            await manager.broadcast(workspace_id, {
                "type": "log",
                "log": {
                    "agent": "integrator",
                    "type": "working",
                    "message": "Conectando componentes...",
                    "timestamp": utc_now().isoformat()
                }
            })
            
            integrator_result = await run_agent_v2(
                "integrator",
                "Verify and fix integration",
                {"files": all_files, "classification": classification},
                db, workspace_id, ultra_mode
            )
            total_credits_used += integrator_result["credits_used"]
            
            integration_fixes = integrator_result["result"].get("fixes", {})
            all_files.update(integration_fixes)
            
            await manager.broadcast(workspace_id, {
                "type": "log",
                "log": {
                    "agent": "integrator",
                    "type": "success",
                    "message": "Integración completada",
                    "timestamp": utc_now().isoformat()
                }
            })
        
        # Add base files for Sandpack
        base_files = {
            "package.json": json.dumps({
                "name": app_name.lower().replace(" ", "-"),
                "private": True,
                "version": "0.0.1",
                "dependencies": {
                    "react": "^18.2.0",
                    "react-dom": "^18.2.0",
                    "react-router-dom": "^6.20.0",
                    "lucide-react": "^0.294.0",
                    "prop-types": "^15.8.1"
                }
            }, indent=2),
            "public/index.html": f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>{app_name}</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-gray-900">
    <div id="root"></div>
</body>
</html>""",
            "src/index.js": """import React from 'react';
import { createRoot } from 'react-dom/client';
import App from './App';

const root = createRoot(document.getElementById('root'));
root.render(<App />);"""
        }
        
        for path, content in base_files.items():
            if path not in all_files:
                all_files[path] = content
        
        # Update workspace in DB
        await db.workspaces.update_one(
            {"workspace_id": workspace_id},
            {
                "$set": {
                    "files": all_files,
                    "status": "completed",
                    "current_version": 1,
                    "classification": classification,
                    "architecture": architecture,
                    "design_system": design_system,
                    "agent_results": agent_results,
                    "updated_at": utc_now()
                },
                "$push": {
                    "versions": {
                        "version": 1,
                        "files": all_files,
                        "created_at": utc_now(),
                        "message": f"[{mode_label}] Initial generation"
                    }
                }
            }
        )
        
        # Deduct credits
        await db.users.update_one(
            {"user_id": user_id},
            {"$inc": {"credits": -total_credits_used, "credits_used": total_credits_used}}
        )
        
        # Get updated user
        updated_user = await db.users.find_one({"user_id": user_id}, {"credits": 1})
        
        # Final broadcast
        await manager.broadcast(workspace_id, {
            "type": "generation_complete",
            "files": all_files,
            "workspace_id": workspace_id,
            "credits_used": total_credits_used
        })
        
        await manager.broadcast(workspace_id, {
            "type": "log",
            "log": {
                "agent": "system",
                "type": "success",
                "message": f"App generada! {len(all_files)} archivos, {total_credits_used} créditos",
                "timestamp": utc_now().isoformat()
            }
        })
        
        return {
            "workspace_id": workspace_id,
            "files": all_files,
            "classification": classification,
            "agent_results": agent_results,
            "credits_used": total_credits_used,
            "credits_remaining": updated_user.get("credits", 0)
        }
        
    except Exception as e:
        logger.error(f"Generation failed: {e}")
        
        await manager.broadcast(workspace_id, {
            "type": "log",
            "log": {
                "agent": "system",
                "type": "error",
                "message": f"Error: {str(e)}",
                "timestamp": utc_now().isoformat()
            }
        })
        
        await db.workspaces.update_one(
            {"workspace_id": workspace_id},
            {"$set": {"status": "failed", "error": str(e)}}
        )
        
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/debug")
async def debug_code(request: Request):
    """Debug code and fix errors - Costs 30 credits per use"""
    from routes.workspace import get_connection_manager
    
    db = request.app.state.db
    user_doc = await get_authenticated_user(request, db)
    user_id = user_doc["user_id"]
    
    body = await request.json()
    workspace_id = body.get("workspace_id")
    error_message = body.get("error", "")
    file_path = body.get("file_path", "")
    console_logs = body.get("console_logs", [])
    
    if not workspace_id:
        raise HTTPException(status_code=400, detail="workspace_id required")
    
    # Debug Agent costs 30 credits
    DEBUG_COST = 30
    if user_doc["credits"] < DEBUG_COST:
        raise HTTPException(
            status_code=402,
            detail=f"Debug Agent requiere {DEBUG_COST} créditos. Tienes {user_doc['credits']}."
        )
    
    workspace = await db.workspaces.find_one(
        {"workspace_id": workspace_id, "user_id": user_id}
    )
    
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")
    
    files = workspace.get("files", {})
    manager = get_connection_manager()
    
    await manager.broadcast(workspace_id, {
        "type": "log",
        "log": {
            "agent": "debugger",
            "type": "working",
            "message": f"Analizando error ({DEBUG_COST} créditos)...",
            "timestamp": utc_now().isoformat()
        }
    })
    
    error_context = {
        "error": error_message,
        "file_path": file_path,
        "console_logs": console_logs[-10:] if console_logs else [],
        "files": files
    }
    
    debug_result = await run_agent_v2(
        "debugger",
        f"""Fix this error:
ERROR: {error_message}
FILE: {file_path if file_path else "Unknown"}""",
        error_context, db, workspace_id
    )
    
    fixes = debug_result["result"].get("fixes", {})
    files.update(fixes)
    
    new_version = workspace.get("current_version", 0) + 1
    await db.workspaces.update_one(
        {"workspace_id": workspace_id},
        {
            "$set": {
                "files": files,
                "current_version": new_version,
                "updated_at": utc_now()
            },
            "$push": {
                "versions": {
                    "version": new_version,
                    "files": files,
                    "created_at": utc_now(),
                    "message": f"Debug fix: {error_message[:50]}"
                }
            }
        }
    )
    
    await db.users.update_one(
        {"user_id": user_id},
        {"$inc": {"credits": -DEBUG_COST, "credits_used": DEBUG_COST}}
    )
    
    updated_user = await db.users.find_one({"user_id": user_id}, {"credits": 1})
    
    await manager.broadcast(workspace_id, {
        "type": "files_updated",
        "files": files
    })
    
    await manager.broadcast(workspace_id, {
        "type": "log",
        "log": {
            "agent": "debugger",
            "type": "success",
            "message": f"Corregido {len(fixes)} archivo(s)",
            "timestamp": utc_now().isoformat()
        }
    })
    
    return {
        "fixes": fixes,
        "error_analysis": debug_result["result"].get("error_analysis", ""),
        "explanation": debug_result["result"].get("explanation", ""),
        "credits_used": DEBUG_COST,
        "credits_remaining": updated_user.get("credits", 0),
        "files": files,
        "version": new_version
    }


@router.get("/templates")
async def list_templates():
    """Get all available app templates"""
    return {"templates": get_all_templates()}


@router.get("/templates/{template_id}")
async def get_template_details(template_id: str):
    """Get a specific template details"""
    template = get_template(template_id)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    return {"id": template_id, **template}


@router.post("/generate-from-template")
async def generate_from_template(request: Request):
    """Generate an app from a predefined template"""
    db = request.app.state.db
    user_doc = await get_authenticated_user(request, db)
    user_id = user_doc["user_id"]
    
    body = await request.json()
    template_id = body.get("template_id")
    app_name = body.get("name", "My App")
    ultra_mode = body.get("ultra_mode", False)
    
    template = get_template(template_id)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    
    description = template["prompt"]
    
    multiplier = ULTRA_MULTIPLIER if ultra_mode else 1
    base_cost = template.get("estimated_credits", 500)
    total_cost = base_cost * multiplier
    
    if user_doc["credits"] < total_cost:
        raise HTTPException(
            status_code=402,
            detail=f"Need {total_cost} credits, you have {user_doc['credits']}"
        )
    
    from routes.workspace import get_connection_manager
    manager = get_connection_manager()
    
    workspace_id = generate_id("ws")
    mode_label = "ULTRA MODE" if ultra_mode else "Normal"
    workspace = {
        "workspace_id": workspace_id,
        "user_id": user_id,
        "name": app_name,
        "description": f"[{mode_label}] Template: {template['name']}",
        "template": template_id,
        "ultra_mode": ultra_mode,
        "files": {},
        "versions": [],
        "current_version": 0,
        "status": "generating",
        "build_logs": [],
        "created_at": utc_now(),
        "updated_at": utc_now()
    }
    await db.workspaces.insert_one(workspace)
    
    total_credits_used = 0
    all_files = {}
    
    try:
        await manager.broadcast(workspace_id, {
            "type": "log",
            "log": {
                "agent": "system",
                "type": "info",
                "message": f"[{mode_label}] Generando: {template['name']}",
                "timestamp": utc_now().isoformat()
            }
        })
        
        classification = {
            "app_type": template_id,
            "complexity": "medium",
            "requires_auth": False,
            "requires_database": False,
            "main_features": template.get("features", []),
            "summary": template.get("description", "")
        }
        
        # Design Agent
        await manager.broadcast(workspace_id, {
            "type": "log",
            "log": {
                "agent": "design",
                "type": "working",
                "message": "Creando diseño...",
                "timestamp": utc_now().isoformat()
            }
        })
        
        design_result = await run_agent_v2(
            "design",
            f"Create design for {template['name']}",
            {"classification": classification},
            db, workspace_id, ultra_mode
        )
        total_credits_used += design_result["credits_used"]
        
        await manager.broadcast(workspace_id, {
            "type": "log",
            "log": {
                "agent": "design",
                "type": "success",
                "message": "Diseño completado",
                "timestamp": utc_now().isoformat()
            }
        })
        
        # Architect
        await manager.broadcast(workspace_id, {
            "type": "log",
            "log": {
                "agent": "architect",
                "type": "working",
                "message": "Diseñando arquitectura...",
                "timestamp": utc_now().isoformat()
            }
        })
        
        architect_result = await run_agent_v2(
            "architect",
            f"Design architecture for: {description}",
            {"classification": classification, "template": template_id},
            db, workspace_id, ultra_mode
        )
        total_credits_used += architect_result["credits_used"]
        architecture = architect_result["result"]
        
        await manager.broadcast(workspace_id, {
            "type": "log",
            "log": {
                "agent": "architect",
                "type": "success",
                "message": "Arquitectura diseñada",
                "timestamp": utc_now().isoformat()
            }
        })
        
        # Frontend
        await manager.broadcast(workspace_id, {
            "type": "log",
            "log": {
                "agent": "frontend",
                "type": "working",
                "message": "Generando React...",
                "timestamp": utc_now().isoformat()
            }
        })
        
        frontend_result = await run_agent_v2(
            "frontend",
            description,
            {"classification": classification, "architecture": architecture, "app_name": app_name},
            db, workspace_id, ultra_mode
        )
        total_credits_used += frontend_result["credits_used"]
        
        frontend_files = frontend_result["result"].get("files", {})
        all_files.update(frontend_files)
        
        await manager.broadcast(workspace_id, {
            "type": "log",
            "log": {
                "agent": "frontend",
                "type": "success",
                "message": f"Generados {len(frontend_files)} archivos",
                "timestamp": utc_now().isoformat()
            }
        })
        
        # Base files
        base_files = {
            "package.json": json.dumps({
                "name": app_name.lower().replace(" ", "-"),
                "private": True,
                "version": "0.0.1",
                "dependencies": {
                    "react": "^18.2.0",
                    "react-dom": "^18.2.0",
                    "react-router-dom": "^6.20.0"
                }
            }, indent=2),
            "public/index.html": f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>{app_name}</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-gray-900">
    <div id="root"></div>
</body>
</html>""",
            "src/index.js": """import React from 'react';
import { createRoot } from 'react-dom/client';
import App from './App';

const root = createRoot(document.getElementById('root'));
root.render(<App />);"""
        }
        
        for path, content in base_files.items():
            if path not in all_files:
                all_files[path] = content
        
        # Update workspace
        await db.workspaces.update_one(
            {"workspace_id": workspace_id},
            {
                "$set": {
                    "files": all_files,
                    "status": "completed",
                    "current_version": 1,
                    "updated_at": utc_now()
                },
                "$push": {
                    "versions": {
                        "version": 1,
                        "files": all_files,
                        "created_at": utc_now(),
                        "message": f"[{mode_label}] Template: {template['name']}"
                    }
                }
            }
        )
        
        await db.users.update_one(
            {"user_id": user_id},
            {"$inc": {"credits": -total_credits_used, "credits_used": total_credits_used}}
        )
        
        updated_user = await db.users.find_one({"user_id": user_id}, {"credits": 1})
        
        await manager.broadcast(workspace_id, {
            "type": "generation_complete",
            "files": all_files,
            "workspace_id": workspace_id,
            "credits_used": total_credits_used
        })
        
        return {
            "workspace_id": workspace_id,
            "files": all_files,
            "template": template_id,
            "ultra_mode": ultra_mode,
            "credits_used": total_credits_used,
            "credits_remaining": updated_user.get("credits", 0)
        }
        
    except Exception as e:
        logger.error(f"Template generation failed: {e}")
        await db.workspaces.update_one(
            {"workspace_id": workspace_id},
            {"$set": {"status": "failed", "error": str(e)}}
        )
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/download/{workspace_id}")
async def download_project_zip(request: Request, workspace_id: str):
    """Download workspace as ZIP file"""
    db = request.app.state.db
    user_doc = await get_authenticated_user(request, db)
    user_id = user_doc["user_id"]
    
    workspace = await db.workspaces.find_one(
        {"workspace_id": workspace_id, "user_id": user_id}
    )
    
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")
    
    files = workspace.get("files", {})
    app_name = workspace.get("name", "app").lower().replace(" ", "-")
    
    zip_buffer = io.BytesIO()
    
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for file_path, content in files.items():
            normalized_path = file_path.lstrip('/')
            full_path = f"{app_name}/{normalized_path}"
            zip_file.writestr(full_path, content)
        
        readme_content = f"""# {workspace.get('name', 'Generated App')}

{workspace.get('description', 'Generated with Melus AI')}

## Getting Started

1. Install dependencies:
   ```bash
   npm install
   ```

2. Run development server:
   ```bash
   npm start
   ```

## Generated by Melus AI

This project was automatically generated using AI agents.

### Agents Used
- Classifier: App type analysis
- Architect: Structure design
- Design: UI/UX system
- Frontend: React code
- Integrator: Component connection
"""
        zip_file.writestr(f"{app_name}/README.md", readme_content)
    
    zip_buffer.seek(0)
    
    return StreamingResponse(
        zip_buffer,
        media_type="application/zip",
        headers={
            "Content-Disposition": f"attachment; filename={app_name}.zip"
        }
    )


# ============================================
# GITHUB INTEGRATION FOR WORKSPACE
# ============================================
@router.post("/push-to-github")
async def push_workspace_to_github(request: Request):
    """Push workspace files to GitHub"""
    db = request.app.state.db
    user_doc = await get_authenticated_user(request, db)
    user_id = user_doc["user_id"]
    
    body = await request.json()
    workspace_id = body.get("workspace_id")
    repo_name = body.get("repo_name")
    private = body.get("private", False)
    
    if not workspace_id:
        raise HTTPException(status_code=400, detail="workspace_id required")
    
    # Check GitHub connection
    connection = await db.github_connections.find_one({"user_id": user_id})
    if not connection:
        raise HTTPException(status_code=400, detail="GitHub no conectado. Conecta tu cuenta primero.")
    
    # Get workspace
    workspace = await db.workspaces.find_one(
        {"workspace_id": workspace_id, "user_id": user_id}
    )
    
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")
    
    # Check credits (50 credits for push)
    PUSH_COST = 50
    if user_doc["credits"] < PUSH_COST:
        raise HTTPException(status_code=402, detail=f"Need {PUSH_COST} credits")
    
    files = workspace.get("files", {})
    app_name = workspace.get("name", "app").lower().replace(" ", "-")
    final_repo_name = repo_name or app_name
    
    try:
        from routes.github import GitHubManager
        
        manager = GitHubManager(connection["github_token"])
        
        # Create repo
        repo_info = manager.create_repository(
            name=final_repo_name,
            description=workspace.get("description", "Generated by Melus AI"),
            private=private
        )
        
        # Prepare files for push
        files_to_push = []
        for path, content in files.items():
            normalized_path = path.lstrip('/')
            files_to_push.append({
                "path": normalized_path,
                "content": content
            })
        
        # Add README
        files_to_push.append({
            "path": "README.md",
            "content": f"# {workspace.get('name', 'App')}\n\nGenerated by Melus AI"
        })
        
        # Push files
        push_result = manager.push_files(
            repo_name=final_repo_name,
            files=files_to_push,
            commit_message=f"Initial commit from Melus AI"
        )
        
        # Deduct credits
        await db.users.update_one(
            {"user_id": user_id},
            {"$inc": {"credits": -PUSH_COST, "credits_used": PUSH_COST}}
        )
        
        # Update workspace with GitHub info
        await db.workspaces.update_one(
            {"workspace_id": workspace_id},
            {
                "$set": {
                    "github_repo": final_repo_name,
                    "github_url": push_result.get("repo_url"),
                    "pushed_to_github": True,
                    "github_pushed_at": utc_now()
                }
            }
        )
        
        updated_user = await db.users.find_one({"user_id": user_id}, {"credits": 1})
        
        return {
            "success": True,
            "repo_name": final_repo_name,
            "repo_url": push_result.get("repo_url"),
            "files_pushed": push_result.get("total_files"),
            "credits_used": PUSH_COST,
            "credits_remaining": updated_user.get("credits", 0)
        }
        
    except Exception as e:
        logger.error(f"GitHub push error: {e}")
        raise HTTPException(status_code=500, detail=str(e))



# ============================================
# DEPLOY ENDPOINTS
# ============================================
@router.post("/deploy")
async def deploy_workspace(request: Request):
    """Deploy workspace to Vercel or Netlify - Costs 100 credits"""
    from services.deploy_service import deploy_service
    
    db = request.app.state.db
    user_doc = await get_authenticated_user(request, db)
    user_id = user_doc["user_id"]
    
    body = await request.json()
    workspace_id = body.get("workspace_id")
    platform = body.get("platform", "vercel")  # vercel or netlify
    
    if not workspace_id:
        raise HTTPException(status_code=400, detail="workspace_id required")
    
    # Deploy costs 100 credits
    DEPLOY_COST = 100
    if user_doc["credits"] < DEPLOY_COST:
        raise HTTPException(
            status_code=402,
            detail=f"Deploy requiere {DEPLOY_COST} créditos. Tienes {user_doc['credits']}."
        )
    
    # Get workspace
    workspace = await db.workspaces.find_one(
        {"workspace_id": workspace_id, "user_id": user_id}
    )
    
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")
    
    files = workspace.get("files", {})
    project_name = workspace.get("name", "melus-app")
    
    # Add deploy configs if not present
    deploy_configs = deploy_service.generate_deploy_configs(project_name)
    for config_path, config_content in deploy_configs.items():
        if config_path not in files:
            files[config_path] = config_content
    
    # Deploy
    result = await deploy_service.deploy(
        platform=platform,
        project_name=project_name,
        files=files
    )
    
    if result.success:
        # Deduct credits
        await db.users.update_one(
            {"user_id": user_id},
            {"$inc": {"credits": -DEPLOY_COST, "credits_used": DEPLOY_COST}}
        )
        
        # Update workspace
        await db.workspaces.update_one(
            {"workspace_id": workspace_id},
            {
                "$set": {
                    "deployed": True,
                    "deploy_platform": platform,
                    "deploy_url": result.url,
                    "deploy_id": result.deploy_id,
                    "deployed_at": utc_now()
                }
            }
        )
        
        updated_user = await db.users.find_one({"user_id": user_id}, {"credits": 1})
        
        return {
            "success": True,
            "platform": platform,
            "url": result.url,
            "deploy_id": result.deploy_id,
            "credits_used": DEPLOY_COST,
            "credits_remaining": updated_user.get("credits", 0)
        }
    else:
        raise HTTPException(
            status_code=500,
            detail=f"Deploy failed: {result.error}"
        )


@router.get("/deploy/configs/{workspace_id}")
async def get_deploy_configs(request: Request, workspace_id: str):
    """Get deployment configuration files for a workspace"""
    from services.deploy_service import deploy_service
    
    db = request.app.state.db
    user_doc = await get_authenticated_user(request, db)
    user_id = user_doc["user_id"]
    
    workspace = await db.workspaces.find_one(
        {"workspace_id": workspace_id, "user_id": user_id}
    )
    
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")
    
    project_name = workspace.get("name", "melus-app")
    configs = deploy_service.generate_deploy_configs(project_name)
    
    return {
        "workspace_id": workspace_id,
        "configs": configs,
        "platforms": ["vercel", "netlify", "docker"],
        "instructions": {
            "vercel": "Run: vercel deploy",
            "netlify": "Run: netlify deploy --prod",
            "docker": "Run: docker-compose up -d"
        }
    }


# ============================================
# PARALLEL AGENT EXECUTION (Optimized)
# ============================================
@router.post("/execute-parallel")
async def execute_agents_parallel(request: Request):
    """
    Execute multiple independent agents in parallel for faster generation
    
    This endpoint runs agents that don't depend on each other simultaneously,
    significantly reducing total generation time.
    """
    from routes.workspace import get_connection_manager
    
    db = request.app.state.db
    user_doc = await get_authenticated_user(request, db)
    user_id = user_doc["user_id"]
    
    body = await request.json()
    workspace_id = body.get("workspace_id")
    agents = body.get("agents", [])
    context = body.get("context", {})
    ultra_mode = body.get("ultra_mode", False)
    
    if not workspace_id:
        raise HTTPException(status_code=400, detail="workspace_id required")
    
    if not agents:
        raise HTTPException(status_code=400, detail="agents list required")
    
    # Calculate total cost
    multiplier = ULTRA_MULTIPLIER if ultra_mode else 1
    total_cost = sum(AGENT_COSTS.get(a, 50) for a in agents) * multiplier
    
    if user_doc["credits"] < total_cost:
        raise HTTPException(
            status_code=402,
            detail=f"Parallel execution requires {total_cost} credits"
        )
    
    manager = get_connection_manager()
    
    await manager.broadcast(workspace_id, {
        "type": "log",
        "log": {
            "agent": "system",
            "type": "info",
            "message": f"Ejecutando {len(agents)} agentes en PARALELO...",
            "timestamp": utc_now().isoformat()
        }
    })
    
    # Create async tasks for each agent
    async def run_single_agent(agent_name):
        try:
            await manager.broadcast(workspace_id, {
                "type": "log",
                "log": {
                    "agent": agent_name,
                    "type": "working",
                    "message": f"Iniciando {agent_name}...",
                    "timestamp": utc_now().isoformat()
                }
            })
            
            result = await run_agent_v2(
                agent_name,
                context.get("task", f"Execute {agent_name} task"),
                context,
                db,
                workspace_id,
                ultra_mode
            )
            
            await manager.broadcast(workspace_id, {
                "type": "log",
                "log": {
                    "agent": agent_name,
                    "type": "success",
                    "message": f"{agent_name} completado",
                    "timestamp": utc_now().isoformat()
                }
            })
            
            return {agent_name: result}
        except Exception as e:
            await manager.broadcast(workspace_id, {
                "type": "log",
                "log": {
                    "agent": agent_name,
                    "type": "error",
                    "message": f"{agent_name} error: {str(e)}",
                    "timestamp": utc_now().isoformat()
                }
            })
            return {agent_name: {"error": str(e)}}
    
    # Run all agents in parallel
    import asyncio
    tasks = [run_single_agent(agent) for agent in agents]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # Combine results
    combined_results = {}
    combined_files = {}
    total_credits_used = 0
    
    for result in results:
        if isinstance(result, dict):
            for agent_name, agent_result in result.items():
                combined_results[agent_name] = agent_result
                if isinstance(agent_result, dict):
                    total_credits_used += agent_result.get("credits_used", 0)
                    files = agent_result.get("result", {}).get("files", {})
                    combined_files.update(files)
    
    # Deduct credits
    await db.users.update_one(
        {"user_id": user_id},
        {"$inc": {"credits": -total_credits_used, "credits_used": total_credits_used}}
    )
    
    updated_user = await db.users.find_one({"user_id": user_id}, {"credits": 1})
    
    await manager.broadcast(workspace_id, {
        "type": "log",
        "log": {
            "agent": "system",
            "type": "success",
            "message": f"Ejecución paralela completada: {len(agents)} agentes, {total_credits_used} créditos",
            "timestamp": utc_now().isoformat()
        }
    })
    
    return {
        "agents_executed": agents,
        "results": combined_results,
        "files": combined_files,
        "credits_used": total_credits_used,
        "credits_remaining": updated_user.get("credits", 0)
    }


# ============================================
# MARKETPLACE ENDPOINTS
# ============================================
@router.get("/marketplace/templates")
async def get_marketplace_templates(request: Request):
    """Get community templates from marketplace"""
    db = request.app.state.db
    
    # Get public templates
    templates = await db.marketplace_templates.find(
        {"status": "approved", "public": True}
    ).sort("downloads", -1).limit(50).to_list(50)
    
    # Serialize
    for t in templates:
        t["_id"] = str(t["_id"])
    
    return {
        "templates": templates,
        "total": len(templates)
    }


@router.post("/marketplace/publish")
async def publish_to_marketplace(request: Request):
    """Publish a workspace as a marketplace template - Costs 50 credits"""
    db = request.app.state.db
    user_doc = await get_authenticated_user(request, db)
    user_id = user_doc["user_id"]
    
    body = await request.json()
    workspace_id = body.get("workspace_id")
    template_name = body.get("name")
    description = body.get("description")
    category = body.get("category", "other")
    price = body.get("price", 0)  # Free or credits to use
    
    if not workspace_id or not template_name:
        raise HTTPException(status_code=400, detail="workspace_id and name required")
    
    PUBLISH_COST = 50
    if user_doc["credits"] < PUBLISH_COST:
        raise HTTPException(
            status_code=402,
            detail=f"Publishing requires {PUBLISH_COST} credits"
        )
    
    workspace = await db.workspaces.find_one(
        {"workspace_id": workspace_id, "user_id": user_id}
    )
    
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")
    
    # Create marketplace template
    template_id = generate_id("mkt")
    marketplace_template = {
        "template_id": template_id,
        "name": template_name,
        "description": description,
        "category": category,
        "price": price,
        "author_id": user_id,
        "author_email": user_doc.get("email"),
        "files": workspace.get("files", {}),
        "classification": workspace.get("classification", {}),
        "downloads": 0,
        "rating": 0,
        "reviews": [],
        "status": "pending",  # pending, approved, rejected
        "public": True,
        "created_at": utc_now(),
        "updated_at": utc_now()
    }
    
    await db.marketplace_templates.insert_one(marketplace_template)
    
    # Deduct credits
    await db.users.update_one(
        {"user_id": user_id},
        {"$inc": {"credits": -PUBLISH_COST, "credits_used": PUBLISH_COST}}
    )
    
    updated_user = await db.users.find_one({"user_id": user_id}, {"credits": 1})
    
    return {
        "success": True,
        "template_id": template_id,
        "status": "pending",
        "message": "Template enviado para revisión",
        "credits_used": PUBLISH_COST,
        "credits_remaining": updated_user.get("credits", 0)
    }


@router.post("/marketplace/use/{template_id}")
async def use_marketplace_template(request: Request, template_id: str):
    """Use a marketplace template to create a new workspace"""
    db = request.app.state.db
    user_doc = await get_authenticated_user(request, db)
    user_id = user_doc["user_id"]
    
    body = await request.json()
    project_name = body.get("name", "My Project")
    
    # Get template
    template = await db.marketplace_templates.find_one(
        {"template_id": template_id, "status": "approved"}
    )
    
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    
    # Check price
    price = template.get("price", 0)
    if user_doc["credits"] < price:
        raise HTTPException(
            status_code=402,
            detail=f"Template costs {price} credits"
        )
    
    # Create workspace from template
    workspace_id = generate_id("ws")
    workspace = {
        "workspace_id": workspace_id,
        "user_id": user_id,
        "name": project_name,
        "description": f"Created from marketplace template: {template['name']}",
        "from_marketplace": True,
        "marketplace_template_id": template_id,
        "files": template.get("files", {}),
        "classification": template.get("classification", {}),
        "versions": [{
            "version": 1,
            "files": template.get("files", {}),
            "created_at": utc_now(),
            "message": f"Created from template: {template['name']}"
        }],
        "current_version": 1,
        "status": "completed",
        "created_at": utc_now(),
        "updated_at": utc_now()
    }
    
    await db.workspaces.insert_one(workspace)
    
    # Update download count
    await db.marketplace_templates.update_one(
        {"template_id": template_id},
        {"$inc": {"downloads": 1}}
    )
    
    # Deduct credits if price > 0
    if price > 0:
        await db.users.update_one(
            {"user_id": user_id},
            {"$inc": {"credits": -price, "credits_used": price}}
        )
        
        # Give credits to author (80% revenue share)
        author_share = int(price * 0.8)
        await db.users.update_one(
            {"user_id": template["author_id"]},
            {"$inc": {"credits": author_share, "credits_earned": author_share}}
        )
    
    updated_user = await db.users.find_one({"user_id": user_id}, {"credits": 1})
    
    return {
        "success": True,
        "workspace_id": workspace_id,
        "files": workspace["files"],
        "credits_used": price,
        "credits_remaining": updated_user.get("credits", 0)
    }


@router.post("/modify")
async def modify_workspace(request: Request):
    """
    Modify an existing workspace based on user instructions.
    Uses the appropriate agents to make changes.
    """
    from routes.workspace import get_connection_manager
    
    db = request.app.state.db
    user_doc = await get_authenticated_user(request, db)
    user_id = user_doc["user_id"]
    
    body = await request.json()
    workspace_id = body.get("workspace_id")
    instruction = body.get("instruction", "")
    
    if not workspace_id:
        raise HTTPException(status_code=400, detail="workspace_id required")
    
    if not instruction:
        raise HTTPException(status_code=400, detail="instruction required")
    
    workspace = await db.workspaces.find_one(
        {"workspace_id": workspace_id, "user_id": user_id}
    )
    
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")
    
    files = workspace.get("files", {})
    manager = get_connection_manager()
    
    MODIFY_COST = 50
    is_unlimited = user_doc.get("unlimited_credits", False) or user_doc.get("is_owner", False)
    
    if not is_unlimited and user_doc["credits"] < MODIFY_COST:
        raise HTTPException(
            status_code=402,
            detail=f"Modificacion requiere {MODIFY_COST} creditos. Tienes {user_doc['credits']}."
        )
    
    await manager.broadcast(workspace_id, {
        "type": "log",
        "log": {
            "agent": "system",
            "type": "working",
            "message": "Procesando modificacion...",
            "timestamp": utc_now().isoformat()
        }
    })
    
    modify_prompt = f"Modify the existing code based on this instruction: {instruction}. Output modified files in JSON format with 'files' key containing file paths and complete contents."
    
    try:
        result = await run_agent_v2(
            "frontend",
            modify_prompt,
            {"files": files, "instruction": instruction},
            db, workspace_id
        )
        
        modified_files = result["result"].get("files", {})
        files.update(modified_files)
        
        new_version = workspace.get("current_version", 0) + 1
        await db.workspaces.update_one(
            {"workspace_id": workspace_id},
            {
                "$set": {
                    "files": files,
                    "current_version": new_version,
                    "updated_at": utc_now()
                },
                "$push": {
                    "versions": {
                        "version": new_version,
                        "files": files,
                        "created_at": utc_now(),
                        "message": f"Modificacion: {instruction[:50]}"
                    }
                }
            }
        )
        
        if not is_unlimited:
            await db.users.update_one(
                {"user_id": user_id},
                {"$inc": {"credits": -MODIFY_COST, "credits_used": MODIFY_COST}}
            )
        
        updated_user = await db.users.find_one({"user_id": user_id}, {"credits": 1})
        
        await manager.broadcast(workspace_id, {
            "type": "files_updated",
            "files": files
        })
        
        return {
            "success": True,
            "files": files,
            "modified_files": list(modified_files.keys()),
            "version": new_version,
            "credits_used": 0 if is_unlimited else MODIFY_COST,
            "credits_remaining": updated_user.get("credits", 0)
        }
        
    except Exception as e:
        logger.error(f"Modification failed: {e}")
        await manager.broadcast(workspace_id, {
            "type": "log",
            "log": {
                "agent": "system",
                "type": "error",
                "message": f"Error: {str(e)}",
                "timestamp": utc_now().isoformat()
            }
        })
        raise HTTPException(status_code=500, detail=str(e))

"""Multi-Agent System for Assistant Melus - AI Orchestration"""
from fastapi import APIRouter, HTTPException, Request
from typing import List, Optional, Dict, Any
import logging
import os
import json
import re
import asyncio
from datetime import datetime

from models import ProjectCreate, ProjectResponse, AgentTask, AgentResponse
from utils import generate_id, utc_now, get_authenticated_user

from emergentintegrations.llm.chat import LlmChat, UserMessage

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/agents", tags=["agents"])

EMERGENT_LLM_KEY = os.environ.get('EMERGENT_LLM_KEY')

# Agent cost per action (credits)
AGENT_COSTS = {
    "orchestrator": 50,
    "design": 100,
    "frontend": 150,
    "backend": 150,
    "database": 100,
    "deploy": 200
}

# Agent system prompts
AGENT_PROMPTS = {
    "orchestrator": """Eres el Agente Orquestador de Assistant Melus. Tu rol es:
1. Analizar los requisitos del usuario para crear aplicaciones
2. Descomponer el proyecto en tareas para cada agente especializado
3. Coordinar el flujo de trabajo entre agentes
4. Asegurar la coherencia y calidad del producto final

Responde siempre en JSON con el siguiente formato:
{
    "project_analysis": "análisis del proyecto",
    "tasks": [
        {"agent": "design|frontend|backend|database|deploy", "task": "descripción", "priority": 1-5}
    ],
    "estimated_credits": número,
    "complexity": "simple|medium|complex"
}""",

    "design": """Eres el Agente de Diseño de Assistant Melus. Tu rol es:
1. Crear wireframes y esquemas de UI/UX
2. Definir la arquitectura de la interfaz
3. Establecer el sistema de diseño (colores, tipografía, espaciado)
4. Generar modelos de datos iniciales

Responde en JSON con:
{
    "ui_components": ["lista de componentes"],
    "color_scheme": {"primary": "#hex", "secondary": "#hex", ...},
    "typography": {"heading": "font", "body": "font"},
    "layout": "descripción del layout",
    "data_models": [{"name": "modelo", "fields": [...]}],
    "wireframe_description": "descripción textual del wireframe"
}""",

    "frontend": """Eres el Agente Frontend de Assistant Melus. Tu rol es:
1. Generar código React moderno y limpio
2. Implementar componentes UI basados en el diseño
3. Manejar estado y routing
4. Integrar con APIs del backend

Genera código completo y funcional en React con TailwindCSS.
Responde en JSON con:
{
    "files": [
        {"path": "src/components/Example.jsx", "content": "código completo"},
        ...
    ],
    "dependencies": ["lista de dependencias npm"],
    "instructions": "instrucciones de implementación"
}""",

    "backend": """Eres el Agente Backend de Assistant Melus. Tu rol es:
1. Crear APIs RESTful con FastAPI
2. Implementar lógica de negocio
3. Manejar autenticación y autorización
4. Integrar con bases de datos

Genera código completo y funcional en Python/FastAPI.
Responde en JSON con:
{
    "files": [
        {"path": "routes/example.py", "content": "código completo"},
        ...
    ],
    "dependencies": ["lista de dependencias pip"],
    "env_vars": ["variables de entorno necesarias"],
    "instructions": "instrucciones de implementación"
}""",

    "database": """Eres el Agente de Base de Datos de Assistant Melus. Tu rol es:
1. Diseñar esquemas de base de datos
2. Crear modelos y migraciones
3. Optimizar consultas
4. Configurar índices

Responde en JSON con:
{
    "database_type": "mongodb|postgresql|mysql",
    "collections": [
        {"name": "nombre", "schema": {...}, "indexes": [...]}
    ],
    "models": [
        {"path": "models/example.py", "content": "código del modelo"}
    ],
    "seed_data": "datos de ejemplo opcionales"
}""",

    "deploy": """Eres el Agente de Despliegue de Assistant Melus. Tu rol es:
1. Configurar entornos de producción
2. Crear Dockerfiles y docker-compose
3. Configurar CI/CD
4. Gestionar variables de entorno

Responde en JSON con:
{
    "platform": "vercel|netlify|aws|docker",
    "files": [
        {"path": "Dockerfile", "content": "contenido"},
        {"path": "docker-compose.yml", "content": "contenido"}
    ],
    "env_template": "template de .env",
    "deploy_instructions": "pasos de despliegue"
}"""
}


async def run_agent(agent_type: str, task: str, context: dict, db) -> dict:
    """Execute a specific agent with a task"""
    if agent_type not in AGENT_PROMPTS:
        raise ValueError(f"Unknown agent type: {agent_type}")
    
    chat = LlmChat(
        api_key=EMERGENT_LLM_KEY,
        session_id=f"agent_{agent_type}_{generate_id('task')}",
        system_message=AGENT_PROMPTS[agent_type]
    )
    chat.with_model("openai", "gpt-4o")
    
    # Build context message
    context_str = json.dumps(context, indent=2, default=str) if context else ""
    full_prompt = f"""Tarea: {task}

Contexto del proyecto:
{context_str}

Por favor, ejecuta tu rol y responde con la información solicitada."""

    response = await chat.send_message(UserMessage(text=full_prompt))
    
    # Try to parse as JSON
    try:
        # Extract JSON from response
        json_match = re.search(r'\{[\s\S]*\}', response)
        if json_match:
            result = json.loads(json_match.group())
        else:
            result = {"raw_response": response}
    except json.JSONDecodeError:
        result = {"raw_response": response}
    
    return {
        "agent": agent_type,
        "task": task,
        "result": result,
        "credits_used": AGENT_COSTS.get(agent_type, 50),
        "timestamp": utc_now().isoformat()
    }


@router.post("/analyze")
async def analyze_project(request: Request, project_data: dict):
    """Analyze project requirements using orchestrator agent"""
    db = request.app.state.db
    user_doc = await get_authenticated_user(request, db)
    user_id = user_doc["user_id"]
    
    description = project_data.get("description", "")
    
    if not description:
        raise HTTPException(status_code=400, detail="Project description required")
    
    # Check credits
    if user_doc["credits"] < AGENT_COSTS["orchestrator"]:
        raise HTTPException(status_code=402, detail="Insufficient credits")
    
    # Run orchestrator
    result = await run_agent(
        "orchestrator",
        f"Analiza este proyecto y crea un plan de desarrollo: {description}",
        {"user_request": description},
        db
    )
    
    # Deduct credits
    credits_used = result["credits_used"]
    await db.users.update_one(
        {"user_id": user_id},
        {
            "$inc": {"credits": -credits_used, "credits_used": credits_used}
        }
    )
    
    # Log agent usage
    await db.agent_usage.insert_one({
        "usage_id": generate_id("usage"),
        "user_id": user_id,
        "agent_type": "orchestrator",
        "credits_used": credits_used,
        "task": "project_analysis",
        "created_at": utc_now()
    })
    
    return {
        "analysis": result["result"],
        "credits_used": credits_used,
        "credits_remaining": user_doc["credits"] - credits_used
    }


@router.post("/execute")
async def execute_agent_task(request: Request, task_data: dict):
    """Execute a specific agent task"""
    db = request.app.state.db
    user_doc = await get_authenticated_user(request, db)
    user_id = user_doc["user_id"]
    
    agent_type = task_data.get("agent_type")
    task = task_data.get("task")
    context = task_data.get("context", {})
    project_id = task_data.get("project_id")
    
    if not agent_type or not task:
        raise HTTPException(status_code=400, detail="Agent type and task required")
    
    if agent_type not in AGENT_COSTS:
        raise HTTPException(status_code=400, detail=f"Invalid agent type: {agent_type}")
    
    # Check credits
    required_credits = AGENT_COSTS[agent_type]
    if user_doc["credits"] < required_credits:
        raise HTTPException(status_code=402, detail="Insufficient credits")
    
    # Run agent
    result = await run_agent(agent_type, task, context, db)
    
    # Deduct credits
    credits_used = result["credits_used"]
    await db.users.update_one(
        {"user_id": user_id},
        {
            "$inc": {"credits": -credits_used, "credits_used": credits_used}
        }
    )
    
    # Log agent usage
    usage_record = {
        "usage_id": generate_id("usage"),
        "user_id": user_id,
        "agent_type": agent_type,
        "credits_used": credits_used,
        "task": task[:200],
        "project_id": project_id,
        "created_at": utc_now()
    }
    await db.agent_usage.insert_one(usage_record)
    
    # Update project if provided
    if project_id:
        await db.projects.update_one(
            {"project_id": project_id},
            {
                "$push": {"agent_results": result},
                "$set": {"updated_at": utc_now()}
            }
        )
    
    return {
        "result": result,
        "credits_used": credits_used,
        "credits_remaining": user_doc["credits"] - credits_used
    }


@router.post("/generate-app")
async def generate_full_app(request: Request, app_data: dict):
    """Generate a full application using all agents"""
    db = request.app.state.db
    user_doc = await get_authenticated_user(request, db)
    user_id = user_doc["user_id"]
    
    description = app_data.get("description", "")
    app_name = app_data.get("name", "Mi Aplicación")
    
    if not description:
        raise HTTPException(status_code=400, detail="App description required")
    
    # Estimate total credits needed
    total_estimated = sum(AGENT_COSTS.values())
    if user_doc["credits"] < total_estimated:
        raise HTTPException(
            status_code=402, 
            detail=f"Insufficient credits. Need approximately {total_estimated} credits"
        )
    
    # Create project record
    project_id = generate_id("proj")
    project = {
        "project_id": project_id,
        "user_id": user_id,
        "name": app_name,
        "description": description,
        "status": "in_progress",
        "agent_results": [],
        "files": [],
        "total_credits_used": 0,
        "created_at": utc_now(),
        "updated_at": utc_now()
    }
    await db.projects.insert_one(project)
    
    results = []
    total_credits = 0
    
    try:
        # Step 1: Orchestrator analysis
        orchestrator_result = await run_agent(
            "orchestrator",
            f"Analiza y planifica el desarrollo de: {description}",
            {"app_name": app_name, "description": description},
            db
        )
        results.append(orchestrator_result)
        total_credits += orchestrator_result["credits_used"]
        
        # Update project with analysis
        await db.projects.update_one(
            {"project_id": project_id},
            {
                "$push": {"agent_results": orchestrator_result},
                "$set": {"analysis": orchestrator_result["result"]}
            }
        )
        
        # Step 2: Design
        design_result = await run_agent(
            "design",
            f"Diseña la UI/UX para: {description}",
            {"analysis": orchestrator_result["result"]},
            db
        )
        results.append(design_result)
        total_credits += design_result["credits_used"]
        
        # Step 3: Database
        database_result = await run_agent(
            "database",
            f"Diseña la base de datos para: {description}",
            {"analysis": orchestrator_result["result"], "design": design_result["result"]},
            db
        )
        results.append(database_result)
        total_credits += database_result["credits_used"]
        
        # Step 4: Backend
        backend_result = await run_agent(
            "backend",
            f"Genera el backend para: {description}",
            {
                "analysis": orchestrator_result["result"],
                "database": database_result["result"]
            },
            db
        )
        results.append(backend_result)
        total_credits += backend_result["credits_used"]
        
        # Step 5: Frontend
        frontend_result = await run_agent(
            "frontend",
            f"Genera el frontend para: {description}",
            {
                "analysis": orchestrator_result["result"],
                "design": design_result["result"],
                "backend": backend_result["result"]
            },
            db
        )
        results.append(frontend_result)
        total_credits += frontend_result["credits_used"]
        
        # Step 6: Deploy config
        deploy_result = await run_agent(
            "deploy",
            f"Configura el despliegue para: {description}",
            {
                "backend": backend_result["result"],
                "frontend": frontend_result["result"]
            },
            db
        )
        results.append(deploy_result)
        total_credits += deploy_result["credits_used"]
        
        # Update project as completed
        await db.projects.update_one(
            {"project_id": project_id},
            {
                "$set": {
                    "status": "completed",
                    "agent_results": results,
                    "total_credits_used": total_credits,
                    "updated_at": utc_now()
                }
            }
        )
        
        # Deduct total credits
        await db.users.update_one(
            {"user_id": user_id},
            {
                "$inc": {"credits": -total_credits, "credits_used": total_credits}
            }
        )
        
        # Log all agent usage
        for result in results:
            await db.agent_usage.insert_one({
                "usage_id": generate_id("usage"),
                "user_id": user_id,
                "agent_type": result["agent"],
                "credits_used": result["credits_used"],
                "project_id": project_id,
                "created_at": utc_now()
            })
        
        return {
            "project_id": project_id,
            "status": "completed",
            "results": results,
            "total_credits_used": total_credits,
            "credits_remaining": user_doc["credits"] - total_credits
        }
        
    except Exception as e:
        # Mark project as failed
        await db.projects.update_one(
            {"project_id": project_id},
            {
                "$set": {
                    "status": "failed",
                    "error": str(e),
                    "agent_results": results,
                    "total_credits_used": total_credits,
                    "updated_at": utc_now()
                }
            }
        )
        
        # Still deduct used credits
        if total_credits > 0:
            await db.users.update_one(
                {"user_id": user_id},
                {
                    "$inc": {"credits": -total_credits, "credits_used": total_credits}
                }
            )
        
        logger.error(f"App generation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Generation failed: {str(e)}")


@router.get("/status/{project_id}")
async def get_project_status(request: Request, project_id: str):
    """Get project generation status"""
    db = request.app.state.db
    user_doc = await get_authenticated_user(request, db)
    user_id = user_doc["user_id"]
    
    project = await db.projects.find_one(
        {"project_id": project_id, "user_id": user_id},
        {"_id": 0}
    )
    
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    return project


@router.get("/costs")
async def get_agent_costs():
    """Get current agent costs"""
    return {
        "costs": AGENT_COSTS,
        "descriptions": {
            "orchestrator": "Análisis y planificación del proyecto",
            "design": "Diseño UI/UX y wireframes",
            "frontend": "Generación de código frontend",
            "backend": "Generación de código backend",
            "database": "Diseño de base de datos",
            "deploy": "Configuración de despliegue"
        }
    }

"""
MelusAI API Gateway - Brain Engine Routes
New routes for the Brain Engine and template-based generation
"""
from fastapi import APIRouter, HTTPException, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional, List, Dict
import asyncio
import json
import logging
import sys
import os

# Add parent directories to path for imports
sys.path.insert(0, '/app')
sys.path.insert(0, '/app/core')

from core.brain_engine import get_brain_engine, BrainEngine, PipelineStage
from core.intent_classifier import get_intent_classifier, IntentType

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/brain", tags=["brain-engine"])


# ================== MODELS ==================

class GenerateRequest(BaseModel):
    prompt: str
    project_name: Optional[str] = None
    preferences: Optional[Dict] = None
    use_multi_agent: Optional[bool] = True  # Enable multi-agent pipeline


class IntentAnalysisRequest(BaseModel):
    prompt: str


class TemplateListRequest(BaseModel):
    intent_type: Optional[str] = None
    complexity: Optional[str] = None


# ================== HELPER FUNCTIONS ==================

async def get_user_from_request(request: Request):
    """Get authenticated user from request"""
    from utils import get_authenticated_user
    db = request.app.state.db
    return await get_authenticated_user(request, db)


# ================== ENDPOINTS ==================

@router.get("/status")
async def get_brain_status(request: Request):
    """Get Brain Engine status"""
    await get_user_from_request(request)
    
    brain = get_brain_engine()
    return brain.get_status()


@router.post("/analyze")
async def analyze_intent(data: IntentAnalysisRequest, request: Request):
    """Analyze a prompt and return intent classification without generating"""
    await get_user_from_request(request)
    
    classifier = get_intent_classifier()
    result = classifier.classify(data.prompt)
    
    return {
        "intent_type": result.intent_type.value,
        "confidence": result.confidence,
        "complexity": result.complexity.value,
        "features": result.features,
        "recommended_template": result.recommended_template,
        "recommended_builder": result.recommended_builder,
        "reasoning": result.reasoning,
        "entities": result.extracted_entities
    }


@router.post("/generate")
async def generate_project(data: GenerateRequest, request: Request):
    """Generate a new project using the Brain Engine"""
    user = await get_user_from_request(request)
    db = request.app.state.db
    
    from utils import generate_id, utc_now
    
    # Create project ID
    project_id = generate_id("proj")
    project_name = data.project_name or f"Proyecto_{project_id[:8]}"
    
    # Save initial project to MongoDB (maintaining compatibility)
    project_doc = {
        "project_id": project_id,
        "user_id": user["user_id"],
        "name": project_name,
        "prompt": data.prompt,
        "status": "planning",
        "agent_status": "brain_engine_starting",
        "created_at": utc_now(),
        "updated_at": utc_now()
    }
    await db.projects.insert_one(project_doc)
    
    # Get brain engine
    brain = get_brain_engine()
    
    # Setup update callback
    async def update_project(event_type: str, event_data: Dict):
        update = {"updated_at": utc_now()}
        
        if event_type == "intent_classified":
            update["intent_type"] = event_data.get("intent_type")
            update["complexity"] = event_data.get("complexity")
            update["features"] = event_data.get("features")
        
        elif event_type == "template_selected":
            update["template"] = event_data.get("template")
            update["builder"] = event_data.get("builder")
        
        elif event_type == "code_generated":
            update["status"] = "generating"
            update["files_count"] = event_data.get("files_count", 0)
        
        elif event_type == "pipeline_completed":
            update["status"] = "completed"
            update["agent_status"] = "complete"
        
        elif event_type == "pipeline_error":
            update["status"] = "error"
            update["error"] = event_data.get("error")
        
        await db.projects.update_one(
            {"project_id": project_id},
            {"$set": update}
        )
    
    brain.on_update(update_project)
    
    # Start generation in background with multi-agent support
    asyncio.create_task(brain.process_prompt(
        data.prompt, 
        project_id, 
        user["user_id"],
        use_multi_agent=data.use_multi_agent
    ))
    
    return {
        "project_id": project_id,
        "name": project_name,
        "status": "started",
        "message": "Generación iniciada. Usa el endpoint /status/{project_id} para seguir el progreso."
    }


@router.get("/project/{project_id}")
async def get_project_status(project_id: str, request: Request):
    """Get status and files for a project"""
    await get_user_from_request(request)
    db = request.app.state.db
    
    # Get from MongoDB
    project = await db.projects.find_one(
        {"project_id": project_id},
        {"_id": 0}
    )
    
    if not project:
        raise HTTPException(status_code=404, detail="Proyecto no encontrado")
    
    # Get from brain engine if active
    brain = get_brain_engine()
    context = brain.get_context(project_id)
    
    if context:
        return {
            "project_id": project_id,
            "name": project.get("name"),
            "status": context.current_stage.value,
            "intent_type": context.intent_result.intent_type.value if context.intent_result else None,
            "complexity": context.intent_result.complexity.value if context.intent_result else None,
            "features": context.intent_result.features if context.intent_result else [],
            "template": context.selected_template,
            "files": context.files,
            "errors": context.errors,
            "metadata": context.metadata
        }
    
    return project


@router.get("/project/{project_id}/files")
async def get_project_files(project_id: str, request: Request):
    """Get generated files for a project"""
    await get_user_from_request(request)
    
    brain = get_brain_engine()
    context = brain.get_context(project_id)
    
    if context and context.files:
        return {"files": context.files}
    
    # Try from MongoDB
    db = request.app.state.db
    project = await db.projects.find_one(
        {"project_id": project_id},
        {"_id": 0, "files": 1}
    )
    
    if project and project.get("files"):
        return {"files": project["files"]}
    
    return {"files": []}


@router.get("/agents/status")
async def get_agents_status(request: Request):
    """Get status of all agents in the multi-agent system"""
    await get_user_from_request(request)
    
    brain = get_brain_engine()
    
    if brain.orchestrator:
        return brain.orchestrator.get_status()
    
    return {
        "status": "orchestrator_not_available",
        "agents": {}
    }


@router.get("/templates")
async def list_templates(request: Request, intent_type: Optional[str] = None, complexity: Optional[str] = None):
    """List available templates"""
    await get_user_from_request(request)
    
    # Return built-in templates from classifier
    classifier = get_intent_classifier()
    
    templates = []
    for intent in IntentType:
        if intent == IntentType.UNKNOWN:
            continue
        
        if intent_type and intent.value != intent_type:
            continue
        
        template_map = classifier.TEMPLATE_MAP.get(intent, {})
        builder = classifier.BUILDER_MAP.get(intent, "web-builder")
        
        for complexity_level, template_name in template_map.items():
            if complexity and complexity != complexity_level:
                continue
            
            templates.append({
                "template_id": template_name,
                "name": template_name.replace("-", " ").title(),
                "intent_type": intent.value,
                "complexity": complexity_level,
                "builder": builder,
                "is_premium": complexity_level in ["complex", "enterprise"]
            })
    
    return {"templates": templates}


@router.get("/intents")
async def list_intents(request: Request):
    """List available intent types"""
    await get_user_from_request(request)
    
    intents = [
        {
            "id": intent.value,
            "name": intent.value.replace("_", " ").title(),
            "description": _get_intent_description(intent)
        }
        for intent in IntentType
        if intent != IntentType.UNKNOWN
    ]
    
    return {"intents": intents}


@router.get("/models")
async def list_models(request: Request, model_type: Optional[str] = None):
    """List all available AI models (GPT, Claude, Gemini, Sora)"""
    await get_user_from_request(request)
    
    try:
        from core.llm_manager import get_llm_manager, ModelType
        
        llm_manager = get_llm_manager()
        
        type_filter = None
        if model_type:
            type_filter = ModelType(model_type) if model_type in [t.value for t in ModelType] else None
        
        models = llm_manager.get_available_models(type_filter)
        
        return {
            "models": models,
            "providers": ["openai", "anthropic", "gemini"],
            "types": ["chat", "code", "video", "image"]
        }
    except Exception as e:
        logger.error(f"Error listing models: {e}")
        return {"models": [], "error": str(e)}


@router.get("/modes")
async def list_agent_modes(request: Request):
    """List all available agent modes (E1, E1.5, E2, Pro, Prototype, Mobile)"""
    await get_user_from_request(request)
    
    try:
        from core.llm_manager import get_all_agent_modes
        
        modes = get_all_agent_modes()
        
        return {"modes": modes}
    except Exception as e:
        logger.error(f"Error listing modes: {e}")
        return {"modes": [], "error": str(e)}


@router.post("/set-mode")
async def set_agent_mode(request: Request, mode: str):
    """Set the agent mode for generation"""
    await get_user_from_request(request)
    
    brain = get_brain_engine()
    
    if brain.orchestrator:
        brain.orchestrator.set_mode(mode)
        return {"success": True, "mode": mode}
    
    return {"success": False, "error": "Orchestrator not available"}


@router.post("/set-model")
async def set_model(request: Request, model_key: str):
    """Set the AI model to use for generation"""
    await get_user_from_request(request)
    
    try:
        from core.llm_manager import get_llm_manager, AVAILABLE_MODELS
        
        if model_key not in AVAILABLE_MODELS:
            return {"success": False, "error": f"Model {model_key} not found"}
        
        llm_manager = get_llm_manager()
        llm_manager.set_default_model(model_key)
        
        model_info = AVAILABLE_MODELS[model_key]
        
        return {
            "success": True, 
            "model": model_key,
            "provider": model_info.provider.value,
            "display_name": model_info.display_name
        }
    except Exception as e:
        logger.error(f"Error setting model: {e}")
        return {"success": False, "error": str(e)}


@router.post("/generate-video")
async def generate_video(request: Request, prompt: str, video_type: str = "promo", duration: int = 4):
    """Generate a promotional video using Sora 2"""
    user = await get_user_from_request(request)
    
    try:
        from core.llm_manager import get_llm_manager
        
        llm_manager = get_llm_manager()
        
        output_path = f"/app/uploads/video_{user['user_id']}_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.mp4"
        
        result = await llm_manager.generate_video(
            prompt=prompt,
            model="sora-2",
            size="1280x720",
            duration=duration,
            output_path=output_path
        )
        
        if result:
            return {
                "success": True,
                "video_path": result,
                "message": "Video generado exitosamente"
            }
        else:
            return {
                "success": False,
                "error": "No se pudo generar el video"
            }
    except Exception as e:
        logger.error(f"Video generation error: {e}")
        return {"success": False, "error": str(e)}


def _get_intent_description(intent: IntentType) -> str:
    """Get description for an intent type"""
    descriptions = {
        IntentType.WEB_APP: "Aplicación web general con funcionalidades personalizadas",
        IntentType.SAAS_APP: "Plataforma SaaS con usuarios, suscripciones y dashboard",
        IntentType.ECOMMERCE: "Tienda online con productos, carrito y pagos",
        IntentType.LANDING_PAGE: "Página de aterrizaje para marketing y conversión",
        IntentType.DASHBOARD: "Panel de control con métricas y visualizaciones",
        IntentType.API_SERVICE: "Servicio API REST o GraphQL",
        IntentType.MOBILE_APP: "Aplicación móvil o PWA",
        IntentType.PORTFOLIO: "Portafolio personal o de agencia",
        IntentType.BLOG: "Blog o sistema de gestión de contenido"
    }
    return descriptions.get(intent, "")


# ================== WEBSOCKET ==================

# Active WebSocket connections by project
ws_connections: Dict[str, List[WebSocket]] = {}


@router.websocket("/ws/{project_id}")
async def project_websocket(websocket: WebSocket, project_id: str):
    """WebSocket for real-time project updates"""
    await websocket.accept()
    
    # Add to connections
    if project_id not in ws_connections:
        ws_connections[project_id] = []
    ws_connections[project_id].append(websocket)
    
    brain = get_brain_engine()
    
    # Setup callback to broadcast to this project's clients
    async def broadcast(event_type: str, data: Dict):
        if data.get("project_id") == project_id:
            message = json.dumps({"type": event_type, "data": data})
            for ws in ws_connections.get(project_id, []):
                try:
                    await ws.send_text(message)
                except:
                    pass
    
    brain.on_update(broadcast)
    
    try:
        # Send initial status
        context = brain.get_context(project_id)
        if context:
            await websocket.send_json({
                "type": "status",
                "data": {
                    "stage": context.current_stage.value,
                    "files_count": len(context.files)
                }
            })
        
        # Keep alive
        while True:
            try:
                data = await asyncio.wait_for(websocket.receive_text(), timeout=30)
                if data == "ping":
                    await websocket.send_text("pong")
            except asyncio.TimeoutError:
                await websocket.send_json({"type": "heartbeat"})
                
    except WebSocketDisconnect:
        pass
    finally:
        if project_id in ws_connections:
            if websocket in ws_connections[project_id]:
                ws_connections[project_id].remove(websocket)

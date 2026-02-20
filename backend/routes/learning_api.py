"""
MelusAI - Learning API Routes
API para el sistema de aprendizaje continuo
"""
from fastapi import APIRouter, HTTPException, Request, BackgroundTasks
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone

from learning.learning_engine import LearningEngine
from learning.feedback_system import FeedbackType

router = APIRouter(prefix="/api/learning", tags=["learning"])

# ============= REQUEST MODELS =============

class RatingRequest(BaseModel):
    project_id: str
    rating: int  # 1-5
    comment: Optional[str] = None

class FeedbackRequest(BaseModel):
    project_id: str
    feedback_type: str
    value: Any
    metadata: Optional[Dict] = None

class SettingRequest(BaseModel):
    key: str
    value: Any

class PromptUpdateRequest(BaseModel):
    prompt_type: str
    content: str
    reason: Optional[str] = None

# ============= HELPER FUNCTIONS =============

def get_db(request: Request):
    return request.app.state.db

async def get_learning_engine(request: Request) -> LearningEngine:
    """Obtener instancia del learning engine"""
    db = get_db(request)
    engine = LearningEngine(db)
    return engine

async def get_user_id(request: Request) -> str:
    """Obtener user ID del token de sesión"""
    token = request.headers.get("X-Session-Token")
    if not token:
        return "anonymous"
    
    db = get_db(request)
    user = await db.users.find_one({"session_token": token}, {"user_id": 1})
    return user["user_id"] if user else token

# ============= FEEDBACK ENDPOINTS =============

@router.post("/feedback/rating")
async def submit_rating(data: RatingRequest, request: Request):
    """
    Enviar rating explícito de un proyecto (1-5 estrellas).
    """
    user_id = await get_user_id(request)
    engine = await get_learning_engine(request)
    
    if not 1 <= data.rating <= 5:
        raise HTTPException(status_code=400, detail="Rating must be between 1 and 5")
    
    await engine.process_user_rating(
        project_id=data.project_id,
        rating=data.rating,
        user_id=user_id,
        comment=data.comment
    )
    
    return {
        "status": "success",
        "message": f"Rating of {data.rating} stars recorded for project {data.project_id}"
    }

@router.post("/feedback/download")
async def record_download(project_id: str, request: Request):
    """Registrar descarga de proyecto (feedback implícito positivo)"""
    user_id = await get_user_id(request)
    engine = await get_learning_engine(request)
    
    await engine.feedback_system.record_download(project_id, user_id)
    
    return {"status": "recorded"}

@router.post("/feedback/preview")
async def record_preview(project_id: str, duration: int = 0, request: Request = None):
    """Registrar vista de preview"""
    engine = await get_learning_engine(request)
    
    await engine.feedback_system.record_preview(project_id, duration)
    
    return {"status": "recorded"}

@router.get("/feedback/project/{project_id}")
async def get_project_feedback(project_id: str, request: Request):
    """Obtener todo el feedback de un proyecto"""
    engine = await get_learning_engine(request)
    
    feedbacks = await engine.feedback_system.get_project_feedbacks(project_id)
    score = await engine.feedback_system.get_project_score(project_id)
    
    return {
        "project_id": project_id,
        "score": score,
        "feedbacks": feedbacks
    }

# ============= MEMORY ENDPOINTS =============

@router.post("/memory/search")
async def search_memory(
    query: str,
    content_types: Optional[List[str]] = None,
    limit: int = 10,
    request: Request = None
):
    """
    Buscar en la memoria vectorial.
    """
    engine = await get_learning_engine(request)
    
    results = await engine.vector_memory.search(
        query=query,
        content_types=content_types,
        limit=limit
    )
    
    return {
        "query": query,
        "results": results,
        "count": len(results)
    }

@router.get("/memory/stats")
async def get_memory_stats(request: Request):
    """Obtener estadísticas de la memoria"""
    engine = await get_learning_engine(request)
    
    stats = await engine.vector_memory.get_stats()
    
    return stats

@router.get("/memory/best/{content_type}")
async def get_best_examples(content_type: str, limit: int = 10, request: Request = None):
    """Obtener los mejores ejemplos de un tipo de contenido"""
    engine = await get_learning_engine(request)
    
    examples = await engine.vector_memory.get_best_examples(content_type, limit)
    
    return {
        "content_type": content_type,
        "examples": examples,
        "count": len(examples)
    }

# ============= CONTEXT ENDPOINTS =============

@router.post("/context/enhanced")
async def get_enhanced_context(
    prompt: str,
    project_type: Optional[str] = None,
    request: Request = None
):
    """
    Obtener contexto mejorado para una generación.
    Incluye ejemplos similares, errores a evitar, etc.
    """
    engine = await get_learning_engine(request)
    
    context = await engine.get_enhanced_context(prompt, project_type)
    
    return {
        "prompt": prompt,
        "context": context
    }

# ============= METRICS ENDPOINTS =============

@router.get("/metrics/stats/{metric_type}")
async def get_metric_stats(metric_type: str, days: int = 7, request: Request = None):
    """Obtener estadísticas de una métrica"""
    engine = await get_learning_engine(request)
    
    from learning.metrics_tracker import MetricType
    
    try:
        mtype = MetricType(metric_type)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid metric type: {metric_type}")
    
    stats = await engine.metrics_tracker.get_metric_stats(mtype, days)
    
    return stats

@router.get("/metrics/trend/{metric_type}")
async def get_metric_trend(metric_type: str, days: int = 14, request: Request = None):
    """Obtener tendencia de una métrica"""
    engine = await get_learning_engine(request)
    
    from learning.metrics_tracker import MetricType
    
    try:
        mtype = MetricType(metric_type)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid metric type: {metric_type}")
    
    trend = await engine.metrics_tracker.get_trend(mtype, days)
    
    return trend

@router.get("/metrics/anomalies/{metric_type}")
async def get_anomalies(metric_type: str, threshold: float = 2.0, request: Request = None):
    """Detectar anomalías en una métrica"""
    engine = await get_learning_engine(request)
    
    from learning.metrics_tracker import MetricType
    
    try:
        mtype = MetricType(metric_type)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid metric type: {metric_type}")
    
    anomalies = await engine.metrics_tracker.detect_anomalies(mtype, threshold)
    
    return {
        "metric_type": metric_type,
        "anomalies": anomalies
    }

@router.get("/metrics/project/{project_id}")
async def get_project_metrics(project_id: str, request: Request):
    """Obtener métricas de un proyecto"""
    engine = await get_learning_engine(request)
    
    metrics = await engine.metrics_tracker.get_project_metrics(project_id)
    
    return metrics

@router.get("/metrics/dashboard")
async def get_metrics_dashboard(request: Request):
    """Obtener estadísticas para el dashboard"""
    engine = await get_learning_engine(request)
    
    dashboard = await engine.metrics_tracker.get_dashboard_stats()
    
    return dashboard

# ============= PROMPT OPTIMIZATION ENDPOINTS =============

@router.get("/prompts/{prompt_type}/performance")
async def get_prompt_performance(prompt_type: str, request: Request):
    """Obtener análisis de rendimiento de un prompt"""
    engine = await get_learning_engine(request)
    
    performance = await engine.prompt_optimizer.analyze_prompt_performance(prompt_type)
    
    return performance

@router.get("/prompts/{prompt_type}/suggest")
async def suggest_prompt_improvement(prompt_type: str, request: Request):
    """Obtener sugerencia de mejora para un prompt"""
    engine = await get_learning_engine(request)
    
    suggestion = await engine.prompt_optimizer.suggest_improvement(prompt_type)
    
    return suggestion

@router.post("/prompts/update")
async def update_prompt(data: PromptUpdateRequest, request: Request):
    """Actualizar un prompt con nueva versión"""
    engine = await get_learning_engine(request)
    
    prompt_id = await engine.prompt_optimizer.apply_improvement(
        prompt_type=data.prompt_type,
        new_content=data.content,
        reason=data.reason
    )
    
    if not prompt_id:
        raise HTTPException(status_code=500, detail="Failed to update prompt")
    
    return {
        "status": "success",
        "prompt_id": prompt_id,
        "prompt_type": data.prompt_type
    }

@router.get("/prompts/{prompt_type}/versions")
async def get_prompt_versions(prompt_type: str, request: Request):
    """Obtener historial de versiones de un prompt"""
    engine = await get_learning_engine(request)
    
    versions = await engine.prompt_optimizer.get_all_versions(prompt_type)
    
    return {
        "prompt_type": prompt_type,
        "versions": versions
    }

@router.post("/prompts/{prompt_type}/rollback/{version}")
async def rollback_prompt(prompt_type: str, version: int, request: Request):
    """Revertir a una versión anterior del prompt"""
    engine = await get_learning_engine(request)
    
    success = await engine.prompt_optimizer.rollback_to_version(prompt_type, version)
    
    if not success:
        raise HTTPException(status_code=404, detail="Version not found")
    
    return {
        "status": "success",
        "prompt_type": prompt_type,
        "active_version": version
    }

# ============= SETTINGS ENDPOINTS =============

@router.get("/settings")
async def get_all_settings(request: Request):
    """Obtener todos los settings del sistema de aprendizaje"""
    engine = await get_learning_engine(request)
    
    settings = {}
    for key in engine.default_settings.keys():
        settings[key] = await engine.get_setting(key)
    
    return {"settings": settings}

@router.put("/settings")
async def update_setting(data: SettingRequest, request: Request):
    """Actualizar un setting"""
    engine = await get_learning_engine(request)
    
    success = await engine.update_setting(data.key, data.value)
    
    if not success:
        raise HTTPException(status_code=500, detail="Failed to update setting")
    
    return {
        "status": "success",
        "key": data.key,
        "value": data.value
    }

# ============= OPTIMIZATION ENDPOINTS =============

@router.post("/optimize/run")
async def run_optimization(background_tasks: BackgroundTasks, request: Request):
    """Ejecutar ciclo de optimización"""
    engine = await get_learning_engine(request)
    
    # Ejecutar en background para no bloquear
    async def run_optimization_task():
        return await engine.run_optimization_cycle()
    
    background_tasks.add_task(run_optimization_task)
    
    return {
        "status": "started",
        "message": "Optimization cycle started in background"
    }

@router.get("/stats")
async def get_learning_stats(request: Request):
    """Obtener estadísticas completas del sistema de aprendizaje"""
    engine = await get_learning_engine(request)
    
    stats = await engine.get_learning_stats()
    
    return stats

@router.get("/export")
async def export_knowledge_base(request: Request):
    """Exportar la base de conocimiento"""
    engine = await get_learning_engine(request)
    
    export = await engine.export_knowledge_base()
    
    return export

# ============= INITIALIZATION ENDPOINT =============

@router.post("/initialize")
async def initialize_learning_system(request: Request):
    """Inicializar el sistema de aprendizaje (crear colecciones e índices)"""
    engine = await get_learning_engine(request)
    
    success = await engine.initialize()
    
    if not success:
        raise HTTPException(status_code=500, detail="Failed to initialize learning system")
    
    return {
        "status": "success",
        "message": "Learning system initialized successfully"
    }

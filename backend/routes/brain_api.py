"""
MelusAI - Brain API Routes
Handles model selection, agent modes, and AI generation tasks
"""
from fastapi import APIRouter, HTTPException, Request, BackgroundTasks
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import logging
import os
import sys

# Add core to path
if '/app/core' not in sys.path:
    sys.path.insert(0, '/app/core')

from core.llm_manager import get_llm_manager, get_available_models, get_available_modes
from core.brain_engine import get_brain_engine

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/brain", tags=["brain"])


# ============= REQUEST MODELS =============

class CreateTaskRequest(BaseModel):
    prompt: str
    model: str = "gpt-4o"
    mode: str = "e1"
    project_type: Optional[str] = None


class ChatRequest(BaseModel):
    message: str
    model: str = "gpt-4o"
    context: Optional[str] = None


class GenerateCodeRequest(BaseModel):
    prompt: str
    language: str = "javascript"
    framework: str = "react"
    model: str = "gpt-4o"


# ============= MODEL & MODE ENDPOINTS =============

@router.get("/models")
async def list_available_models():
    """Get all available AI models"""
    models = get_available_models()
    
    # Group by provider
    grouped = {}
    for model in models:
        provider = model["provider"]
        if provider not in grouped:
            grouped[provider] = []
        grouped[provider].append(model)
    
    return {
        "models": models,
        "by_provider": grouped,
        "default": "gpt-4o"
    }


@router.get("/modes")
async def list_available_modes():
    """Get all available agent modes"""
    modes = get_available_modes()
    
    return {
        "modes": modes,
        "default": "e1",
        "description": {
            "e1": "Fast iterations, good for simple projects",
            "e1.5": "Enhanced quality with better context handling",
            "e2": "Full multi-agent pipeline for complex projects",
            "pro": "Maximum quality with best models",
            "prototype": "Rapid frontend prototyping",
            "mobile": "Mobile-first development"
        }
    }


@router.get("/status")
async def get_brain_status():
    """Get current brain engine status"""
    brain = get_brain_engine()
    llm_manager = get_llm_manager()
    
    return {
        "status": "operational",
        "brain_status": brain.get_status(),
        "current_model": llm_manager.default_model,
        "current_mode": llm_manager.current_mode,
        "llm_available": brain.llm_client is not None,
        "orchestrator_available": brain.orchestrator is not None
    }


# ============= TASK ENDPOINTS =============

@router.post("/create-task")
async def create_generation_task(
    data: CreateTaskRequest,
    request: Request,
    background_tasks: BackgroundTasks
):
    """
    Create a new code generation task.
    Uses the Brain Engine to classify intent and generate code.
    """
    db = request.app.state.db
    
    # Get user from session
    token = request.headers.get("X-Session-Token")
    user_id = "anonymous"
    
    if token:
        user = await db.users.find_one({"session_token": token}, {"_id": 0, "user_id": 1})
        if user:
            user_id = user["user_id"]
    
    # Configure LLM manager
    llm_manager = get_llm_manager()
    llm_manager.set_mode(data.mode)
    llm_manager.set_default_model(data.model)
    
    # Get brain engine
    brain = get_brain_engine()
    
    # Generate project ID
    import uuid
    project_id = f"proj_{uuid.uuid4().hex[:12]}"
    
    # Determine if we should use multi-agent based on mode
    use_multi_agent = data.mode in ["e2", "pro"]
    
    # Store initial project record
    project_doc = {
        "id": project_id,
        "user_id": user_id,
        "prompt": data.prompt,
        "model": data.model,
        "mode": data.mode,
        "phase": "planning",
        "status": "Processing your request...",
        "files": {},
        "plan": {},
        "errors": [],
        "created_at": __import__('datetime').datetime.utcnow()
    }
    await db.projects.insert_one(project_doc)
    
    # Run pipeline in background
    async def run_brain_pipeline():
        try:
            context = await brain.process_prompt(
                prompt=data.prompt,
                project_id=project_id,
                user_id=user_id,
                use_multi_agent=use_multi_agent
            )
            
            # Convert files list to dict
            files_dict = {}
            for f in context.files:
                path = f.get("path", "")
                content = f.get("content", "")
                if path and content:
                    files_dict[path] = content
            
            # Update project with results
            await db.projects.update_one(
                {"id": project_id},
                {"$set": {
                    "phase": context.current_stage.value,
                    "status": "completed" if context.current_stage.value == "complete" else "error",
                    "files": files_dict,
                    "plan": context.metadata.get("plan", {}),
                    "intent": {
                        "type": context.intent_result.intent_type.value if context.intent_result else "web_app",
                        "confidence": context.intent_result.confidence if context.intent_result else 0,
                        "features": context.intent_result.features if context.intent_result else []
                    },
                    "errors": context.errors
                }}
            )
            
        except Exception as e:
            logger.error(f"Brain pipeline error: {e}")
            await db.projects.update_one(
                {"id": project_id},
                {"$set": {
                    "phase": "error",
                    "status": f"Error: {str(e)}",
                    "errors": [str(e)]
                }}
            )
    
    background_tasks.add_task(run_brain_pipeline)
    
    return {
        "project_id": project_id,
        "status": "started",
        "model": data.model,
        "mode": data.mode,
        "message": "Your project is being generated..."
    }


@router.get("/task/{project_id}")
async def get_task_status(project_id: str, request: Request):
    """Get the status of a generation task"""
    db = request.app.state.db
    
    project = await db.projects.find_one(
        {"id": project_id},
        {"_id": 0}
    )
    
    if not project:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return {
        "project_id": project_id,
        "phase": project.get("phase"),
        "status": project.get("status"),
        "files_count": len(project.get("files", {})),
        "intent": project.get("intent", {}),
        "errors": project.get("errors", [])
    }


# ============= CHAT ENDPOINTS =============

@router.post("/chat")
async def quick_chat(data: ChatRequest, request: Request):
    """
    Quick chat with AI model.
    No project context, just direct question/answer.
    """
    llm_manager = get_llm_manager()
    
    try:
        response = await llm_manager.chat(
            prompt=data.message,
            model=data.model,
            system_message=data.context or "You are a helpful AI assistant specialized in software development."
        )
        
        return {
            "response": response,
            "model": data.model
        }
        
    except Exception as e:
        logger.error(f"Chat error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate-code")
async def generate_code(data: GenerateCodeRequest, request: Request):
    """
    Generate code snippet.
    For quick code generation without full project.
    """
    llm_manager = get_llm_manager()
    
    try:
        code = await llm_manager.generate_code(
            prompt=data.prompt,
            language=data.language,
            framework=data.framework,
            model=data.model
        )
        
        # Clean code from markdown blocks
        if "```" in code:
            lines = code.split("\n")
            clean_lines = []
            in_code = False
            for line in lines:
                if line.startswith("```"):
                    in_code = not in_code
                    continue
                if in_code or not line.startswith("```"):
                    clean_lines.append(line)
            code = "\n".join(clean_lines)
        
        return {
            "code": code.strip(),
            "language": data.language,
            "framework": data.framework,
            "model": data.model
        }
        
    except Exception as e:
        logger.error(f"Code generation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============= ANALYSIS ENDPOINTS =============

@router.post("/analyze")
async def analyze_code(request: Request):
    """Analyze code for issues and improvements"""
    body = await request.json()
    code = body.get("code", "")
    analysis_type = body.get("type", "review")
    model = body.get("model", "gpt-4o")
    
    if not code:
        raise HTTPException(status_code=400, detail="No code provided")
    
    llm_manager = get_llm_manager()
    
    try:
        result = await llm_manager.analyze_code(
            code=code,
            analysis_type=analysis_type,
            model=model
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Analysis error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============= INTENT CLASSIFICATION =============

@router.post("/classify")
async def classify_intent(request: Request):
    """Classify the intent of a prompt"""
    body = await request.json()
    prompt = body.get("prompt", "")
    
    if not prompt:
        raise HTTPException(status_code=400, detail="No prompt provided")
    
    brain = get_brain_engine()
    intent = brain.intent_classifier.classify(prompt)
    
    return {
        "intent_type": intent.intent_type.value,
        "confidence": intent.confidence,
        "complexity": intent.complexity.value,
        "features": intent.features,
        "recommended_template": intent.recommended_template,
        "recommended_builder": intent.recommended_builder
    }

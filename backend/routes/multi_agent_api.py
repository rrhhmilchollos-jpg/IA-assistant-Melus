"""
MelusAI Multi-Agent API Routes
Endpoints for interacting with the multi-agent system
"""
from fastapi import APIRouter, HTTPException, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional, List, Dict
import asyncio
import json
import logging

from multi_agent_system import (
    get_orchestrator, AgentType, AgentStatus, TaskPriority
)
from utils import get_authenticated_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/agents-v3", tags=["multi-agent"])


# Request/Response Models
class StartPipelineRequest(BaseModel):
    prompt: str
    project_name: Optional[str] = None


class TaskRequest(BaseModel):
    agent_type: str
    description: str
    input_data: Optional[Dict] = None
    priority: Optional[str] = "medium"


class MessageRequest(BaseModel):
    to_agent: Optional[str] = None
    content: str
    data: Optional[Dict] = None


# WebSocket connections for real-time updates
agent_connections: Dict[str, List[WebSocket]] = {}


async def broadcast_to_project(project_id: str, event_type: str, data: Dict):
    """Broadcast update to all connected clients for a project"""
    connections = agent_connections.get(project_id, [])
    message = json.dumps({"type": event_type, "data": data})
    
    disconnected = []
    for websocket in connections:
        try:
            await websocket.send_text(message)
        except Exception:
            disconnected.append(websocket)
    
    # Remove disconnected clients
    for ws in disconnected:
        connections.remove(ws)


# Endpoints
@router.get("/status")
async def get_agent_system_status(request: Request):
    """Get current status of all agents"""
    await get_authenticated_user(request, request.app.state.db)
    
    orchestrator = get_orchestrator()
    return orchestrator.get_status()


@router.get("/agents")
async def list_agents(request: Request):
    """List all available agents and their current status"""
    await get_authenticated_user(request, request.app.state.db)
    
    orchestrator = get_orchestrator()
    agents = []
    
    for agent_type, agent in orchestrator.agents.items():
        agents.append(agent.get_status())
    
    return {"agents": agents}


@router.get("/agents/{agent_type}")
async def get_agent_status(agent_type: str, request: Request):
    """Get status of a specific agent"""
    await get_authenticated_user(request, request.app.state.db)
    
    try:
        agent_enum = AgentType(agent_type)
    except ValueError:
        raise HTTPException(status_code=404, detail=f"Unknown agent type: {agent_type}")
    
    orchestrator = get_orchestrator()
    agent = orchestrator.get_agent(agent_enum)
    
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    return agent.get_status()


@router.post("/pipeline/start")
async def start_pipeline(request_data: StartPipelineRequest, request: Request):
    """Start a new multi-agent pipeline"""
    user = await get_authenticated_user(request, request.app.state.db)
    db = request.app.state.db
    
    from utils import generate_id
    
    # Create project
    project_id = generate_id("proj")
    
    # Save project to DB
    project_doc = {
        "project_id": project_id,
        "user_id": user["user_id"],
        "name": request_data.project_name or f"Project_{project_id[:8]}",
        "prompt": request_data.prompt,
        "status": "planning",
        "agent_status": "starting",
        "created_at": __import__("datetime").datetime.now(__import__("datetime").timezone.utc)
    }
    await db.projects.insert_one(project_doc)
    
    # Get orchestrator and set up callbacks
    orchestrator = get_orchestrator()
    
    async def update_callback(event_type: str, data: Dict):
        # Update project status in DB
        if event_type in ["pipeline_completed", "pipeline_error"]:
            status = "completed" if event_type == "pipeline_completed" else "error"
            await db.projects.update_one(
                {"project_id": project_id},
                {"$set": {"status": status, "agent_status": event_type}}
            )
        
        # Broadcast to WebSocket clients
        await broadcast_to_project(project_id, event_type, data)
    
    orchestrator.on_update(update_callback)
    
    # Start pipeline in background
    asyncio.create_task(orchestrator.run_pipeline(request_data.prompt, project_id))
    
    return {
        "project_id": project_id,
        "status": "started",
        "message": "Pipeline started. Connect to WebSocket for real-time updates."
    }


@router.post("/task")
async def create_task(task_request: TaskRequest, request: Request):
    """Create a new task for an agent"""
    await get_authenticated_user(request, request.app.state.db)
    
    try:
        agent_type = AgentType(task_request.agent_type)
        priority = TaskPriority(task_request.priority)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    orchestrator = get_orchestrator()
    
    task = await orchestrator.create_task(
        agent_type=agent_type,
        description=task_request.description,
        input_data=task_request.input_data or {},
        priority=priority
    )
    
    # Execute task
    result = await orchestrator.execute_task(task)
    
    return {
        "task_id": task.id,
        "status": task.status.value,
        "result": result
    }


@router.get("/tasks")
async def list_tasks(request: Request):
    """List all tasks"""
    await get_authenticated_user(request, request.app.state.db)
    
    orchestrator = get_orchestrator()
    
    return {
        "pending": [t.to_dict() for t in orchestrator.task_queue],
        "completed": [t.to_dict() for t in orchestrator.completed_tasks[-50:]]  # Last 50
    }


@router.get("/messages")
async def list_messages(request: Request, limit: int = 50):
    """List recent agent messages"""
    await get_authenticated_user(request, request.app.state.db)
    
    orchestrator = get_orchestrator()
    
    messages = orchestrator.message_queue[-limit:]
    return {
        "messages": [m.to_dict() for m in messages],
        "total": len(orchestrator.message_queue)
    }


@router.get("/costs")
async def get_costs(request: Request):
    """Get cost tracking information"""
    await get_authenticated_user(request, request.app.state.db)
    
    orchestrator = get_orchestrator()
    cost_controller = orchestrator.get_agent(AgentType.COST_CONTROLLER)
    
    return cost_controller.get_usage_stats()


# WebSocket endpoint for real-time updates
@router.websocket("/ws/{project_id}")
async def agent_websocket(websocket: WebSocket, project_id: str):
    """WebSocket for real-time agent updates"""
    await websocket.accept()
    
    # Add to connections
    if project_id not in agent_connections:
        agent_connections[project_id] = []
    agent_connections[project_id].append(websocket)
    
    try:
        # Send initial status
        orchestrator = get_orchestrator()
        await websocket.send_json({
            "type": "connected",
            "data": orchestrator.get_status()
        })
        
        # Keep connection alive
        while True:
            try:
                # Wait for messages (ping/pong)
                data = await asyncio.wait_for(
                    websocket.receive_text(),
                    timeout=30.0
                )
                
                if data == "ping":
                    await websocket.send_text("pong")
                    
            except asyncio.TimeoutError:
                # Send heartbeat
                await websocket.send_json({"type": "heartbeat"})
                
    except WebSocketDisconnect:
        pass
    finally:
        # Remove from connections
        if project_id in agent_connections:
            if websocket in agent_connections[project_id]:
                agent_connections[project_id].remove(websocket)


# SSE endpoint for streaming updates
@router.get("/stream/{project_id}")
async def stream_updates(project_id: str, request: Request):
    """Server-Sent Events stream for agent updates"""
    await get_authenticated_user(request, request.app.state.db)
    
    async def event_generator():
        orchestrator = get_orchestrator()
        
        # Send initial status
        yield f"data: {json.dumps({'type': 'status', 'data': orchestrator.get_status()})}\n\n"
        
        # Create queue for this client
        queue = asyncio.Queue()
        
        async def callback(event_type: str, data: Dict):
            await queue.put({"type": event_type, "data": data})
        
        orchestrator.on_update(callback)
        
        try:
            while True:
                try:
                    event = await asyncio.wait_for(queue.get(), timeout=30.0)
                    yield f"data: {json.dumps(event)}\n\n"
                except asyncio.TimeoutError:
                    yield f"data: {json.dumps({'type': 'heartbeat'})}\n\n"
        except asyncio.CancelledError:
            pass
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive"
        }
    )

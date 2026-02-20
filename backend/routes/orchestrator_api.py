"""
MelusAI - Orchestrator API Routes
"""
from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
import uuid

from orchestrator_models import (
    Objective, ObjectiveCreate, ObjectiveStatus, ObjectiveType,
    Task, TaskStatus, Agent, AgentRole, PerformanceLog,
    AutonomousLoop, LoopState
)

router = APIRouter(prefix="/api/orchestrator", tags=["orchestrator"])

# In-memory storage (would be MongoDB in production)
objectives_db: Dict[str, dict] = {}
tasks_db: Dict[str, dict] = {}
agents_db: Dict[str, dict] = {}
loops_db: Dict[str, dict] = {}
performance_logs_db: List[dict] = []

# Initialize default agents
def init_agents():
    default_agents = [
        {"role": "planner", "name": "Strategic Planner", "model": "gpt-4-turbo", "status": "active", "tasks_completed": 0, "success_rate": 100, "avg_cost": 0},
        {"role": "research", "name": "Research Agent", "model": "gpt-4", "status": "active", "tasks_completed": 0, "success_rate": 100, "avg_cost": 0},
        {"role": "reasoning", "name": "Reasoning Agent", "model": "gpt-4-turbo", "status": "active", "tasks_completed": 0, "success_rate": 100, "avg_cost": 0},
        {"role": "content", "name": "Content Creator", "model": "gpt-4", "status": "active", "tasks_completed": 0, "success_rate": 100, "avg_cost": 0},
        {"role": "code", "name": "Code Agent", "model": "gpt-4-turbo", "status": "active", "tasks_completed": 0, "success_rate": 100, "avg_cost": 0},
        {"role": "automation", "name": "Automation Agent", "model": "gpt-4", "status": "active", "tasks_completed": 0, "success_rate": 100, "avg_cost": 0},
        {"role": "qa", "name": "QA Agent", "model": "gpt-4", "status": "active", "tasks_completed": 0, "success_rate": 100, "avg_cost": 0},
        {"role": "security", "name": "Security Agent", "model": "gpt-4", "status": "active", "tasks_completed": 0, "success_rate": 100, "avg_cost": 0},
        {"role": "optimization", "name": "Optimization Agent", "model": "gpt-4", "status": "active", "tasks_completed": 0, "success_rate": 100, "avg_cost": 0},
        {"role": "cost_control", "name": "Cost Controller", "model": "gpt-4", "status": "active", "tasks_completed": 0, "success_rate": 100, "avg_cost": 0},
    ]
    for agent in default_agents:
        agent_id = f"agent_{agent['role']}"
        agents_db[agent_id] = {
            "id": agent_id,
            **agent,
            "reputation_score": 100,
            "created_at": datetime.now(timezone.utc).isoformat()
        }

init_agents()

# ============= OBJECTIVES =============

@router.post("/objectives")
async def create_objective(data: ObjectiveCreate):
    obj_id = f"obj_{uuid.uuid4().hex[:12]}"
    objective = {
        "id": obj_id,
        "title": data.title,
        "description": data.description,
        "type": data.type.value,
        "priority": data.priority,
        "status": "pending",
        "cost_budget": data.cost_budget,
        "cost_used": 0,
        "auto_mode": data.auto_mode,
        "quality_score": None,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat()
    }
    objectives_db[obj_id] = objective
    return objective

@router.get("/objectives")
async def get_objectives():
    return list(objectives_db.values())

@router.get("/objectives/{objective_id}")
async def get_objective(objective_id: str):
    if objective_id not in objectives_db:
        raise HTTPException(status_code=404, detail="Objective not found")
    
    objective = objectives_db[objective_id]
    tasks = [t for t in tasks_db.values() if t.get("objective_id") == objective_id]
    
    return {
        "objective": objective,
        "tasks": tasks,
        "task_count": len(tasks),
        "completed_tasks": len([t for t in tasks if t.get("status") == "completed"])
    }

@router.post("/objectives/{objective_id}/start")
async def start_objective(objective_id: str):
    if objective_id not in objectives_db:
        raise HTTPException(status_code=404, detail="Objective not found")
    
    objectives_db[objective_id]["status"] = "in_progress"
    objectives_db[objective_id]["updated_at"] = datetime.now(timezone.utc).isoformat()
    
    # Create initial tasks
    _create_tasks_for_objective(objective_id)
    
    return {"status": "started", "objective_id": objective_id}

@router.post("/objectives/{objective_id}/pause")
async def pause_objective(objective_id: str):
    if objective_id not in objectives_db:
        raise HTTPException(status_code=404, detail="Objective not found")
    
    objectives_db[objective_id]["status"] = "paused"
    return {"status": "paused"}

@router.post("/objectives/{objective_id}/resume")
async def resume_objective(objective_id: str):
    if objective_id not in objectives_db:
        raise HTTPException(status_code=404, detail="Objective not found")
    
    objectives_db[objective_id]["status"] = "in_progress"
    return {"status": "resumed"}

def _create_tasks_for_objective(objective_id: str):
    objective = objectives_db[objective_id]
    obj_type = objective.get("type", "mixed")
    
    # Define tasks based on objective type
    task_templates = {
        "code": [
            {"title": "Planning", "agent": "planner", "phase": 1},
            {"title": "Architecture Design", "agent": "reasoning", "phase": 2},
            {"title": "Implementation", "agent": "code", "phase": 3},
            {"title": "Testing", "agent": "qa", "phase": 4},
            {"title": "Security Review", "agent": "security", "phase": 5},
            {"title": "Optimization", "agent": "optimization", "phase": 6},
        ],
        "content": [
            {"title": "Research", "agent": "research", "phase": 1},
            {"title": "Planning", "agent": "planner", "phase": 2},
            {"title": "Writing", "agent": "content", "phase": 3},
            {"title": "QA Review", "agent": "qa", "phase": 4},
            {"title": "SEO Optimization", "agent": "optimization", "phase": 5},
        ],
        "automation": [
            {"title": "Requirements Analysis", "agent": "planner", "phase": 1},
            {"title": "Design", "agent": "reasoning", "phase": 2},
            {"title": "Implementation", "agent": "automation", "phase": 3},
            {"title": "Testing", "agent": "qa", "phase": 4},
        ],
        "research": [
            {"title": "Data Collection", "agent": "research", "phase": 1},
            {"title": "Analysis", "agent": "reasoning", "phase": 2},
            {"title": "Report Generation", "agent": "content", "phase": 3},
        ],
        "mixed": [
            {"title": "Planning", "agent": "planner", "phase": 1},
            {"title": "Research", "agent": "research", "phase": 2},
            {"title": "Execution", "agent": "code", "phase": 3},
            {"title": "Review", "agent": "qa", "phase": 4},
        ]
    }
    
    templates = task_templates.get(obj_type, task_templates["mixed"])
    
    for template in templates:
        task_id = f"task_{uuid.uuid4().hex[:12]}"
        tasks_db[task_id] = {
            "id": task_id,
            "objective_id": objective_id,
            "title": template["title"],
            "agent_role": template["agent"],
            "agent_id": f"agent_{template['agent']}",
            "phase": template["phase"],
            "status": "queued",
            "progress": 0,
            "created_at": datetime.now(timezone.utc).isoformat()
        }

# ============= TASKS =============

@router.get("/tasks")
async def get_tasks(objective_id: Optional[str] = None):
    if objective_id:
        return [t for t in tasks_db.values() if t.get("objective_id") == objective_id]
    return list(tasks_db.values())

@router.get("/tasks/{task_id}")
async def get_task(task_id: str):
    if task_id not in tasks_db:
        raise HTTPException(status_code=404, detail="Task not found")
    return tasks_db[task_id]

@router.post("/tasks/{task_id}/execute")
async def execute_task(task_id: str):
    if task_id not in tasks_db:
        raise HTTPException(status_code=404, detail="Task not found")
    
    task = tasks_db[task_id]
    task["status"] = "running"
    task["started_at"] = datetime.now(timezone.utc).isoformat()
    
    # Simulate task execution (would call LLM here)
    import random
    task["progress"] = random.randint(20, 100)
    
    if task["progress"] == 100:
        task["status"] = "completed"
        task["completed_at"] = datetime.now(timezone.utc).isoformat()
        task["result_score"] = random.uniform(0.7, 1.0)
        
        # Update agent stats
        agent_id = task.get("agent_id")
        if agent_id in agents_db:
            agents_db[agent_id]["tasks_completed"] += 1
    
    return task

# ============= AGENTS =============

@router.get("/agents")
async def get_agents():
    return list(agents_db.values())

@router.get("/agents/{agent_id}")
async def get_agent(agent_id: str):
    if agent_id not in agents_db:
        raise HTTPException(status_code=404, detail="Agent not found")
    return agents_db[agent_id]

@router.post("/agents/{agent_id}/toggle")
async def toggle_agent(agent_id: str):
    if agent_id not in agents_db:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    current = agents_db[agent_id]["status"]
    agents_db[agent_id]["status"] = "inactive" if current == "active" else "active"
    return agents_db[agent_id]

# ============= DASHBOARD STATS =============

@router.get("/stats")
async def get_dashboard_stats():
    total_objectives = len(objectives_db)
    active_objectives = len([o for o in objectives_db.values() if o.get("status") == "in_progress"])
    completed_objectives = len([o for o in objectives_db.values() if o.get("status") == "completed"])
    
    total_tasks = len(tasks_db)
    completed_tasks = len([t for t in tasks_db.values() if t.get("status") == "completed"])
    running_tasks = len([t for t in tasks_db.values() if t.get("status") == "running"])
    
    active_agents = len([a for a in agents_db.values() if a.get("status") == "active"])
    
    total_cost = sum(o.get("cost_used", 0) for o in objectives_db.values())
    
    # Agent performance
    agent_stats = []
    for agent in agents_db.values():
        agent_stats.append({
            "id": agent["id"],
            "name": agent["name"],
            "role": agent["role"],
            "tasks_completed": agent.get("tasks_completed", 0),
            "success_rate": agent.get("success_rate", 100),
            "status": agent.get("status", "active")
        })
    
    return {
        "objectives": {
            "total": total_objectives,
            "active": active_objectives,
            "completed": completed_objectives
        },
        "tasks": {
            "total": total_tasks,
            "completed": completed_tasks,
            "running": running_tasks,
            "queued": total_tasks - completed_tasks - running_tasks
        },
        "agents": {
            "total": len(agents_db),
            "active": active_agents,
            "list": agent_stats
        },
        "cost": {
            "total": total_cost,
            "average_per_objective": total_cost / total_objectives if total_objectives > 0 else 0
        },
        "performance": {
            "avg_quality_score": 0.85,
            "tasks_per_hour": 12,
            "success_rate": 95
        }
    }

@router.get("/activity")
async def get_recent_activity():
    """Get recent activity log"""
    activities = []
    
    # Get recent tasks
    for task in sorted(tasks_db.values(), key=lambda x: x.get("created_at", ""), reverse=True)[:10]:
        activities.append({
            "type": "task",
            "action": task.get("status"),
            "title": task.get("title"),
            "agent": task.get("agent_role"),
            "timestamp": task.get("created_at")
        })
    
    # Get recent objectives
    for obj in sorted(objectives_db.values(), key=lambda x: x.get("created_at", ""), reverse=True)[:5]:
        activities.append({
            "type": "objective",
            "action": obj.get("status"),
            "title": obj.get("title"),
            "timestamp": obj.get("created_at")
        })
    
    return sorted(activities, key=lambda x: x.get("timestamp", ""), reverse=True)[:15]

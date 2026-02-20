"""
MelusAI - Multi-Agent Orchestrator API Routes
Full code generation engine for web apps, 2D/3D games, and mobile applications
"""
from fastapi import APIRouter, HTTPException, Request
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
import uuid
import os
import asyncio
import json
import logging

from orchestrator_models import (
    Objective, ObjectiveCreate, ObjectiveStatus, ObjectiveType,
    Task, TaskStatus, AgentRole
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/orchestrator", tags=["orchestrator"])

# ============= LLM INTEGRATION =============

async def call_llm(prompt: str, system_message: str, model: str = "gpt-4o") -> Dict[str, Any]:
    """Call LLM using emergent integrations"""
    try:
        from emergentintegrations.llm.chat import LlmChat, UserMessage
        
        api_key = os.environ.get('EMERGENT_LLM_KEY')
        if not api_key:
            raise ValueError("EMERGENT_LLM_KEY not configured")
        
        chat = LlmChat(
            api_key=api_key,
            session_id=f"task_{uuid.uuid4().hex[:8]}",
            system_message=system_message
        ).with_model("openai", model)
        
        user_message = UserMessage(text=prompt)
        response = await chat.send_message(user_message)
        
        return {
            "success": True,
            "response": response,
            "tokens_used": len(prompt.split()) + len(response.split()) * 2,  # Estimate
            "cost": 0.01  # Approximate cost
        }
    except Exception as e:
        logger.error(f"LLM call failed: {e}")
        return {
            "success": False,
            "error": str(e),
            "response": None
        }

# ============= AGENT SYSTEM PROMPTS =============

AGENT_PROMPTS = {
    "planner": """You are the Strategic Planner Agent for MelusAI - an advanced AI code generation platform.
Your role is to analyze user requirements and create detailed execution plans.

For any project, you must:
1. Break down the requirements into specific, actionable tasks
2. Identify the technology stack needed
3. Define the project structure
4. List all files that need to be created
5. Specify dependencies required

Output your plan as a structured JSON with:
- project_name: string
- tech_stack: {frontend, backend, database, additional}
- files_to_create: [{path, description, priority}]
- dependencies: {npm: [], pip: []}
- estimated_complexity: low/medium/high""",

    "reasoning": """You are the Architecture Agent for MelusAI.
Your role is to design the technical architecture for applications.

You specialize in:
- System design and architecture patterns
- Database schema design
- API endpoint design
- Component hierarchy for frontends
- Game architecture (for 2D/3D games)

Output detailed technical specifications that other agents can implement.""",

    "code": """You are the Code Agent for MelusAI - the primary code generator.
You write production-quality code for:
- Full-stack web applications (React, Next.js, Vue, FastAPI, Node.js)
- 2D games (Phaser, PixiJS, Canvas)
- 3D games (Three.js, Babylon.js, Unity WebGL)
- Mobile apps (React Native, Flutter concepts)

IMPORTANT RULES:
1. Write complete, working code - no placeholders or TODOs
2. Include all imports and dependencies
3. Add proper error handling
4. Follow best practices for the framework
5. Make code production-ready

When generating files, output as JSON:
{
    "files": [
        {"path": "relative/path/to/file.ext", "content": "full file content here"}
    ]
}""",

    "content": """You are the Content Agent for MelusAI.
You create:
- Documentation and README files
- Comments and code documentation
- User-facing text content
- SEO metadata
- Game narratives and dialogues""",

    "qa": """You are the QA Agent for MelusAI.
Review code for:
1. Bugs and logical errors
2. Security vulnerabilities
3. Performance issues
4. Best practice violations
5. Missing error handling

Output a quality report with issues found and fixes needed.""",

    "security": """You are the Security Agent for MelusAI.
Audit code for:
1. SQL injection vulnerabilities
2. XSS vulnerabilities
3. Authentication/authorization issues
4. Exposed secrets or credentials
5. Insecure dependencies

Output a security report with severity levels.""",

    "optimization": """You are the Optimization Agent for MelusAI.
Optimize code for:
1. Performance (loading time, runtime)
2. Bundle size
3. Memory usage
4. Database queries
5. API response times

Suggest specific optimizations with code changes.""",

    "research": """You are the Research Agent for MelusAI.
Research and provide information about:
1. Best libraries and frameworks for the task
2. Code examples and patterns
3. API documentation
4. Game development techniques
5. Current best practices""",

    "automation": """You are the Automation Agent for MelusAI.
Create automation configurations for:
1. CI/CD pipelines
2. Build scripts
3. Deployment configurations
4. Testing automation
5. Environment setup"""
}

# ============= DEFAULT AGENTS =============

DEFAULT_AGENTS = [
    {"id": "agent_planner", "role": "planner", "name": "Strategic Planner", "model": "gpt-4o", "status": "active"},
    {"id": "agent_research", "role": "research", "name": "Research Agent", "model": "gpt-4o", "status": "active"},
    {"id": "agent_reasoning", "role": "reasoning", "name": "Architecture Agent", "model": "gpt-4o", "status": "active"},
    {"id": "agent_content", "role": "content", "name": "Content Creator", "model": "gpt-4o", "status": "active"},
    {"id": "agent_code", "role": "code", "name": "Code Agent", "model": "gpt-4o", "status": "active"},
    {"id": "agent_automation", "role": "automation", "name": "Automation Agent", "model": "gpt-4o", "status": "active"},
    {"id": "agent_qa", "role": "qa", "name": "QA Agent", "model": "gpt-4o", "status": "active"},
    {"id": "agent_security", "role": "security", "name": "Security Agent", "model": "gpt-4o", "status": "active"},
    {"id": "agent_optimization", "role": "optimization", "name": "Optimization Agent", "model": "gpt-4o", "status": "active"},
    {"id": "agent_cost_control", "role": "cost_control", "name": "Cost Controller", "model": "gpt-4o", "status": "active"},
]

# ============= TASK TEMPLATES BY PROJECT TYPE =============

TASK_TEMPLATES = {
    "web_app": [
        {"title": "Project Planning", "agent": "planner", "phase": 1},
        {"title": "Architecture Design", "agent": "reasoning", "phase": 2},
        {"title": "Backend Implementation", "agent": "code", "phase": 3},
        {"title": "Frontend Implementation", "agent": "code", "phase": 4},
        {"title": "Database Setup", "agent": "code", "phase": 5},
        {"title": "API Integration", "agent": "code", "phase": 6},
        {"title": "Testing & QA", "agent": "qa", "phase": 7},
        {"title": "Security Audit", "agent": "security", "phase": 8},
        {"title": "Optimization", "agent": "optimization", "phase": 9},
    ],
    "game_2d": [
        {"title": "Game Design Document", "agent": "planner", "phase": 1},
        {"title": "Game Architecture", "agent": "reasoning", "phase": 2},
        {"title": "Game Engine Setup", "agent": "code", "phase": 3},
        {"title": "Sprite & Asset System", "agent": "code", "phase": 4},
        {"title": "Game Logic Implementation", "agent": "code", "phase": 5},
        {"title": "UI/Menu System", "agent": "code", "phase": 6},
        {"title": "Sound Integration", "agent": "code", "phase": 7},
        {"title": "Game Testing", "agent": "qa", "phase": 8},
        {"title": "Performance Optimization", "agent": "optimization", "phase": 9},
    ],
    "game_3d": [
        {"title": "3D Game Design", "agent": "planner", "phase": 1},
        {"title": "3D Architecture", "agent": "reasoning", "phase": 2},
        {"title": "Three.js/Babylon Setup", "agent": "code", "phase": 3},
        {"title": "3D Models & Scenes", "agent": "code", "phase": 4},
        {"title": "Camera & Controls", "agent": "code", "phase": 5},
        {"title": "Physics & Collision", "agent": "code", "phase": 6},
        {"title": "Lighting & Effects", "agent": "code", "phase": 7},
        {"title": "Game Mechanics", "agent": "code", "phase": 8},
        {"title": "Performance Testing", "agent": "qa", "phase": 9},
        {"title": "WebGL Optimization", "agent": "optimization", "phase": 10},
    ],
    "mobile_app": [
        {"title": "Mobile App Planning", "agent": "planner", "phase": 1},
        {"title": "Mobile Architecture", "agent": "reasoning", "phase": 2},
        {"title": "React Native Setup", "agent": "code", "phase": 3},
        {"title": "Screen Implementation", "agent": "code", "phase": 4},
        {"title": "Navigation System", "agent": "code", "phase": 5},
        {"title": "State Management", "agent": "code", "phase": 6},
        {"title": "API Integration", "agent": "code", "phase": 7},
        {"title": "Mobile Testing", "agent": "qa", "phase": 8},
        {"title": "Mobile Optimization", "agent": "optimization", "phase": 9},
    ],
    "landing_page": [
        {"title": "Landing Page Planning", "agent": "planner", "phase": 1},
        {"title": "Design Architecture", "agent": "reasoning", "phase": 2},
        {"title": "HTML/CSS Implementation", "agent": "code", "phase": 3},
        {"title": "Responsive Design", "agent": "code", "phase": 4},
        {"title": "Animations & Effects", "agent": "code", "phase": 5},
        {"title": "SEO Optimization", "agent": "content", "phase": 6},
        {"title": "Performance Check", "agent": "optimization", "phase": 7},
    ],
    "code": [  # Default for general code projects
        {"title": "Planning", "agent": "planner", "phase": 1},
        {"title": "Architecture Design", "agent": "reasoning", "phase": 2},
        {"title": "Implementation", "agent": "code", "phase": 3},
        {"title": "Testing", "agent": "qa", "phase": 4},
        {"title": "Security Review", "agent": "security", "phase": 5},
        {"title": "Optimization", "agent": "optimization", "phase": 6},
    ],
}

# ============= DATABASE HELPERS =============

def get_db(request: Request):
    """Get database from request state"""
    return request.app.state.db

async def ensure_indexes(db):
    """Ensure MongoDB indexes exist"""
    await db.orchestrator_objectives.create_index("id", unique=True)
    await db.orchestrator_objectives.create_index("user_id")
    await db.orchestrator_objectives.create_index("status")
    await db.orchestrator_tasks.create_index("id", unique=True)
    await db.orchestrator_tasks.create_index("objective_id")
    await db.orchestrator_agents.create_index("id", unique=True)

async def init_agents_if_empty(db):
    """Initialize default agents if none exist"""
    count = await db.orchestrator_agents.count_documents({})
    if count == 0:
        for agent in DEFAULT_AGENTS:
            agent_doc = {
                **agent,
                "tasks_completed": 0,
                "success_rate": 100,
                "avg_cost": 0,
                "reputation_score": 100,
                "created_at": datetime.now(timezone.utc).isoformat()
            }
            await db.orchestrator_agents.insert_one(agent_doc)

# ============= OBJECTIVES ENDPOINTS =============

@router.post("/objectives")
async def create_objective(data: ObjectiveCreate, request: Request):
    """Create a new objective/project"""
    db = get_db(request)
    await ensure_indexes(db)
    await init_agents_if_empty(db)
    
    obj_id = f"obj_{uuid.uuid4().hex[:12]}"
    
    # Detect project type from description
    project_type = detect_project_type(data.description)
    
    objective = {
        "id": obj_id,
        "title": data.title,
        "description": data.description,
        "type": data.type.value,
        "project_type": project_type,
        "priority": data.priority,
        "status": "pending",
        "cost_budget": data.cost_budget,
        "cost_used": 0,
        "auto_mode": data.auto_mode,
        "quality_score": None,
        "generated_files": [],
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat()
    }
    
    await db.orchestrator_objectives.insert_one(objective)
    
    # Remove MongoDB _id from response
    objective.pop("_id", None)
    return objective

def detect_project_type(description: str) -> str:
    """Detect the type of project from description"""
    desc_lower = description.lower()
    
    if any(word in desc_lower for word in ["3d", "three.js", "babylon", "webgl", "3d game"]):
        return "game_3d"
    elif any(word in desc_lower for word in ["2d game", "phaser", "pixi", "canvas game", "platformer", "shooter"]):
        return "game_2d"
    elif any(word in desc_lower for word in ["mobile", "react native", "flutter", "ios", "android", "app store"]):
        return "mobile_app"
    elif any(word in desc_lower for word in ["landing", "landing page", "marketing", "portfolio"]):
        return "landing_page"
    else:
        return "web_app"

@router.get("/objectives")
async def get_objectives(request: Request):
    """Get all objectives"""
    db = get_db(request)
    objectives = await db.orchestrator_objectives.find({}, {"_id": 0}).to_list(100)
    return objectives

@router.get("/objectives/{objective_id}")
async def get_objective(objective_id: str, request: Request):
    """Get a specific objective with its tasks"""
    db = get_db(request)
    
    objective = await db.orchestrator_objectives.find_one(
        {"id": objective_id}, {"_id": 0}
    )
    if not objective:
        raise HTTPException(status_code=404, detail="Objective not found")
    
    tasks = await db.orchestrator_tasks.find(
        {"objective_id": objective_id}, {"_id": 0}
    ).to_list(100)
    
    return {
        "objective": objective,
        "tasks": tasks,
        "task_count": len(tasks),
        "completed_tasks": len([t for t in tasks if t.get("status") == "completed"])
    }

@router.post("/objectives/{objective_id}/start")
async def start_objective(objective_id: str, request: Request):
    """Start processing an objective - creates tasks and begins execution"""
    db = get_db(request)
    
    objective = await db.orchestrator_objectives.find_one({"id": objective_id})
    if not objective:
        raise HTTPException(status_code=404, detail="Objective not found")
    
    # Update status
    await db.orchestrator_objectives.update_one(
        {"id": objective_id},
        {"$set": {"status": "in_progress", "updated_at": datetime.now(timezone.utc).isoformat()}}
    )
    
    # Create tasks based on project type
    project_type = objective.get("project_type", "code")
    templates = TASK_TEMPLATES.get(project_type, TASK_TEMPLATES["code"])
    
    for template in templates:
        task_id = f"task_{uuid.uuid4().hex[:12]}"
        task = {
            "id": task_id,
            "objective_id": objective_id,
            "title": template["title"],
            "agent_role": template["agent"],
            "agent_id": f"agent_{template['agent']}",
            "phase": template["phase"],
            "status": "queued",
            "progress": 0,
            "input_data": {
                "objective_title": objective["title"],
                "objective_description": objective["description"],
                "project_type": project_type
            },
            "output_data": None,
            "generated_files": [],
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        await db.orchestrator_tasks.insert_one(task)
    
    # If auto_mode is enabled, start executing tasks in background
    if objective.get("auto_mode", True):
        asyncio.create_task(execute_objective_tasks(db, objective_id))
    
    return {"status": "started", "objective_id": objective_id, "project_type": project_type}

async def execute_objective_tasks(db, objective_id: str):
    """Execute all tasks for an objective sequentially"""
    try:
        tasks = await db.orchestrator_tasks.find(
            {"objective_id": objective_id}
        ).sort("phase", 1).to_list(100)
        
        accumulated_context = ""
        generated_files = []
        
        for task in tasks:
            task_id = task["id"]
            agent_role = task["agent_role"]
            
            # Update task status to running
            await db.orchestrator_tasks.update_one(
                {"id": task_id},
                {"$set": {"status": "running", "started_at": datetime.now(timezone.utc).isoformat()}}
            )
            
            # Get the system prompt for this agent
            system_prompt = AGENT_PROMPTS.get(agent_role, AGENT_PROMPTS["code"])
            
            # Build the task prompt
            task_prompt = build_task_prompt(task, accumulated_context, generated_files)
            
            # Call LLM
            result = await call_llm(task_prompt, system_prompt)
            
            if result["success"]:
                # Parse output for generated files (for code agent)
                files_from_task = []
                if agent_role == "code":
                    files_from_task = parse_generated_files(result["response"])
                    generated_files.extend(files_from_task)
                
                # Update task with results
                await db.orchestrator_tasks.update_one(
                    {"id": task_id},
                    {"$set": {
                        "status": "completed",
                        "output_data": {"response": result["response"][:5000]},  # Truncate for storage
                        "generated_files": files_from_task,
                        "tokens_used": result.get("tokens_used", 0),
                        "cost": result.get("cost", 0),
                        "completed_at": datetime.now(timezone.utc).isoformat()
                    }}
                )
                
                # Add to accumulated context for next tasks
                accumulated_context += f"\n\n--- {task['title']} Output ---\n{result['response'][:2000]}"
                
                # Update agent stats
                await db.orchestrator_agents.update_one(
                    {"id": task["agent_id"]},
                    {"$inc": {"tasks_completed": 1}}
                )
            else:
                await db.orchestrator_tasks.update_one(
                    {"id": task_id},
                    {"$set": {
                        "status": "failed",
                        "error_message": result.get("error", "Unknown error"),
                        "completed_at": datetime.now(timezone.utc).isoformat()
                    }}
                )
        
        # Update objective with all generated files
        await db.orchestrator_objectives.update_one(
            {"id": objective_id},
            {"$set": {
                "status": "completed",
                "generated_files": generated_files,
                "completed_at": datetime.now(timezone.utc).isoformat()
            }}
        )
        
    except Exception as e:
        logger.error(f"Error executing tasks for {objective_id}: {e}")
        await db.orchestrator_objectives.update_one(
            {"id": objective_id},
            {"$set": {"status": "failed", "error": str(e)}}
        )

def build_task_prompt(task: dict, context: str, generated_files: list) -> str:
    """Build the prompt for a specific task"""
    input_data = task.get("input_data", {})
    
    prompt = f"""Project: {input_data.get('objective_title', 'Unknown')}
Description: {input_data.get('objective_description', 'No description')}
Project Type: {input_data.get('project_type', 'web_app')}
Current Task: {task['title']}

"""
    
    if context:
        prompt += f"Previous work done:\n{context}\n\n"
    
    if generated_files:
        prompt += f"Files already generated: {[f['path'] for f in generated_files]}\n\n"
    
    prompt += f"""Now complete the task: {task['title']}

Be thorough and generate complete, production-ready output."""
    
    return prompt

def parse_generated_files(response: str) -> list:
    """Parse generated files from LLM response"""
    files = []
    
    try:
        # Try to find JSON with files array
        if '{"files":' in response or '"files":' in response:
            import re
            json_match = re.search(r'\{[^{}]*"files"\s*:\s*\[[^\]]*\][^{}]*\}', response, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group())
                files = data.get("files", [])
        
        # Also look for code blocks with file paths
        if not files:
            import re
            # Match patterns like ```javascript // path/to/file.js or ```python # path/to/file.py
            code_blocks = re.findall(r'```(\w+)?\s*(?://|#)\s*([^\n]+)\n(.*?)```', response, re.DOTALL)
            for lang, path, content in code_blocks:
                if path and content:
                    files.append({"path": path.strip(), "content": content.strip()})
    except Exception as e:
        logger.error(f"Error parsing files: {e}")
    
    return files

@router.post("/objectives/{objective_id}/pause")
async def pause_objective(objective_id: str, request: Request):
    """Pause an objective"""
    db = get_db(request)
    
    result = await db.orchestrator_objectives.update_one(
        {"id": objective_id},
        {"$set": {"status": "paused", "updated_at": datetime.now(timezone.utc).isoformat()}}
    )
    
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Objective not found")
    
    return {"status": "paused"}

@router.post("/objectives/{objective_id}/resume")
async def resume_objective(objective_id: str, request: Request):
    """Resume a paused objective"""
    db = get_db(request)
    
    objective = await db.orchestrator_objectives.find_one({"id": objective_id})
    if not objective:
        raise HTTPException(status_code=404, detail="Objective not found")
    
    await db.orchestrator_objectives.update_one(
        {"id": objective_id},
        {"$set": {"status": "in_progress", "updated_at": datetime.now(timezone.utc).isoformat()}}
    )
    
    # Continue execution
    asyncio.create_task(execute_objective_tasks(db, objective_id))
    
    return {"status": "resumed"}

# ============= TASKS ENDPOINTS =============

@router.get("/tasks")
async def get_tasks(request: Request, objective_id: Optional[str] = None):
    """Get tasks, optionally filtered by objective"""
    db = get_db(request)
    
    query = {}
    if objective_id:
        query["objective_id"] = objective_id
    
    tasks = await db.orchestrator_tasks.find(query, {"_id": 0}).to_list(100)
    return tasks

@router.get("/tasks/{task_id}")
async def get_task(task_id: str, request: Request):
    """Get a specific task"""
    db = get_db(request)
    
    task = await db.orchestrator_tasks.find_one({"id": task_id}, {"_id": 0})
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return task

@router.post("/tasks/{task_id}/execute")
async def execute_single_task(task_id: str, request: Request):
    """Manually execute a single task"""
    db = get_db(request)
    
    task = await db.orchestrator_tasks.find_one({"id": task_id})
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Update status
    await db.orchestrator_tasks.update_one(
        {"id": task_id},
        {"$set": {"status": "running", "started_at": datetime.now(timezone.utc).isoformat()}}
    )
    
    # Get context from previous tasks
    previous_tasks = await db.orchestrator_tasks.find({
        "objective_id": task["objective_id"],
        "phase": {"$lt": task["phase"]},
        "status": "completed"
    }).to_list(100)
    
    context = ""
    generated_files = []
    for pt in previous_tasks:
        if pt.get("output_data"):
            context += f"\n{pt['title']}: {pt['output_data'].get('response', '')[:1000]}"
        generated_files.extend(pt.get("generated_files", []))
    
    # Execute
    system_prompt = AGENT_PROMPTS.get(task["agent_role"], AGENT_PROMPTS["code"])
    task_prompt = build_task_prompt(task, context, generated_files)
    
    result = await call_llm(task_prompt, system_prompt)
    
    if result["success"]:
        files = parse_generated_files(result["response"]) if task["agent_role"] == "code" else []
        
        await db.orchestrator_tasks.update_one(
            {"id": task_id},
            {"$set": {
                "status": "completed",
                "output_data": {"response": result["response"][:5000]},
                "generated_files": files,
                "completed_at": datetime.now(timezone.utc).isoformat()
            }}
        )
        
        task["status"] = "completed"
        task["output_data"] = {"response": result["response"][:2000]}
        task["generated_files"] = files
    else:
        await db.orchestrator_tasks.update_one(
            {"id": task_id},
            {"$set": {"status": "failed", "error_message": result.get("error")}}
        )
        task["status"] = "failed"
        task["error_message"] = result.get("error")
    
    task.pop("_id", None)
    return task

# ============= AGENTS ENDPOINTS =============

@router.get("/agents")
async def get_agents(request: Request):
    """Get all agents"""
    db = get_db(request)
    await init_agents_if_empty(db)
    
    agents = await db.orchestrator_agents.find({}, {"_id": 0}).to_list(20)
    return agents

@router.get("/agents/{agent_id}")
async def get_agent(agent_id: str, request: Request):
    """Get a specific agent"""
    db = get_db(request)
    
    agent = await db.orchestrator_agents.find_one({"id": agent_id}, {"_id": 0})
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    return agent

@router.post("/agents/{agent_id}/toggle")
async def toggle_agent(agent_id: str, request: Request):
    """Toggle agent active status"""
    db = get_db(request)
    
    agent = await db.orchestrator_agents.find_one({"id": agent_id})
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    new_status = "inactive" if agent["status"] == "active" else "active"
    
    await db.orchestrator_agents.update_one(
        {"id": agent_id},
        {"$set": {"status": new_status}}
    )
    
    agent["status"] = new_status
    agent.pop("_id", None)
    return agent

# ============= DASHBOARD STATS =============

@router.get("/stats")
async def get_dashboard_stats(request: Request):
    """Get dashboard statistics"""
    db = get_db(request)
    await init_agents_if_empty(db)
    
    # Count objectives
    total_objectives = await db.orchestrator_objectives.count_documents({})
    active_objectives = await db.orchestrator_objectives.count_documents({"status": "in_progress"})
    completed_objectives = await db.orchestrator_objectives.count_documents({"status": "completed"})
    
    # Count tasks
    total_tasks = await db.orchestrator_tasks.count_documents({})
    completed_tasks = await db.orchestrator_tasks.count_documents({"status": "completed"})
    running_tasks = await db.orchestrator_tasks.count_documents({"status": "running"})
    
    # Get agents
    agents = await db.orchestrator_agents.find({}, {"_id": 0}).to_list(20)
    active_agents = len([a for a in agents if a.get("status") == "active"])
    
    # Calculate total cost
    pipeline = [{"$group": {"_id": None, "total": {"$sum": "$cost_used"}}}]
    cost_result = await db.orchestrator_objectives.aggregate(pipeline).to_list(1)
    total_cost = cost_result[0]["total"] if cost_result else 0
    
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
            "total": len(agents),
            "active": active_agents,
            "list": agents
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
async def get_recent_activity(request: Request):
    """Get recent activity log"""
    db = get_db(request)
    
    activities = []
    
    # Get recent tasks
    tasks = await db.orchestrator_tasks.find({}, {"_id": 0}).sort("created_at", -1).to_list(15)
    for task in tasks:
        activities.append({
            "type": "task",
            "action": task.get("status"),
            "title": task.get("title"),
            "agent": task.get("agent_role"),
            "timestamp": task.get("created_at")
        })
    
    # Get recent objectives
    objectives = await db.orchestrator_objectives.find({}, {"_id": 0}).sort("created_at", -1).to_list(5)
    for obj in objectives:
        activities.append({
            "type": "objective",
            "action": obj.get("status"),
            "title": obj.get("title"),
            "timestamp": obj.get("created_at")
        })
    
    # Sort by timestamp
    activities.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
    
    return activities[:15]

# ============= FILES ENDPOINT =============

@router.get("/objectives/{objective_id}/files")
async def get_generated_files(objective_id: str, request: Request):
    """Get all generated files for an objective"""
    db = get_db(request)
    
    objective = await db.orchestrator_objectives.find_one({"id": objective_id}, {"_id": 0})
    if not objective:
        raise HTTPException(status_code=404, detail="Objective not found")
    
    # Collect files from objective and all tasks
    all_files = objective.get("generated_files", [])
    
    tasks = await db.orchestrator_tasks.find(
        {"objective_id": objective_id, "generated_files": {"$exists": True, "$ne": []}},
        {"_id": 0, "generated_files": 1, "title": 1}
    ).to_list(100)
    
    for task in tasks:
        for f in task.get("generated_files", []):
            f["source_task"] = task.get("title")
            all_files.append(f)
    
    return {"files": all_files, "count": len(all_files)}

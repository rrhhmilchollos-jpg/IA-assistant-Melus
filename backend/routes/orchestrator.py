"""
MelusAI - Multi-Agent Orchestrator Core
Hierarchical Orchestrator with Meta-Planner and Agent Router
"""
import asyncio
import json
import time
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional, Tuple
from enum import Enum
import uuid
import os

from models.orchestrator_models import (
    Objective, ObjectiveCreate, ObjectiveStatus, ObjectiveType,
    Task, TaskCreate, TaskStatus,
    Agent, AgentRole, AgentConfig, ModelProvider,
    PerformanceLog, LoopState, AutonomousLoop,
    PipelineType, Pipeline, PipelineStep
)


class MetaPlanner:
    """
    Interprets global objectives and decides pipeline type.
    Prioritizes resources and creates high-level strategy.
    """
    
    def __init__(self, db):
        self.db = db
        
    async def analyze_objective(self, objective: Objective) -> Dict[str, Any]:
        """Analyze objective and create execution strategy"""
        
        # Determine pipeline type based on objective
        pipeline_type = self._determine_pipeline_type(objective)
        
        # Estimate resource requirements
        resources = self._estimate_resources(objective)
        
        # Create execution plan
        plan = {
            "objective_id": objective.id,
            "pipeline_type": pipeline_type,
            "priority": objective.priority,
            "estimated_cost": resources["estimated_cost"],
            "estimated_time_minutes": resources["estimated_time"],
            "required_agents": resources["required_agents"],
            "phases": self._create_phases(objective, pipeline_type),
            "success_criteria": self._define_success_criteria(objective),
            "fallback_strategy": self._create_fallback_strategy(objective)
        }
        
        return plan
    
    def _determine_pipeline_type(self, objective: Objective) -> PipelineType:
        """Determine the best pipeline type for this objective"""
        type_mapping = {
            ObjectiveType.CONTENT: PipelineType.CONTENT_CREATION,
            ObjectiveType.CODE: PipelineType.CODE_GENERATION,
            ObjectiveType.AUTOMATION: PipelineType.AUTOMATION_SETUP,
            ObjectiveType.RESEARCH: PipelineType.RESEARCH_ANALYSIS,
            ObjectiveType.MIXED: PipelineType.MIXED_WORKFLOW
        }
        return type_mapping.get(objective.type, PipelineType.MIXED_WORKFLOW)
    
    def _estimate_resources(self, objective: Objective) -> Dict[str, Any]:
        """Estimate required resources for objective"""
        # Base estimates by type
        estimates = {
            ObjectiveType.CONTENT: {"cost": 0.5, "time": 10, "agents": [AgentRole.CONTENT, AgentRole.QA]},
            ObjectiveType.CODE: {"cost": 1.0, "time": 30, "agents": [AgentRole.CODE, AgentRole.QA, AgentRole.SECURITY]},
            ObjectiveType.AUTOMATION: {"cost": 0.8, "time": 20, "agents": [AgentRole.AUTOMATION, AgentRole.CODE]},
            ObjectiveType.RESEARCH: {"cost": 0.3, "time": 15, "agents": [AgentRole.RESEARCH, AgentRole.REASONING]},
            ObjectiveType.MIXED: {"cost": 1.5, "time": 45, "agents": [AgentRole.PLANNER, AgentRole.CODE, AgentRole.CONTENT]}
        }
        
        base = estimates.get(objective.type, estimates[ObjectiveType.MIXED])
        
        # Adjust by priority
        priority_multiplier = 1 + (objective.priority - 5) * 0.1
        
        return {
            "estimated_cost": base["cost"] * priority_multiplier,
            "estimated_time": int(base["time"] * priority_multiplier),
            "required_agents": base["agents"]
        }
    
    def _create_phases(self, objective: Objective, pipeline_type: PipelineType) -> List[Dict]:
        """Create execution phases for the objective"""
        phases = [
            {"name": "planning", "description": "Decompose objective into tasks", "agent": AgentRole.PLANNER},
            {"name": "research", "description": "Gather required information", "agent": AgentRole.RESEARCH},
        ]
        
        if pipeline_type == PipelineType.CODE_GENERATION:
            phases.extend([
                {"name": "architecture", "description": "Design system architecture", "agent": AgentRole.REASONING},
                {"name": "implementation", "description": "Write code", "agent": AgentRole.CODE},
                {"name": "testing", "description": "Test and validate", "agent": AgentRole.QA},
                {"name": "security_review", "description": "Security audit", "agent": AgentRole.SECURITY},
            ])
        elif pipeline_type == PipelineType.CONTENT_CREATION:
            phases.extend([
                {"name": "outline", "description": "Create content outline", "agent": AgentRole.CONTENT},
                {"name": "writing", "description": "Write content", "agent": AgentRole.CONTENT},
                {"name": "review", "description": "Quality review", "agent": AgentRole.QA},
                {"name": "optimization", "description": "SEO and optimization", "agent": AgentRole.OPTIMIZATION},
            ])
        elif pipeline_type == PipelineType.AUTOMATION_SETUP:
            phases.extend([
                {"name": "design", "description": "Design automation flow", "agent": AgentRole.AUTOMATION},
                {"name": "implementation", "description": "Implement automation", "agent": AgentRole.CODE},
                {"name": "testing", "description": "Test automation", "agent": AgentRole.QA},
            ])
        
        phases.append({"name": "finalization", "description": "Final review and delivery", "agent": AgentRole.OPTIMIZATION})
        
        return phases
    
    def _define_success_criteria(self, objective: Objective) -> Dict[str, Any]:
        """Define success criteria for the objective"""
        return {
            "min_quality_score": 0.8,
            "max_cost": objective.cost_budget or 10.0,
            "deadline": objective.deadline.isoformat() if objective.deadline else None,
            "required_outputs": self._get_required_outputs(objective.type)
        }
    
    def _get_required_outputs(self, obj_type: ObjectiveType) -> List[str]:
        """Get required outputs based on objective type"""
        outputs = {
            ObjectiveType.CONTENT: ["content", "metadata", "seo_data"],
            ObjectiveType.CODE: ["source_code", "tests", "documentation"],
            ObjectiveType.AUTOMATION: ["workflow_config", "scripts", "schedule"],
            ObjectiveType.RESEARCH: ["report", "data", "insights"],
            ObjectiveType.MIXED: ["deliverables", "documentation"]
        }
        return outputs.get(obj_type, ["output"])
    
    def _create_fallback_strategy(self, objective: Objective) -> Dict[str, Any]:
        """Create fallback strategy in case of failures"""
        return {
            "max_retries": 3,
            "fallback_model": ModelProvider.GPT4_TURBO,
            "reduce_scope_on_failure": True,
            "notify_on_critical_failure": True
        }


class TaskDecomposer:
    """
    Decomposes objectives into executable micro-tasks.
    Creates hierarchical task tree.
    """
    
    def __init__(self, db):
        self.db = db
    
    async def decompose(self, objective: Objective, plan: Dict[str, Any]) -> List[Task]:
        """Decompose objective into tasks based on plan"""
        tasks = []
        task_order = 0
        
        for phase in plan["phases"]:
            task_id = f"task_{uuid.uuid4().hex[:12]}"
            
            task = Task(
                id=task_id,
                objective_id=objective.id,
                parent_task_id=None,
                title=f"{phase['name'].title()} Phase",
                description=phase["description"],
                agent_role=phase["agent"],
                status=TaskStatus.QUEUED,
                priority=objective.priority,
                input_data={
                    "objective_description": objective.description,
                    "phase": phase["name"],
                    "order": task_order
                },
                dependencies=[tasks[-1].id] if tasks else [],
                created_at=datetime.now(timezone.utc)
            )
            
            tasks.append(task)
            task_order += 1
        
        return tasks
    
    async def create_subtasks(self, parent_task: Task, subtask_definitions: List[Dict]) -> List[Task]:
        """Create subtasks for a parent task"""
        subtasks = []
        
        for i, definition in enumerate(subtask_definitions):
            subtask = Task(
                id=f"task_{uuid.uuid4().hex[:12]}",
                objective_id=parent_task.objective_id,
                parent_task_id=parent_task.id,
                title=definition.get("title", f"Subtask {i+1}"),
                description=definition.get("description", ""),
                agent_role=definition.get("agent_role", parent_task.agent_role),
                status=TaskStatus.QUEUED,
                priority=parent_task.priority,
                input_data=definition.get("input_data", {}),
                dependencies=definition.get("dependencies", []),
                created_at=datetime.now(timezone.utc)
            )
            subtasks.append(subtask)
        
        return subtasks


class AgentRouter:
    """
    Routes tasks to optimal agents.
    Controls cost/performance balance.
    """
    
    def __init__(self, db):
        self.db = db
        self.agents: Dict[str, Agent] = {}
        self._initialize_agents()
    
    def _initialize_agents(self):
        """Initialize all available agents"""
        agent_configs = [
            # Cognitive Agents
            {
                "role": AgentRole.PLANNER,
                "name": "Strategic Planner",
                "description": "Divides strategy and creates execution plans",
                "model": ModelProvider.GPT4_TURBO,
                "tools": ["reasoning", "planning"]
            },
            {
                "role": AgentRole.RESEARCH,
                "name": "Research Agent",
                "description": "Web scraping, API calls, trend analysis",
                "model": ModelProvider.GPT4,
                "tools": ["web_scraper", "api_caller", "search"]
            },
            {
                "role": AgentRole.REASONING,
                "name": "Reasoning Agent",
                "description": "Deep analysis, comparisons, architecture decisions",
                "model": ModelProvider.GPT4_TURBO,
                "tools": ["reasoning", "analysis"]
            },
            # Productive Agents
            {
                "role": AgentRole.CONTENT,
                "name": "Content Creator",
                "description": "Blogs, scripts, social posts, SEO",
                "model": ModelProvider.GPT4,
                "tools": ["writing", "seo", "formatting"]
            },
            {
                "role": AgentRole.CODE,
                "name": "Code Agent",
                "description": "Backend, frontend, APIs, tests, refactoring",
                "model": ModelProvider.GPT4_TURBO,
                "tools": ["code_executor", "git_operations", "file_system"]
            },
            {
                "role": AgentRole.AUTOMATION,
                "name": "Automation Agent",
                "description": "Webhooks, integrations, bots, scheduling",
                "model": ModelProvider.GPT4,
                "tools": ["scheduler", "api_caller", "social_media"]
            },
            # Control Agents
            {
                "role": AgentRole.QA,
                "name": "QA Agent",
                "description": "Quality evaluation, coherence checking",
                "model": ModelProvider.GPT4,
                "tools": ["testing", "validation"]
            },
            {
                "role": AgentRole.SECURITY,
                "name": "Security Agent",
                "description": "Vulnerability review, security audit",
                "model": ModelProvider.GPT4,
                "tools": ["security_scan", "code_analysis"]
            },
            {
                "role": AgentRole.OPTIMIZATION,
                "name": "Optimization Agent",
                "description": "Output improvement, performance optimization",
                "model": ModelProvider.GPT4,
                "tools": ["optimization", "benchmarking"]
            },
            {
                "role": AgentRole.COST_CONTROL,
                "name": "Cost Controller",
                "description": "Model usage optimization, budget management",
                "model": ModelProvider.GPT4,
                "tools": ["metrics", "budgeting"]
            },
        ]
        
        for config in agent_configs:
            agent_id = f"agent_{config['role'].value}"
            self.agents[agent_id] = Agent(
                id=agent_id,
                role=config["role"],
                name=config["name"],
                description=config["description"],
                model=config["model"],
                config=AgentConfig(
                    tools_enabled=config["tools"]
                ),
                is_active=True,
                created_at=datetime.now(timezone.utc)
            )
    
    async def route_task(self, task: Task) -> Tuple[Agent, ModelProvider]:
        """Route task to optimal agent and model"""
        
        # Find agents that can handle this role
        suitable_agents = [
            agent for agent in self.agents.values()
            if agent.role == task.agent_role and agent.is_active
        ]
        
        if not suitable_agents:
            # Fallback to a general agent
            suitable_agents = [self.agents.get(f"agent_{AgentRole.REASONING.value}")]
        
        # Select best agent based on reputation and performance
        best_agent = max(suitable_agents, key=lambda a: a.reputation_score * a.success_rate)
        
        # Determine optimal model based on task complexity and budget
        model = await self._select_model(task, best_agent)
        
        return best_agent, model
    
    async def _select_model(self, task: Task, agent: Agent) -> ModelProvider:
        """Select optimal model for task"""
        
        # High priority tasks get better models
        if task.priority >= 8:
            return ModelProvider.GPT4_TURBO
        
        # Code tasks need more capable models
        if task.agent_role == AgentRole.CODE:
            return ModelProvider.GPT4_TURBO
        
        # Default to agent's configured model
        return agent.model
    
    def get_agent(self, agent_id: str) -> Optional[Agent]:
        """Get agent by ID"""
        return self.agents.get(agent_id)
    
    def get_agents_by_role(self, role: AgentRole) -> List[Agent]:
        """Get all agents with a specific role"""
        return [a for a in self.agents.values() if a.role == role]
    
    async def update_agent_metrics(self, agent_id: str, task_result: Dict[str, Any]):
        """Update agent metrics after task completion"""
        agent = self.agents.get(agent_id)
        if not agent:
            return
        
        agent.total_tasks += 1
        
        if task_result.get("success"):
            agent.successful_tasks += 1
            # Increase reputation for success
            agent.reputation_score = min(100, agent.reputation_score + 0.5)
        else:
            agent.failed_tasks += 1
            # Decrease reputation for failure
            agent.reputation_score = max(0, agent.reputation_score - 2)
        
        agent.success_rate = agent.successful_tasks / agent.total_tasks if agent.total_tasks > 0 else 1.0
        agent.last_active_at = datetime.now(timezone.utc)
        
        # Update average cost and latency
        if "cost" in task_result:
            agent.avg_cost = (agent.avg_cost * (agent.total_tasks - 1) + task_result["cost"]) / agent.total_tasks
        if "latency_ms" in task_result:
            agent.avg_latency_ms = (agent.avg_latency_ms * (agent.total_tasks - 1) + task_result["latency_ms"]) / agent.total_tasks


class Orchestrator:
    """
    Main orchestrator that coordinates all components.
    Manages the autonomous execution loop.
    """
    
    def __init__(self, db):
        self.db = db
        self.meta_planner = MetaPlanner(db)
        self.task_decomposer = TaskDecomposer(db)
        self.agent_router = AgentRouter(db)
        self.active_loops: Dict[str, AutonomousLoop] = {}
        self.is_running = False
    
    async def create_objective(self, user_id: str, objective_data: ObjectiveCreate) -> Objective:
        """Create a new objective and start processing"""
        
        objective = Objective(
            id=f"obj_{uuid.uuid4().hex[:12]}",
            user_id=user_id,
            title=objective_data.title,
            description=objective_data.description,
            type=objective_data.type,
            priority=objective_data.priority,
            status=ObjectiveStatus.PENDING,
            cost_budget=objective_data.cost_budget,
            deadline=objective_data.deadline,
            auto_mode=objective_data.auto_mode,
            config=objective_data.config,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        
        # Save to database
        await self.db.objectives.insert_one(objective.dict())
        
        # If auto mode, start processing
        if objective.auto_mode:
            asyncio.create_task(self.process_objective(objective))
        
        return objective
    
    async def process_objective(self, objective: Objective):
        """Process an objective through the full pipeline"""
        
        try:
            # Update status
            objective.status = ObjectiveStatus.PLANNING
            await self._update_objective(objective)
            
            # Create plan
            plan = await self.meta_planner.analyze_objective(objective)
            
            # Decompose into tasks
            tasks = await self.task_decomposer.decompose(objective, plan)
            
            # Save tasks
            for task in tasks:
                await self.db.tasks.insert_one(task.dict())
            
            # Start autonomous loop
            loop = AutonomousLoop(
                id=f"loop_{uuid.uuid4().hex[:12]}",
                objective_id=objective.id,
                current_state=LoopState.EXECUTING,
                auto_improve=objective.auto_mode,
                created_at=datetime.now(timezone.utc)
            )
            
            self.active_loops[objective.id] = loop
            await self.db.loops.insert_one(loop.dict())
            
            # Execute tasks
            objective.status = ObjectiveStatus.IN_PROGRESS
            await self._update_objective(objective)
            
            await self._execute_tasks(objective, tasks, loop)
            
            # Evaluate results
            loop.current_state = LoopState.EVALUATING
            await self._evaluate_results(objective, loop)
            
            # Improve if needed
            if loop.auto_improve:
                loop.current_state = LoopState.IMPROVING
                await self._improve_results(objective, loop)
            
            # Finalize
            objective.status = ObjectiveStatus.COMPLETED
            objective.completed_at = datetime.now(timezone.utc)
            await self._update_objective(objective)
            
        except Exception as e:
            objective.status = ObjectiveStatus.FAILED
            objective.result = {"error": str(e)}
            await self._update_objective(objective)
    
    async def _execute_tasks(self, objective: Objective, tasks: List[Task], loop: AutonomousLoop):
        """Execute all tasks for an objective"""
        
        for task in tasks:
            if not self.active_loops.get(objective.id, {}).is_active:
                break
            
            # Route to agent
            agent, model = await self.agent_router.route_task(task)
            
            # Update task
            task.agent_id = agent.id
            task.model_used = model
            task.status = TaskStatus.RUNNING
            task.started_at = datetime.now(timezone.utc)
            await self.db.tasks.update_one({"id": task.id}, {"$set": task.dict()})
            
            # Execute task (simplified - would call actual LLM here)
            start_time = time.time()
            result = await self._execute_single_task(task, agent, model)
            execution_time = int((time.time() - start_time) * 1000)
            
            # Update task with results
            task.status = TaskStatus.COMPLETED if result.get("success") else TaskStatus.FAILED
            task.output_data = result.get("output", {})
            task.execution_time_ms = execution_time
            task.tokens_used = result.get("tokens", 0)
            task.cost = result.get("cost", 0)
            task.result_score = result.get("quality_score")
            task.completed_at = datetime.now(timezone.utc)
            
            await self.db.tasks.update_one({"id": task.id}, {"$set": task.dict()})
            
            # Update agent metrics
            await self.agent_router.update_agent_metrics(agent.id, {
                "success": result.get("success"),
                "cost": task.cost,
                "latency_ms": execution_time
            })
            
            # Log performance
            log = PerformanceLog(
                id=f"log_{uuid.uuid4().hex[:12]}",
                task_id=task.id,
                agent_id=agent.id,
                objective_id=objective.id,
                model_used=model,
                tokens_input=result.get("tokens_input", 0),
                tokens_output=result.get("tokens_output", 0),
                latency_ms=execution_time,
                cost=task.cost,
                quality_score=task.result_score,
                success=result.get("success", False),
                timestamp=datetime.now(timezone.utc)
            )
            await self.db.performance_logs.insert_one(log.dict())
            
            # Update objective cost
            objective.cost_used += task.cost
            await self._update_objective(objective)
    
    async def _execute_single_task(self, task: Task, agent: Agent, model: ModelProvider) -> Dict[str, Any]:
        """Execute a single task with the assigned agent"""
        # This would be the actual LLM call
        # Simplified for now
        return {
            "success": True,
            "output": {"result": f"Task {task.title} completed"},
            "tokens": 500,
            "tokens_input": 200,
            "tokens_output": 300,
            "cost": 0.01,
            "quality_score": 0.9
        }
    
    async def _evaluate_results(self, objective: Objective, loop: AutonomousLoop):
        """Evaluate the results of all tasks"""
        tasks = await self.db.tasks.find({"objective_id": objective.id}).to_list(100)
        
        if not tasks:
            return
        
        # Calculate average quality score
        scores = [t.get("result_score", 0) for t in tasks if t.get("result_score")]
        avg_score = sum(scores) / len(scores) if scores else 0
        
        # Update objective
        objective.quality_score = avg_score
        
        # Update loop metrics
        loop.metrics["avg_quality_score"] = avg_score
        loop.metrics["total_tasks"] = len(tasks)
        loop.metrics["successful_tasks"] = sum(1 for t in tasks if t.get("status") == TaskStatus.COMPLETED.value)
        
        await self._update_objective(objective)
        await self.db.loops.update_one({"id": loop.id}, {"$set": loop.dict()})
    
    async def _improve_results(self, objective: Objective, loop: AutonomousLoop):
        """Attempt to improve results if quality is below threshold"""
        if objective.quality_score and objective.quality_score >= 0.8:
            return
        
        loop.iteration += 1
        
        if loop.iteration >= loop.max_iterations:
            return
        
        # Would trigger improvement tasks here
        loop.improvements_made.append(f"Iteration {loop.iteration}: Quality improvement attempted")
        
        await self.db.loops.update_one({"id": loop.id}, {"$set": loop.dict()})
    
    async def _update_objective(self, objective: Objective):
        """Update objective in database"""
        objective.updated_at = datetime.now(timezone.utc)
        await self.db.objectives.update_one(
            {"id": objective.id},
            {"$set": objective.dict()}
        )
    
    async def pause_objective(self, objective_id: str):
        """Pause an objective"""
        if objective_id in self.active_loops:
            self.active_loops[objective_id].is_active = False
        
        await self.db.objectives.update_one(
            {"id": objective_id},
            {"$set": {"status": ObjectiveStatus.PAUSED.value}}
        )
    
    async def resume_objective(self, objective_id: str):
        """Resume a paused objective"""
        objective = await self.db.objectives.find_one({"id": objective_id})
        if objective:
            objective = Objective(**objective)
            asyncio.create_task(self.process_objective(objective))
    
    def get_all_agents(self) -> List[Agent]:
        """Get all registered agents"""
        return list(self.agent_router.agents.values())
    
    async def get_objective_status(self, objective_id: str) -> Dict[str, Any]:
        """Get detailed status of an objective"""
        objective = await self.db.objectives.find_one({"id": objective_id})
        tasks = await self.db.tasks.find({"objective_id": objective_id}).to_list(100)
        loop = self.active_loops.get(objective_id)
        
        return {
            "objective": objective,
            "tasks": tasks,
            "loop": loop.dict() if loop else None,
            "agents_used": list(set(t.get("agent_id") for t in tasks if t.get("agent_id")))
        }

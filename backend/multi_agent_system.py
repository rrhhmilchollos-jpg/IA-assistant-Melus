"""
MelusAI Multi-Agent System
Sistema de 6 agentes especializados con orquestador inteligente
"""
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import logging
import asyncio
import json
from utils import generate_id, utc_now

logger = logging.getLogger(__name__)


class AgentType(str, Enum):
    PLANNER = "planner"
    RESEARCHER = "researcher"
    DEVELOPER = "developer"
    QA = "qa"
    OPTIMIZER = "optimizer"
    COST_CONTROLLER = "cost_controller"


class AgentStatus(str, Enum):
    IDLE = "idle"
    WORKING = "working"
    COMPLETED = "completed"
    ERROR = "error"
    WAITING = "waiting"


class TaskPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class AgentMessage:
    """Message between agents"""
    id: str
    from_agent: AgentType
    to_agent: Optional[AgentType]  # None = broadcast
    content: str
    data: Dict = field(default_factory=dict)
    timestamp: datetime = field(default_factory=utc_now)
    
    def to_dict(self):
        return {
            "id": self.id,
            "from_agent": self.from_agent.value,
            "to_agent": self.to_agent.value if self.to_agent else None,
            "content": self.content,
            "data": self.data,
            "timestamp": self.timestamp.isoformat()
        }


@dataclass
class AgentTask:
    """Task assigned to an agent"""
    id: str
    agent_type: AgentType
    description: str
    priority: TaskPriority = TaskPriority.MEDIUM
    input_data: Dict = field(default_factory=dict)
    output_data: Dict = field(default_factory=dict)
    status: AgentStatus = AgentStatus.IDLE
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error: Optional[str] = None
    
    def to_dict(self):
        return {
            "id": self.id,
            "agent_type": self.agent_type.value,
            "description": self.description,
            "priority": self.priority.value,
            "input_data": self.input_data,
            "output_data": self.output_data,
            "status": self.status.value,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "error": self.error
        }


class BaseAgent:
    """Base class for all agents"""
    
    def __init__(self, agent_type: AgentType, orchestrator: 'Orchestrator'):
        self.agent_type = agent_type
        self.orchestrator = orchestrator
        self.status = AgentStatus.IDLE
        self.current_task: Optional[AgentTask] = None
        self.history: List[AgentTask] = []
        
    @property
    def name(self) -> str:
        return self.agent_type.value.replace("_", " ").title()
    
    @property
    def description(self) -> str:
        descriptions = {
            AgentType.PLANNER: "Analyzes requirements and creates project plans",
            AgentType.RESEARCHER: "Researches best practices and technologies",
            AgentType.DEVELOPER: "Writes and generates code",
            AgentType.QA: "Tests and validates code quality",
            AgentType.OPTIMIZER: "Optimizes performance and code quality",
            AgentType.COST_CONTROLLER: "Manages costs and resource usage"
        }
        return descriptions.get(self.agent_type, "")
    
    async def execute(self, task: AgentTask) -> Dict:
        """Execute a task - to be overridden by subclasses"""
        raise NotImplementedError
    
    async def send_message(self, to_agent: Optional[AgentType], content: str, data: Dict = None):
        """Send message to another agent or broadcast"""
        message = AgentMessage(
            id=generate_id("msg"),
            from_agent=self.agent_type,
            to_agent=to_agent,
            content=content,
            data=data or {}
        )
        await self.orchestrator.route_message(message)
    
    async def receive_message(self, message: AgentMessage):
        """Receive and process a message"""
        logger.info(f"{self.name} received message: {message.content}")
    
    def get_status(self) -> Dict:
        return {
            "agent_type": self.agent_type.value,
            "name": self.name,
            "description": self.description,
            "status": self.status.value,
            "current_task": self.current_task.to_dict() if self.current_task else None,
            "tasks_completed": len(self.history)
        }


class PlannerAgent(BaseAgent):
    """Plans project structure and requirements"""
    
    def __init__(self, orchestrator: 'Orchestrator'):
        super().__init__(AgentType.PLANNER, orchestrator)
    
    async def execute(self, task: AgentTask) -> Dict:
        """Analyze requirements and create project plan"""
        self.status = AgentStatus.WORKING
        self.current_task = task
        task.status = AgentStatus.WORKING
        task.started_at = utc_now()
        
        try:
            prompt = task.input_data.get("prompt", "")
            
            # Generate project plan using LLM
            plan = await self._generate_plan(prompt)
            
            task.output_data = plan
            task.status = AgentStatus.COMPLETED
            task.completed_at = utc_now()
            
            # Notify researcher to start researching
            await self.send_message(
                AgentType.RESEARCHER,
                "Plan ready, start researching technologies",
                {"plan": plan}
            )
            
            return plan
            
        except Exception as e:
            task.status = AgentStatus.ERROR
            task.error = str(e)
            logger.error(f"Planner error: {e}")
            raise
        finally:
            self.status = AgentStatus.IDLE
            self.current_task = None
            self.history.append(task)
    
    async def _generate_plan(self, prompt: str) -> Dict:
        """Generate project plan from prompt"""
        # This will use the LLM
        return {
            "project_name": f"Project_{generate_id('proj')[:8]}",
            "description": prompt,
            "type": "web_app",
            "stack": {
                "frontend": "React + TailwindCSS",
                "backend": "FastAPI",
                "database": "MongoDB",
                "auth": "JWT"
            },
            "features": [],
            "pages": [],
            "apis": [],
            "estimated_complexity": "medium",
            "estimated_files": 10
        }


class ResearcherAgent(BaseAgent):
    """Researches best practices and technologies"""
    
    def __init__(self, orchestrator: 'Orchestrator'):
        super().__init__(AgentType.RESEARCHER, orchestrator)
    
    async def execute(self, task: AgentTask) -> Dict:
        """Research technologies and best practices"""
        self.status = AgentStatus.WORKING
        self.current_task = task
        task.status = AgentStatus.WORKING
        task.started_at = utc_now()
        
        try:
            plan = task.input_data.get("plan", {})
            
            research = await self._research_stack(plan)
            
            task.output_data = research
            task.status = AgentStatus.COMPLETED
            task.completed_at = utc_now()
            
            # Notify developer to start coding
            await self.send_message(
                AgentType.DEVELOPER,
                "Research complete, start development",
                {"plan": plan, "research": research}
            )
            
            return research
            
        except Exception as e:
            task.status = AgentStatus.ERROR
            task.error = str(e)
            raise
        finally:
            self.status = AgentStatus.IDLE
            self.current_task = None
            self.history.append(task)
    
    async def _research_stack(self, plan: Dict) -> Dict:
        """Research best practices for the stack"""
        return {
            "recommendations": [],
            "libraries": [],
            "patterns": [],
            "security_considerations": [],
            "performance_tips": []
        }


class DeveloperAgent(BaseAgent):
    """Generates code"""
    
    def __init__(self, orchestrator: 'Orchestrator'):
        super().__init__(AgentType.DEVELOPER, orchestrator)
    
    async def execute(self, task: AgentTask) -> Dict:
        """Generate code based on plan and research"""
        self.status = AgentStatus.WORKING
        self.current_task = task
        task.status = AgentStatus.WORKING
        task.started_at = utc_now()
        
        try:
            plan = task.input_data.get("plan", {})
            research = task.input_data.get("research", {})
            
            code = await self._generate_code(plan, research)
            
            task.output_data = code
            task.status = AgentStatus.COMPLETED
            task.completed_at = utc_now()
            
            # Notify QA to start testing
            await self.send_message(
                AgentType.QA,
                "Code ready for review",
                {"code": code}
            )
            
            return code
            
        except Exception as e:
            task.status = AgentStatus.ERROR
            task.error = str(e)
            raise
        finally:
            self.status = AgentStatus.IDLE
            self.current_task = None
            self.history.append(task)
    
    async def _generate_code(self, plan: Dict, research: Dict) -> Dict:
        """Generate code files"""
        return {
            "files": [],
            "dependencies": {},
            "scripts": {}
        }


class QAAgent(BaseAgent):
    """Tests and validates code"""
    
    def __init__(self, orchestrator: 'Orchestrator'):
        super().__init__(AgentType.QA, orchestrator)
    
    async def execute(self, task: AgentTask) -> Dict:
        """Test and validate code"""
        self.status = AgentStatus.WORKING
        self.current_task = task
        task.status = AgentStatus.WORKING
        task.started_at = utc_now()
        
        try:
            code = task.input_data.get("code", {})
            
            results = await self._run_tests(code)
            
            task.output_data = results
            task.status = AgentStatus.COMPLETED
            task.completed_at = utc_now()
            
            if results.get("passed"):
                # Notify optimizer
                await self.send_message(
                    AgentType.OPTIMIZER,
                    "Tests passed, ready for optimization",
                    {"code": code, "test_results": results}
                )
            else:
                # Send back to developer
                await self.send_message(
                    AgentType.DEVELOPER,
                    "Tests failed, fix required",
                    {"code": code, "test_results": results}
                )
            
            return results
            
        except Exception as e:
            task.status = AgentStatus.ERROR
            task.error = str(e)
            raise
        finally:
            self.status = AgentStatus.IDLE
            self.current_task = None
            self.history.append(task)
    
    async def _run_tests(self, code: Dict) -> Dict:
        """Run tests on code"""
        return {
            "passed": True,
            "tests_run": 0,
            "tests_passed": 0,
            "tests_failed": 0,
            "coverage": 0,
            "issues": []
        }


class OptimizerAgent(BaseAgent):
    """Optimizes code performance and quality"""
    
    def __init__(self, orchestrator: 'Orchestrator'):
        super().__init__(AgentType.OPTIMIZER, orchestrator)
    
    async def execute(self, task: AgentTask) -> Dict:
        """Optimize code"""
        self.status = AgentStatus.WORKING
        self.current_task = task
        task.status = AgentStatus.WORKING
        task.started_at = utc_now()
        
        try:
            code = task.input_data.get("code", {})
            
            optimized = await self._optimize_code(code)
            
            task.output_data = optimized
            task.status = AgentStatus.COMPLETED
            task.completed_at = utc_now()
            
            return optimized
            
        except Exception as e:
            task.status = AgentStatus.ERROR
            task.error = str(e)
            raise
        finally:
            self.status = AgentStatus.IDLE
            self.current_task = None
            self.history.append(task)
    
    async def _optimize_code(self, code: Dict) -> Dict:
        """Optimize code for performance"""
        return {
            "optimized_files": [],
            "improvements": [],
            "metrics": {
                "bundle_size_reduction": "0%",
                "performance_improvement": "0%"
            }
        }


class CostControllerAgent(BaseAgent):
    """Manages costs and resource usage"""
    
    def __init__(self, orchestrator: 'Orchestrator'):
        super().__init__(AgentType.COST_CONTROLLER, orchestrator)
        self.token_usage = 0
        self.cost_usd = 0.0
    
    async def execute(self, task: AgentTask) -> Dict:
        """Monitor and control costs"""
        self.status = AgentStatus.WORKING
        self.current_task = task
        task.status = AgentStatus.WORKING
        task.started_at = utc_now()
        
        try:
            operation = task.input_data.get("operation", "check")
            
            if operation == "check":
                result = self._check_budget()
            elif operation == "track":
                result = self._track_usage(task.input_data)
            else:
                result = {"status": "unknown_operation"}
            
            task.output_data = result
            task.status = AgentStatus.COMPLETED
            task.completed_at = utc_now()
            
            return result
            
        except Exception as e:
            task.status = AgentStatus.ERROR
            task.error = str(e)
            raise
        finally:
            self.status = AgentStatus.IDLE
            self.current_task = None
            self.history.append(task)
    
    def _check_budget(self) -> Dict:
        """Check current budget status"""
        return {
            "token_usage": self.token_usage,
            "cost_usd": self.cost_usd,
            "budget_remaining": 100.0 - self.cost_usd,
            "status": "ok" if self.cost_usd < 100 else "exceeded"
        }
    
    def _track_usage(self, data: Dict) -> Dict:
        """Track token usage"""
        tokens = data.get("tokens", 0)
        cost = data.get("cost", 0.0)
        self.token_usage += tokens
        self.cost_usd += cost
        return self._check_budget()
    
    def get_usage_stats(self) -> Dict:
        return {
            "total_tokens": self.token_usage,
            "total_cost_usd": self.cost_usd,
            "average_cost_per_request": self.cost_usd / max(1, len(self.history))
        }


class Orchestrator:
    """
    Central orchestrator that coordinates all agents
    """
    
    def __init__(self):
        self.agents: Dict[AgentType, BaseAgent] = {}
        self.message_queue: List[AgentMessage] = []
        self.task_queue: List[AgentTask] = []
        self.completed_tasks: List[AgentTask] = []
        self.current_project_id: Optional[str] = None
        self.callbacks: List[callable] = []
        
        # Initialize agents
        self._init_agents()
    
    def _init_agents(self):
        """Initialize all agents"""
        self.agents[AgentType.PLANNER] = PlannerAgent(self)
        self.agents[AgentType.RESEARCHER] = ResearcherAgent(self)
        self.agents[AgentType.DEVELOPER] = DeveloperAgent(self)
        self.agents[AgentType.QA] = QAAgent(self)
        self.agents[AgentType.OPTIMIZER] = OptimizerAgent(self)
        self.agents[AgentType.COST_CONTROLLER] = CostControllerAgent(self)
    
    def on_update(self, callback: callable):
        """Register callback for updates"""
        self.callbacks.append(callback)
    
    async def notify_update(self, event_type: str, data: Dict):
        """Notify all callbacks of an update"""
        for callback in self.callbacks:
            try:
                await callback(event_type, data)
            except Exception as e:
                logger.error(f"Callback error: {e}")
    
    async def route_message(self, message: AgentMessage):
        """Route message to appropriate agent(s)"""
        self.message_queue.append(message)
        
        await self.notify_update("message", message.to_dict())
        
        if message.to_agent:
            # Direct message
            agent = self.agents.get(message.to_agent)
            if agent:
                await agent.receive_message(message)
        else:
            # Broadcast
            for agent in self.agents.values():
                if agent.agent_type != message.from_agent:
                    await agent.receive_message(message)
    
    async def create_task(
        self, 
        agent_type: AgentType, 
        description: str,
        input_data: Dict = None,
        priority: TaskPriority = TaskPriority.MEDIUM
    ) -> AgentTask:
        """Create and queue a new task"""
        task = AgentTask(
            id=generate_id("task"),
            agent_type=agent_type,
            description=description,
            priority=priority,
            input_data=input_data or {}
        )
        self.task_queue.append(task)
        
        await self.notify_update("task_created", task.to_dict())
        
        return task
    
    async def execute_task(self, task: AgentTask) -> Dict:
        """Execute a task with the appropriate agent"""
        agent = self.agents.get(task.agent_type)
        if not agent:
            raise ValueError(f"Unknown agent type: {task.agent_type}")
        
        await self.notify_update("task_started", {
            "task": task.to_dict(),
            "agent": agent.get_status()
        })
        
        try:
            result = await agent.execute(task)
            
            await self.notify_update("task_completed", {
                "task": task.to_dict(),
                "result": result
            })
            
            self.completed_tasks.append(task)
            return result
            
        except Exception as e:
            await self.notify_update("task_error", {
                "task": task.to_dict(),
                "error": str(e)
            })
            raise
    
    async def run_pipeline(self, prompt: str, project_id: str) -> Dict:
        """Run the full agent pipeline for a project"""
        self.current_project_id = project_id
        
        await self.notify_update("pipeline_started", {
            "project_id": project_id,
            "prompt": prompt
        })
        
        try:
            # Phase 1: Planning
            plan_task = await self.create_task(
                AgentType.PLANNER,
                "Create project plan",
                {"prompt": prompt},
                TaskPriority.HIGH
            )
            plan = await self.execute_task(plan_task)
            
            # Phase 2: Research
            research_task = await self.create_task(
                AgentType.RESEARCHER,
                "Research technologies and best practices",
                {"plan": plan},
                TaskPriority.HIGH
            )
            research = await self.execute_task(research_task)
            
            # Phase 3: Development
            dev_task = await self.create_task(
                AgentType.DEVELOPER,
                "Generate code",
                {"plan": plan, "research": research},
                TaskPriority.HIGH
            )
            code = await self.execute_task(dev_task)
            
            # Phase 4: QA
            qa_task = await self.create_task(
                AgentType.QA,
                "Test and validate code",
                {"code": code},
                TaskPriority.MEDIUM
            )
            test_results = await self.execute_task(qa_task)
            
            # Phase 5: Optimization
            if test_results.get("passed"):
                opt_task = await self.create_task(
                    AgentType.OPTIMIZER,
                    "Optimize code",
                    {"code": code},
                    TaskPriority.LOW
                )
                optimized = await self.execute_task(opt_task)
            else:
                optimized = code
            
            # Track costs
            cost_task = await self.create_task(
                AgentType.COST_CONTROLLER,
                "Track usage",
                {"operation": "check"},
                TaskPriority.LOW
            )
            costs = await self.execute_task(cost_task)
            
            result = {
                "project_id": project_id,
                "plan": plan,
                "research": research,
                "code": optimized,
                "test_results": test_results,
                "costs": costs,
                "status": "completed"
            }
            
            await self.notify_update("pipeline_completed", result)
            
            return result
            
        except Exception as e:
            await self.notify_update("pipeline_error", {
                "project_id": project_id,
                "error": str(e)
            })
            raise
        finally:
            self.current_project_id = None
    
    def get_status(self) -> Dict:
        """Get current orchestrator status"""
        return {
            "agents": {
                agent_type.value: agent.get_status() 
                for agent_type, agent in self.agents.items()
            },
            "current_project": self.current_project_id,
            "pending_tasks": len(self.task_queue),
            "completed_tasks": len(self.completed_tasks),
            "messages_processed": len(self.message_queue)
        }
    
    def get_agent(self, agent_type: AgentType) -> BaseAgent:
        """Get a specific agent"""
        return self.agents.get(agent_type)


# Global orchestrator instance
orchestrator = Orchestrator()


def get_orchestrator() -> Orchestrator:
    """Get the global orchestrator instance"""
    return orchestrator

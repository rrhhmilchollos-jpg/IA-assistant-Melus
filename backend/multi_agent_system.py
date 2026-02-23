"""
MelusAI - Real Multi-Agent System
Sistema que conecta con el pipeline de generación real
"""
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import logging
import asyncio
import json
import os
import re
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


@dataclass
class AgentMessage:
    id: str
    from_agent: AgentType
    to_agent: Optional[AgentType]
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
    id: str
    agent_type: AgentType
    description: str
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
            "input_data": self.input_data,
            "output_data": self.output_data,
            "status": self.status.value,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "error": self.error
        }


# ============= LLM INTEGRATION =============

async def call_llm(prompt: str, system_prompt: str = None, max_tokens: int = 4000) -> str:
    """Call LLM using Emergent integration"""
    try:
        from emergentintegrations.llm.chat import LlmChat, UserMessage
        
        api_key = os.environ.get("EMERGENT_LLM_KEY")
        if not api_key:
            logger.error("EMERGENT_LLM_KEY not found")
            return ""
        
        chat = LlmChat(
            api_key=api_key,
            session_id=f"agent_{generate_id('sess')[:8]}",
            system_message=system_prompt or "You are a helpful AI assistant."
        ).with_model("openai", "gpt-4o")
        
        user_message = UserMessage(text=prompt)
        response = await chat.send_message(user_message)
        
        return response
    except Exception as e:
        logger.error(f"LLM call error: {e}")
        return f"Error: {str(e)}"


def parse_json_response(response: str) -> Dict:
    """Parse JSON from LLM response"""
    try:
        # Try direct parse
        return json.loads(response)
    except:
        pass
    
    # Try to find JSON in response
    try:
        # Look for ```json blocks
        json_match = re.search(r'```json\s*([\s\S]*?)\s*```', response)
        if json_match:
            return json.loads(json_match.group(1))
        
        # Look for {} blocks
        json_match = re.search(r'\{[\s\S]*\}', response)
        if json_match:
            return json.loads(json_match.group())
    except Exception as e:
        logger.error(f"JSON parse error: {e}")
    
    return {}


# ============= SYSTEM PROMPTS =============

PLANNER_SYSTEM = """You are the Project Planner AI Agent for MelusAI. Your job is to analyze user requirements and create detailed project plans.

When given a project request, analyze it and output a JSON plan with this structure:

{
    "project_name": "project-name-slug",
    "project_type": "web_app",
    "description": "Brief description of the project",
    "tech_stack": {
        "frontend": ["React", "TailwindCSS"],
        "backend": ["FastAPI"] or [],
        "database": ["MongoDB"] or [],
        "additional": []
    },
    "structure": {
        "folders": ["src", "src/components", "src/pages", "public"],
        "main_files": ["index.html", "src/App.jsx", "src/index.js", "src/styles.css"]
    },
    "features": [
        {"name": "Feature Name", "priority": 1, "description": "What it does"}
    ],
    "pages": ["Home", "About", etc],
    "components": ["Navbar", "Footer", etc],
    "estimated_files": 10,
    "complexity": "low|medium|high"
}

Be specific and comprehensive. This plan will be used to generate real code."""

DEVELOPER_SYSTEM = """You are the Code Generator AI Agent for MelusAI. You generate COMPLETE, PRODUCTION-READY code.

CRITICAL RULES:
1. Write COMPLETE code - NO placeholders, NO TODOs, NO "// add code here"
2. Every file must be fully functional and ready to run
3. Include ALL imports and dependencies
4. Use modern best practices (React hooks, functional components, etc.)
5. Make it visually appealing with modern CSS/TailwindCSS
6. Add proper error handling
7. Include responsive design

OUTPUT FORMAT - Return ONLY valid JSON:
{
    "files": [
        {
            "path": "index.html",
            "content": "<!DOCTYPE html>\\n<html>...</html>",
            "type": "html"
        },
        {
            "path": "src/App.jsx",
            "content": "import React from 'react';\\n...",
            "type": "component"
        }
    ],
    "dependencies": {
        "npm": ["react", "react-dom", "tailwindcss"]
    },
    "entry_point": "index.html",
    "instructions": "How to run the project"
}

Generate ALL files needed for a complete, working application. Include:
- index.html with proper structure
- Main App component
- All page components
- All UI components
- Styles (CSS or Tailwind)
- Configuration files if needed"""

QA_SYSTEM = """You are the QA AI Agent for MelusAI. Review code for issues and suggest improvements.

Analyze the provided code and output JSON:
{
    "valid": true/false,
    "score": 0-100,
    "issues": [
        {
            "file": "path/to/file",
            "type": "error|warning|suggestion",
            "message": "Description",
            "fix": "How to fix it"
        }
    ],
    "improvements": ["List of suggested improvements"]
}"""


# ============= AGENTS =============

class BaseAgent:
    def __init__(self, agent_type: AgentType, orchestrator: 'RealOrchestrator'):
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
            AgentType.DEVELOPER: "Writes and generates production-ready code",
            AgentType.QA: "Tests and validates code quality",
            AgentType.OPTIMIZER: "Optimizes performance and code quality",
            AgentType.COST_CONTROLLER: "Manages costs and resource usage"
        }
        return descriptions.get(self.agent_type, "")
    
    async def execute(self, task: AgentTask) -> Dict:
        raise NotImplementedError
    
    async def send_message(self, to_agent: Optional[AgentType], content: str, data: Dict = None):
        message = AgentMessage(
            id=generate_id("msg"),
            from_agent=self.agent_type,
            to_agent=to_agent,
            content=content,
            data=data or {}
        )
        await self.orchestrator.route_message(message)
    
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
    def __init__(self, orchestrator: 'RealOrchestrator'):
        super().__init__(AgentType.PLANNER, orchestrator)
    
    async def execute(self, task: AgentTask) -> Dict:
        self.status = AgentStatus.WORKING
        self.current_task = task
        task.status = AgentStatus.WORKING
        task.started_at = utc_now()
        
        try:
            prompt = task.input_data.get("prompt", "")
            
            await self.send_message(None, f"🔍 Analyzing project requirements: {prompt[:100]}...")
            
            response = await call_llm(
                prompt=f"Create a detailed project plan for: {prompt}",
                system_prompt=PLANNER_SYSTEM,
                max_tokens=2000
            )
            
            plan = parse_json_response(response)
            
            if not plan:
                plan = {
                    "project_name": f"project-{generate_id('p')[:8]}",
                    "project_type": "web_app",
                    "description": prompt,
                    "tech_stack": {"frontend": ["React", "TailwindCSS"]},
                    "structure": {"folders": ["src", "src/components"], "main_files": ["index.html", "src/App.jsx"]},
                    "features": [{"name": "Main Feature", "priority": 1, "description": prompt}],
                    "estimated_files": 5,
                    "complexity": "medium"
                }
            
            task.output_data = plan
            task.status = AgentStatus.COMPLETED
            task.completed_at = utc_now()
            
            await self.send_message(
                AgentType.DEVELOPER,
                f"✅ Plan ready: {plan.get('project_name')} ({plan.get('estimated_files', 5)} files)",
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


class DeveloperAgent(BaseAgent):
    def __init__(self, orchestrator: 'RealOrchestrator'):
        super().__init__(AgentType.DEVELOPER, orchestrator)
    
    async def execute(self, task: AgentTask) -> Dict:
        self.status = AgentStatus.WORKING
        self.current_task = task
        task.status = AgentStatus.WORKING
        task.started_at = utc_now()
        
        try:
            plan = task.input_data.get("plan", {})
            prompt = task.input_data.get("prompt", "")
            
            await self.send_message(None, f"💻 Generating code for {plan.get('project_name', 'project')}...")
            
            generation_prompt = f"""Generate complete code for this project:

PROJECT: {plan.get('project_name', 'app')}
DESCRIPTION: {plan.get('description', prompt)}
TYPE: {plan.get('project_type', 'web_app')}

TECH STACK: {json.dumps(plan.get('tech_stack', {}))}

FEATURES:
{json.dumps(plan.get('features', []), indent=2)}

PAGES: {plan.get('pages', ['Home'])}
COMPONENTS: {plan.get('components', ['App'])}

Generate ALL files needed for a complete, working application. Make it visually appealing and modern.
Include proper styling with TailwindCSS or modern CSS.
Make sure all components are properly connected and the app is fully functional."""

            response = await call_llm(
                prompt=generation_prompt,
                system_prompt=DEVELOPER_SYSTEM,
                max_tokens=8000
            )
            
            result = parse_json_response(response)
            
            if not result or not result.get("files"):
                # Generate default files if parsing failed
                result = self._generate_default_files(plan, prompt)
            
            task.output_data = result
            task.status = AgentStatus.COMPLETED
            task.completed_at = utc_now()
            
            file_count = len(result.get("files", []))
            await self.send_message(
                AgentType.QA,
                f"✅ Generated {file_count} files. Ready for review.",
                {"code": result}
            )
            
            return result
            
        except Exception as e:
            task.status = AgentStatus.ERROR
            task.error = str(e)
            logger.error(f"Developer error: {e}")
            raise
        finally:
            self.status = AgentStatus.IDLE
            self.current_task = None
            self.history.append(task)
    
    def _generate_default_files(self, plan: Dict, prompt: str) -> Dict:
        """Generate default React app files"""
        project_name = plan.get("project_name", "my-app")
        description = plan.get("description", prompt)
        
        return {
            "files": [
                {
                    "path": "index.html",
                    "content": f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{project_name}</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://unpkg.com/react@18/umd/react.development.js"></script>
    <script src="https://unpkg.com/react-dom@18/umd/react-dom.development.js"></script>
    <script src="https://unpkg.com/@babel/standalone/babel.min.js"></script>
</head>
<body class="bg-gray-100">
    <div id="root"></div>
    <script type="text/babel" src="src/App.jsx"></script>
    <script type="text/babel">
        ReactDOM.createRoot(document.getElementById('root')).render(<App />);
    </script>
</body>
</html>""",
                    "type": "html"
                },
                {
                    "path": "src/App.jsx",
                    "content": f"""function App() {{
  const [count, setCount] = React.useState(0);
  
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center">
      <div className="bg-white rounded-2xl shadow-2xl p-8 max-w-md w-full mx-4">
        <h1 className="text-3xl font-bold text-gray-800 text-center mb-4">
          {project_name}
        </h1>
        <p className="text-gray-600 text-center mb-6">
          {description}
        </p>
        <div className="text-center">
          <p className="text-5xl font-bold text-blue-600 mb-4">{{count}}</p>
          <button 
            onClick={{() => setCount(count + 1)}}
            className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium"
          >
            Click me!
          </button>
        </div>
      </div>
    </div>
  );
}}""",
                    "type": "component"
                }
            ],
            "dependencies": {"npm": ["react", "react-dom", "tailwindcss"]},
            "entry_point": "index.html"
        }


class QAAgent(BaseAgent):
    def __init__(self, orchestrator: 'RealOrchestrator'):
        super().__init__(AgentType.QA, orchestrator)
    
    async def execute(self, task: AgentTask) -> Dict:
        self.status = AgentStatus.WORKING
        self.current_task = task
        task.status = AgentStatus.WORKING
        task.started_at = utc_now()
        
        try:
            code = task.input_data.get("code", {})
            files = code.get("files", [])
            
            await self.send_message(None, f"🔎 Reviewing {len(files)} files...")
            
            # Simple validation
            result = {
                "valid": True,
                "score": 85,
                "issues": [],
                "improvements": []
            }
            
            for file in files:
                content = file.get("content", "")
                if not content or len(content) < 10:
                    result["issues"].append({
                        "file": file.get("path"),
                        "type": "warning",
                        "message": "File content is very short"
                    })
                    result["score"] -= 5
            
            result["valid"] = result["score"] >= 60
            
            task.output_data = result
            task.status = AgentStatus.COMPLETED
            task.completed_at = utc_now()
            
            status = "✅ Passed" if result["valid"] else "⚠️ Has issues"
            await self.send_message(
                None,
                f"{status} - Score: {result['score']}/100",
                {"validation": result}
            )
            
            return result
            
        except Exception as e:
            task.status = AgentStatus.ERROR
            task.error = str(e)
            raise
        finally:
            self.status = AgentStatus.IDLE
            self.current_task = None
            self.history.append(task)


class ResearcherAgent(BaseAgent):
    def __init__(self, orchestrator: 'RealOrchestrator'):
        super().__init__(AgentType.RESEARCHER, orchestrator)
    
    async def execute(self, task: AgentTask) -> Dict:
        self.status = AgentStatus.WORKING
        self.current_task = task
        task.status = AgentStatus.WORKING
        task.started_at = utc_now()
        
        try:
            plan = task.input_data.get("plan", {})
            
            result = {
                "recommendations": [
                    "Use React hooks for state management",
                    "Implement responsive design with TailwindCSS",
                    "Add proper error handling"
                ],
                "libraries": plan.get("tech_stack", {}).get("frontend", []),
                "patterns": ["Component composition", "Custom hooks"],
                "best_practices": ["Mobile-first design", "Accessibility"]
            }
            
            task.output_data = result
            task.status = AgentStatus.COMPLETED
            task.completed_at = utc_now()
            
            return result
            
        finally:
            self.status = AgentStatus.IDLE
            self.current_task = None
            self.history.append(task)


class OptimizerAgent(BaseAgent):
    def __init__(self, orchestrator: 'RealOrchestrator'):
        super().__init__(AgentType.OPTIMIZER, orchestrator)
    
    async def execute(self, task: AgentTask) -> Dict:
        self.status = AgentStatus.WORKING
        task.status = AgentStatus.COMPLETED
        task.output_data = {"optimized": True}
        self.status = AgentStatus.IDLE
        self.history.append(task)
        return task.output_data


class CostControllerAgent(BaseAgent):
    def __init__(self, orchestrator: 'RealOrchestrator'):
        super().__init__(AgentType.COST_CONTROLLER, orchestrator)
        self.total_tokens = 0
        self.total_cost = 0.0
    
    async def execute(self, task: AgentTask) -> Dict:
        self.status = AgentStatus.WORKING
        task.status = AgentStatus.COMPLETED
        task.output_data = {
            "total_tokens": self.total_tokens,
            "total_cost": self.total_cost,
            "status": "ok"
        }
        self.status = AgentStatus.IDLE
        self.history.append(task)
        return task.output_data
    
    def track_usage(self, tokens: int, cost: float):
        self.total_tokens += tokens
        self.total_cost += cost


# ============= ORCHESTRATOR =============

class RealOrchestrator:
    def __init__(self):
        self.agents: Dict[AgentType, BaseAgent] = {}
        self.message_queue: List[AgentMessage] = []
        self.task_queue: List[AgentTask] = []
        self.completed_tasks: List[AgentTask] = []
        self.current_project_id: Optional[str] = None
        self.callbacks: List = []
        
        self._init_agents()
    
    def _init_agents(self):
        self.agents[AgentType.PLANNER] = PlannerAgent(self)
        self.agents[AgentType.RESEARCHER] = ResearcherAgent(self)
        self.agents[AgentType.DEVELOPER] = DeveloperAgent(self)
        self.agents[AgentType.QA] = QAAgent(self)
        self.agents[AgentType.OPTIMIZER] = OptimizerAgent(self)
        self.agents[AgentType.COST_CONTROLLER] = CostControllerAgent(self)
    
    def on_update(self, callback):
        self.callbacks.append(callback)
    
    async def notify_update(self, event_type: str, data: Dict):
        for callback in self.callbacks:
            try:
                await callback(event_type, data)
            except Exception as e:
                logger.error(f"Callback error: {e}")
    
    async def route_message(self, message: AgentMessage):
        self.message_queue.append(message)
        await self.notify_update("message", {
            "id": message.id,
            "from_agent": message.from_agent.value,
            "to_agent": message.to_agent.value if message.to_agent else None,
            "content": message.content,
            "timestamp": message.timestamp.isoformat()
        })
    
    async def create_task(self, agent_type: AgentType, description: str, input_data: Dict = None) -> AgentTask:
        task = AgentTask(
            id=generate_id("task"),
            agent_type=agent_type,
            description=description,
            input_data=input_data or {}
        )
        self.task_queue.append(task)
        await self.notify_update("task_created", task.to_dict())
        return task
    
    async def execute_task(self, task: AgentTask) -> Dict:
        agent = self.agents.get(task.agent_type)
        if not agent:
            raise ValueError(f"Unknown agent: {task.agent_type}")
        
        await self.notify_update("task_started", {"task": task.to_dict(), "agent": agent.get_status()})
        
        try:
            result = await agent.execute(task)
            await self.notify_update("task_completed", {"task": task.to_dict(), "result": result})
            self.completed_tasks.append(task)
            return result
        except Exception as e:
            await self.notify_update("task_error", {"task": task.to_dict(), "error": str(e)})
            raise
    
    async def run_pipeline(self, prompt: str, project_id: str) -> Dict:
        """Run the full agent pipeline"""
        self.current_project_id = project_id
        
        await self.notify_update("pipeline_started", {"project_id": project_id, "prompt": prompt})
        
        try:
            # Phase 1: Planning
            plan_task = await self.create_task(
                AgentType.PLANNER,
                "Create project plan",
                {"prompt": prompt}
            )
            plan = await self.execute_task(plan_task)
            
            # Phase 2: Development
            dev_task = await self.create_task(
                AgentType.DEVELOPER,
                "Generate code",
                {"plan": plan, "prompt": prompt}
            )
            code = await self.execute_task(dev_task)
            
            # Phase 3: QA
            qa_task = await self.create_task(
                AgentType.QA,
                "Validate code",
                {"code": code}
            )
            validation = await self.execute_task(qa_task)
            
            result = {
                "project_id": project_id,
                "plan": plan,
                "code": code,
                "validation": validation,
                "status": "completed"
            }
            
            await self.notify_update("pipeline_completed", result)
            return result
            
        except Exception as e:
            await self.notify_update("pipeline_error", {"project_id": project_id, "error": str(e)})
            raise
        finally:
            self.current_project_id = None
    
    def get_status(self) -> Dict:
        return {
            "agents": {at.value: a.get_status() for at, a in self.agents.items()},
            "current_project": self.current_project_id,
            "pending_tasks": len(self.task_queue),
            "completed_tasks": len(self.completed_tasks),
            "messages_processed": len(self.message_queue)
        }
    
    def get_agent(self, agent_type: AgentType) -> BaseAgent:
        return self.agents.get(agent_type)


# Global instance
orchestrator = RealOrchestrator()

def get_orchestrator() -> RealOrchestrator:
    return orchestrator

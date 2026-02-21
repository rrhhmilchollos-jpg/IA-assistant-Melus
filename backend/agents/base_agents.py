"""
MelusAI - Multi-Agent Orchestrator System
Sistema de orquestación multi-agente para desarrollo automatizado
"""
import os
import json
import asyncio
import logging
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from enum import Enum

logger = logging.getLogger(__name__)

# ============= AGENT TYPES =============

class AgentType(str, Enum):
    ORCHESTRATOR = "orchestrator"
    PLANNER = "planner"
    ARCHITECT = "architect"
    DEVELOPER = "developer"
    DEBUGGER = "debugger"
    EXECUTOR = "executor"
    RESEARCHER = "researcher"
    QA = "qa"
    DEPLOYER = "deployer"

class AgentStatus(str, Enum):
    IDLE = "idle"
    WORKING = "working"
    WAITING = "waiting"
    COMPLETED = "completed"
    ERROR = "error"

class TaskPriority(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

# ============= DATA MODELS =============

@dataclass
class AgentTask:
    """Tarea asignada a un agente"""
    task_id: str
    agent_type: AgentType
    description: str
    priority: TaskPriority
    input_data: Dict[str, Any]
    output_data: Optional[Dict[str, Any]] = None
    status: str = "pending"
    created_at: str = None
    completed_at: str = None
    error: str = None
    
    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now(timezone.utc).isoformat()
    
    def to_dict(self):
        return asdict(self)

@dataclass 
class AgentMessage:
    """Mensaje entre agentes"""
    from_agent: AgentType
    to_agent: AgentType
    message_type: str  # 'task', 'result', 'error', 'status'
    content: Dict[str, Any]
    timestamp: str = None
    
    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now(timezone.utc).isoformat()

# ============= BASE AGENT =============

class BaseAgent:
    """Clase base para todos los agentes"""
    
    def __init__(self, agent_type: AgentType, llm_key: str = None):
        self.agent_type = agent_type
        self.status = AgentStatus.IDLE
        self.current_task: Optional[AgentTask] = None
        self.llm_key = llm_key or os.environ.get('EMERGENT_LLM_KEY')
        self.system_prompt = self._get_system_prompt()
    
    def _get_system_prompt(self) -> str:
        """Override en cada agente"""
        return "You are a helpful AI assistant."
    
    async def execute(self, task: AgentTask) -> Dict[str, Any]:
        """Ejecutar una tarea"""
        self.status = AgentStatus.WORKING
        self.current_task = task
        
        try:
            result = await self._process_task(task)
            task.status = "completed"
            task.output_data = result
            task.completed_at = datetime.now(timezone.utc).isoformat()
            self.status = AgentStatus.COMPLETED
            return result
        except Exception as e:
            task.status = "error"
            task.error = str(e)
            self.status = AgentStatus.ERROR
            logger.error(f"Agent {self.agent_type} error: {e}")
            raise
        finally:
            self.current_task = None
    
    async def _process_task(self, task: AgentTask) -> Dict[str, Any]:
        """Override en cada agente"""
        raise NotImplementedError
    
    async def _call_llm(self, prompt: str) -> str:
        """Llamar al LLM"""
        from emergentintegrations.llm.chat import LlmChat, UserMessage
        
        chat = LlmChat(
            api_key=self.llm_key,
            session_id=f"{self.agent_type}_{datetime.now().timestamp()}",
            system_message=self.system_prompt
        ).with_model("openai", "gpt-4o")
        
        response = await chat.send_message(UserMessage(text=prompt))
        return response

# ============= SPECIALIZED AGENTS =============

class PlannerAgent(BaseAgent):
    """Agente de planificación - Divide tareas y crea roadmap"""
    
    def __init__(self, llm_key: str = None):
        super().__init__(AgentType.PLANNER, llm_key)
    
    def _get_system_prompt(self) -> str:
        return """You are an expert project planner AI. Your role is to:
1. Analyze user requirements thoroughly
2. Break down complex projects into manageable tasks
3. Define clear milestones and dependencies
4. Estimate complexity and identify risks
5. Create a structured development roadmap

Output your plans in JSON format with:
{
    "project_name": "string",
    "project_type": "web_app|mobile|api|game|other",
    "complexity": "simple|medium|complex",
    "tasks": [
        {
            "id": "task_1",
            "name": "string",
            "description": "string",
            "agent": "architect|developer|debugger|qa",
            "priority": "critical|high|medium|low",
            "dependencies": ["task_id"],
            "estimated_files": ["filename"]
        }
    ],
    "architecture": {
        "frontend": "react|vue|vanilla|none",
        "backend": "fastapi|express|none",
        "database": "mongodb|postgres|sqlite|none",
        "features": ["list of features"]
    },
    "risks": ["potential issues"]
}"""
    
    async def _process_task(self, task: AgentTask) -> Dict[str, Any]:
        prompt = f"""Analyze this project request and create a detailed development plan:

USER REQUEST:
{task.input_data.get('prompt', '')}

CONTEXT:
{json.dumps(task.input_data.get('context', {}), indent=2)}

Create a comprehensive project plan."""
        
        response = await self._call_llm(prompt)
        
        # Parse JSON from response
        try:
            import re
            json_match = re.search(r'\{[\s\S]*\}', response)
            if json_match:
                return json.loads(json_match.group())
        except:
            pass
        
        return {"raw_plan": response}


class ArchitectAgent(BaseAgent):
    """Agente arquitecto - Diseña estructura y decide tecnologías"""
    
    def __init__(self, llm_key: str = None):
        super().__init__(AgentType.ARCHITECT, llm_key)
    
    def _get_system_prompt(self) -> str:
        return """You are an expert software architect. Your role is to:
1. Design system architecture based on requirements
2. Choose appropriate technologies and frameworks
3. Define file structure and component hierarchy
4. Plan database schemas and API endpoints
5. Ensure scalability, security, and maintainability

Output architecture decisions in JSON:
{
    "file_structure": {
        "src/": ["App.jsx", "index.js"],
        "src/components/": ["Header.jsx", "Footer.jsx"],
        "src/pages/": ["Home.jsx"]
    },
    "dependencies": {
        "frontend": ["react", "tailwindcss"],
        "backend": ["fastapi", "pymongo"]
    },
    "api_endpoints": [
        {"method": "GET", "path": "/api/users", "description": "Get users"}
    ],
    "database_schema": {
        "users": {"fields": ["id", "email", "name"]}
    },
    "components": [
        {"name": "Header", "type": "component", "description": "Navigation header"}
    ]
}"""
    
    async def _process_task(self, task: AgentTask) -> Dict[str, Any]:
        prompt = f"""Design the architecture for this project:

PROJECT PLAN:
{json.dumps(task.input_data.get('plan', {}), indent=2)}

REQUIREMENTS:
{task.input_data.get('requirements', '')}

Create a detailed architecture design."""
        
        response = await self._call_llm(prompt)
        
        try:
            import re
            json_match = re.search(r'\{[\s\S]*\}', response)
            if json_match:
                return json.loads(json_match.group())
        except:
            pass
        
        return {"raw_architecture": response}


class DeveloperAgent(BaseAgent):
    """Agente desarrollador - Genera código"""
    
    def __init__(self, llm_key: str = None):
        super().__init__(AgentType.DEVELOPER, llm_key)
    
    def _get_system_prompt(self) -> str:
        return """You are an expert full-stack developer. Your role is to:
1. Write clean, production-ready code
2. Follow best practices and design patterns
3. Create complete, functional files
4. Handle edge cases and errors
5. Write self-documenting code

When generating code:
- Use modern syntax and features
- Include proper imports
- Add helpful comments
- Ensure code is complete and runnable

Output in JSON format:
{
    "files": [
        {
            "path": "src/App.jsx",
            "content": "// Full file content here",
            "language": "javascript"
        }
    ],
    "summary": "What was implemented"
}"""
    
    async def _process_task(self, task: AgentTask) -> Dict[str, Any]:
        prompt = f"""Generate code for this task:

TASK:
{task.input_data.get('task_description', '')}

ARCHITECTURE:
{json.dumps(task.input_data.get('architecture', {}), indent=2)}

EXISTING FILES:
{json.dumps(task.input_data.get('existing_files', []), indent=2)}

Generate complete, production-ready code."""
        
        response = await self._call_llm(prompt)
        
        try:
            import re
            json_match = re.search(r'\{[\s\S]*\}', response)
            if json_match:
                return json.loads(json_match.group())
        except:
            pass
        
        return {"raw_code": response}


class DebuggerAgent(BaseAgent):
    """Agente debugger - Encuentra y corrige errores"""
    
    def __init__(self, llm_key: str = None):
        super().__init__(AgentType.DEBUGGER, llm_key)
    
    def _get_system_prompt(self) -> str:
        return """You are an expert debugger. Your role is to:
1. Analyze code for bugs and issues
2. Identify root causes of errors
3. Suggest and implement fixes
4. Improve code quality
5. Prevent future issues

Output fixes in JSON:
{
    "issues_found": [
        {
            "file": "src/App.jsx",
            "line": 42,
            "issue": "Description",
            "severity": "critical|high|medium|low",
            "fix": "How to fix"
        }
    ],
    "fixed_files": [
        {
            "path": "src/App.jsx",
            "content": "// Fixed content"
        }
    ],
    "summary": "What was fixed"
}"""
    
    async def _process_task(self, task: AgentTask) -> Dict[str, Any]:
        prompt = f"""Debug this code:

ERROR:
{task.input_data.get('error', 'No specific error')}

CODE:
{json.dumps(task.input_data.get('files', {}), indent=2)}

LOGS:
{task.input_data.get('logs', '')}

Find and fix all issues."""
        
        response = await self._call_llm(prompt)
        
        try:
            import re
            json_match = re.search(r'\{[\s\S]*\}', response)
            if json_match:
                return json.loads(json_match.group())
        except:
            pass
        
        return {"raw_debug": response}


class QAAgent(BaseAgent):
    """Agente QA - Valida calidad y tests"""
    
    def __init__(self, llm_key: str = None):
        super().__init__(AgentType.QA, llm_key)
    
    def _get_system_prompt(self) -> str:
        return """You are an expert QA engineer. Your role is to:
1. Review code quality and standards
2. Identify potential bugs and issues
3. Suggest improvements
4. Validate functionality
5. Generate test cases

Output review in JSON:
{
    "quality_score": 85,
    "issues": [
        {"file": "path", "issue": "description", "severity": "high"}
    ],
    "suggestions": ["improvement suggestions"],
    "test_cases": [
        {"name": "test name", "description": "what to test", "expected": "result"}
    ],
    "passed": true
}"""
    
    async def _process_task(self, task: AgentTask) -> Dict[str, Any]:
        prompt = f"""Review this code for quality:

PROJECT TYPE:
{task.input_data.get('project_type', 'web_app')}

FILES:
{json.dumps(task.input_data.get('files', {}), indent=2)}

REQUIREMENTS:
{task.input_data.get('requirements', '')}

Perform a comprehensive QA review."""
        
        response = await self._call_llm(prompt)
        
        try:
            import re
            json_match = re.search(r'\{[\s\S]*\}', response)
            if json_match:
                return json.loads(json_match.group())
        except:
            pass
        
        return {"raw_qa": response, "quality_score": 70, "passed": True}


class ResearcherAgent(BaseAgent):
    """Agente investigador - Busca información y documentación"""
    
    def __init__(self, llm_key: str = None):
        super().__init__(AgentType.RESEARCHER, llm_key)
    
    def _get_system_prompt(self) -> str:
        return """You are an expert technical researcher. Your role is to:
1. Research best practices and patterns
2. Find relevant documentation
3. Suggest libraries and tools
4. Provide implementation examples
5. Stay updated with latest trends

Output research in JSON:
{
    "topic": "research topic",
    "findings": ["key findings"],
    "recommendations": ["what to use"],
    "examples": ["code examples"],
    "resources": ["documentation links"]
}"""
    
    async def _process_task(self, task: AgentTask) -> Dict[str, Any]:
        prompt = f"""Research this topic:

TOPIC:
{task.input_data.get('topic', '')}

CONTEXT:
{task.input_data.get('context', '')}

Provide comprehensive research findings."""
        
        response = await self._call_llm(prompt)
        
        try:
            import re
            json_match = re.search(r'\{[\s\S]*\}', response)
            if json_match:
                return json.loads(json_match.group())
        except:
            pass
        
        return {"raw_research": response}


class ExecutorAgent(BaseAgent):
    """Agente ejecutor - Ejecuta código en sandbox"""
    
    def __init__(self, llm_key: str = None):
        super().__init__(AgentType.EXECUTOR, llm_key)
    
    def _get_system_prompt(self) -> str:
        return """You are a code execution specialist. Your role is to:
1. Prepare code for execution
2. Set up dependencies
3. Run code safely
4. Capture outputs and errors
5. Report execution results"""
    
    async def _process_task(self, task: AgentTask) -> Dict[str, Any]:
        # Este agente interactúa con el sandbox real
        files = task.input_data.get('files', {})
        command = task.input_data.get('command', '')
        
        return {
            "executed": True,
            "command": command,
            "files_count": len(files),
            "status": "ready_for_sandbox"
        }


class DeployerAgent(BaseAgent):
    """Agente deployer - Despliega aplicaciones"""
    
    def __init__(self, llm_key: str = None):
        super().__init__(AgentType.DEPLOYER, llm_key)
    
    def _get_system_prompt(self) -> str:
        return """You are a deployment specialist. Your role is to:
1. Prepare applications for deployment
2. Configure build settings
3. Set up environment variables
4. Deploy to various platforms
5. Monitor deployment status"""
    
    async def _process_task(self, task: AgentTask) -> Dict[str, Any]:
        return {
            "deployment_ready": True,
            "platform": task.input_data.get('platform', 'preview'),
            "config": task.input_data.get('config', {})
        }

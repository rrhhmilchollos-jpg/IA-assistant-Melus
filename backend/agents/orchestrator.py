"""
MelusAI - Orchestrator Agent
Coordina todos los agentes y gestiona el flujo de trabajo
"""
import os
import json
import asyncio
import logging
import uuid
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional

from .base_agents import (
    AgentType, AgentStatus, TaskPriority, AgentTask, AgentMessage,
    PlannerAgent, ArchitectAgent, DeveloperAgent, DebuggerAgent,
    QAAgent, ResearcherAgent, ExecutorAgent, DeployerAgent
)

logger = logging.getLogger(__name__)


class ProjectOrchestration:
    """Estado de orquestación de un proyecto"""
    
    def __init__(self, project_id: str, prompt: str):
        self.project_id = project_id
        self.prompt = prompt
        self.status = "initializing"
        self.current_phase = "planning"
        self.tasks: List[AgentTask] = []
        self.completed_tasks: List[str] = []
        self.active_agents: Dict[str, AgentStatus] = {}
        self.plan: Dict = {}
        self.architecture: Dict = {}
        self.files: Dict[str, str] = {}
        self.logs: List[Dict] = []
        self.errors: List[str] = []
        self.created_at = datetime.now(timezone.utc).isoformat()
        self.updated_at = self.created_at
    
    def add_log(self, agent: str, message: str, level: str = "info"):
        self.logs.append({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "agent": agent,
            "message": message,
            "level": level
        })
        self.updated_at = datetime.now(timezone.utc).isoformat()
    
    def to_dict(self) -> Dict:
        return {
            "project_id": self.project_id,
            "prompt": self.prompt,
            "status": self.status,
            "current_phase": self.current_phase,
            "tasks_total": len(self.tasks),
            "tasks_completed": len(self.completed_tasks),
            "active_agents": self.active_agents,
            "files_count": len(self.files),
            "errors": self.errors,
            "logs": self.logs[-20:],  # Last 20 logs
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }


class OrchestratorAgent:
    """
    Agente orquestador principal.
    Coordina todos los demás agentes y gestiona el flujo de trabajo.
    """
    
    def __init__(self, db=None):
        self.db = db
        self.llm_key = os.environ.get('EMERGENT_LLM_KEY')
        
        # Inicializar todos los agentes
        self.agents = {
            AgentType.PLANNER: PlannerAgent(self.llm_key),
            AgentType.ARCHITECT: ArchitectAgent(self.llm_key),
            AgentType.DEVELOPER: DeveloperAgent(self.llm_key),
            AgentType.DEBUGGER: DebuggerAgent(self.llm_key),
            AgentType.QA: QAAgent(self.llm_key),
            AgentType.RESEARCHER: ResearcherAgent(self.llm_key),
            AgentType.EXECUTOR: ExecutorAgent(self.llm_key),
            AgentType.DEPLOYER: DeployerAgent(self.llm_key),
        }
        
        # Estado activo de orquestaciones
        self.orchestrations: Dict[str, ProjectOrchestration] = {}
    
    async def start_project(self, project_id: str, prompt: str, context: Dict = None) -> ProjectOrchestration:
        """Iniciar orquestación de un nuevo proyecto"""
        
        orchestration = ProjectOrchestration(project_id, prompt)
        self.orchestrations[project_id] = orchestration
        
        orchestration.add_log("orchestrator", f"Starting project: {prompt[:100]}...")
        orchestration.status = "running"
        
        try:
            # Fase 1: Planning
            await self._run_planning_phase(orchestration, context)
            
            # Fase 2: Architecture
            await self._run_architecture_phase(orchestration)
            
            # Fase 3: Development
            await self._run_development_phase(orchestration)
            
            # Fase 4: QA
            await self._run_qa_phase(orchestration)
            
            # Fase 5: Finalization
            await self._run_finalization_phase(orchestration)
            
            orchestration.status = "completed"
            orchestration.add_log("orchestrator", "Project completed successfully!", "success")
            
        except Exception as e:
            orchestration.status = "error"
            orchestration.errors.append(str(e))
            orchestration.add_log("orchestrator", f"Error: {e}", "error")
            logger.error(f"Orchestration error: {e}")
        
        return orchestration
    
    async def _run_planning_phase(self, orch: ProjectOrchestration, context: Dict = None):
        """Fase de planificación"""
        orch.current_phase = "planning"
        orch.active_agents[AgentType.PLANNER.value] = AgentStatus.WORKING.value
        orch.add_log("planner", "Analyzing requirements and creating plan...")
        
        task = AgentTask(
            task_id=f"plan_{uuid.uuid4().hex[:8]}",
            agent_type=AgentType.PLANNER,
            description="Create project plan",
            priority=TaskPriority.CRITICAL,
            input_data={
                "prompt": orch.prompt,
                "context": context or {}
            }
        )
        
        planner = self.agents[AgentType.PLANNER]
        result = await planner.execute(task)
        
        orch.plan = result
        orch.tasks.append(task)
        orch.completed_tasks.append(task.task_id)
        orch.active_agents[AgentType.PLANNER.value] = AgentStatus.COMPLETED.value
        orch.add_log("planner", f"Plan created: {result.get('project_name', 'Project')}", "success")
        
        # Stream to WebSocket if available
        await self._stream_update(orch.project_id, "phase", "Planning completed")
    
    async def _run_architecture_phase(self, orch: ProjectOrchestration):
        """Fase de arquitectura"""
        orch.current_phase = "architecture"
        orch.active_agents[AgentType.ARCHITECT.value] = AgentStatus.WORKING.value
        orch.add_log("architect", "Designing system architecture...")
        
        task = AgentTask(
            task_id=f"arch_{uuid.uuid4().hex[:8]}",
            agent_type=AgentType.ARCHITECT,
            description="Design architecture",
            priority=TaskPriority.CRITICAL,
            input_data={
                "plan": orch.plan,
                "requirements": orch.prompt
            }
        )
        
        architect = self.agents[AgentType.ARCHITECT]
        result = await architect.execute(task)
        
        orch.architecture = result
        orch.tasks.append(task)
        orch.completed_tasks.append(task.task_id)
        orch.active_agents[AgentType.ARCHITECT.value] = AgentStatus.COMPLETED.value
        orch.add_log("architect", "Architecture designed", "success")
        
        await self._stream_update(orch.project_id, "phase", "Architecture completed")
    
    async def _run_development_phase(self, orch: ProjectOrchestration):
        """Fase de desarrollo"""
        orch.current_phase = "development"
        orch.active_agents[AgentType.DEVELOPER.value] = AgentStatus.WORKING.value
        orch.add_log("developer", "Generating code...")
        
        # Obtener tareas de desarrollo del plan
        dev_tasks = orch.plan.get('tasks', [])
        
        if not dev_tasks:
            # Si no hay tareas específicas, crear una tarea general
            dev_tasks = [{
                "id": "main_dev",
                "name": "Generate main application",
                "description": f"Create complete application for: {orch.prompt}"
            }]
        
        for dev_task in dev_tasks:
            task = AgentTask(
                task_id=f"dev_{uuid.uuid4().hex[:8]}",
                agent_type=AgentType.DEVELOPER,
                description=dev_task.get('description', dev_task.get('name', 'Development task')),
                priority=TaskPriority.HIGH,
                input_data={
                    "task_description": dev_task.get('description', orch.prompt),
                    "architecture": orch.architecture,
                    "existing_files": list(orch.files.keys())
                }
            )
            
            developer = self.agents[AgentType.DEVELOPER]
            result = await developer.execute(task)
            
            # Agregar archivos generados
            files = result.get('files', [])
            for file in files:
                if isinstance(file, dict) and 'path' in file and 'content' in file:
                    orch.files[file['path']] = file['content']
                    orch.add_log("developer", f"Created: {file['path']}")
                    await self._stream_update(orch.project_id, "file", f"Created: {file['path']}")
            
            orch.tasks.append(task)
            orch.completed_tasks.append(task.task_id)
        
        orch.active_agents[AgentType.DEVELOPER.value] = AgentStatus.COMPLETED.value
        orch.add_log("developer", f"Generated {len(orch.files)} files", "success")
        
        await self._stream_update(orch.project_id, "phase", "Development completed")
    
    async def _run_qa_phase(self, orch: ProjectOrchestration):
        """Fase de QA"""
        orch.current_phase = "qa"
        orch.active_agents[AgentType.QA.value] = AgentStatus.WORKING.value
        orch.add_log("qa", "Running quality checks...")
        
        task = AgentTask(
            task_id=f"qa_{uuid.uuid4().hex[:8]}",
            agent_type=AgentType.QA,
            description="Quality assurance review",
            priority=TaskPriority.HIGH,
            input_data={
                "files": orch.files,
                "project_type": orch.plan.get('project_type', 'web_app'),
                "requirements": orch.prompt
            }
        )
        
        qa = self.agents[AgentType.QA]
        result = await qa.execute(task)
        
        quality_score = result.get('quality_score', 70)
        issues = result.get('issues', [])
        
        orch.tasks.append(task)
        orch.completed_tasks.append(task.task_id)
        orch.active_agents[AgentType.QA.value] = AgentStatus.COMPLETED.value
        
        # Si hay issues críticos, intentar corregir
        critical_issues = [i for i in issues if i.get('severity') == 'critical']
        
        if critical_issues and len(orch.files) > 0:
            orch.add_log("qa", f"Found {len(critical_issues)} critical issues, debugging...", "warning")
            orch.active_agents[AgentType.DEBUGGER.value] = AgentStatus.WORKING.value
            
            debug_task = AgentTask(
                task_id=f"debug_{uuid.uuid4().hex[:8]}",
                agent_type=AgentType.DEBUGGER,
                description="Fix critical issues",
                priority=TaskPriority.CRITICAL,
                input_data={
                    "files": orch.files,
                    "error": json.dumps(critical_issues)
                }
            )
            
            debugger = self.agents[AgentType.DEBUGGER]
            debug_result = await debugger.execute(debug_task)
            
            # Aplicar fixes
            fixed_files = debug_result.get('fixed_files', [])
            for file in fixed_files:
                if isinstance(file, dict) and 'path' in file and 'content' in file:
                    orch.files[file['path']] = file['content']
                    orch.add_log("debugger", f"Fixed: {file['path']}")
            
            orch.tasks.append(debug_task)
            orch.completed_tasks.append(debug_task.task_id)
            orch.active_agents[AgentType.DEBUGGER.value] = AgentStatus.COMPLETED.value
        
        orch.add_log("qa", f"Quality score: {quality_score}%", "success")
        await self._stream_update(orch.project_id, "phase", f"QA completed (Score: {quality_score}%)")
    
    async def _run_finalization_phase(self, orch: ProjectOrchestration):
        """Fase de finalización"""
        orch.current_phase = "finalization"
        orch.add_log("orchestrator", "Finalizing project...")
        
        # Guardar en DB si está disponible
        if self.db:
            await self.db.orchestrations.update_one(
                {"project_id": orch.project_id},
                {"$set": {
                    "plan": orch.plan,
                    "architecture": orch.architecture,
                    "files": orch.files,
                    "status": "completed",
                    "updated_at": datetime.now(timezone.utc).isoformat()
                }},
                upsert=True
            )
        
        orch.current_phase = "completed"
        await self._stream_update(orch.project_id, "complete", f"Project ready with {len(orch.files)} files")
    
    async def _stream_update(self, project_id: str, update_type: str, message: str):
        """Enviar actualización via WebSocket"""
        try:
            from websocket_manager import ws_manager
            await ws_manager.send_log(project_id, update_type, message)
        except Exception as e:
            logger.debug(f"WebSocket not available: {e}")
    
    def get_orchestration_status(self, project_id: str) -> Optional[Dict]:
        """Obtener estado de una orquestación"""
        if project_id in self.orchestrations:
            return self.orchestrations[project_id].to_dict()
        return None
    
    def get_all_orchestrations(self) -> List[Dict]:
        """Obtener todas las orquestaciones activas"""
        return [orch.to_dict() for orch in self.orchestrations.values()]

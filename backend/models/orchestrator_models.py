"""
MelusAI - Multi-Agent Orchestrator System
Database Models for PostgreSQL/MongoDB
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

# ============= ENUMS =============

class ObjectiveType(str, Enum):
    CONTENT = "content"
    CODE = "code"
    AUTOMATION = "automation"
    MIXED = "mixed"
    RESEARCH = "research"

class ObjectiveStatus(str, Enum):
    PENDING = "pending"
    PLANNING = "planning"
    IN_PROGRESS = "in_progress"
    EVALUATING = "evaluating"
    COMPLETED = "completed"
    FAILED = "failed"
    PAUSED = "paused"

class TaskStatus(str, Enum):
    QUEUED = "queued"
    ASSIGNED = "assigned"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    RETRYING = "retrying"

class AgentRole(str, Enum):
    # Cognitive Agents
    PLANNER = "planner"
    RESEARCH = "research"
    REASONING = "reasoning"
    # Productive Agents
    CONTENT = "content"
    CODE = "code"
    AUTOMATION = "automation"
    # Control Agents
    QA = "qa"
    SECURITY = "security"
    OPTIMIZATION = "optimization"
    COST_CONTROL = "cost_control"
    # Meta Agents
    META_PLANNER = "meta_planner"
    TASK_DECOMPOSER = "task_decomposer"
    AGENT_ROUTER = "agent_router"

class ModelProvider(str, Enum):
    GPT4 = "gpt-4"
    GPT4_TURBO = "gpt-4-turbo"
    GPT5 = "gpt-5"
    CLAUDE_SONNET = "claude-sonnet"
    CLAUDE_OPUS = "claude-opus"
    GEMINI = "gemini"
    LOCAL = "local"

# ============= OBJECTIVES =============

class ObjectiveCreate(BaseModel):
    title: str
    description: str
    type: ObjectiveType
    priority: int = Field(default=5, ge=1, le=10)
    cost_budget: Optional[float] = None
    deadline: Optional[datetime] = None
    auto_mode: bool = True
    config: Dict[str, Any] = {}

class Objective(BaseModel):
    id: str
    user_id: str
    title: str
    description: str
    type: ObjectiveType
    priority: int
    status: ObjectiveStatus = ObjectiveStatus.PENDING
    cost_budget: Optional[float] = None
    cost_used: float = 0.0
    deadline: Optional[datetime] = None
    auto_mode: bool = True
    config: Dict[str, Any] = {}
    result: Optional[Dict[str, Any]] = None
    quality_score: Optional[float] = None
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime] = None

# ============= TASKS =============

class TaskCreate(BaseModel):
    objective_id: str
    parent_task_id: Optional[str] = None
    title: str
    description: str
    agent_role: AgentRole
    priority: int = 5
    input_data: Dict[str, Any] = {}
    dependencies: List[str] = []

class Task(BaseModel):
    id: str
    objective_id: str
    parent_task_id: Optional[str] = None
    title: str
    description: str
    agent_role: AgentRole
    agent_id: Optional[str] = None
    model_used: Optional[ModelProvider] = None
    status: TaskStatus = TaskStatus.QUEUED
    priority: int
    input_data: Dict[str, Any] = {}
    output_data: Optional[Dict[str, Any]] = None
    dependencies: List[str] = []
    execution_time_ms: Optional[int] = None
    tokens_used: int = 0
    cost: float = 0.0
    result_score: Optional[float] = None
    retry_count: int = 0
    error_message: Optional[str] = None
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

# ============= AGENTS =============

class AgentConfig(BaseModel):
    temperature: float = 0.7
    max_tokens: int = 4000
    timeout_seconds: int = 120
    retry_limit: int = 3
    tools_enabled: List[str] = []

class Agent(BaseModel):
    id: str
    role: AgentRole
    name: str
    description: str
    model: ModelProvider
    config: AgentConfig
    is_active: bool = True
    success_rate: float = 1.0
    avg_cost: float = 0.0
    avg_latency_ms: float = 0.0
    total_tasks: int = 0
    successful_tasks: int = 0
    failed_tasks: int = 0
    reputation_score: float = 100.0
    created_at: datetime
    last_active_at: Optional[datetime] = None

# ============= MEMORY =============

class MemoryType(str, Enum):
    SHORT_TERM = "short_term"
    LONG_TERM = "long_term"
    STRATEGIC = "strategic"
    PROJECT = "project"

class MemoryVector(BaseModel):
    id: str
    user_id: str
    memory_type: MemoryType
    content: str
    embedding: List[float]
    metadata: Dict[str, Any] = {}
    project_id: Optional[str] = None
    objective_id: Optional[str] = None
    relevance_score: float = 1.0
    access_count: int = 0
    created_at: datetime
    last_accessed_at: Optional[datetime] = None

# ============= PERFORMANCE LOGS =============

class PerformanceLog(BaseModel):
    id: str
    task_id: str
    agent_id: str
    objective_id: str
    model_used: ModelProvider
    tokens_input: int
    tokens_output: int
    latency_ms: int
    cost: float
    quality_score: Optional[float] = None
    success: bool
    error_type: Optional[str] = None
    timestamp: datetime

# ============= PIPELINE =============

class PipelineType(str, Enum):
    CONTENT_CREATION = "content_creation"
    CODE_GENERATION = "code_generation"
    AUTOMATION_SETUP = "automation_setup"
    RESEARCH_ANALYSIS = "research_analysis"
    MIXED_WORKFLOW = "mixed_workflow"

class PipelineStep(BaseModel):
    order: int
    agent_role: AgentRole
    action: str
    input_mapping: Dict[str, str] = {}
    output_key: str
    conditions: Dict[str, Any] = {}

class Pipeline(BaseModel):
    id: str
    name: str
    type: PipelineType
    description: str
    steps: List[PipelineStep]
    is_active: bool = True
    success_rate: float = 1.0
    avg_execution_time_ms: int = 0
    total_runs: int = 0
    created_at: datetime

# ============= TOOLS =============

class ToolType(str, Enum):
    CODE_EXECUTOR = "code_executor"
    WEB_SCRAPER = "web_scraper"
    API_CALLER = "api_caller"
    GIT_OPERATIONS = "git_operations"
    DATABASE = "database"
    FILE_SYSTEM = "file_system"
    SOCIAL_MEDIA = "social_media"
    SCHEDULER = "scheduler"

class Tool(BaseModel):
    id: str
    name: str
    type: ToolType
    description: str
    config: Dict[str, Any] = {}
    is_active: bool = True
    requires_auth: bool = False
    rate_limit: Optional[int] = None
    last_used_at: Optional[datetime] = None

# ============= AUTONOMOUS LOOP =============

class LoopState(str, Enum):
    IDLE = "idle"
    PLANNING = "planning"
    EXECUTING = "executing"
    EVALUATING = "evaluating"
    IMPROVING = "improving"
    PUBLISHING = "publishing"
    MEASURING = "measuring"
    ADJUSTING = "adjusting"

class AutonomousLoop(BaseModel):
    id: str
    objective_id: str
    current_state: LoopState
    iteration: int = 0
    max_iterations: int = 10
    auto_improve: bool = True
    auto_publish: bool = False
    metrics: Dict[str, float] = {}
    improvements_made: List[str] = []
    is_active: bool = True
    created_at: datetime
    last_iteration_at: Optional[datetime] = None

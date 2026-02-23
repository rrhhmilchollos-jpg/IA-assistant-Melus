"""
MelusAI LLM Provider Manager
Unified interface for multiple AI models: GPT, Claude, Gemini, Sora
"""
import os
import logging
from typing import Optional, Dict, Any, List
from enum import Enum
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)


class LLMProvider(Enum):
    """Available LLM providers"""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GEMINI = "gemini"


class ModelType(Enum):
    """Types of AI models"""
    CHAT = "chat"
    CODE = "code"
    VIDEO = "video"
    IMAGE = "image"


@dataclass
class ModelConfig:
    """Configuration for an AI model"""
    provider: LLMProvider
    model_id: str
    display_name: str
    model_type: ModelType
    context_length: int
    is_pro: bool = False
    is_fast: bool = False
    cost_multiplier: float = 1.0
    description: str = ""


# Available Models Registry
AVAILABLE_MODELS: Dict[str, ModelConfig] = {
    # OpenAI Models
    "gpt-5.2-codex": ModelConfig(
        provider=LLMProvider.OPENAI,
        model_id="gpt-5.2",
        display_name="GPT-5.2 Codex",
        model_type=ModelType.CODE,
        context_length=128000,
        description="OpenAI's Latest Codex Model - Best for code generation"
    ),
    "gpt-5.1": ModelConfig(
        provider=LLMProvider.OPENAI,
        model_id="gpt-5.1",
        display_name="GPT-5.1",
        model_type=ModelType.CHAT,
        context_length=128000,
        description="OpenAI's recommended model"
    ),
    "gpt-4o": ModelConfig(
        provider=LLMProvider.OPENAI,
        model_id="gpt-4o",
        display_name="GPT-4o",
        model_type=ModelType.CHAT,
        context_length=128000,
        description="Fast multimodal model"
    ),
    "o3": ModelConfig(
        provider=LLMProvider.OPENAI,
        model_id="o3",
        display_name="O3 Reasoning",
        model_type=ModelType.CODE,
        context_length=200000,
        is_pro=True,
        description="Advanced reasoning model"
    ),
    
    # Anthropic Claude Models
    "claude-4.6-opus": ModelConfig(
        provider=LLMProvider.ANTHROPIC,
        model_id="claude-opus-4-6",
        display_name="Claude 4.6 Opus",
        model_type=ModelType.CHAT,
        context_length=200000,
        is_pro=True,
        description="Anthropic's Most Advanced Model"
    ),
    "claude-4.6-opus-1m": ModelConfig(
        provider=LLMProvider.ANTHROPIC,
        model_id="claude-opus-4-6",
        display_name="Claude 4.6 Opus - 1M",
        model_type=ModelType.CHAT,
        context_length=1000000,
        is_pro=True,
        description="1 Million Context"
    ),
    "claude-4.6-opus-fast": ModelConfig(
        provider=LLMProvider.ANTHROPIC,
        model_id="claude-opus-4-6",
        display_name="Claude 4.6 Opus - Fast",
        model_type=ModelType.CHAT,
        context_length=200000,
        is_pro=True,
        is_fast=True,
        cost_multiplier=6.0,
        description="Anthropic's Fastest Model (6x costlier)"
    ),
    "claude-4.6-sonnet": ModelConfig(
        provider=LLMProvider.ANTHROPIC,
        model_id="claude-sonnet-4-6",
        display_name="Claude 4.6 Sonnet",
        model_type=ModelType.CHAT,
        context_length=200000,
        description="Anthropic's Latest Model (200k Context)"
    ),
    "claude-4.6-sonnet-1m": ModelConfig(
        provider=LLMProvider.ANTHROPIC,
        model_id="claude-sonnet-4-6",
        display_name="Claude 4.6 Sonnet - 1M",
        model_type=ModelType.CHAT,
        context_length=1000000,
        is_pro=True,
        description="1 Million Context"
    ),
    "claude-4.5-opus": ModelConfig(
        provider=LLMProvider.ANTHROPIC,
        model_id="claude-opus-4-5-20251101",
        display_name="Claude 4.5 Opus",
        model_type=ModelType.CHAT,
        context_length=200000,
        description="Anthropic's Advanced Model"
    ),
    "claude-4.5-sonnet": ModelConfig(
        provider=LLMProvider.ANTHROPIC,
        model_id="claude-sonnet-4-5-20250929",
        display_name="Claude 4.5 Sonnet",
        model_type=ModelType.CHAT,
        context_length=200000,
        description="200k Context"
    ),
    "claude-4-sonnet": ModelConfig(
        provider=LLMProvider.ANTHROPIC,
        model_id="claude-4-sonnet-20250514",
        display_name="Claude 4 Sonnet",
        model_type=ModelType.CHAT,
        context_length=200000,
        description="Recommended Claude model"
    ),
    
    # Google Gemini Models
    "gemini-3-pro": ModelConfig(
        provider=LLMProvider.GEMINI,
        model_id="gemini-3-pro-preview",
        display_name="Gemini 3 Pro",
        model_type=ModelType.CHAT,
        context_length=1000000,
        description="Google's Latest Model"
    ),
    "gemini-3-flash": ModelConfig(
        provider=LLMProvider.GEMINI,
        model_id="gemini-3-flash-preview",
        display_name="Gemini 3 Flash",
        model_type=ModelType.CHAT,
        context_length=1000000,
        is_fast=True,
        description="Fast Gemini model"
    ),
    "gemini-2.5-pro": ModelConfig(
        provider=LLMProvider.GEMINI,
        model_id="gemini-2.5-pro",
        display_name="Gemini 2.5 Pro",
        model_type=ModelType.CHAT,
        context_length=1000000,
        description="Recommended Gemini model"
    ),
}

# Video Models
VIDEO_MODELS: Dict[str, ModelConfig] = {
    "sora-2": ModelConfig(
        provider=LLMProvider.OPENAI,
        model_id="sora-2",
        display_name="Sora 2",
        model_type=ModelType.VIDEO,
        context_length=0,
        description="Standard video generation"
    ),
    "sora-2-pro": ModelConfig(
        provider=LLMProvider.OPENAI,
        model_id="sora-2-pro",
        display_name="Sora 2 Pro",
        model_type=ModelType.VIDEO,
        context_length=0,
        is_pro=True,
        description="High quality video generation"
    ),
}


class LLMManager:
    """
    Manages LLM instances for different providers and models
    """
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.environ.get('EMERGENT_LLM_KEY')
        self._chat_instances: Dict[str, Any] = {}
        self._current_model: str = "gpt-4o"
    
    def get_available_models(self, model_type: Optional[ModelType] = None) -> List[Dict]:
        """Get list of available models"""
        models = []
        
        for key, config in AVAILABLE_MODELS.items():
            if model_type and config.model_type != model_type:
                continue
            
            models.append({
                "id": key,
                "model_id": config.model_id,
                "name": config.display_name,
                "provider": config.provider.value,
                "type": config.model_type.value,
                "context_length": config.context_length,
                "is_pro": config.is_pro,
                "is_fast": config.is_fast,
                "description": config.description
            })
        
        # Add video models
        for key, config in VIDEO_MODELS.items():
            if model_type and config.model_type != model_type:
                continue
            
            models.append({
                "id": key,
                "model_id": config.model_id,
                "name": config.display_name,
                "provider": config.provider.value,
                "type": config.model_type.value,
                "is_pro": config.is_pro,
                "description": config.description
            })
        
        return models
    
    def get_chat_client(self, model_key: str = "gpt-4o", session_id: str = "default"):
        """Get or create a chat client for the specified model"""
        from emergentintegrations.llm.chat import LlmChat
        
        cache_key = f"{model_key}_{session_id}"
        
        if cache_key not in self._chat_instances:
            config = AVAILABLE_MODELS.get(model_key)
            if not config:
                # Default to gpt-4o if model not found
                config = AVAILABLE_MODELS.get("gpt-4o")
                model_key = "gpt-4o"
            
            chat = LlmChat(
                api_key=self.api_key,
                session_id=session_id,
                system_message="Eres un experto desarrollador de software. Generas código limpio, moderno y funcional."
            ).with_model(config.provider.value, config.model_id)
            
            self._chat_instances[cache_key] = chat
            logger.info(f"Created chat client for {model_key} ({config.model_id})")
        
        return self._chat_instances[cache_key]
    
    async def chat(
        self, 
        message: str, 
        model_key: str = "gpt-4o", 
        session_id: str = "default"
    ) -> str:
        """Send a chat message and get response"""
        from emergentintegrations.llm.chat import UserMessage
        
        client = self.get_chat_client(model_key, session_id)
        user_message = UserMessage(text=message)
        response = await client.send_message(user_message)
        
        return response
    
    async def generate_video(
        self,
        prompt: str,
        model: str = "sora-2",
        size: str = "1280x720",
        duration: int = 4,
        output_path: str = "/app/uploads/generated_video.mp4"
    ) -> Optional[str]:
        """Generate video using Sora 2"""
        try:
            from emergentintegrations.llm.openai.video_generation import OpenAIVideoGeneration
            
            video_gen = OpenAIVideoGeneration(api_key=self.api_key)
            
            logger.info(f"Generating video with Sora 2: {prompt[:50]}...")
            
            video_bytes = video_gen.text_to_video(
                prompt=prompt,
                model=model,
                size=size,
                duration=duration,
                max_wait_time=600
            )
            
            if video_bytes:
                video_gen.save_video(video_bytes, output_path)
                logger.info(f"Video saved to {output_path}")
                return output_path
            
            return None
            
        except Exception as e:
            logger.error(f"Video generation error: {e}")
            return None
    
    def set_default_model(self, model_key: str):
        """Set the default model for chat"""
        if model_key in AVAILABLE_MODELS:
            self._current_model = model_key
            logger.info(f"Default model set to {model_key}")
        else:
            logger.warning(f"Model {model_key} not found, keeping {self._current_model}")


# Agent Modes Configuration
class AgentMode(Enum):
    """Different agent operation modes"""
    E1 = "e1"           # Estable y meticuloso
    E1_5 = "e1.5"       # Balanced
    E2 = "e2"           # Meticuloso y persistente
    PRO = "pro"         # Professional full-stack
    PROTOTYPE = "prototype"  # Quick prototype (frontend only)
    MOBILE = "mobile"   # Mobile app specialist


@dataclass
class AgentModeConfig:
    """Configuration for an agent mode"""
    mode: AgentMode
    display_name: str
    description: str
    default_model: str
    capabilities: List[str]
    speed: str  # fast, balanced, thorough
    focus: str  # frontend, backend, fullstack, mobile


AGENT_MODES: Dict[str, AgentModeConfig] = {
    "e1": AgentModeConfig(
        mode=AgentMode.E1,
        display_name="E-1",
        description="Estable y meticuloso - Ideal para proyectos que requieren precisión",
        default_model="gpt-4o",
        capabilities=["frontend", "backend", "database", "deployment"],
        speed="balanced",
        focus="fullstack"
    ),
    "e1.5": AgentModeConfig(
        mode=AgentMode.E1_5,
        display_name="E-1.5",
        description="Equilibrado - Balance entre velocidad y calidad",
        default_model="claude-4-sonnet",
        capabilities=["frontend", "backend", "database", "deployment", "testing"],
        speed="balanced",
        focus="fullstack"
    ),
    "e2": AgentModeConfig(
        mode=AgentMode.E2,
        display_name="E-2",
        description="Meticuloso y persistente - Para proyectos complejos",
        default_model="claude-4.6-opus",
        capabilities=["frontend", "backend", "database", "deployment", "testing", "optimization"],
        speed="thorough",
        focus="fullstack"
    ),
    "pro": AgentModeConfig(
        mode=AgentMode.PRO,
        display_name="Pro",
        description="Profesional - Máxima calidad con GPT-5.2 Codex",
        default_model="gpt-5.2-codex",
        capabilities=["frontend", "backend", "database", "deployment", "testing", "optimization", "security"],
        speed="thorough",
        focus="fullstack"
    ),
    "prototype": AgentModeConfig(
        mode=AgentMode.PROTOTYPE,
        display_name="Prototipo",
        description="Solo Frontend - Rápido para prototipos y demos",
        default_model="gemini-3-flash",
        capabilities=["frontend"],
        speed="fast",
        focus="frontend"
    ),
    "mobile": AgentModeConfig(
        mode=AgentMode.MOBILE,
        display_name="Móvil",
        description="Especialista en apps móviles - React Native / Flutter",
        default_model="claude-4.5-sonnet",
        capabilities=["mobile-frontend", "mobile-backend", "push-notifications"],
        speed="balanced",
        focus="mobile"
    ),
}


def get_agent_mode_config(mode: str) -> Optional[AgentModeConfig]:
    """Get configuration for an agent mode"""
    return AGENT_MODES.get(mode.lower())


def get_all_agent_modes() -> List[Dict]:
    """Get all available agent modes"""
    return [
        {
            "id": key,
            "name": config.display_name,
            "description": config.description,
            "default_model": config.default_model,
            "capabilities": config.capabilities,
            "speed": config.speed,
            "focus": config.focus
        }
        for key, config in AGENT_MODES.items()
    ]


# Singleton instance
_llm_manager: Optional[LLMManager] = None


def get_llm_manager() -> LLMManager:
    """Get or create the singleton LLMManager instance"""
    global _llm_manager
    if _llm_manager is None:
        _llm_manager = LLMManager()
    return _llm_manager

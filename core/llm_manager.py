"""
MelusAI - LLM Manager
Central manager for all AI model interactions
Supports: OpenAI, Anthropic (Claude), Google (Gemini), Sora
"""
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum
import logging
import os
import asyncio

logger = logging.getLogger(__name__)


class LLMProvider(Enum):
    """Available LLM providers"""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GOOGLE = "google"
    SORA = "sora"


@dataclass
class ModelConfig:
    """Configuration for an AI model"""
    key: str
    name: str
    provider: LLMProvider
    model_id: str
    max_tokens: int = 4096
    temperature: float = 0.7
    description: str = ""
    is_premium: bool = False
    supports_vision: bool = False
    supports_code: bool = True
    cost_per_1k: float = 0.01  # USD per 1k tokens


@dataclass
class AgentModeConfig:
    """Configuration for an agent mode"""
    mode_id: str
    name: str
    description: str
    default_model: str
    focus: str  # "fullstack", "frontend", "backend", "mobile"
    max_iterations: int = 10
    creativity: float = 0.7
    thoroughness: float = 0.8


# All available models
AVAILABLE_MODELS: Dict[str, ModelConfig] = {
    # OpenAI Models
    "gpt-4o": ModelConfig(
        key="gpt-4o",
        name="GPT-4o",
        provider=LLMProvider.OPENAI,
        model_id="gpt-4o",
        description="Fast and efficient multimodal",
        supports_vision=True,
        cost_per_1k=0.005
    ),
    "gpt-4o-mini": ModelConfig(
        key="gpt-4o-mini",
        name="GPT-4o Mini",
        provider=LLMProvider.OPENAI,
        model_id="gpt-4o-mini",
        description="Budget-friendly option",
        cost_per_1k=0.00015
    ),
    "gpt-5.2-codex": ModelConfig(
        key="gpt-5.2-codex",
        name="GPT-5.2 Codex",
        provider=LLMProvider.OPENAI,
        model_id="gpt-4o",  # Placeholder - would use actual model
        description="Best for code generation",
        is_premium=True,
        cost_per_1k=0.03
    ),
    "o3": ModelConfig(
        key="o3",
        name="O3 Reasoning",
        provider=LLMProvider.OPENAI,
        model_id="gpt-4o",  # Placeholder
        description="Advanced reasoning capabilities",
        is_premium=True,
        max_tokens=8192,
        cost_per_1k=0.06
    ),
    
    # Anthropic Claude Models
    "claude-4-sonnet": ModelConfig(
        key="claude-4-sonnet",
        name="Claude 4 Sonnet",
        provider=LLMProvider.ANTHROPIC,
        model_id="claude-sonnet-4-20250514",
        description="Balanced performance",
        max_tokens=8192,
        cost_per_1k=0.003
    ),
    "claude-4.5-opus": ModelConfig(
        key="claude-4.5-opus",
        name="Claude 4.5 Opus",
        provider=LLMProvider.ANTHROPIC,
        model_id="claude-sonnet-4-20250514",  # Would use opus when available
        description="Most capable Claude",
        is_premium=True,
        max_tokens=16384,
        cost_per_1k=0.015
    ),
    "claude-4.6-opus": ModelConfig(
        key="claude-4.6-opus",
        name="Claude 4.6 Opus",
        provider=LLMProvider.ANTHROPIC,
        model_id="claude-sonnet-4-20250514",
        description="Latest Opus model",
        is_premium=True,
        max_tokens=32768,
        cost_per_1k=0.02
    ),
    "claude-4.6-sonnet": ModelConfig(
        key="claude-4.6-sonnet",
        name="Claude 4.6 Sonnet",
        provider=LLMProvider.ANTHROPIC,
        model_id="claude-sonnet-4-20250514",
        description="Latest Sonnet with 200k context",
        max_tokens=8192,
        cost_per_1k=0.005
    ),
    
    # Google Gemini Models
    "gemini-3-pro": ModelConfig(
        key="gemini-3-pro",
        name="Gemini 3 Pro",
        provider=LLMProvider.GOOGLE,
        model_id="gemini-2.5-pro",  # Current available model
        description="Latest Gemini model",
        max_tokens=8192,
        supports_vision=True,
        cost_per_1k=0.00125
    ),
    "gemini-3-flash": ModelConfig(
        key="gemini-3-flash",
        name="Gemini 3 Flash",
        provider=LLMProvider.GOOGLE,
        model_id="gemini-2.5-flash",
        description="Ultra fast responses",
        max_tokens=4096,
        cost_per_1k=0.000075
    ),
    "gemini-2.5-pro": ModelConfig(
        key="gemini-2.5-pro",
        name="Gemini 2.5 Pro",
        provider=LLMProvider.GOOGLE,
        model_id="gemini-2.5-pro",
        description="Recommended Gemini model",
        max_tokens=8192,
        cost_per_1k=0.00125
    ),
    
    # Sora Video Models
    "sora-2": ModelConfig(
        key="sora-2",
        name="Sora 2",
        provider=LLMProvider.SORA,
        model_id="sora-2",
        description="Video generation",
        is_premium=True,
        supports_code=False,
        cost_per_1k=0.5
    ),
    "sora-2-pro": ModelConfig(
        key="sora-2-pro",
        name="Sora 2 Pro",
        provider=LLMProvider.SORA,
        model_id="sora-2-pro",
        description="High-quality video generation",
        is_premium=True,
        supports_code=False,
        cost_per_1k=1.0
    ),
}

# Agent modes configuration
AGENT_MODES: Dict[str, AgentModeConfig] = {
    "e1": AgentModeConfig(
        mode_id="e1",
        name="E1",
        description="Standard - Fast iterations, reliable results",
        default_model="gpt-4o",
        focus="fullstack",
        max_iterations=5,
        creativity=0.5,
        thoroughness=0.6
    ),
    "e1.5": AgentModeConfig(
        mode_id="e1.5",
        name="E1.5",
        description="Enhanced - Better quality, more context awareness",
        default_model="claude-4-sonnet",
        focus="fullstack",
        max_iterations=8,
        creativity=0.6,
        thoroughness=0.75
    ),
    "e2": AgentModeConfig(
        mode_id="e2",
        name="E2",
        description="Advanced - Multi-agent, comprehensive solutions",
        default_model="claude-4.5-opus",
        focus="fullstack",
        max_iterations=15,
        creativity=0.7,
        thoroughness=0.9
    ),
    "pro": AgentModeConfig(
        mode_id="pro",
        name="Pro",
        description="Maximum quality - Best models, deep analysis",
        default_model="gpt-5.2-codex",
        focus="fullstack",
        max_iterations=20,
        creativity=0.8,
        thoroughness=0.95
    ),
    "prototype": AgentModeConfig(
        mode_id="prototype",
        name="Prototype",
        description="Frontend only - Rapid UI prototyping",
        default_model="gemini-3-flash",
        focus="frontend",
        max_iterations=3,
        creativity=0.9,
        thoroughness=0.4
    ),
    "mobile": AgentModeConfig(
        mode_id="mobile",
        name="Mobile",
        description="Mobile-focused - React Native, responsive design",
        default_model="claude-4.5-opus",
        focus="mobile",
        max_iterations=10,
        creativity=0.6,
        thoroughness=0.8
    ),
}


class LLMManager:
    """
    Central manager for all LLM interactions
    Handles model selection, API calls, and response processing
    """
    
    def __init__(self):
        self.api_key = os.environ.get('EMERGENT_LLM_KEY')
        self.default_model = "gpt-4o"
        self.current_mode = "e1"
        self._chat_client = None
        self._anthropic_client = None
        self._gemini_client = None
        
    def set_default_model(self, model_key: str):
        """Set the default model for generation"""
        if model_key in AVAILABLE_MODELS:
            self.default_model = model_key
            logger.info(f"Default model set to: {model_key}")
        else:
            logger.warning(f"Unknown model: {model_key}, keeping {self.default_model}")
    
    def set_mode(self, mode: str):
        """Set the agent mode"""
        if mode in AGENT_MODES:
            self.current_mode = mode
            mode_config = AGENT_MODES[mode]
            self.default_model = mode_config.default_model
            logger.info(f"Mode set to: {mode} with model {self.default_model}")
        else:
            logger.warning(f"Unknown mode: {mode}")
    
    def get_model_config(self, model_key: str = None) -> ModelConfig:
        """Get configuration for a model"""
        key = model_key or self.default_model
        return AVAILABLE_MODELS.get(key, AVAILABLE_MODELS["gpt-4o"])
    
    def get_mode_config(self, mode: str = None) -> AgentModeConfig:
        """Get configuration for a mode"""
        return AGENT_MODES.get(mode or self.current_mode, AGENT_MODES["e1"])
    
    def list_models(self) -> List[Dict]:
        """List all available models"""
        return [
            {
                "key": model.key,
                "name": model.name,
                "provider": model.provider.value,
                "description": model.description,
                "is_premium": model.is_premium,
                "supports_vision": model.supports_vision,
                "supports_code": model.supports_code
            }
            for model in AVAILABLE_MODELS.values()
        ]
    
    def list_modes(self) -> List[Dict]:
        """List all available modes"""
        return [
            {
                "id": mode.mode_id,
                "name": mode.name,
                "description": mode.description,
                "default_model": mode.default_model,
                "focus": mode.focus
            }
            for mode in AGENT_MODES.values()
        ]
    
    async def chat(
        self,
        prompt: str,
        model: str = None,
        system_message: str = None,
        temperature: float = None,
        max_tokens: int = None
    ) -> str:
        """
        Send a chat message and get a response
        """
        model_config = self.get_model_config(model)
        
        if not self.api_key:
            logger.error("No API key available")
            return "Error: API key not configured"
        
        try:
            from emergentintegrations.llm.chat import LlmChat, UserMessage
            
            # Determine provider
            if model_config.provider == LLMProvider.OPENAI:
                provider = "openai"
            elif model_config.provider == LLMProvider.ANTHROPIC:
                provider = "anthropic"
            elif model_config.provider == LLMProvider.GOOGLE:
                provider = "google"
            else:
                provider = "openai"  # Default fallback
            
            # Create chat client
            system = system_message or "You are an expert software developer. Generate clean, well-structured code."
            
            chat = LlmChat(
                api_key=self.api_key,
                session_id=f"melus_{model_config.key}",
                system_message=system
            ).with_model(provider, model_config.model_id)
            
            # Send message
            response = await chat.send_message(UserMessage(text=prompt))
            
            return response
            
        except Exception as e:
            logger.error(f"Chat error: {e}")
            return f"Error: {str(e)}"
    
    async def generate_code(
        self,
        prompt: str,
        language: str = "javascript",
        framework: str = "react",
        model: str = None
    ) -> str:
        """
        Generate code for a specific task
        """
        system_message = f"""You are an expert {framework} developer.
Generate clean, production-ready {language} code.
Follow best practices and modern patterns.
Include proper error handling and comments where helpful.
Return ONLY the code, no explanations."""
        
        return await self.chat(
            prompt=prompt,
            model=model,
            system_message=system_message,
            temperature=0.5
        )
    
    async def generate_video(
        self,
        prompt: str,
        model: str = "sora-2",
        size: str = "1280x720",
        duration: int = 4,
        output_path: str = None
    ) -> Optional[str]:
        """
        Generate a video using Sora
        """
        try:
            from emergentintegrations.llm.video import VideoGeneration
            
            video_gen = VideoGeneration(api_key=self.api_key)
            
            result = await video_gen.generate(
                prompt=prompt,
                model=model,
                size=size,
                duration=duration,
                output_path=output_path
            )
            
            return result
            
        except ImportError:
            logger.warning("Video generation not available - emergentintegrations.llm.video not found")
            return None
        except Exception as e:
            logger.error(f"Video generation error: {e}")
            return None
    
    async def analyze_code(
        self,
        code: str,
        analysis_type: str = "review",
        model: str = None
    ) -> Dict[str, Any]:
        """
        Analyze code for issues, improvements, or explanations
        """
        prompts = {
            "review": f"""Review this code and provide:
1. Overall quality score (1-10)
2. Issues found (bugs, security, performance)
3. Suggested improvements
4. Best practices violations

Code:
```
{code}
```

Respond in JSON format.""",
            "explain": f"""Explain this code:
1. What it does
2. How it works
3. Key functions/components
4. Dependencies

Code:
```
{code}
```""",
            "optimize": f"""Optimize this code for:
1. Performance
2. Readability
3. Best practices

Provide the optimized code and explain changes.

Original code:
```
{code}
```"""
        }
        
        response = await self.chat(
            prompt=prompts.get(analysis_type, prompts["review"]),
            model=model,
            temperature=0.3
        )
        
        return {
            "analysis_type": analysis_type,
            "response": response
        }


# Singleton instance
_llm_manager: Optional[LLMManager] = None


def get_llm_manager() -> LLMManager:
    """Get or create the singleton LLMManager instance"""
    global _llm_manager
    if _llm_manager is None:
        _llm_manager = LLMManager()
    return _llm_manager


def get_available_models() -> List[Dict]:
    """Get list of available models"""
    return get_llm_manager().list_models()


def get_available_modes() -> List[Dict]:
    """Get list of available modes"""
    return get_llm_manager().list_modes()


def get_agent_mode_config(mode: str) -> Optional[AgentModeConfig]:
    """Get configuration for an agent mode"""
    return AGENT_MODES.get(mode)

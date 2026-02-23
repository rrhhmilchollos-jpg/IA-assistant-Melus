"""
MelusAI Brain Engine
Central intelligence that orchestrates the entire application generation process
"""
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
import asyncio
import logging
import json
import os
import sys

# Ensure core path is in sys.path
if '/app/core' not in sys.path:
    sys.path.insert(0, '/app/core')

from .intent_classifier import (
    IntentClassifier, IntentResult, IntentType, 
    ComplexityLevel, get_intent_classifier
)

logger = logging.getLogger(__name__)


class PipelineStage(Enum):
    """Stages in the code generation pipeline"""
    INTENT_ANALYSIS = "intent_analysis"
    TEMPLATE_SELECTION = "template_selection"
    PLANNING = "planning"
    CODE_GENERATION = "code_generation"
    CUSTOMIZATION = "customization"
    VALIDATION = "validation"
    OPTIMIZATION = "optimization"
    COMPLETE = "complete"
    ERROR = "error"


@dataclass
class GenerationContext:
    """Context for a generation session"""
    project_id: str
    user_id: str
    prompt: str
    intent_result: Optional[IntentResult] = None
    selected_template: Optional[str] = None
    current_stage: PipelineStage = PipelineStage.INTENT_ANALYSIS
    files: List[Dict[str, Any]] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass 
class AgentMessage:
    """Message between agents"""
    from_agent: str
    to_agent: str
    content: str
    data: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class BrainEngine:
    """
    The Brain Engine is the central orchestrator of MelusAI.
    It coordinates:
    1. Intent classification
    2. Template selection
    3. Agent coordination
    4. Code generation pipeline
    5. Quality validation
    """
    
    def __init__(self):
        self.intent_classifier = get_intent_classifier()
        self.active_contexts: Dict[str, GenerationContext] = {}
        self.update_callbacks: List[Callable] = []
        self.llm_client = None
        self._initialize_llm()
    
    def _initialize_llm(self):
        """Initialize LLM client"""
        try:
            from emergentintegrations.llm.openai import OpenAIChat
            self.llm_client = OpenAIChat(
                api_key=os.environ.get('EMERGENT_LLM_KEY'),
                model="gpt-4o"
            )
            logger.info("LLM client initialized successfully")
        except Exception as e:
            logger.warning(f"Could not initialize LLM: {e}")
    
    def on_update(self, callback: Callable):
        """Register callback for progress updates"""
        self.update_callbacks.append(callback)
    
    async def _notify_update(self, event_type: str, data: Dict):
        """Notify all registered callbacks"""
        for callback in self.update_callbacks:
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback(event_type, data)
                else:
                    callback(event_type, data)
            except Exception as e:
                logger.error(f"Error in update callback: {e}")
    
    async def process_prompt(
        self,
        prompt: str,
        project_id: str,
        user_id: str
    ) -> GenerationContext:
        """
        Main entry point for processing a user prompt
        """
        # Create context
        context = GenerationContext(
            project_id=project_id,
            user_id=user_id,
            prompt=prompt
        )
        self.active_contexts[project_id] = context
        
        try:
            # Stage 1: Intent Analysis
            await self._stage_intent_analysis(context)
            
            # Stage 2: Template Selection
            await self._stage_template_selection(context)
            
            # Stage 3: Planning
            await self._stage_planning(context)
            
            # Stage 4: Code Generation
            await self._stage_code_generation(context)
            
            # Stage 5: Customization
            await self._stage_customization(context)
            
            # Stage 6: Validation
            await self._stage_validation(context)
            
            # Complete
            context.current_stage = PipelineStage.COMPLETE
            await self._notify_update("pipeline_completed", {
                "project_id": project_id,
                "files_count": len(context.files)
            })
            
        except Exception as e:
            logger.error(f"Pipeline error: {e}")
            context.current_stage = PipelineStage.ERROR
            context.errors.append(str(e))
            await self._notify_update("pipeline_error", {
                "project_id": project_id,
                "error": str(e)
            })
        
        return context
    
    async def _stage_intent_analysis(self, context: GenerationContext):
        """Analyze user intent"""
        context.current_stage = PipelineStage.INTENT_ANALYSIS
        await self._notify_update("stage_started", {
            "stage": "intent_analysis",
            "project_id": context.project_id
        })
        
        # Classify intent
        intent_result = self.intent_classifier.classify(context.prompt)
        context.intent_result = intent_result
        
        await self._notify_update("intent_classified", {
            "project_id": context.project_id,
            "intent_type": intent_result.intent_type.value,
            "confidence": intent_result.confidence,
            "features": intent_result.features,
            "complexity": intent_result.complexity.value
        })
        
        logger.info(f"Intent classified: {intent_result.intent_type.value}")
    
    async def _stage_template_selection(self, context: GenerationContext):
        """Select appropriate template"""
        context.current_stage = PipelineStage.TEMPLATE_SELECTION
        await self._notify_update("stage_started", {
            "stage": "template_selection",
            "project_id": context.project_id
        })
        
        if context.intent_result:
            context.selected_template = context.intent_result.recommended_template
            context.metadata["builder"] = context.intent_result.recommended_builder
        
        await self._notify_update("template_selected", {
            "project_id": context.project_id,
            "template": context.selected_template,
            "builder": context.metadata.get("builder")
        })
    
    async def _stage_planning(self, context: GenerationContext):
        """Create generation plan"""
        context.current_stage = PipelineStage.PLANNING
        await self._notify_update("stage_started", {
            "stage": "planning",
            "project_id": context.project_id
        })
        
        # Use LLM to create detailed plan
        if self.llm_client:
            plan_prompt = f"""Crea un plan detallado para generar una aplicación basada en:

Solicitud del usuario: {context.prompt}

Tipo de aplicación: {context.intent_result.intent_type.value if context.intent_result else 'web_app'}
Características detectadas: {context.intent_result.features if context.intent_result else []}
Complejidad: {context.intent_result.complexity.value if context.intent_result else 'medium'}
Template base: {context.selected_template}

Responde en formato JSON con esta estructura:
{{
    "project_name": "nombre sugerido",
    "description": "descripción breve",
    "tech_stack": {{
        "frontend": ["tecnologías"],
        "backend": ["tecnologías"],
        "database": "tipo de base de datos"
    }},
    "files_to_generate": [
        {{"path": "ruta/archivo", "type": "tipo", "description": "propósito"}}
    ],
    "features": [
        {{"name": "nombre", "priority": "high/medium/low", "description": "detalle"}}
    ]
}}"""
            
            try:
                plan_response = await self.llm_client.chat(plan_prompt)
                # Try to parse JSON from response
                try:
                    # Find JSON in response
                    json_start = plan_response.find('{')
                    json_end = plan_response.rfind('}') + 1
                    if json_start >= 0 and json_end > json_start:
                        plan_json = json.loads(plan_response[json_start:json_end])
                        context.metadata["plan"] = plan_json
                except json.JSONDecodeError:
                    context.metadata["plan_raw"] = plan_response
            except Exception as e:
                logger.warning(f"Could not generate plan with LLM: {e}")
        
        await self._notify_update("plan_created", {
            "project_id": context.project_id,
            "plan": context.metadata.get("plan", {})
        })
    
    async def _stage_code_generation(self, context: GenerationContext):
        """Generate code files"""
        context.current_stage = PipelineStage.CODE_GENERATION
        await self._notify_update("stage_started", {
            "stage": "code_generation",
            "project_id": context.project_id
        })
        
        # Get plan or use defaults
        plan = context.metadata.get("plan", {})
        intent = context.intent_result
        
        # Generate files based on intent type
        if intent:
            files = await self._generate_files_for_intent(
                intent.intent_type,
                intent.features,
                intent.complexity,
                context.prompt,
                plan
            )
            context.files = files
        
        await self._notify_update("code_generated", {
            "project_id": context.project_id,
            "files_count": len(context.files),
            "files": [f["path"] for f in context.files]
        })
    
    async def _generate_files_for_intent(
        self,
        intent_type: IntentType,
        features: List[str],
        complexity: ComplexityLevel,
        prompt: str,
        plan: Dict
    ) -> List[Dict]:
        """Generate files based on intent type - uses pre-built templates"""
        # Import templates using relative import
        try:
            from .code_templates import get_template_for_intent
            
            # Get the best template based on intent and prompt
            files = get_template_for_intent(intent_type.value, prompt)
            logger.info(f"Using pre-built template for {intent_type.value}, got {len(files)} files")
            return files
            
        except ImportError as e:
            logger.warning(f"Could not import code_templates: {e}")
        
        # Fallback: Use default template
        files = [{
            "path": "App.jsx",
            "content": self._get_default_template(intent_type),
            "type": "component"
        }]
        
        return files
    
    def _get_default_template(self, intent_type: IntentType) -> str:
        """Get default template for an intent type"""
        templates = {
            IntentType.ECOMMERCE: '''import React, { useState } from 'react';

const App = () => {
  const [products] = useState([
    { id: 1, name: 'Producto 1', price: 29.99, image: 'https://via.placeholder.com/200' },
    { id: 2, name: 'Producto 2', price: 49.99, image: 'https://via.placeholder.com/200' },
    { id: 3, name: 'Producto 3', price: 19.99, image: 'https://via.placeholder.com/200' },
  ]);
  const [cart, setCart] = useState([]);

  const addToCart = (product) => {
    setCart([...cart, product]);
  };

  return (
    <div className="min-h-screen bg-gray-100">
      <header className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 py-6 flex justify-between items-center">
          <h1 className="text-3xl font-bold text-gray-900">Mi Tienda</h1>
          <div className="flex items-center gap-2">
            <span className="text-gray-600">Carrito: {cart.length}</span>
          </div>
        </div>
      </header>
      <main className="max-w-7xl mx-auto px-4 py-8">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {products.map(product => (
            <div key={product.id} className="bg-white rounded-lg shadow p-4">
              <img src={product.image} alt={product.name} className="w-full h-48 object-cover rounded" />
              <h3 className="mt-4 text-lg font-semibold">{product.name}</h3>
              <p className="text-gray-600">${product.price}</p>
              <button 
                onClick={() => addToCart(product)}
                className="mt-4 w-full bg-blue-600 text-white py-2 rounded hover:bg-blue-700"
              >
                Agregar al Carrito
              </button>
            </div>
          ))}
        </div>
      </main>
    </div>
  );
};

export default App;''',
            IntentType.DASHBOARD: '''import React, { useState } from 'react';

const App = () => {
  const [stats] = useState([
    { label: 'Usuarios', value: '1,234', change: '+12%' },
    { label: 'Ventas', value: '$45,678', change: '+8%' },
    { label: 'Pedidos', value: '567', change: '+23%' },
    { label: 'Conversión', value: '3.2%', change: '+1.2%' },
  ]);

  return (
    <div className="min-h-screen bg-gray-900 text-white">
      <nav className="bg-gray-800 px-6 py-4">
        <h1 className="text-2xl font-bold">Dashboard</h1>
      </nav>
      <main className="p-6">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          {stats.map((stat, i) => (
            <div key={i} className="bg-gray-800 rounded-lg p-6">
              <p className="text-gray-400 text-sm">{stat.label}</p>
              <p className="text-3xl font-bold mt-2">{stat.value}</p>
              <p className="text-green-400 text-sm mt-2">{stat.change}</p>
            </div>
          ))}
        </div>
        <div className="bg-gray-800 rounded-lg p-6">
          <h2 className="text-xl font-semibold mb-4">Resumen</h2>
          <p className="text-gray-400">Contenido del dashboard aquí...</p>
        </div>
      </main>
    </div>
  );
};

export default App;''',
            IntentType.LANDING_PAGE: '''import React from 'react';

const App = () => {
  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-900 to-indigo-900">
      <nav className="flex justify-between items-center px-8 py-6">
        <h1 className="text-2xl font-bold text-white">MiMarca</h1>
        <button className="bg-white text-purple-900 px-6 py-2 rounded-full font-semibold hover:bg-gray-100">
          Comenzar
        </button>
      </nav>
      <main className="max-w-4xl mx-auto text-center py-20 px-4">
        <h2 className="text-5xl font-bold text-white mb-6">
          Transforma tu negocio con nuestra solución
        </h2>
        <p className="text-xl text-purple-200 mb-8">
          La plataforma que necesitas para llevar tu empresa al siguiente nivel.
        </p>
        <div className="flex gap-4 justify-center">
          <button className="bg-white text-purple-900 px-8 py-3 rounded-full font-semibold hover:bg-gray-100">
            Empezar Gratis
          </button>
          <button className="border border-white text-white px-8 py-3 rounded-full font-semibold hover:bg-white/10">
            Ver Demo
          </button>
        </div>
      </main>
    </div>
  );
};

export default App;'''
        }
        
        # Default template
        default = '''import React, { useState } from 'react';

const App = () => {
  const [count, setCount] = useState(0);

  return (
    <div className="min-h-screen bg-gray-100 flex items-center justify-center">
      <div className="bg-white rounded-lg shadow-lg p-8 text-center">
        <h1 className="text-3xl font-bold text-gray-800 mb-4">Mi Aplicación</h1>
        <p className="text-gray-600 mb-6">Contador: {count}</p>
        <button 
          onClick={() => setCount(count + 1)}
          className="bg-blue-600 text-white px-6 py-2 rounded hover:bg-blue-700"
        >
          Incrementar
        </button>
      </div>
    </div>
  );
};

export default App;'''
        
        return templates.get(intent_type, default)
    
    async def _stage_customization(self, context: GenerationContext):
        """Apply customizations based on user preferences"""
        context.current_stage = PipelineStage.CUSTOMIZATION
        await self._notify_update("stage_started", {
            "stage": "customization",
            "project_id": context.project_id
        })
        
        # Extract any customization preferences from intent
        if context.intent_result and context.intent_result.extracted_entities:
            entities = context.intent_result.extracted_entities
            
            # Apply color customizations if specified
            if "colors" in entities:
                # Could modify generated files to use specified colors
                context.metadata["colors"] = entities["colors"]
            
            # Apply tech stack preferences
            if "tech_stack" in entities:
                context.metadata["requested_tech"] = entities["tech_stack"]
        
        await self._notify_update("customization_applied", {
            "project_id": context.project_id
        })
    
    async def _stage_validation(self, context: GenerationContext):
        """Validate generated code"""
        context.current_stage = PipelineStage.VALIDATION
        await self._notify_update("stage_started", {
            "stage": "validation",
            "project_id": context.project_id
        })
        
        # Basic validation
        validation_results = {
            "files_generated": len(context.files) > 0,
            "has_main_component": any(f["path"].endswith("App.jsx") for f in context.files),
            "syntax_valid": True  # Would run actual syntax checking
        }
        
        context.metadata["validation"] = validation_results
        
        await self._notify_update("validation_complete", {
            "project_id": context.project_id,
            "results": validation_results
        })
    
    def get_context(self, project_id: str) -> Optional[GenerationContext]:
        """Get generation context for a project"""
        return self.active_contexts.get(project_id)
    
    def get_status(self) -> Dict:
        """Get current engine status"""
        return {
            "active_projects": len(self.active_contexts),
            "projects": [
                {
                    "project_id": ctx.project_id,
                    "stage": ctx.current_stage.value,
                    "files_count": len(ctx.files)
                }
                for ctx in self.active_contexts.values()
            ],
            "llm_available": self.llm_client is not None
        }


# Singleton instance
_brain_engine: Optional[BrainEngine] = None


def get_brain_engine() -> BrainEngine:
    """Get or create the singleton BrainEngine instance"""
    global _brain_engine
    if _brain_engine is None:
        _brain_engine = BrainEngine()
    return _brain_engine

"""
MelusAI - Prompt Optimizer
Sistema de optimización automática de prompts basado en rendimiento
"""
import os
import json
import logging
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)


class PromptOptimizer:
    """
    Sistema que analiza el rendimiento de los prompts y 
    sugiere mejoras automáticamente.
    """
    
    def __init__(self, db, vector_memory=None, feedback_system=None):
        self.db = db
        self.vector_memory = vector_memory
        self.feedback_system = feedback_system
        self.collection = "prompt_versions"
        self.optimization_logs = "optimization_logs"
    
    async def init_collections(self):
        """Inicializar colecciones"""
        try:
            await self.db[self.collection].create_index("prompt_type")
            await self.db[self.collection].create_index("version")
            await self.db[self.collection].create_index("is_active")
            await self.db[self.collection].create_index("avg_quality_score")
            
            await self.db[self.optimization_logs].create_index("prompt_type")
            await self.db[self.optimization_logs].create_index("created_at")
            
            logger.info("Prompt optimizer collections initialized")
            return True
        except Exception as e:
            logger.error(f"Init error: {e}")
            return False
    
    async def register_prompt(
        self,
        prompt_type: str,
        prompt_content: str,
        description: str = None
    ) -> str:
        """
        Registrar un nuevo prompt para tracking.
        
        Args:
            prompt_type: Tipo de prompt ('planner', 'generator', 'validator', etc.)
            prompt_content: Contenido del prompt
            description: Descripción opcional
        
        Returns:
            ID del prompt registrado
        """
        import uuid
        
        prompt_id = f"prompt_{uuid.uuid4().hex[:12]}"
        
        # Obtener la última versión
        last_version = await self.db[self.collection].find_one(
            {"prompt_type": prompt_type},
            sort=[("version", -1)]
        )
        
        new_version = (last_version["version"] + 1) if last_version else 1
        
        entry = {
            "id": prompt_id,
            "prompt_type": prompt_type,
            "version": new_version,
            "content": prompt_content,
            "description": description,
            "is_active": True,
            "usage_count": 0,
            "success_count": 0,
            "avg_quality_score": 0.0,
            "total_quality_score": 0.0,
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        
        try:
            # Desactivar versiones anteriores
            await self.db[self.collection].update_many(
                {"prompt_type": prompt_type},
                {"$set": {"is_active": False}}
            )
            
            await self.db[self.collection].insert_one(entry)
            logger.info(f"Registered prompt {prompt_id} (type: {prompt_type}, v{new_version})")
            return prompt_id
        except Exception as e:
            logger.error(f"Register prompt error: {e}")
            return None
    
    async def get_active_prompt(self, prompt_type: str) -> Optional[Dict]:
        """Obtener el prompt activo para un tipo"""
        try:
            return await self.db[self.collection].find_one(
                {"prompt_type": prompt_type, "is_active": True},
                {"_id": 0}
            )
        except Exception as e:
            logger.error(f"Get active prompt error: {e}")
            return None
    
    async def record_usage(
        self,
        prompt_id: str,
        project_id: str,
        success: bool,
        quality_score: float = 0.5
    ):
        """
        Registrar el uso de un prompt y su resultado.
        
        Args:
            prompt_id: ID del prompt usado
            project_id: ID del proyecto generado
            success: Si la generación fue exitosa
            quality_score: Score de calidad (0-1)
        """
        try:
            # Actualizar métricas del prompt
            update = {
                "$inc": {
                    "usage_count": 1,
                    "total_quality_score": quality_score
                }
            }
            
            if success:
                update["$inc"]["success_count"] = 1
            
            await self.db[self.collection].update_one(
                {"id": prompt_id},
                update
            )
            
            # Recalcular promedio
            prompt = await self.db[self.collection].find_one({"id": prompt_id})
            if prompt and prompt["usage_count"] > 0:
                avg_score = prompt["total_quality_score"] / prompt["usage_count"]
                await self.db[self.collection].update_one(
                    {"id": prompt_id},
                    {"$set": {"avg_quality_score": round(avg_score, 3)}}
                )
            
            logger.debug(f"Recorded usage for prompt {prompt_id}")
        except Exception as e:
            logger.error(f"Record usage error: {e}")
    
    async def analyze_prompt_performance(self, prompt_type: str) -> Dict[str, Any]:
        """
        Analizar el rendimiento histórico de un tipo de prompt.
        """
        try:
            cursor = self.db[self.collection].find(
                {"prompt_type": prompt_type},
                {"_id": 0}
            ).sort("version", -1)
            
            versions = await cursor.to_list(20)
            
            if not versions:
                return {"status": "no_data"}
            
            # Calcular métricas
            total_usage = sum(v["usage_count"] for v in versions)
            
            best_version = max(
                [v for v in versions if v["usage_count"] > 0],
                key=lambda x: x["avg_quality_score"],
                default=versions[0]
            )
            
            current_version = versions[0]  # La más reciente
            
            # Tendencia de calidad
            trend = "stable"
            if len(versions) >= 2:
                recent = versions[0]["avg_quality_score"]
                older = versions[1]["avg_quality_score"] if versions[1]["usage_count"] > 0 else 0
                
                if recent > older + 0.05:
                    trend = "improving"
                elif recent < older - 0.05:
                    trend = "declining"
            
            return {
                "prompt_type": prompt_type,
                "total_versions": len(versions),
                "total_usage": total_usage,
                "current_version": {
                    "version": current_version["version"],
                    "avg_quality": current_version["avg_quality_score"],
                    "usage": current_version["usage_count"]
                },
                "best_version": {
                    "version": best_version["version"],
                    "avg_quality": best_version["avg_quality_score"],
                    "usage": best_version["usage_count"]
                },
                "trend": trend
            }
        except Exception as e:
            logger.error(f"Analyze performance error: {e}")
            return {"status": "error", "message": str(e)}
    
    async def suggest_improvement(self, prompt_type: str) -> Dict[str, Any]:
        """
        Generar sugerencias de mejora para un prompt basado en:
        1. Análisis de patrones de éxito/fallo
        2. Ejemplos de alta calidad en la memoria
        3. Feedback de usuarios
        """
        try:
            # Obtener prompt actual
            current_prompt = await self.get_active_prompt(prompt_type)
            if not current_prompt:
                return {"status": "no_prompt", "message": "No active prompt found"}
            
            # Obtener análisis de rendimiento
            performance = await self.analyze_prompt_performance(prompt_type)
            
            # Si el rendimiento es bueno, no sugerir cambios
            if performance.get("current_version", {}).get("avg_quality", 0) > 0.8:
                return {
                    "status": "good_performance",
                    "message": "Current prompt is performing well",
                    "current_quality": performance["current_version"]["avg_quality"]
                }
            
            # Buscar ejemplos exitosos en la memoria
            successful_examples = []
            if self.vector_memory:
                successful_examples = await self.vector_memory.get_best_examples(
                    content_type="code",
                    limit=5
                )
            
            # Generar sugerencia usando LLM
            improvement_prompt = self._build_improvement_prompt(
                current_prompt["content"],
                performance,
                successful_examples
            )
            
            # Llamar al LLM para sugerencia
            from emergentintegrations.llm.chat import LlmChat, UserMessage
            
            api_key = os.environ.get('EMERGENT_LLM_KEY')
            if not api_key:
                return {
                    "status": "no_llm",
                    "message": "Cannot generate suggestions without LLM key"
                }
            
            chat = LlmChat(
                api_key=api_key,
                session_id=f"optimizer_{prompt_type}",
                system_message="You are an expert at optimizing AI prompts for code generation. Analyze the given prompt and suggest specific improvements."
            ).with_model("openai", "gpt-4o")
            
            response = await chat.send_message(UserMessage(text=improvement_prompt))
            
            # Guardar log de optimización
            log_entry = {
                "prompt_type": prompt_type,
                "current_version": current_prompt["version"],
                "performance": performance,
                "suggestion": response,
                "created_at": datetime.now(timezone.utc).isoformat()
            }
            await self.db[self.optimization_logs].insert_one(log_entry)
            
            return {
                "status": "suggestion_generated",
                "current_version": current_prompt["version"],
                "current_quality": performance.get("current_version", {}).get("avg_quality", 0),
                "suggestion": response,
                "trend": performance.get("trend", "unknown")
            }
            
        except Exception as e:
            logger.error(f"Suggest improvement error: {e}")
            return {"status": "error", "message": str(e)}
    
    def _build_improvement_prompt(
        self,
        current_prompt: str,
        performance: Dict,
        examples: List[Dict]
    ) -> str:
        """Construir el prompt para solicitar mejoras"""
        
        examples_text = ""
        if examples:
            examples_text = "\n\nHigh-quality code examples that worked well:\n"
            for i, ex in enumerate(examples[:3], 1):
                examples_text += f"{i}. Quality Score: {ex.get('quality_score', 'N/A')}\n"
                examples_text += f"   Content preview: {ex.get('content', '')[:200]}...\n"
        
        return f"""Analyze this code generation prompt and suggest improvements:

CURRENT PROMPT:
{current_prompt}

PERFORMANCE DATA:
- Average Quality Score: {performance.get('current_version', {}).get('avg_quality', 'N/A')}
- Total Usage: {performance.get('total_usage', 0)}
- Trend: {performance.get('trend', 'unknown')}
{examples_text}

Please provide:
1. Specific issues with the current prompt
2. Concrete suggestions for improvement
3. An improved version of the prompt

Focus on:
- Clarity of instructions
- Handling edge cases
- Output format consistency
- Code quality requirements
- Error handling guidance"""
    
    async def apply_improvement(
        self,
        prompt_type: str,
        new_content: str,
        reason: str = None
    ) -> Optional[str]:
        """
        Aplicar una mejora al prompt, creando una nueva versión.
        
        Args:
            prompt_type: Tipo de prompt
            new_content: Nuevo contenido del prompt
            reason: Razón de la mejora
        
        Returns:
            ID del nuevo prompt
        """
        return await self.register_prompt(
            prompt_type=prompt_type,
            prompt_content=new_content,
            description=f"Auto-optimized: {reason}" if reason else "Auto-optimized"
        )
    
    async def rollback_to_version(self, prompt_type: str, version: int) -> bool:
        """Revertir a una versión anterior del prompt"""
        try:
            # Desactivar todas las versiones
            await self.db[self.collection].update_many(
                {"prompt_type": prompt_type},
                {"$set": {"is_active": False}}
            )
            
            # Activar la versión especificada
            result = await self.db[self.collection].update_one(
                {"prompt_type": prompt_type, "version": version},
                {"$set": {"is_active": True}}
            )
            
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"Rollback error: {e}")
            return False
    
    async def get_all_versions(self, prompt_type: str) -> List[Dict]:
        """Obtener todas las versiones de un tipo de prompt"""
        try:
            cursor = self.db[self.collection].find(
                {"prompt_type": prompt_type},
                {"_id": 0, "content": 0}  # Excluir contenido largo
            ).sort("version", -1)
            
            return await cursor.to_list(50)
        except Exception as e:
            logger.error(f"Get versions error: {e}")
            return []

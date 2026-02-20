"""
MelusAI - Learning Engine
Motor principal de aprendizaje continuo que coordina todos los subsistemas
"""
import os
import json
import logging
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional

from .vector_memory import VectorMemoryStore
from .feedback_system import FeedbackSystem, FeedbackType
from .prompt_optimizer import PromptOptimizer
from .metrics_tracker import MetricsTracker, MetricType

logger = logging.getLogger(__name__)


class LearningEngine:
    """
    Motor de aprendizaje continuo que:
    1. Almacena interacciones exitosas en memoria vectorial
    2. Procesa feedback de usuarios
    3. Optimiza prompts automáticamente
    4. Trackea métricas de rendimiento
    5. Proporciona contexto mejorado para generaciones
    """
    
    def __init__(self, db):
        self.db = db
        self.vector_memory = VectorMemoryStore(db)
        self.feedback_system = FeedbackSystem(db)
        self.prompt_optimizer = PromptOptimizer(db, self.vector_memory, self.feedback_system)
        self.metrics_tracker = MetricsTracker(db)
        
        self.settings_collection = "learning_settings"
        
        # Configuración por defecto
        self.default_settings = {
            "auto_learn": True,
            "min_quality_threshold": 0.6,
            "auto_optimize_prompts": True,
            "optimization_frequency_hours": 24,
            "max_memory_entries": 10000,
            "cleanup_low_quality": True
        }
    
    async def initialize(self):
        """Inicializar todos los subsistemas"""
        try:
            await self.vector_memory.init_collection()
            await self.feedback_system.init_collections()
            await self.prompt_optimizer.init_collections()
            await self.metrics_tracker.init_collections()
            
            # Crear índices para settings
            await self.db[self.settings_collection].create_index("key", unique=True)
            
            # Inicializar settings si no existen
            for key, value in self.default_settings.items():
                await self.db[self.settings_collection].update_one(
                    {"key": key},
                    {"$setOnInsert": {"key": key, "value": value}},
                    upsert=True
                )
            
            logger.info("Learning engine initialized successfully")
            return True
        except Exception as e:
            logger.error(f"Learning engine init error: {e}")
            return False
    
    async def get_setting(self, key: str) -> Any:
        """Obtener un setting"""
        doc = await self.db[self.settings_collection].find_one({"key": key})
        if doc:
            return doc["value"]
        return self.default_settings.get(key)
    
    async def update_setting(self, key: str, value: Any) -> bool:
        """Actualizar un setting"""
        try:
            await self.db[self.settings_collection].update_one(
                {"key": key},
                {"$set": {"value": value}},
                upsert=True
            )
            return True
        except Exception as e:
            logger.error(f"Update setting error: {e}")
            return False
    
    async def learn_from_generation(
        self,
        project_id: str,
        prompt: str,
        plan: Dict[str, Any],
        generated_files: Dict[str, str],
        validation_result: Dict[str, Any],
        generation_time: float,
        user_id: str = None
    ):
        """
        Aprender de una generación completada.
        
        Args:
            project_id: ID del proyecto
            prompt: Prompt original del usuario
            plan: Plan generado
            generated_files: Archivos generados {path: content}
            validation_result: Resultado de validación
            generation_time: Tiempo de generación en segundos
            user_id: ID del usuario
        """
        try:
            auto_learn = await self.get_setting("auto_learn")
            if not auto_learn:
                logger.debug("Auto-learn disabled, skipping")
                return
            
            # Calcular score de calidad inicial basado en validación
            validation_score = validation_result.get("score", 70) / 100.0
            had_errors = not validation_result.get("valid", True)
            
            # Registrar métricas
            await self.metrics_tracker.record_generation_metrics(
                project_id=project_id,
                generation_time_seconds=generation_time,
                files_count=len(generated_files),
                validation_score=validation_score,
                had_errors=had_errors
            )
            
            min_quality = await self.get_setting("min_quality_threshold")
            
            # Si la calidad es suficiente, almacenar en memoria
            if validation_score >= min_quality:
                # Almacenar prompt exitoso
                await self.vector_memory.store(
                    content_type="prompt",
                    content=prompt,
                    metadata={
                        "project_type": plan.get("project_type", "unknown"),
                        "complexity": plan.get("complexity", "medium"),
                        "features": plan.get("features", [])[:5]
                    },
                    project_id=project_id,
                    user_id=user_id,
                    quality_score=validation_score
                )
                
                # Almacenar código generado de alta calidad
                for file_path, content in list(generated_files.items())[:10]:
                    if len(content) > 100:  # Solo archivos con contenido significativo
                        await self.vector_memory.store(
                            content_type="code",
                            content=content[:5000],  # Limitar tamaño
                            metadata={
                                "file_path": file_path,
                                "project_type": plan.get("project_type", "unknown")
                            },
                            project_id=project_id,
                            user_id=user_id,
                            quality_score=validation_score
                        )
                
                logger.info(f"Learned from project {project_id} (quality: {validation_score})")
            else:
                logger.debug(f"Project {project_id} below quality threshold ({validation_score} < {min_quality})")
                
        except Exception as e:
            logger.error(f"Learn from generation error: {e}")
    
    async def learn_from_error(
        self,
        project_id: str,
        error_type: str,
        error_message: str,
        context: Dict[str, Any] = None
    ):
        """
        Aprender de un error para evitarlo en el futuro.
        """
        try:
            # Registrar feedback negativo
            await self.feedback_system.record_error(
                project_id=project_id,
                error_type=error_type,
                error_message=error_message
            )
            
            # Almacenar en memoria con calidad baja
            await self.vector_memory.store(
                content_type="error",
                content=f"Error: {error_type}\n{error_message}",
                metadata={
                    "error_type": error_type,
                    "context": context
                },
                project_id=project_id,
                quality_score=0.1  # Calidad baja para aprender qué evitar
            )
            
            logger.info(f"Learned from error in project {project_id}")
        except Exception as e:
            logger.error(f"Learn from error error: {e}")
    
    async def learn_from_iteration(
        self,
        project_id: str,
        original_code: str,
        user_request: str,
        modified_code: str,
        user_id: str = None
    ):
        """
        Aprender de una iteración/modificación solicitada por el usuario.
        """
        try:
            # Registrar iteración
            await self.feedback_system.record_iteration(
                project_id=project_id,
                iteration_type="modification",
                user_id=user_id
            )
            
            # Almacenar el patrón de modificación
            await self.vector_memory.store(
                content_type="solution",
                content=f"Request: {user_request}\n\nSolution:\n{modified_code[:3000]}",
                metadata={
                    "request": user_request,
                    "original_preview": original_code[:500]
                },
                project_id=project_id,
                user_id=user_id,
                quality_score=0.7  # Asumimos que las iteraciones son valiosas
            )
            
            logger.info(f"Learned from iteration in project {project_id}")
        except Exception as e:
            logger.error(f"Learn from iteration error: {e}")
    
    async def get_enhanced_context(
        self,
        user_prompt: str,
        project_type: str = None
    ) -> Dict[str, Any]:
        """
        Obtener contexto mejorado para una nueva generación basado en
        aprendizajes previos.
        
        Args:
            user_prompt: Prompt del usuario
            project_type: Tipo de proyecto (opcional)
        
        Returns:
            Diccionario con ejemplos y contexto relevante
        """
        try:
            context = {
                "similar_prompts": [],
                "code_examples": [],
                "common_errors": [],
                "solutions": [],
                "recommendations": []
            }
            
            # Buscar prompts similares exitosos
            similar_prompts = await self.vector_memory.search(
                query=user_prompt,
                content_types=["prompt"],
                min_quality=0.6,
                limit=3
            )
            context["similar_prompts"] = [
                {
                    "content": p["content"],
                    "project_type": p["metadata"].get("project_type"),
                    "quality": p["quality_score"]
                }
                for p in similar_prompts
            ]
            
            # Buscar código de ejemplo relevante
            code_examples = await self.vector_memory.search(
                query=user_prompt,
                content_types=["code"],
                min_quality=0.7,
                limit=3
            )
            context["code_examples"] = [
                {
                    "file_path": c["metadata"].get("file_path"),
                    "preview": c["content"][:500],
                    "quality": c["quality_score"]
                }
                for c in code_examples
            ]
            
            # Buscar errores comunes para evitar
            common_errors = await self.vector_memory.search(
                query=user_prompt,
                content_types=["error"],
                limit=3
            )
            context["common_errors"] = [
                {
                    "error_type": e["metadata"].get("error_type"),
                    "message": e["content"][:200]
                }
                for e in common_errors
            ]
            
            # Buscar soluciones previas
            solutions = await self.vector_memory.search(
                query=user_prompt,
                content_types=["solution"],
                min_quality=0.5,
                limit=2
            )
            context["solutions"] = [
                {
                    "request": s["metadata"].get("request"),
                    "preview": s["content"][:300]
                }
                for s in solutions
            ]
            
            # Generar recomendaciones
            if similar_prompts:
                context["recommendations"].append(
                    "Found similar successful projects - using their patterns"
                )
            if common_errors:
                context["recommendations"].append(
                    f"Watch out for common errors: {[e['metadata'].get('error_type') for e in common_errors]}"
                )
            
            return context
        except Exception as e:
            logger.error(f"Get enhanced context error: {e}")
            return {}
    
    async def process_user_rating(
        self,
        project_id: str,
        rating: int,
        user_id: str,
        comment: str = None
    ):
        """
        Procesar rating explícito del usuario.
        """
        try:
            # Registrar rating
            await self.feedback_system.record_explicit_rating(
                project_id=project_id,
                rating=rating,
                user_id=user_id,
                comment=comment
            )
            
            # Obtener el score actualizado
            score = await self.feedback_system.get_project_score(project_id)
            
            if score:
                # Actualizar quality scores en la memoria
                # Buscar entradas relacionadas con este proyecto
                cursor = self.vector_memory.db[self.vector_memory.collection_name].find(
                    {"project_id": project_id}
                )
                
                async for entry in cursor:
                    new_quality = (entry["quality_score"] + score["overall_score"]) / 2
                    await self.vector_memory.update_quality_score(
                        entry["id"],
                        new_quality
                    )
            
            logger.info(f"Processed rating {rating} for project {project_id}")
        except Exception as e:
            logger.error(f"Process rating error: {e}")
    
    async def run_optimization_cycle(self) -> Dict[str, Any]:
        """
        Ejecutar un ciclo de optimización:
        1. Analizar rendimiento de prompts
        2. Generar sugerencias de mejora
        3. Limpiar memoria de baja calidad
        4. Agregar métricas
        """
        try:
            results = {
                "prompt_analysis": {},
                "suggestions": {},
                "cleanup": {},
                "metrics_aggregated": False
            }
            
            auto_optimize = await self.get_setting("auto_optimize_prompts")
            
            # Analizar prompts
            prompt_types = ["planner", "generator", "validator", "fixer", "iterator"]
            
            for ptype in prompt_types:
                analysis = await self.prompt_optimizer.analyze_prompt_performance(ptype)
                results["prompt_analysis"][ptype] = analysis
                
                # Generar sugerencias si el rendimiento es bajo
                if auto_optimize and analysis.get("current_version", {}).get("avg_quality", 1) < 0.6:
                    suggestion = await self.prompt_optimizer.suggest_improvement(ptype)
                    results["suggestions"][ptype] = suggestion
            
            # Limpiar memoria de baja calidad
            cleanup_enabled = await self.get_setting("cleanup_low_quality")
            if cleanup_enabled:
                deleted = await self.vector_memory.delete_low_quality(threshold=0.15)
                results["cleanup"] = {"deleted_entries": deleted}
            
            # Agregar métricas diarias
            results["metrics_aggregated"] = await self.metrics_tracker.aggregate_daily()
            
            logger.info("Optimization cycle completed")
            return results
        except Exception as e:
            logger.error(f"Optimization cycle error: {e}")
            return {"error": str(e)}
    
    async def get_learning_stats(self) -> Dict[str, Any]:
        """
        Obtener estadísticas completas del sistema de aprendizaje.
        """
        try:
            memory_stats = await self.vector_memory.get_stats()
            feedback_stats = await self.feedback_system.get_stats()
            metrics_dashboard = await self.metrics_tracker.get_dashboard_stats()
            
            # Obtener rendimiento de prompts
            prompt_stats = {}
            for ptype in ["planner", "generator", "validator"]:
                prompt_stats[ptype] = await self.prompt_optimizer.analyze_prompt_performance(ptype)
            
            return {
                "memory": memory_stats,
                "feedback": feedback_stats,
                "metrics": metrics_dashboard,
                "prompts": prompt_stats,
                "settings": {
                    "auto_learn": await self.get_setting("auto_learn"),
                    "auto_optimize_prompts": await self.get_setting("auto_optimize_prompts"),
                    "min_quality_threshold": await self.get_setting("min_quality_threshold")
                },
                "generated_at": datetime.now(timezone.utc).isoformat()
            }
        except Exception as e:
            logger.error(f"Get learning stats error: {e}")
            return {"error": str(e)}
    
    async def export_knowledge_base(self) -> Dict[str, Any]:
        """
        Exportar la base de conocimiento para backup o transferencia.
        """
        try:
            # Obtener mejores entradas de cada tipo
            knowledge = {
                "prompts": await self.vector_memory.get_best_examples("prompt", 50),
                "code": await self.vector_memory.get_best_examples("code", 50),
                "solutions": await self.vector_memory.get_best_examples("solution", 20),
                "errors_to_avoid": await self.vector_memory.get_best_examples("error", 20)
            }
            
            # Remover embeddings para reducir tamaño
            for category in knowledge.values():
                for entry in category:
                    entry.pop("embedding", None)
            
            return {
                "version": "1.0",
                "exported_at": datetime.now(timezone.utc).isoformat(),
                "knowledge": knowledge
            }
        except Exception as e:
            logger.error(f"Export error: {e}")
            return {"error": str(e)}

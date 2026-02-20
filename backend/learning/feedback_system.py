"""
MelusAI - Feedback System
Sistema de scoring y feedback de usuarios
"""
import logging
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional
from enum import Enum

logger = logging.getLogger(__name__)


class FeedbackType(str, Enum):
    """Tipos de feedback"""
    EXPLICIT_RATING = "explicit_rating"      # Rating directo del usuario (1-5 estrellas)
    PROJECT_DOWNLOAD = "project_download"     # Usuario descargó el proyecto
    PROJECT_PREVIEW = "project_preview"       # Usuario vio el preview
    ITERATION_REQUEST = "iteration_request"   # Usuario pidió cambios
    ERROR_REPORT = "error_report"            # Usuario reportó error
    REGENERATION = "regeneration"            # Usuario regeneró el proyecto
    TIME_TO_COMPLETE = "time_to_complete"    # Tiempo que tomó el usuario
    WORKSPACE_TIME = "workspace_time"        # Tiempo en workspace


class FeedbackSystem:
    """
    Sistema de feedback para medir la calidad de las generaciones.
    Combina feedback explícito e implícito.
    """
    
    def __init__(self, db):
        self.db = db
        self.collection = "feedback_entries"
        self.project_scores = "project_quality_scores"
    
    async def init_collections(self):
        """Inicializar colecciones e índices"""
        try:
            await self.db[self.collection].create_index("project_id")
            await self.db[self.collection].create_index("user_id")
            await self.db[self.collection].create_index("feedback_type")
            await self.db[self.collection].create_index("created_at")
            
            await self.db[self.project_scores].create_index("project_id", unique=True)
            await self.db[self.project_scores].create_index("overall_score")
            
            logger.info("Feedback collections initialized")
            return True
        except Exception as e:
            logger.error(f"Init collections error: {e}")
            return False
    
    async def record_feedback(
        self,
        project_id: str,
        feedback_type: FeedbackType,
        value: Any,
        user_id: str = None,
        metadata: Dict = None
    ) -> str:
        """
        Registrar feedback sobre un proyecto.
        
        Args:
            project_id: ID del proyecto
            feedback_type: Tipo de feedback
            value: Valor del feedback (rating, duración, etc.)
            user_id: ID del usuario
            metadata: Metadatos adicionales
        
        Returns:
            ID del feedback registrado
        """
        import uuid
        
        feedback_id = f"fb_{uuid.uuid4().hex[:12]}"
        
        entry = {
            "id": feedback_id,
            "project_id": project_id,
            "user_id": user_id,
            "feedback_type": feedback_type.value,
            "value": value,
            "metadata": metadata or {},
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        
        try:
            await self.db[self.collection].insert_one(entry)
            
            # Actualizar score del proyecto
            await self._update_project_score(project_id)
            
            logger.info(f"Recorded feedback {feedback_id} for project {project_id}")
            return feedback_id
        except Exception as e:
            logger.error(f"Record feedback error: {e}")
            return None
    
    async def record_explicit_rating(
        self,
        project_id: str,
        rating: int,
        user_id: str,
        comment: str = None
    ) -> str:
        """
        Registrar rating explícito del usuario (1-5 estrellas).
        """
        if not 1 <= rating <= 5:
            rating = max(1, min(5, rating))
        
        return await self.record_feedback(
            project_id=project_id,
            feedback_type=FeedbackType.EXPLICIT_RATING,
            value=rating,
            user_id=user_id,
            metadata={"comment": comment} if comment else None
        )
    
    async def record_download(self, project_id: str, user_id: str = None) -> str:
        """Registrar que el usuario descargó el proyecto"""
        return await self.record_feedback(
            project_id=project_id,
            feedback_type=FeedbackType.PROJECT_DOWNLOAD,
            value=1,
            user_id=user_id
        )
    
    async def record_preview(self, project_id: str, duration_seconds: int = 0) -> str:
        """Registrar que el usuario vio el preview"""
        return await self.record_feedback(
            project_id=project_id,
            feedback_type=FeedbackType.PROJECT_PREVIEW,
            value=duration_seconds
        )
    
    async def record_iteration(
        self,
        project_id: str,
        iteration_type: str,
        user_id: str = None
    ) -> str:
        """Registrar solicitud de iteración/cambio"""
        return await self.record_feedback(
            project_id=project_id,
            feedback_type=FeedbackType.ITERATION_REQUEST,
            value=1,
            user_id=user_id,
            metadata={"iteration_type": iteration_type}
        )
    
    async def record_error(
        self,
        project_id: str,
        error_type: str,
        error_message: str
    ) -> str:
        """Registrar error reportado"""
        return await self.record_feedback(
            project_id=project_id,
            feedback_type=FeedbackType.ERROR_REPORT,
            value=1,
            metadata={
                "error_type": error_type,
                "error_message": error_message
            }
        )
    
    async def record_regeneration(self, project_id: str, reason: str = None) -> str:
        """Registrar regeneración del proyecto (indica insatisfacción)"""
        return await self.record_feedback(
            project_id=project_id,
            feedback_type=FeedbackType.REGENERATION,
            value=1,
            metadata={"reason": reason} if reason else None
        )
    
    async def _update_project_score(self, project_id: str):
        """
        Calcular y actualizar el score de calidad del proyecto.
        Score combinado de feedback explícito e implícito.
        """
        try:
            # Obtener todos los feedbacks del proyecto
            feedbacks = await self.db[self.collection].find(
                {"project_id": project_id}
            ).to_list(100)
            
            if not feedbacks:
                return
            
            # Calcular scores por categoría
            scores = {
                "explicit_avg": 0,
                "download_count": 0,
                "preview_count": 0,
                "iteration_count": 0,
                "error_count": 0,
                "regeneration_count": 0
            }
            
            explicit_ratings = []
            
            for fb in feedbacks:
                fb_type = fb["feedback_type"]
                value = fb["value"]
                
                if fb_type == FeedbackType.EXPLICIT_RATING.value:
                    explicit_ratings.append(value)
                elif fb_type == FeedbackType.PROJECT_DOWNLOAD.value:
                    scores["download_count"] += 1
                elif fb_type == FeedbackType.PROJECT_PREVIEW.value:
                    scores["preview_count"] += 1
                elif fb_type == FeedbackType.ITERATION_REQUEST.value:
                    scores["iteration_count"] += 1
                elif fb_type == FeedbackType.ERROR_REPORT.value:
                    scores["error_count"] += 1
                elif fb_type == FeedbackType.REGENERATION.value:
                    scores["regeneration_count"] += 1
            
            # Calcular promedio de ratings explícitos
            if explicit_ratings:
                scores["explicit_avg"] = sum(explicit_ratings) / len(explicit_ratings)
            
            # Calcular score general (0-1)
            # Pesos: rating explícito (40%), downloads (20%), previews (10%), 
            #        iteraciones (-15%), errores (-10%), regeneraciones (-5%)
            
            explicit_score = scores["explicit_avg"] / 5.0 if scores["explicit_avg"] > 0 else 0.5
            download_bonus = min(scores["download_count"] * 0.05, 0.2)
            preview_bonus = min(scores["preview_count"] * 0.02, 0.1)
            iteration_penalty = min(scores["iteration_count"] * 0.03, 0.15)
            error_penalty = min(scores["error_count"] * 0.05, 0.2)
            regeneration_penalty = min(scores["regeneration_count"] * 0.1, 0.2)
            
            overall_score = (
                explicit_score * 0.4 +
                0.5 * 0.4 +  # Base score
                download_bonus +
                preview_bonus -
                iteration_penalty -
                error_penalty -
                regeneration_penalty
            )
            
            # Clamp to 0-1
            overall_score = max(0.0, min(1.0, overall_score))
            
            # Guardar score
            await self.db[self.project_scores].update_one(
                {"project_id": project_id},
                {"$set": {
                    "project_id": project_id,
                    "overall_score": round(overall_score, 3),
                    "breakdown": scores,
                    "feedback_count": len(feedbacks),
                    "updated_at": datetime.now(timezone.utc).isoformat()
                }},
                upsert=True
            )
            
            logger.debug(f"Updated score for {project_id}: {overall_score}")
            
        except Exception as e:
            logger.error(f"Update project score error: {e}")
    
    async def get_project_score(self, project_id: str) -> Optional[Dict]:
        """Obtener score de calidad de un proyecto"""
        try:
            score = await self.db[self.project_scores].find_one(
                {"project_id": project_id},
                {"_id": 0}
            )
            return score
        except Exception as e:
            logger.error(f"Get project score error: {e}")
            return None
    
    async def get_project_feedbacks(
        self,
        project_id: str,
        feedback_types: List[FeedbackType] = None
    ) -> List[Dict]:
        """Obtener todos los feedbacks de un proyecto"""
        try:
            filter_query = {"project_id": project_id}
            if feedback_types:
                filter_query["feedback_type"] = {
                    "$in": [ft.value for ft in feedback_types]
                }
            
            cursor = self.db[self.collection].find(
                filter_query,
                {"_id": 0}
            ).sort("created_at", -1)
            
            return await cursor.to_list(100)
        except Exception as e:
            logger.error(f"Get feedbacks error: {e}")
            return []
    
    async def get_high_quality_projects(
        self,
        min_score: float = 0.7,
        limit: int = 20
    ) -> List[Dict]:
        """Obtener proyectos de alta calidad para aprendizaje"""
        try:
            cursor = self.db[self.project_scores].find(
                {"overall_score": {"$gte": min_score}},
                {"_id": 0}
            ).sort("overall_score", -1).limit(limit)
            
            return await cursor.to_list(length=limit)
        except Exception as e:
            logger.error(f"Get high quality projects error: {e}")
            return []
    
    async def get_stats(self) -> Dict[str, Any]:
        """Obtener estadísticas del sistema de feedback"""
        try:
            total_feedback = await self.db[self.collection].count_documents({})
            total_scores = await self.db[self.project_scores].count_documents({})
            
            # Distribución de scores
            pipeline = [
                {"$bucket": {
                    "groupBy": "$overall_score",
                    "boundaries": [0, 0.3, 0.5, 0.7, 0.9, 1.01],
                    "default": "other",
                    "output": {"count": {"$sum": 1}}
                }}
            ]
            
            score_distribution = {}
            async for doc in self.db[self.project_scores].aggregate(pipeline):
                score_distribution[str(doc["_id"])] = doc["count"]
            
            # Feedback por tipo
            type_pipeline = [
                {"$group": {
                    "_id": "$feedback_type",
                    "count": {"$sum": 1}
                }}
            ]
            
            feedback_by_type = {}
            async for doc in self.db[self.collection].aggregate(type_pipeline):
                feedback_by_type[doc["_id"]] = doc["count"]
            
            return {
                "total_feedbacks": total_feedback,
                "total_scored_projects": total_scores,
                "score_distribution": score_distribution,
                "feedback_by_type": feedback_by_type
            }
        except Exception as e:
            logger.error(f"Stats error: {e}")
            return {}

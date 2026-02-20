"""
MelusAI - Metrics Tracker
Sistema de seguimiento de métricas de rendimiento
"""
import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Any, Optional
from enum import Enum

logger = logging.getLogger(__name__)


class MetricType(str, Enum):
    """Tipos de métricas"""
    GENERATION_TIME = "generation_time"
    TOKEN_USAGE = "token_usage"
    FILES_GENERATED = "files_generated"
    ERROR_RATE = "error_rate"
    VALIDATION_SCORE = "validation_score"
    USER_SATISFACTION = "user_satisfaction"
    ITERATION_COUNT = "iteration_count"
    FIRST_TRY_SUCCESS = "first_try_success"


class MetricsTracker:
    """
    Sistema de tracking de métricas para analizar rendimiento
    y detectar anomalías.
    """
    
    def __init__(self, db):
        self.db = db
        self.collection = "metrics"
        self.daily_aggregates = "metrics_daily"
    
    async def init_collections(self):
        """Inicializar colecciones e índices"""
        try:
            await self.db[self.collection].create_index("metric_type")
            await self.db[self.collection].create_index("project_id")
            await self.db[self.collection].create_index("timestamp")
            await self.db[self.collection].create_index([
                ("metric_type", 1),
                ("timestamp", -1)
            ])
            
            await self.db[self.daily_aggregates].create_index("date", unique=True)
            
            logger.info("Metrics collections initialized")
            return True
        except Exception as e:
            logger.error(f"Init error: {e}")
            return False
    
    async def record_metric(
        self,
        metric_type: MetricType,
        value: float,
        project_id: str = None,
        user_id: str = None,
        metadata: Dict = None
    ) -> str:
        """
        Registrar una métrica.
        
        Args:
            metric_type: Tipo de métrica
            value: Valor numérico
            project_id: ID del proyecto relacionado
            user_id: ID del usuario
            metadata: Datos adicionales
        
        Returns:
            ID de la métrica registrada
        """
        import uuid
        
        metric_id = f"metric_{uuid.uuid4().hex[:12]}"
        
        entry = {
            "id": metric_id,
            "metric_type": metric_type.value,
            "value": value,
            "project_id": project_id,
            "user_id": user_id,
            "metadata": metadata or {},
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        try:
            await self.db[self.collection].insert_one(entry)
            logger.debug(f"Recorded metric {metric_type.value}: {value}")
            return metric_id
        except Exception as e:
            logger.error(f"Record metric error: {e}")
            return None
    
    async def record_generation_metrics(
        self,
        project_id: str,
        generation_time_seconds: float,
        files_count: int,
        tokens_used: int = 0,
        validation_score: float = 0.0,
        had_errors: bool = False,
        iteration_count: int = 0
    ):
        """
        Registrar métricas completas de una generación de proyecto.
        """
        metrics = [
            (MetricType.GENERATION_TIME, generation_time_seconds),
            (MetricType.FILES_GENERATED, files_count),
            (MetricType.TOKEN_USAGE, tokens_used),
            (MetricType.VALIDATION_SCORE, validation_score),
            (MetricType.ERROR_RATE, 1.0 if had_errors else 0.0),
            (MetricType.ITERATION_COUNT, iteration_count),
            (MetricType.FIRST_TRY_SUCCESS, 0.0 if had_errors else 1.0)
        ]
        
        for metric_type, value in metrics:
            await self.record_metric(
                metric_type=metric_type,
                value=value,
                project_id=project_id
            )
    
    async def get_metric_stats(
        self,
        metric_type: MetricType,
        days: int = 7
    ) -> Dict[str, Any]:
        """
        Obtener estadísticas de una métrica en los últimos N días.
        """
        try:
            cutoff = datetime.now(timezone.utc) - timedelta(days=days)
            cutoff_str = cutoff.isoformat()
            
            pipeline = [
                {
                    "$match": {
                        "metric_type": metric_type.value,
                        "timestamp": {"$gte": cutoff_str}
                    }
                },
                {
                    "$group": {
                        "_id": None,
                        "count": {"$sum": 1},
                        "avg": {"$avg": "$value"},
                        "min": {"$min": "$value"},
                        "max": {"$max": "$value"},
                        "sum": {"$sum": "$value"}
                    }
                }
            ]
            
            result = None
            async for doc in self.db[self.collection].aggregate(pipeline):
                result = doc
            
            if not result:
                return {
                    "metric_type": metric_type.value,
                    "days": days,
                    "count": 0,
                    "avg": 0,
                    "min": 0,
                    "max": 0,
                    "sum": 0
                }
            
            return {
                "metric_type": metric_type.value,
                "days": days,
                "count": result["count"],
                "avg": round(result["avg"], 3),
                "min": round(result["min"], 3),
                "max": round(result["max"], 3),
                "sum": round(result["sum"], 3)
            }
        except Exception as e:
            logger.error(f"Get stats error: {e}")
            return {"error": str(e)}
    
    async def get_trend(
        self,
        metric_type: MetricType,
        days: int = 14
    ) -> Dict[str, Any]:
        """
        Obtener tendencia de una métrica dividida por día.
        """
        try:
            cutoff = datetime.now(timezone.utc) - timedelta(days=days)
            cutoff_str = cutoff.isoformat()
            
            pipeline = [
                {
                    "$match": {
                        "metric_type": metric_type.value,
                        "timestamp": {"$gte": cutoff_str}
                    }
                },
                {
                    "$addFields": {
                        "date": {"$substr": ["$timestamp", 0, 10]}
                    }
                },
                {
                    "$group": {
                        "_id": "$date",
                        "avg": {"$avg": "$value"},
                        "count": {"$sum": 1}
                    }
                },
                {"$sort": {"_id": 1}}
            ]
            
            daily_data = []
            async for doc in self.db[self.collection].aggregate(pipeline):
                daily_data.append({
                    "date": doc["_id"],
                    "avg": round(doc["avg"], 3),
                    "count": doc["count"]
                })
            
            # Calcular tendencia
            trend = "stable"
            if len(daily_data) >= 2:
                first_half = daily_data[:len(daily_data)//2]
                second_half = daily_data[len(daily_data)//2:]
                
                first_avg = sum(d["avg"] for d in first_half) / len(first_half) if first_half else 0
                second_avg = sum(d["avg"] for d in second_half) / len(second_half) if second_half else 0
                
                change = second_avg - first_avg
                if abs(change) > first_avg * 0.1:  # >10% change
                    trend = "increasing" if change > 0 else "decreasing"
            
            return {
                "metric_type": metric_type.value,
                "days": days,
                "trend": trend,
                "daily_data": daily_data
            }
        except Exception as e:
            logger.error(f"Get trend error: {e}")
            return {"error": str(e)}
    
    async def detect_anomalies(
        self,
        metric_type: MetricType,
        threshold_std: float = 2.0
    ) -> List[Dict]:
        """
        Detectar anomalías en una métrica (valores fuera de N desviaciones estándar).
        """
        try:
            # Obtener últimos 100 valores
            cursor = self.db[self.collection].find(
                {"metric_type": metric_type.value},
                {"_id": 0}
            ).sort("timestamp", -1).limit(100)
            
            entries = await cursor.to_list(100)
            
            if len(entries) < 10:
                return []
            
            # Calcular media y desviación estándar
            values = [e["value"] for e in entries]
            mean = sum(values) / len(values)
            variance = sum((v - mean) ** 2 for v in values) / len(values)
            std = variance ** 0.5
            
            if std == 0:
                return []
            
            # Encontrar anomalías
            anomalies = []
            for entry in entries:
                z_score = abs(entry["value"] - mean) / std
                if z_score > threshold_std:
                    anomalies.append({
                        "id": entry["id"],
                        "value": entry["value"],
                        "z_score": round(z_score, 2),
                        "timestamp": entry["timestamp"],
                        "project_id": entry.get("project_id")
                    })
            
            return anomalies[:20]  # Limitar a 20
        except Exception as e:
            logger.error(f"Detect anomalies error: {e}")
            return []
    
    async def get_project_metrics(self, project_id: str) -> Dict[str, Any]:
        """
        Obtener todas las métricas de un proyecto.
        """
        try:
            cursor = self.db[self.collection].find(
                {"project_id": project_id},
                {"_id": 0}
            )
            
            metrics = await cursor.to_list(50)
            
            # Agrupar por tipo
            grouped = {}
            for m in metrics:
                mtype = m["metric_type"]
                if mtype not in grouped:
                    grouped[mtype] = []
                grouped[mtype].append({
                    "value": m["value"],
                    "timestamp": m["timestamp"]
                })
            
            return {
                "project_id": project_id,
                "metrics_count": len(metrics),
                "by_type": grouped
            }
        except Exception as e:
            logger.error(f"Get project metrics error: {e}")
            return {"error": str(e)}
    
    async def aggregate_daily(self) -> bool:
        """
        Agregar métricas del día anterior para reportes.
        Se debería ejecutar una vez al día.
        """
        try:
            yesterday = datetime.now(timezone.utc) - timedelta(days=1)
            date_str = yesterday.strftime("%Y-%m-%d")
            
            # Verificar si ya existe
            existing = await self.db[self.daily_aggregates].find_one({"date": date_str})
            if existing:
                logger.info(f"Daily aggregate for {date_str} already exists")
                return True
            
            # Calcular agregados
            start = yesterday.replace(hour=0, minute=0, second=0).isoformat()
            end = yesterday.replace(hour=23, minute=59, second=59).isoformat()
            
            pipeline = [
                {
                    "$match": {
                        "timestamp": {"$gte": start, "$lte": end}
                    }
                },
                {
                    "$group": {
                        "_id": "$metric_type",
                        "count": {"$sum": 1},
                        "avg": {"$avg": "$value"},
                        "min": {"$min": "$value"},
                        "max": {"$max": "$value"},
                        "sum": {"$sum": "$value"}
                    }
                }
            ]
            
            aggregates = {}
            async for doc in self.db[self.collection].aggregate(pipeline):
                aggregates[doc["_id"]] = {
                    "count": doc["count"],
                    "avg": round(doc["avg"], 3),
                    "min": round(doc["min"], 3),
                    "max": round(doc["max"], 3),
                    "sum": round(doc["sum"], 3)
                }
            
            await self.db[self.daily_aggregates].insert_one({
                "date": date_str,
                "aggregates": aggregates,
                "created_at": datetime.now(timezone.utc).isoformat()
            })
            
            logger.info(f"Created daily aggregate for {date_str}")
            return True
        except Exception as e:
            logger.error(f"Aggregate daily error: {e}")
            return False
    
    async def get_dashboard_stats(self) -> Dict[str, Any]:
        """
        Obtener estadísticas para el dashboard.
        """
        try:
            # Estadísticas generales
            total_metrics = await self.db[self.collection].count_documents({})
            
            # Métricas de los últimos 7 días
            week_stats = {}
            for metric_type in MetricType:
                stats = await self.get_metric_stats(metric_type, days=7)
                week_stats[metric_type.value] = stats
            
            # Proyectos generados hoy
            today_start = datetime.now(timezone.utc).replace(
                hour=0, minute=0, second=0
            ).isoformat()
            
            today_count = await self.db[self.collection].count_documents({
                "metric_type": MetricType.GENERATION_TIME.value,
                "timestamp": {"$gte": today_start}
            })
            
            return {
                "total_metrics": total_metrics,
                "projects_today": today_count,
                "week_stats": week_stats,
                "generated_at": datetime.now(timezone.utc).isoformat()
            }
        except Exception as e:
            logger.error(f"Dashboard stats error: {e}")
            return {"error": str(e)}

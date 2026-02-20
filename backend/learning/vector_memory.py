"""
MelusAI - Vector Memory Store
Sistema de memoria persistente usando embeddings vectoriales
"""
import os
import json
import logging
import hashlib
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict

logger = logging.getLogger(__name__)

@dataclass
class MemoryEntry:
    """Representa una entrada en la memoria vectorial"""
    id: str
    content_type: str  # 'prompt', 'code', 'feedback', 'error', 'solution'
    content: str
    embedding: List[float]
    metadata: Dict[str, Any]
    project_id: Optional[str]
    user_id: Optional[str]
    quality_score: float
    created_at: str
    
    def to_dict(self) -> Dict:
        return asdict(self)


class VectorMemoryStore:
    """
    Almacén de memoria vectorial para el aprendizaje continuo.
    Utiliza embeddings para encontrar contexto relevante.
    """
    
    def __init__(self, db):
        self.db = db
        self.collection_name = "learning_memory"
        self.embedding_dim = 1536  # OpenAI text-embedding-3-small dimension
        self._openai_client = None
        
    async def init_collection(self):
        """Inicializar la colección con índices necesarios"""
        try:
            # Crear índices para búsquedas eficientes
            await self.db[self.collection_name].create_index("content_type")
            await self.db[self.collection_name].create_index("quality_score")
            await self.db[self.collection_name].create_index("created_at")
            await self.db[self.collection_name].create_index("project_id")
            await self.db[self.collection_name].create_index("user_id")
            
            # Índice compuesto para búsquedas comunes
            await self.db[self.collection_name].create_index([
                ("content_type", 1),
                ("quality_score", -1)
            ])
            
            logger.info("Vector memory collection initialized")
            return True
        except Exception as e:
            logger.error(f"Failed to init collection: {e}")
            return False
    
    def _get_openai_client(self):
        """Lazy load OpenAI client"""
        if self._openai_client is None:
            try:
                from openai import OpenAI
                api_key = os.environ.get('EMERGENT_LLM_KEY')
                if api_key:
                    self._openai_client = OpenAI(
                        api_key=api_key,
                        base_url="https://api.emergent.sh/v1"
                    )
            except Exception as e:
                logger.warning(f"Could not initialize OpenAI client: {e}")
        return self._openai_client
    
    async def get_embedding(self, text: str) -> List[float]:
        """Obtener embedding de texto usando OpenAI text-embedding-3-small"""
        try:
            client = self._get_openai_client()
            if client is None:
                logger.warning("No OpenAI client, using fallback embedding")
                return self._fallback_embedding(text)
            
            # Truncar texto si es muy largo (max 8191 tokens aprox)
            truncated_text = text[:8000].replace("\n", " ").strip()
            
            if not truncated_text:
                return self._fallback_embedding(text)
            
            # Llamar a OpenAI Embeddings API
            response = client.embeddings.create(
                model="text-embedding-3-small",
                input=truncated_text,
                encoding_format="float"
            )
            
            embedding = response.data[0].embedding
            logger.debug(f"Generated embedding with {len(embedding)} dimensions")
            return embedding
            
        except Exception as e:
            logger.warning(f"OpenAI embedding failed, using fallback: {e}")
            return self._fallback_embedding(text)
    
    def _fallback_embedding(self, text: str) -> List[float]:
        """Embedding basado en hash para fallback"""
        import hashlib
        import struct
        
        # Crear un embedding determinístico basado en el contenido
        text_hash = hashlib.sha256(text.encode()).digest()
        
        # Expandir a 1536 dimensiones usando el hash como semilla
        embedding = []
        for i in range(0, self.embedding_dim, 8):
            # Rotar el hash para generar más valores
            rotated = hashlib.sha256(text_hash + struct.pack('i', i)).digest()
            for j in range(0, min(8, self.embedding_dim - i)):
                # Normalizar a [-1, 1]
                val = (rotated[j % 32] / 127.5) - 1.0
                embedding.append(val)
        
        return embedding[:self.embedding_dim]
    
    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calcular similitud coseno entre dos vectores"""
        import math
        
        if not vec1 or not vec2 or len(vec1) != len(vec2):
            return 0.0
        
        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        norm1 = math.sqrt(sum(a * a for a in vec1))
        norm2 = math.sqrt(sum(b * b for b in vec2))
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return dot_product / (norm1 * norm2)
    
    async def store(
        self,
        content_type: str,
        content: str,
        metadata: Dict[str, Any] = None,
        project_id: str = None,
        user_id: str = None,
        quality_score: float = 0.5
    ) -> str:
        """
        Almacenar una nueva entrada en la memoria.
        
        Args:
            content_type: Tipo de contenido ('prompt', 'code', 'feedback', 'error', 'solution')
            content: El contenido a almacenar
            metadata: Metadatos adicionales
            project_id: ID del proyecto relacionado
            user_id: ID del usuario
            quality_score: Puntuación de calidad (0-1)
        
        Returns:
            ID de la entrada creada
        """
        import uuid
        
        entry_id = f"mem_{uuid.uuid4().hex[:12]}"
        embedding = await self.get_embedding(content)
        
        entry = MemoryEntry(
            id=entry_id,
            content_type=content_type,
            content=content,
            embedding=embedding,
            metadata=metadata or {},
            project_id=project_id,
            user_id=user_id,
            quality_score=quality_score,
            created_at=datetime.now(timezone.utc).isoformat()
        )
        
        try:
            await self.db[self.collection_name].insert_one(entry.to_dict())
            logger.info(f"Stored memory entry: {entry_id} (type: {content_type})")
            return entry_id
        except Exception as e:
            logger.error(f"Failed to store memory: {e}")
            return None
    
    async def search(
        self,
        query: str,
        content_types: List[str] = None,
        min_quality: float = 0.3,
        limit: int = 10,
        project_id: str = None
    ) -> List[Dict[str, Any]]:
        """
        Buscar entradas similares en la memoria.
        
        Args:
            query: Texto de búsqueda
            content_types: Filtrar por tipos de contenido
            min_quality: Puntuación mínima de calidad
            limit: Número máximo de resultados
            project_id: Filtrar por proyecto
        
        Returns:
            Lista de entradas similares con scores
        """
        query_embedding = await self.get_embedding(query)
        
        # Construir filtro
        filter_query = {"quality_score": {"$gte": min_quality}}
        
        if content_types:
            filter_query["content_type"] = {"$in": content_types}
        
        if project_id:
            filter_query["project_id"] = project_id
        
        try:
            # Obtener candidatos
            cursor = self.db[self.collection_name].find(
                filter_query,
                {"_id": 0}
            ).limit(limit * 5)  # Obtener más para filtrar por similitud
            
            candidates = await cursor.to_list(length=limit * 5)
            
            # Calcular similitud y ordenar
            results = []
            for entry in candidates:
                similarity = self._cosine_similarity(
                    query_embedding,
                    entry.get("embedding", [])
                )
                
                if similarity > 0.3:  # Umbral mínimo de similitud
                    results.append({
                        "id": entry["id"],
                        "content_type": entry["content_type"],
                        "content": entry["content"],
                        "metadata": entry.get("metadata", {}),
                        "quality_score": entry["quality_score"],
                        "similarity": similarity,
                        "created_at": entry["created_at"]
                    })
            
            # Ordenar por similitud
            results.sort(key=lambda x: x["similarity"], reverse=True)
            
            return results[:limit]
            
        except Exception as e:
            logger.error(f"Search error: {e}")
            return []
    
    async def get_by_id(self, entry_id: str) -> Optional[Dict]:
        """Obtener entrada por ID"""
        try:
            entry = await self.db[self.collection_name].find_one(
                {"id": entry_id},
                {"_id": 0, "embedding": 0}
            )
            return entry
        except Exception as e:
            logger.error(f"Get by ID error: {e}")
            return None
    
    async def update_quality_score(self, entry_id: str, new_score: float) -> bool:
        """Actualizar puntuación de calidad de una entrada"""
        try:
            result = await self.db[self.collection_name].update_one(
                {"id": entry_id},
                {"$set": {"quality_score": new_score}}
            )
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"Update quality error: {e}")
            return False
    
    async def get_best_examples(
        self,
        content_type: str,
        limit: int = 5
    ) -> List[Dict]:
        """Obtener los mejores ejemplos de un tipo de contenido"""
        try:
            cursor = self.db[self.collection_name].find(
                {"content_type": content_type},
                {"_id": 0, "embedding": 0}
            ).sort("quality_score", -1).limit(limit)
            
            return await cursor.to_list(length=limit)
        except Exception as e:
            logger.error(f"Get best examples error: {e}")
            return []
    
    async def delete_low_quality(self, threshold: float = 0.2) -> int:
        """Eliminar entradas de baja calidad"""
        try:
            result = await self.db[self.collection_name].delete_many(
                {"quality_score": {"$lt": threshold}}
            )
            logger.info(f"Deleted {result.deleted_count} low-quality entries")
            return result.deleted_count
        except Exception as e:
            logger.error(f"Delete low quality error: {e}")
            return 0
    
    async def get_stats(self) -> Dict[str, Any]:
        """Obtener estadísticas de la memoria"""
        try:
            total = await self.db[self.collection_name].count_documents({})
            
            # Contar por tipo
            pipeline = [
                {"$group": {
                    "_id": "$content_type",
                    "count": {"$sum": 1},
                    "avg_quality": {"$avg": "$quality_score"}
                }}
            ]
            
            type_stats = {}
            async for doc in self.db[self.collection_name].aggregate(pipeline):
                type_stats[doc["_id"]] = {
                    "count": doc["count"],
                    "avg_quality": round(doc["avg_quality"], 3)
                }
            
            return {
                "total_entries": total,
                "by_type": type_stats
            }
        except Exception as e:
            logger.error(f"Stats error: {e}")
            return {"total_entries": 0, "by_type": {}}

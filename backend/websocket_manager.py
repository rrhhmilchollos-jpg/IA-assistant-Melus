"""
MelusAI - WebSocket Manager
Sistema de streaming en tiempo real para logs del pipeline
"""
import asyncio
import json
import logging
from datetime import datetime, timezone
from typing import Dict, Set, Optional, Any
from fastapi import WebSocket, WebSocketDisconnect
from enum import Enum

logger = logging.getLogger(__name__)


class LogLevel(str, Enum):
    """Niveles de log para el streaming"""
    INFO = "info"
    SUCCESS = "success"
    WARNING = "warning"
    ERROR = "error"
    PHASE = "phase"
    FILE = "file"
    PROGRESS = "progress"


class ConnectionManager:
    """
    Gestor de conexiones WebSocket para streaming de logs.
    Permite múltiples clientes escuchando el mismo proyecto.
    """
    
    def __init__(self):
        # Mapeo: project_id -> set de conexiones WebSocket
        self.active_connections: Dict[str, Set[WebSocket]] = {}
        # Historial de logs por proyecto (últimos 100)
        self.log_history: Dict[str, list] = {}
        self.max_history = 100
    
    async def connect(self, websocket: WebSocket, project_id: str):
        """Conectar un cliente al stream de un proyecto"""
        await websocket.accept()
        
        if project_id not in self.active_connections:
            self.active_connections[project_id] = set()
        
        self.active_connections[project_id].add(websocket)
        logger.info(f"WebSocket connected for project {project_id}")
        
        # Enviar historial de logs existentes
        if project_id in self.log_history:
            for log in self.log_history[project_id]:
                try:
                    await websocket.send_json(log)
                except:
                    pass
    
    def disconnect(self, websocket: WebSocket, project_id: str):
        """Desconectar un cliente"""
        if project_id in self.active_connections:
            self.active_connections[project_id].discard(websocket)
            if not self.active_connections[project_id]:
                del self.active_connections[project_id]
        logger.info(f"WebSocket disconnected for project {project_id}")
    
    async def broadcast(self, project_id: str, message: Dict[str, Any]):
        """Enviar mensaje a todos los clientes conectados a un proyecto"""
        # Agregar timestamp
        message["timestamp"] = datetime.now(timezone.utc).isoformat()
        
        # Guardar en historial
        if project_id not in self.log_history:
            self.log_history[project_id] = []
        self.log_history[project_id].append(message)
        
        # Limitar historial
        if len(self.log_history[project_id]) > self.max_history:
            self.log_history[project_id] = self.log_history[project_id][-self.max_history:]
        
        # Enviar a todos los clientes conectados
        if project_id in self.active_connections:
            disconnected = set()
            for websocket in self.active_connections[project_id]:
                try:
                    await websocket.send_json(message)
                except Exception as e:
                    logger.warning(f"Failed to send to websocket: {e}")
                    disconnected.add(websocket)
            
            # Limpiar conexiones rotas
            for ws in disconnected:
                self.active_connections[project_id].discard(ws)
    
    async def send_log(
        self,
        project_id: str,
        level: LogLevel,
        message: str,
        details: Optional[Dict] = None
    ):
        """Enviar un log al stream de un proyecto"""
        log_entry = {
            "type": "log",
            "level": level.value,
            "message": message,
            "details": details or {}
        }
        await self.broadcast(project_id, log_entry)
    
    async def send_phase_update(
        self,
        project_id: str,
        phase: str,
        status: str,
        progress: float = None
    ):
        """Enviar actualización de fase"""
        update = {
            "type": "phase_update",
            "phase": phase,
            "status": status,
        }
        if progress is not None:
            update["progress"] = progress
        await self.broadcast(project_id, update)
    
    async def send_file_created(
        self,
        project_id: str,
        file_path: str,
        file_size: int = 0
    ):
        """Notificar creación de archivo"""
        await self.broadcast(project_id, {
            "type": "file_created",
            "file_path": file_path,
            "file_size": file_size
        })
    
    async def send_error(
        self,
        project_id: str,
        error_type: str,
        error_message: str
    ):
        """Enviar error al stream"""
        await self.broadcast(project_id, {
            "type": "error",
            "error_type": error_type,
            "error_message": error_message
        })
    
    async def send_complete(
        self,
        project_id: str,
        preview_url: str = None,
        files_count: int = 0
    ):
        """Notificar que el proyecto está completo"""
        await self.broadcast(project_id, {
            "type": "complete",
            "preview_url": preview_url,
            "files_count": files_count
        })
    
    def clear_history(self, project_id: str):
        """Limpiar historial de un proyecto"""
        if project_id in self.log_history:
            del self.log_history[project_id]
    
    def get_connection_count(self, project_id: str = None) -> int:
        """Obtener número de conexiones activas"""
        if project_id:
            return len(self.active_connections.get(project_id, set()))
        return sum(len(conns) for conns in self.active_connections.values())


# Instancia global del manager
ws_manager = ConnectionManager()


async def websocket_endpoint(websocket: WebSocket, project_id: str):
    """
    Endpoint WebSocket para streaming de logs de un proyecto.
    
    Uso desde frontend:
    const ws = new WebSocket('ws://host/api/ws/projects/{project_id}');
    ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        console.log(data.type, data.message);
    };
    """
    await ws_manager.connect(websocket, project_id)
    
    try:
        while True:
            # Esperar mensajes del cliente (pings, comandos)
            data = await websocket.receive_text()
            
            try:
                message = json.loads(data)
                
                # Manejar ping
                if message.get("type") == "ping":
                    await websocket.send_json({"type": "pong"})
                
                # Otros comandos del cliente pueden añadirse aquí
                
            except json.JSONDecodeError:
                pass
                
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket, project_id)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        ws_manager.disconnect(websocket, project_id)

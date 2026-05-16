"""
WebSocket Manager for real-time updates.
"""
import asyncio
import json
from datetime import datetime
from typing import Dict, List, Set
from fastapi import WebSocket, WebSocketDisconnect

from ..utils.logging import get_logger

logger = get_logger("websocket")


class ConnectionManager:
    """Manages WebSocket connections for real-time updates."""
    
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}
        self.agent_subscribers: Dict[str, Set[str]] = {}  # agent_id -> set of connection_ids
    
    async def connect(self, websocket: WebSocket, client_id: str):
        await websocket.accept()
        if client_id not in self.active_connections:
            self.active_connections[client_id] = []
        self.active_connections[client_id].append(websocket)
        logger.info(f"WebSocket connected: {client_id}")
    
    def disconnect(self, websocket: WebSocket, client_id: str):
        if client_id in self.active_connections:
            if websocket in self.active_connections[client_id]:
                self.active_connections[client_id].remove(websocket)
            if not self.active_connections[client_id]:
                del self.active_connections[client_id]
        logger.info(f"WebSocket disconnected: {client_id}")
    
    async def send_personal_message(self, message: dict, websocket: WebSocket):
        try:
            await websocket.send_json(message)
        except Exception as e:
            logger.error(f"WebSocket send error: {e}")
    
    async def broadcast(self, message: dict):
        disconnected = []
        for client_id, connections in self.active_connections.items():
            for conn in connections:
                try:
                    await conn.send_json(message)
                except Exception:
                    disconnected.append((client_id, conn))
        
        # Clean up disconnected
        for client_id, conn in disconnected:
            self.disconnect(conn, client_id)
    
    async def broadcast_agent_update(self, agent_id: str, data: dict):
        """Broadcast update to all clients subscribed to an agent."""
        message = {
            "type": "agent_update",
            "agent_id": agent_id,
            "timestamp": datetime.utcnow().isoformat(),
            "data": data,
        }
        await self.broadcast(message)
    
    async def broadcast_vitals(self, vitals: dict):
        message = {
            "type": "vitals_update",
            "timestamp": datetime.utcnow().isoformat(),
            "data": vitals,
        }
        await self.broadcast(message)
    
    async def broadcast_alert(self, alert: dict):
        message = {
            "type": "alert",
            "timestamp": datetime.utcnow().isoformat(),
            "data": alert,
        }
        await self.broadcast(message)


manager = ConnectionManager()

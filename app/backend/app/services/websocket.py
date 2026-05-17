"""
Enterprise WebSocket Manager for real-time updates.
Supports topic-based subscriptions, heartbeats, and connection rooms.
"""
import asyncio
import json
from datetime import datetime
from typing import Dict, List, Optional, Set
from fastapi import WebSocket

from ..utils.logging import get_logger

logger = get_logger("websocket")

HEARTBEAT_INTERVAL = 15  # seconds


class ConnectionManager:
    """Production WebSocket manager with topic pub/sub and heartbeat monitoring."""

    def __init__(self):
        # client_id -> list of websockets
        self.active_connections: Dict[str, WebSocket] = {}
        # topic -> set of client_ids (e.g. "swarm", "agent:guardian")
        self.subscriptions: Dict[str, Set[str]] = {}
        self._heartbeat_task: Optional[asyncio.Task] = None

    # ── Lifecycle ────────────────────────────────────

    async def connect(self, websocket: WebSocket, client_id: str):
        await websocket.accept()
        self.active_connections[client_id] = websocket
        # Auto-subscribe to global swarm channel
        self._subscribe(client_id, "swarm")
        logger.info(f"WS connected: {client_id} | total={len(self.active_connections)}")
        await self.send_to(client_id, {
            "type": "connected",
            "client_id": client_id,
            "timestamp": datetime.utcnow().isoformat(),
            "message": "Connected to AfriSwarm real-time channel",
        })
        if not self._heartbeat_task or self._heartbeat_task.done():
            self._heartbeat_task = asyncio.create_task(self._heartbeat_loop())

    def disconnect(self, client_id: str):
        self.active_connections.pop(client_id, None)
        for subscribers in self.subscriptions.values():
            subscribers.discard(client_id)
        logger.info(f"WS disconnected: {client_id} | total={len(self.active_connections)}")

    # ── Subscriptions ────────────────────────────────

    def _subscribe(self, client_id: str, topic: str):
        if topic not in self.subscriptions:
            self.subscriptions[topic] = set()
        self.subscriptions[topic].add(client_id)

    def subscribe_to_agent(self, client_id: str, agent_id: str):
        self._subscribe(client_id, f"agent:{agent_id}")

    # ── Messaging ────────────────────────────────────

    async def send_to(self, client_id: str, message: dict):
        ws = self.active_connections.get(client_id)
        if ws:
            try:
                await ws.send_json(message)
            except Exception as e:
                logger.warning(f"Send failed to {client_id}: {e}")
                self.disconnect(client_id)

    async def broadcast(self, message: dict, topic: str = "swarm"):
        """Broadcast to all clients subscribed to a topic."""
        subscribers = self.subscriptions.get(topic, set()).copy()
        dead = []
        for client_id in subscribers:
            ws = self.active_connections.get(client_id)
            if ws:
                try:
                    await ws.send_json(message)
                except Exception:
                    dead.append(client_id)
        for c in dead:
            self.disconnect(c)

    async def broadcast_swarm(self, event_type: str, data: dict):
        """Broadcast a typed swarm event to all connected clients."""
        await self.broadcast({
            "type": event_type,
            "timestamp": datetime.utcnow().isoformat(),
            "data": data,
        })

    async def broadcast_agent_update(self, agent_id: str, data: dict):
        """Broadcast agent-specific updates to swarm channel (visible to all)."""
        await self.broadcast_swarm("agent_update", {"agent_id": agent_id, **data})

    async def broadcast_vitals(self, vitals: dict):
        await self.broadcast_swarm("vitals_update", vitals)

    async def broadcast_alert(self, alert: dict):
        await self.broadcast_swarm("alert", alert)

    async def broadcast_swarm_message(self, response: dict, agents_involved: list):
        """Broadcast swarm chat response with full metadata."""
        await self.broadcast_swarm("swarm_response", {
            "response": response,
            "agents_involved": agents_involved,
        })

    # ── Heartbeat ────────────────────────────────────

    async def _heartbeat_loop(self):
        while True:
            await asyncio.sleep(HEARTBEAT_INTERVAL)
            if not self.active_connections:
                continue
            ping = {"type": "ping", "timestamp": datetime.utcnow().isoformat()}
            dead = []
            for client_id, ws in list(self.active_connections.items()):
                try:
                    await ws.send_json(ping)
                except Exception:
                    dead.append(client_id)
            for c in dead:
                self.disconnect(c)

    @property
    def connection_count(self) -> int:
        return len(self.active_connections)


manager = ConnectionManager()

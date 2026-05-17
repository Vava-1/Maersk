"""
AfriSwarm Maersk Resilience Swarm - FastAPI Backend
Production-grade API with WebSockets, authentication, and full agent orchestration.
"""
from __future__ import annotations

import asyncio
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Depends, status, BackgroundTasks, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
import os

from .config import settings
from .state import (
    SwarmState, AgentHealth, AgentStatus, SystemVitals, TaskPriority,
    AgentMessage, DisruptionEvent, RouteAlternative, ComplianceCheck,
    ConfidenceScore, ROIMetric, KnowledgeEntry
)
from .graphs.swarm_graph import swarm_graph, initialize_swarm_state, _registry
from .services.websocket import manager
from .utils.logging import get_logger, AgentLogger
from .utils.security import (
    verify_password, get_password_hash, create_access_token,
    decode_access_token, check_permission, api_rate_limiter,
    auth_rate_limiter
)

logger = get_logger("main")


# ───────────────────────────────────────────────
# Pydantic Request/Response Models
# ───────────────────────────────────────────────
class ChatRequest(BaseModel):
    message: str
    user_id: str = "default_user"
    priority: str = "medium"
    context: Dict[str, Any] = Field(default_factory=dict)


class ChatResponse(BaseModel):
    response: Dict[str, Any]
    trace_id: str
    confidence: Optional[float]
    estimated_roi: float
    agents_involved: List[str]
    human_escalation_required: bool
    timestamp: str


class AgentQueryRequest(BaseModel):
    agent_id: str
    query: str
    context: Dict[str, Any] = Field(default_factory=dict)


class TaskRequest(BaseModel):
    title: str
    description: str
    agent_id: Optional[str] = None
    priority: str = "medium"
    context: Dict[str, Any] = Field(default_factory=dict)


class LoginRequest(BaseModel):
    username: str
    password: str


class SwarmStatusResponse(BaseModel):
    active_agents: int
    total_agents: int
    system_health: float
    tasks_in_progress: int
    tasks_completed: int
    swarm_consciousness: float
    uptime_seconds: float
    version: str


# ───────────────────────────────────────────────
# Authentication
# ───────────────────────────────────────────────
security = HTTPBearer(auto_error=False)

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    if not credentials:
        return {"user_id": "anonymous", "role": "viewer"}
    
    token = credentials.credentials
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    return {"user_id": payload.get("sub", "unknown"), "role": payload.get("role", "viewer")}


# ───────────────────────────────────────────────
# Global State
# ───────────────────────────────────────────────
class SwarmRuntime:
    """Global runtime state for the swarm."""
    
    def __init__(self):
        self.state = initialize_swarm_state()
        self.messages: List[Dict] = []
        self.started_at = datetime.utcnow()
        self.is_running = True
        self._monitoring_task = None
    
    @property
    def uptime_seconds(self) -> float:
        return (datetime.utcnow() - self.started_at).total_seconds()
    
    async def start_monitoring(self):
        """Start background monitoring."""
        while self.is_running:
            try:
                # Update system vitals
                vitals = self.state.get("system_vitals", SystemVitals())
                vitals.overall_health_score = self._calculate_health()
                vitals.active_agents = sum(
                    1 for h in self.state.get("agent_health", {}).values()
                    if h.status not in [AgentStatus.OFFLINE, AgentStatus.ERROR]
                )
                vitals.total_agents = 14
                vitals.uptime_hours = self.uptime_seconds / 3600
                vitals.timestamp = datetime.utcnow()
                
                self.state["system_vitals"] = vitals
                
                # Broadcast vitals via WebSocket
                try:
                    await manager.broadcast_vitals({
                        "overall_health": vitals.overall_health_score,
                        "active_agents": vitals.active_agents,
                        "consciousness": vitals.swarm_consciousness_index,
                        "tasks_in_progress": vitals.tasks_in_progress,
                        "uptime_hours": vitals.uptime_hours,
                    })
                except Exception:
                    pass
                
                await asyncio.sleep(5)  # 5-second monitoring cycle
            except Exception as e:
                logger.error(f"Monitoring error: {e}")
                await asyncio.sleep(10)
    
    def _calculate_health(self) -> float:
        health_scores = []
        for h in self.state.get("agent_health", {}).values():
            if h.status == AgentStatus.HEALTHY:
                health_scores.append(1.0)
            elif h.status == AgentStatus.IDLE:
                health_scores.append(0.9)
            elif h.status == AgentStatus.BUSY:
                health_scores.append(0.7)
            elif h.status == AgentStatus.DEGRADED:
                health_scores.append(0.4)
            elif h.status == AgentStatus.RECOVERING:
                health_scores.append(0.5)
            else:
                health_scores.append(0.1)
        
        return round(sum(health_scores) / max(len(health_scores), 1), 3)


# Global runtime
runtime = SwarmRuntime()


# ───────────────────────────────────────────────
# Lifespan
# ───────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(f"=== {settings.APP_NAME} v{settings.APP_VERSION} starting ===")
    
    # Start background monitoring
    monitoring_task = asyncio.create_task(runtime.start_monitoring())
    
    yield
    
    # Shutdown
    logger.info("=== AfriSwarm shutting down ===")
    runtime.is_running = False
    monitoring_task.cancel()
    try:
        await monitoring_task
    except asyncio.CancelledError:
        pass


# ───────────────────────────────────────────────
# Create App
# ───────────────────────────────────────────────
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Production-grade autonomous multi-agent system for global shipping and logistics",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global API Rate Limiter Middleware
@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    # Only rate limit API paths
    if request.url.path.startswith("/api/") and not request.url.path.startswith("/api/v1/auth"):
        client_ip = request.client.host if request.client else "unknown"
        if not api_rate_limiter.is_allowed(client_ip):
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={"detail": "Too many requests. Please slow down."}
            )
    return await call_next(request)



# ───────────────────────────────────────────────
# Health & Status Endpoints
# ───────────────────────────────────────────────

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "version": settings.APP_VERSION,
        "timestamp": datetime.utcnow().isoformat(),
        "uptime_seconds": runtime.uptime_seconds,
        "agents_active": sum(
            1 for h in runtime.state.get("agent_health", {}).values()
            if h.status not in [AgentStatus.OFFLINE, AgentStatus.ERROR]
        ),
    }


@app.get("/api/v1/status", response_model=SwarmStatusResponse)
async def swarm_status():
    vitals = runtime.state.get("system_vitals", SystemVitals())
    return SwarmStatusResponse(
        active_agents=vitals.active_agents,
        total_agents=14,
        system_health=vitals.overall_health_score,
        tasks_in_progress=vitals.tasks_in_progress,
        tasks_completed=vitals.tasks_completed_last_hour,
        swarm_consciousness=vitals.swarm_consciousness_index,
        uptime_seconds=runtime.uptime_seconds,
        version=settings.APP_VERSION,
    )


# ───────────────────────────────────────────────
# Authentication Endpoints
# ───────────────────────────────────────────────

@app.post("/api/v1/auth/login")
async def login(request: LoginRequest, req: Request):
    client_ip = req.client.host if req.client else "unknown"
    if not auth_rate_limiter.is_allowed(f"auth_{client_ip}"):
        raise HTTPException(status_code=429, detail="Too many login attempts")

    if request.username == settings.ADMIN_USERNAME and request.password == settings.ADMIN_PASSWORD:
        token = create_access_token({
            "sub": request.username,
            "role": "admin",
            "iat": datetime.utcnow(),
        })
        return {"access_token": token, "token_type": "bearer", "role": "admin"}
    
    if request.username == settings.OPERATOR_USERNAME and request.password == settings.OPERATOR_PASSWORD:
        token = create_access_token({
            "sub": request.username,
            "role": "operator",
            "iat": datetime.utcnow(),
        })
        return {"access_token": token, "token_type": "bearer", "role": "operator"}
    
    raise HTTPException(status_code=401, detail="Invalid credentials")



# ───────────────────────────────────────────────
# Agent Management Endpoints
# ───────────────────────────────────────────────

@app.get("/api/v1/agents")
async def list_agents():
    """List all 14 agents with their current status."""
    agents = []
    for agent_id, health in runtime.state.get("agent_health", {}).items():
        agent_obj = _registry.agents.get(agent_id)
        agents.append({
            "agent_id": health.agent_id,
            "agent_name": health.agent_name,
            "status": health.status.value,
            "consciousness_score": health.consciousness_score,
            "version": health.version,
            "uptime_seconds": health.uptime_seconds,
            "tasks_completed": health.total_tasks_completed,
            "tasks_failed": health.total_tasks_failed,
            "avg_response_ms": health.average_response_time_ms,
            "active_tools": health.active_tools,
            "description": agent_obj.DESCRIPTION if agent_obj else "",
            "capabilities": agent_obj.CAPABILITIES if agent_obj else [],
            "recent_errors": health.recent_errors[-5:] if health.recent_errors else [],
        })
    return {"agents": agents, "total": len(agents), "timestamp": datetime.utcnow().isoformat()}


@app.get("/api/v1/agents/{agent_id}")
async def get_agent(agent_id: str):
    """Get detailed status of a specific agent."""
    health = runtime.state.get("agent_health", {}).get(agent_id)
    if not health:
        raise HTTPException(status_code=404, detail=f"Agent {agent_id} not found")
    
    agent_obj = _registry.agents.get(agent_id)
    return {
        "agent_id": health.agent_id,
        "agent_name": health.agent_name,
        "status": health.status.value,
        "consciousness_score": health.consciousness_score,
        "cpu_usage": health.cpu_usage_percent,
        "memory_usage_mb": health.memory_usage_mb,
        "version": health.version,
        "uptime_seconds": health.uptime_seconds,
        "tasks_completed": health.total_tasks_completed,
        "tasks_failed": health.total_tasks_failed,
        "avg_response_ms": health.average_response_time_ms,
        "consecutive_failures": health.consecutive_failures,
        "active_tools": health.active_tools,
        "healing_actions": health.healing_actions_taken,
        "description": agent_obj.DESCRIPTION if agent_obj else "",
        "capabilities": agent_obj.CAPABILITIES if agent_obj else [],
    }


@app.post("/api/v1/agents/{agent_id}/chat")
async def chat_with_agent(agent_id: str, request: AgentQueryRequest):
    """Chat with a specific agent (Swarm Integrated)."""
    if agent_id not in _registry.agents:
        raise HTTPException(status_code=404, detail=f"Agent {agent_id} not found")
    
    agent = _registry.agents[agent_id]
    
    # Update state for swarm execution
    runtime.state["user_query"] = f"[Direct Message to {agent.agent_name}]: {request.query}"
    runtime.state["context"] = request.context
    
    try:
        # Route through the full swarm so the agent can gather context from others
        result = await swarm_graph.ainvoke(runtime.state)
        runtime.state = result
        
        return {
            "agent_id": agent_id,
            "response": result.get("final_response", {}),
            "timestamp": datetime.utcnow().isoformat(),
        }
    except Exception as e:
        logger.error(f"Agent chat error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/agents/{agent_id}/heal")
async def heal_agent(agent_id: str):
    """Trigger healing for a specific agent."""
    guardian = _registry.agents["guardian"]
    runtime.state["context"] = {"heal_target": agent_id}
    
    try:
        result = await guardian.process(runtime.state)
        return {
            "agent_id": agent_id,
            "healing_initiated": True,
            "timestamp": datetime.utcnow().isoformat(),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ───────────────────────────────────────────────
# Swarm Orchestration Endpoints
# ───────────────────────────────────────────────

@app.post("/api/v1/swarm/chat", response_model=ChatResponse)
async def swarm_chat(request: ChatRequest):
    """Send a message to the swarm - orchestrated by the Orchestrator."""
    trace_id = str(uuid.uuid4())[:8]
    
    try:
        # Set up state
        runtime.state["user_query"] = request.message
        runtime.state["user_id"] = request.user_id
        runtime.state["priority"] = request.priority
        runtime.state["context"] = request.context
        runtime.state["trace_id"] = trace_id
        runtime.state["iteration_count"] = 0
        
        # Execute through LangGraph
        result = await swarm_graph.ainvoke(runtime.state)
        
        # Update runtime state
        runtime.state = result
        
        # Build response
        final = result.get("final_response", {})
        agents_involved = final.get("agents_involved", [])
        
        return ChatResponse(
            response=final,
            trace_id=trace_id,
            confidence=result.get("confidence").score if result.get("confidence") else None,
            estimated_roi=result.get("estimated_roi_impact", 0),
            agents_involved=agents_involved,
            human_escalation_required=result.get("human_escalation_required", False),
            timestamp=datetime.utcnow().isoformat(),
        )
    
    except Exception as e:
        logger.error(f"Swarm chat error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ───────────────────────────────────────────────
# Guardian Endpoints
# ───────────────────────────────────────────────

@app.get("/api/v1/guardian/vitals")
async def get_vitals():
    """Get current system vitals."""
    vitals = runtime.state.get("system_vitals", SystemVitals())
    return vitals.model_dump() if hasattr(vitals, "model_dump") else dict(vitals)


@app.get("/api/v1/guardian/healing-log")
async def get_healing_log(limit: int = 100):
    """Get recent healing actions."""
    healing = runtime.state.get("healing_actions", [])
    return {
        "healing_actions": [
            h.model_dump() if hasattr(h, "model_dump") else dict(h)
            for h in healing[-limit:]
        ],
        "total": len(healing),
    }


@app.get("/api/v1/guardian/consciousness")
async def get_consciousness_scores():
    """Get consciousness scores for all agents."""
    scores = {}
    for agent_id, health in runtime.state.get("agent_health", {}).items():
        scores[agent_id] = health.consciousness_score
    return {"consciousness_scores": scores, "average": round(sum(scores.values()) / max(len(scores), 1), 3)}


@app.get("/api/v1/guardian/alerts")
async def get_active_alerts():
    """Get active alerts."""
    alerts = runtime.state.get("active_alerts", [])
    return {"alerts": alerts, "count": len(alerts)}


# ───────────────────────────────────────────────
# Risk & Disruption Endpoints
# ───────────────────────────────────────────────

@app.get("/api/v1/risk/events")
async def get_risk_events(active_only: bool = True):
    """Get current disruption events."""
    events = runtime.state.get("disruption_events", {})
    if active_only:
        events = {k: v for k, v in events.items() if getattr(v, "is_active", True)}
    
    return {
        "events": [
            e.model_dump() if hasattr(e, "model_dump") else dict(e)
            for e in events.values()
        ],
        "count": len(events),
    }


# ───────────────────────────────────────────────
# Analytics Endpoints
# ───────────────────────────────────────────────

@app.get("/api/v1/analytics/dashboard")
async def get_dashboard(period: str = "24h"):
    """Get analytics dashboard data."""
    analytics_agent = _registry.agents["analytics"]
    runtime.state["context"] = {"period": period}
    
    try:
        result = await analytics_agent.process(runtime.state)
        return result.get("final_response", {}).get("analytics", {})
    except Exception as e:
        logger.error(f"Analytics error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/analytics/trends")
async def get_trends(days: int = 30):
    """Get historical trends."""
    analytics_agent = _registry.agents["analytics"]
    try:
        trends = await analytics_agent.generate_trends(days)
        return {"trends": trends, "days": days}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ───────────────────────────────────────────────
# Africa Specialist Endpoints
# ───────────────────────────────────────────────

@app.get("/api/v1/africa/corridors")
async def get_africa_corridors():
    """Get Africa corridor analysis."""
    africa_agent = _registry.agents["africa_specialist"]
    return {
        "corridors": list(africa_agent.AFRICA_CORRIDORS.keys()),
        "ports": list(africa_agent.AFRICA_PORTS.keys()),
    }


@app.get("/api/v1/africa/corridors/{corridor_id}")
async def get_corridor_detail(corridor_id: str):
    africa_agent = _registry.agents["africa_specialist"]
    runtime.state["context"] = {"corridor_id": corridor_id}
    
    try:
        result = await africa_agent.process(runtime.state)
        return result.get("final_response", {}).get("corridor_analysis", {})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/africa/ports/{port_id}")
async def get_port_detail(port_id: str):
    africa_agent = _registry.agents["africa_specialist"]
    runtime.state["context"] = {"port_id": port_id}
    
    try:
        result = await africa_agent.process(runtime.state)
        return result.get("final_response", {}).get("port_analysis", {})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ───────────────────────────────────────────────
# WebSocket Endpoint
# ───────────────────────────────────────────────

@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str, token: Optional[str] = None):
    # Require authentication for websocket
    if not token or not decode_access_token(token):
        await websocket.accept()
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Unauthorized")
        return

    await manager.connect(websocket, client_id)
    try:
        while True:
            data = await websocket.receive_json()
            msg_type = data.get("type", "message")
            
            if msg_type == "chat":
                # Process chat through swarm
                runtime.state["user_query"] = data.get("message", "")
                runtime.state["user_id"] = client_id
                runtime.state["context"] = data.get("context", {})
                
                result = await swarm_graph.ainvoke(runtime.state)
                runtime.state = result
                
                await manager.send_personal_message({
                    "type": "chat_response",
                    "data": result.get("final_response", {}),
                    "trace_id": str(uuid.uuid4())[:8],
                }, websocket)
            
            elif msg_type == "subscribe_agent":
                agent_id = data.get("agent_id")
                await manager.send_personal_message({
                    "type": "subscription_confirmed",
                    "agent_id": agent_id,
                }, websocket)
            
            elif msg_type == "ping":
                await manager.send_personal_message({
                    "type": "pong",
                    "timestamp": datetime.utcnow().isoformat(),
                }, websocket)
    
    except WebSocketDisconnect:
        manager.disconnect(websocket, client_id)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(websocket, client_id)


# ───────────────────────────────────────────────
# Demo Scenarios Endpoints
# ───────────────────────────────────────────────

DEMO_SCENARIOS = {
    "red_sea_crisis": {
        "name": "Red Sea Shipping Crisis",
        "description": "Houthi attacks disrupting Red Sea transit - reroute via Cape",
        "query": "Red Sea crisis: Find alternative route from Shanghai to Rotterdam",
        "expected_agents": ["orchestrator", "geopolitical_risk", "route_optimizer", "compliance"],
    },
    "eu_cbam_compliance": {
        "name": "EU CBAM Compliance Check",
        "description": "Verify CBAM compliance for steel shipment to EU",
        "query": "Check EU CBAM compliance for steel container from Shanghai to Hamburg",
        "expected_agents": ["orchestrator", "compliance", "esg", "data_integration"],
    },
    "africa_route_optimization": {
        "name": "Africa Route Optimization",
        "description": "Optimize Mombasa to Kampala corridor routing",
        "query": "Optimize shipping route from Mombasa to Kampala for container cargo",
        "expected_agents": ["orchestrator", "route_optimizer", "africa_specialist", "geopolitical_risk"],
    },
    "port_congestion_incident": {
        "name": "Port Congestion Incident",
        "description": "Handle Durban port congestion emergency",
        "query": "Durban port is congested - reroute container to alternative port urgently",
        "expected_agents": ["orchestrator", "incident_response", "route_optimizer", "africa_specialist"],
    },
    "supplier_risk_alert": {
        "name": "Supplier Risk Alert",
        "description": "Assess supplier risk for Lagos port operations",
        "query": "Assess supplier risk for our Lagos port operations partner",
        "expected_agents": ["orchestrator", "supplier_risk", "africa_specialist", "security_audit"],
    },
}


@app.get("/api/v1/demos/scenarios")
async def list_demo_scenarios():
    """List available demo scenarios."""
    return {"scenarios": DEMO_SCENARIOS}


@app.post("/api/v1/demos/run/{scenario_id}")
async def run_demo_scenario(scenario_id: str):
    """Run a demo scenario."""
    scenario = DEMO_SCENARIOS.get(scenario_id)
    if not scenario:
        raise HTTPException(status_code=404, detail=f"Scenario {scenario_id} not found")
    
    # Execute through swarm
    runtime.state["user_query"] = scenario["query"]
    runtime.state["context"] = {"scenario": scenario_id, **scenario}
    
    try:
        result = await swarm_graph.ainvoke(runtime.state)
        runtime.state = result
        
        return {
            "scenario_id": scenario_id,
            "scenario": scenario,
            "result": result.get("final_response", {}),
            "agents_involved": result.get("final_response", {}).get("agents_involved", []),
            "trace_id": result.get("trace_id"),
            "timestamp": datetime.utcnow().isoformat(),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ───────────────────────────────────────────────
# Static Frontend Serving
# ───────────────────────────────────────────────
static_dir = os.path.join(os.path.dirname(__file__), "..", "..", "static")
if os.path.exists(static_dir):
    app.mount("/assets", StaticFiles(directory=os.path.join(static_dir, "assets")), name="assets")
    
    @app.get("/{catchall:path}")
    async def serve_react_app(catchall: str):
        # Serve index.html for all non-API paths to support React Router
        if not catchall.startswith("api/"):
            index_path = os.path.join(static_dir, "index.html")
            if os.path.exists(index_path):
                return FileResponse(index_path)
        raise HTTPException(status_code=404, detail="Not Found")


# ───────────────────────────────────────────────
# Run Server
# ───────────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        workers=settings.WORKERS,
        reload=settings.DEBUG,
    )

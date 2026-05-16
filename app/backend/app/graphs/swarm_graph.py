"""
AfriSwarm LangGraph - The execution graph orchestrating all 14 agents.
Implements hierarchical routing through Orchestrator with Guardian oversight.
"""
import asyncio
from datetime import datetime
from typing import Any, Dict, List, Optional, TypedDict

from langgraph.graph import StateGraph, END

from ..state import SwarmState, AgentHealth, AgentStatus, SystemVitals, TaskStatus
from ..config import settings
from ..utils.logging import get_logger
from ..agents.orchestrator import OrchestratorAgent
from ..agents.guardian import GuardianAgent
from ..agents.geopolitical_risk import GeopoliticalRiskAgent
from ..agents.route_optimizer import RouteOptimizerAgent
from ..agents.compliance import ComplianceAgent
from ..agents.esg import ESGAgent
from ..agents.supplier_risk import SupplierRiskAgent
from ..agents.inventory import InventoryForecasterAgent
from ..agents.incident_response import IncidentResponseAgent
from ..agents.data_integration import DataIntegrationAgent
from ..agents.analytics import AnalyticsAgent
from ..agents.africa_specialist import AfricaSpecialistAgent
from ..agents.security import SecurityAgent
from ..agents.knowledge import KnowledgeAgent


logger = get_logger("swarm_graph")


# ───────────────────────────────────────────────
# Agent Registry
# ───────────────────────────────────────────────
class AgentRegistry:
    """Registry of all 14 AfriSwarm agents."""
    
    def __init__(self):
        self.agents: Dict[str, Any] = {}
        self._initialize_agents()
    
    def _initialize_agents(self):
        """Initialize all 14 agents with default configuration."""
        agent_classes = [
            ("orchestrator", OrchestratorAgent),
            ("guardian", GuardianAgent),
            ("geopolitical_risk", GeopoliticalRiskAgent),
            ("route_optimizer", RouteOptimizerAgent),
            ("compliance", ComplianceAgent),
            ("esg", ESGAgent),
            ("supplier_risk", SupplierRiskAgent),
            ("inventory_forecaster", InventoryForecasterAgent),
            ("incident_response", IncidentResponseAgent),
            ("data_integration", DataIntegrationAgent),
            ("analytics", AnalyticsAgent),
            ("africa_specialist", AfricaSpecialistAgent),
            ("security_audit", SecurityAgent),
            ("knowledge", KnowledgeAgent),
        ]
        
        for agent_id, agent_class in agent_classes:
            try:
                self.agents[agent_id] = agent_class()
                logger.info(f"Agent initialized: {agent_id}")
            except Exception as e:
                logger.error(f"Failed to initialize agent {agent_id}: {e}")
                # Create a minimal fallback
                self.agents[agent_id] = agent_class.__new__(agent_class)
                self.agents[agent_id].agent_id = agent_id
                self.agents[agent_id].agent_name = agent_id


# Global registry
_registry = AgentRegistry()


# ───────────────────────────────────────────────
# Graph Node Functions
# ───────────────────────────────────────────────

async def orchestrator_node(state: SwarmState) -> SwarmState:
    """Orchestrator node - routes tasks and coordinates agents."""
    agent = _registry.agents["orchestrator"]
    try:
        return await agent.process(state)
    except Exception as e:
        logger.error(f"Orchestrator error: {e}")
        state["final_response"] = {"error": str(e), "agent": "orchestrator"}
        return state


async def guardian_node(state: SwarmState) -> SwarmState:
    """Guardian node - monitors and heals the swarm."""
    agent = _registry.agents["guardian"]
    try:
        return await agent.process(state)
    except Exception as e:
        logger.error(f"Guardian error: {e}")
        return state


async def route_optimizer_node(state: SwarmState) -> SwarmState:
    agent = _registry.agents["route_optimizer"]
    try:
        return await agent.process(state)
    except Exception as e:
        logger.error(f"Route optimizer error: {e}")
        return state


async def geopolitical_risk_node(state: SwarmState) -> SwarmState:
    agent = _registry.agents["geopolitical_risk"]
    try:
        return await agent.process(state)
    except Exception as e:
        logger.error(f"Geopolitical risk error: {e}")
        return state


async def compliance_node(state: SwarmState) -> SwarmState:
    agent = _registry.agents["compliance"]
    try:
        return await agent.process(state)
    except Exception as e:
        logger.error(f"Compliance error: {e}")
        return state


async def esg_node(state: SwarmState) -> SwarmState:
    agent = _registry.agents["esg"]
    try:
        return await agent.process(state)
    except Exception as e:
        logger.error(f"ESG error: {e}")
        return state


async def supplier_risk_node(state: SwarmState) -> SwarmState:
    agent = _registry.agents["supplier_risk"]
    try:
        return await agent.process(state)
    except Exception as e:
        logger.error(f"Supplier risk error: {e}")
        return state


async def inventory_node(state: SwarmState) -> SwarmState:
    agent = _registry.agents["inventory_forecaster"]
    try:
        return await agent.process(state)
    except Exception as e:
        logger.error(f"Inventory error: {e}")
        return state


async def incident_response_node(state: SwarmState) -> SwarmState:
    agent = _registry.agents["incident_response"]
    try:
        return await agent.process(state)
    except Exception as e:
        logger.error(f"Incident response error: {e}")
        return state


async def data_integration_node(state: SwarmState) -> SwarmState:
    agent = _registry.agents["data_integration"]
    try:
        return await agent.process(state)
    except Exception as e:
        logger.error(f"Data integration error: {e}")
        return state


async def analytics_node(state: SwarmState) -> SwarmState:
    agent = _registry.agents["analytics"]
    try:
        return await agent.process(state)
    except Exception as e:
        logger.error(f"Analytics error: {e}")
        return state


async def africa_specialist_node(state: SwarmState) -> SwarmState:
    agent = _registry.agents["africa_specialist"]
    try:
        return await agent.process(state)
    except Exception as e:
        logger.error(f"Africa specialist error: {e}")
        return state


async def security_node(state: SwarmState) -> SwarmState:
    agent = _registry.agents["security_audit"]
    try:
        return await agent.process(state)
    except Exception as e:
        logger.error(f"Security error: {e}")
        return state


async def knowledge_node(state: SwarmState) -> SwarmState:
    agent = _registry.agents["knowledge"]
    try:
        return await agent.process(state)
    except Exception as e:
        logger.error(f"Knowledge error: {e}")
        return state


# ───────────────────────────────────────────────
# Routing Logic
# ───────────────────────────────────────────────

def route_by_orchestrator(state: SwarmState) -> str:
    """Determine next agent based on orchestrator decomposition."""
    tasks = state.get("tasks", {})
    pending = [t for t in tasks.values() if t.status == TaskStatus.PENDING]
    
    if not pending:
        return "analytics"
    
    # Route to first pending task's assigned agent
    next_task = pending[0]
    agent_id = next_task.assigned_agent_id
    
    # Validate agent_id maps to a valid node
    valid_nodes = [
        "route_optimizer", "geopolitical_risk", "compliance", "esg",
        "supplier_risk", "inventory_forecaster", "incident_response",
        "data_integration", "africa_specialist", "security_audit", "knowledge"
    ]
    
    return agent_id if agent_id in valid_nodes else "analytics"


def should_continue(state: SwarmState) -> str:
    """Determine if processing should continue or end."""
    iteration = state.get("iteration_count", 0)
    max_iter = state.get("max_iterations", 10)
    
    if iteration >= max_iter:
        return "end"
    
    pending = [t for t in state.get("tasks", {}).values() if t.status == TaskStatus.PENDING]
    if not pending:
        return "end"
    
    return "continue"


def guardian_check(state: SwarmState) -> str:
    """Guardian decides whether to continue or heal."""
    vitals = state.get("system_vitals")
    if vitals and vitals.overall_health_score < 0.3:
        return "heal"
    return "proceed"


# ───────────────────────────────────────────────
# Build the Graph
# ───────────────────────────────────────────────

def build_swarm_graph() -> StateGraph:
    """Build the AfriSwarm LangGraph with all 14 agents."""
    
    # Create graph with SwarmState
    workflow = StateGraph(SwarmState)
    
    # Add all nodes
    workflow.add_node("orchestrator", orchestrator_node)
    workflow.add_node("guardian", guardian_node)
    workflow.add_node("route_optimizer", route_optimizer_node)
    workflow.add_node("geopolitical_risk", geopolitical_risk_node)
    workflow.add_node("compliance", compliance_node)
    workflow.add_node("esg", esg_node)
    workflow.add_node("supplier_risk", supplier_risk_node)
    workflow.add_node("inventory_forecaster", inventory_node)
    workflow.add_node("incident_response", incident_response_node)
    workflow.add_node("data_integration", data_integration_node)
    workflow.add_node("analytics", analytics_node)
    workflow.add_node("africa_specialist", africa_specialist_node)
    workflow.add_node("security_audit", security_node)
    workflow.add_node("knowledge", knowledge_node)
    
    # Define edges
    # Start -> Orchestrator
    workflow.set_entry_point("orchestrator")
    
    # Orchestrator -> Guardian (always check health)
    workflow.add_edge("orchestrator", "guardian")
    
    # Guardian -> routing decision
    workflow.add_conditional_edges(
        "guardian",
        guardian_check,
        {
            "heal": "guardian",  # Loop back for healing
            "proceed": route_by_orchestrator,
        }
    )
    
    # All specialized agents -> Analytics for final aggregation
    for node in [
        "route_optimizer", "geopolitical_risk", "compliance", "esg",
        "supplier_risk", "inventory_forecaster", "incident_response",
        "data_integration", "africa_specialist", "security_audit", "knowledge"
    ]:
        workflow.add_conditional_edges(
            node,
            should_continue,
            {
                "continue": "guardian",  # Back to guardian for health check
                "end": "analytics",
            }
        )
    
    # Analytics -> END
    workflow.add_edge("analytics", END)
    
    return workflow.compile()


# Global graph instance
swarm_graph = build_swarm_graph()


# ───────────────────────────────────────────────
# Initialize Agent Health State
# ───────────────────────────────────────────────

def initialize_swarm_state() -> SwarmState:
    """Initialize the swarm state with all 14 agents."""
    agent_configs = [
        ("orchestrator", "Orchestrator", AgentStatus.IDLE),
        ("guardian", "System Guardian", AgentStatus.HEALTHY),
        ("geopolitical_risk", "Geopolitical Risk Monitor", AgentStatus.IDLE),
        ("route_optimizer", "Route & Logistics Optimizer", AgentStatus.IDLE),
        ("compliance", "Compliance & Regulatory Agent", AgentStatus.IDLE),
        ("esg", "ESG & Sustainability Agent", AgentStatus.IDLE),
        ("supplier_risk", "Supplier Risk & Performance Agent", AgentStatus.IDLE),
        ("inventory_forecaster", "Inventory & Demand Forecaster", AgentStatus.IDLE),
        ("incident_response", "Incident Response & Workflow Executor", AgentStatus.IDLE),
        ("data_integration", "Data Integration & Vision Agent", AgentStatus.IDLE),
        ("analytics", "Analytics & ROI Dashboard Agent", AgentStatus.IDLE),
        ("africa_specialist", "Africa / Emerging Markets Specialist", AgentStatus.IDLE),
        ("security_audit", "Security, Audit & Compliance Guardian", AgentStatus.HEALTHY),
        ("knowledge", "Knowledge & Learning Agent", AgentStatus.IDLE),
    ]
    
    agent_health = {}
    for agent_id, name, status in agent_configs:
        agent_health[agent_id] = AgentHealth(
            agent_id=agent_id,
            agent_name=name,
            status=status,
            consciousness_score=1.0,
            uptime_seconds=0,
            total_tasks_completed=0,
            total_tasks_failed=0,
            average_response_time_ms=0,
        )
    
    return SwarmState(
        session_id=f"session_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
        trace_id=f"trace_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
        timestamp=datetime.utcnow().isoformat(),
        user_query="",
        user_id="system",
        priority="medium",
        context={},
        agent_health=agent_health,
        active_agents=list(agent_health.keys()),
        agent_messages=[],
        tasks={},
        current_task_id=None,
        pending_tasks=[],
        completed_tasks=[],
        failed_tasks=[],
        shipments={},
        route_alternatives={},
        disruption_events={},
        compliance_checks={},
        esg_metrics={},
        supplier_risks={},
        system_vitals=SystemVitals(
            overall_health_score=1.0,
            active_agents=14,
            total_agents=14,
            swarm_consciousness_index=1.0,
        ),
        healing_actions=[],
        active_alerts=[],
        knowledge_entries=[],
        roi_metrics={},
        final_response={},
        reasoning_trace="",
        confidence=None,
        human_escalation_required=False,
        suggested_actions=[],
        estimated_roi_impact=0.0,
        audit_logs=[],
        security_flags=[],
        iteration_count=0,
        max_iterations=10,
        graph_checkpoint_id=None,
    )

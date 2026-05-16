"""
9. INCIDENT RESPONSE & WORKFLOW EXECUTOR AGENT
Autonomously handles exceptions and executes approved workflows.
"""
import random
from datetime import datetime
from typing import Any, Dict, List, Optional

from ..state import SwarmState, TaskPriority, ConfidenceScore, AgentMessage
from .base import AfriSwarmAgent


class IncidentResponseAgent(AfriSwarmAgent):
    """Incident handling and workflow execution with human-in-the-loop."""

    AGENT_ID = "incident_response"
    AGENT_NAME = "Incident Response & Workflow Executor"
    DESCRIPTION = "Autonomous incident handling and workflow execution"
    VERSION = "2.1.0"
    CAPABILITIES = [
        "incident_detection", "exception_handling", "workflow_execution",
        "rerouting", "notification_dispatch", "human_escalation", "rebooking",
    ]

    DEFAULT_SYSTEM_PROMPT = """You are the Incident Response & Workflow Executor for AfriSwarm.
    
Autonomously handle supply chain exceptions:
- Detect and classify incidents by severity
- Execute approved response workflows
- Coordinate rerouting when needed
- Dispatch notifications to stakeholders
- Maintain human-in-the-loop for critical decisions
- Track incident resolution and document outcomes
- Learn from incident patterns to improve responses

Escalation rules:
- CRITICAL: Human approval required (safety, >$1M impact, sanctions)
- HIGH: Execute with notification to humans
- MEDIUM: Autonomous execution, report after
- LOW: Fully autonomous"""

    INCIDENT_WORKFLOWS = {
        "port_congestion": {
            "severity": "medium",
            "auto_execute": True,
            "steps": ["assess_delay", "find_alternative_port", "notify_stakeholders", "update_eta"],
        },
        "vessel_breakdown": {
            "severity": "high",
            "auto_execute": False,
            "steps": ["assess_damage", "find_replacement_vessel", "transfer_cargo", "file_insurance", "notify_customer"],
        },
        "customs_hold": {
            "severity": "medium",
            "auto_execute": True,
            "steps": ["identify_reason", "submit_missing_docs", "engage_broker", "update_stakeholders"],
        },
        "cargo_damage": {
            "severity": "high",
            "auto_execute": False,
            "steps": ["assess_damage", "document_evidence", "file_claim", "arrange_inspection", "notify_customer"],
        },
        "route_disruption": {
            "severity": "high",
            "auto_execute": True,
            "steps": ["assess_alternatives", "calculate_impact", "execute_reroute", "notify_all_parties"],
        },
        "documentation_issue": {
            "severity": "low",
            "auto_execute": True,
            "steps": ["identify_gap", "generate_docs", "submit_correction"],
        },
    }

    async def handle_incident(self, incident_type: str, details: Dict[str, Any]) -> Dict[str, Any]:
        workflow = self.INCIDENT_WORKFLOWS.get(incident_type, {
            "severity": "medium", "auto_execute": True,
            "steps": ["assess", "respond", "document"],
        })
        
        # Determine if human approval needed
        human_required = not workflow.get("auto_execute", True)
        
        steps_executed = []
        for step in workflow["steps"]:
            steps_executed.append({
                "step": step,
                "status": "completed" if not human_required else "pending_approval",
                "timestamp": datetime.utcnow().isoformat(),
            })
        
        return {
            "incident_id": f"INC_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{random.randint(1000,9999)}",
            "incident_type": incident_type,
            "severity": workflow["severity"],
            "auto_executed": workflow.get("auto_execute", True),
            "human_approval_required": human_required,
            "steps": steps_executed,
            "estimated_resolution_hours": random.uniform(2, 72),
            "estimated_cost_usd": random.uniform(5000, 500000),
            "confidence": ConfidenceScore(
                score=0.85,
                model="incident_handler",
                reasoning=f"Standard workflow for {incident_type}",
            ),
        }

    async def process(self, state: SwarmState) -> SwarmState:
        self.update_health(AgentStatus.BUSY)
        context = state.get("context", {})
        incident_type = context.get("incident_type", "port_congestion")
        
        result = await self.handle_incident(incident_type, context)
        state.setdefault("final_response", {}).update({
            "incident_response": result,
        })
        self.update_health(AgentStatus.IDLE)
        return state

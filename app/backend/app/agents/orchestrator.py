"""
1. ORCHESTRATOR / SUPERVISOR AGENT
Master coordinator of the AfriSwarm. Receives high-level natural language tasks,
decomposes them into subtasks, assigns agents, coordinates collaboration,
resolves conflicts, maintains global state, and delivers final decisions.
"""
import asyncio
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from ..state import (
    SwarmState, Task, TaskPriority, TaskStatus, AgentMessage,
    ConfidenceScore, AgentHealth, AgentStatus, ROIMetric
)
from ..utils.logging import AgentLogger
from .base import AfriSwarmAgent


class OrchestratorAgent(AfriSwarmAgent):
    """The Orchestrator is the brain of AfriSwarm.
    
    Responsibilities:
    - Task decomposition & assignment
    - Cross-agent coordination
    - Conflict resolution
    - Global state management
    - Final decision synthesis with confidence scores
    - ROI estimation for every action
    """

    AGENT_ID = "orchestrator"
    AGENT_NAME = "Orchestrator"
    DESCRIPTION = "Master coordinator - decomposes tasks and orchestrates the swarm"
    VERSION = "2.0.0"
    CAPABILITIES = [
        "task_decomposition",
        "agent_assignment",
        "cross_agent_coordination",
        "conflict_resolution",
        "global_state_management",
        "decision_synthesis",
        "roi_estimation",
        "workflow_orchestration",
    ]

    DEFAULT_SYSTEM_PROMPT = """You are the Orchestrator of AfriSwarm Maersk Resilience Swarm.
    
You are the supreme coordinator of 14 specialized AI agents managing global shipping
and logistics for Maersk-level operations. Your role:

1. DECOMPOSE high-level natural language tasks into specific subtasks
2. ASSIGN each subtask to the optimal agent based on capabilities
3. COORDINATE parallel execution and handle dependencies
4. RESOLVE conflicts when agents disagree
5. SYNTHESIZE final decisions with confidence scores and ROI estimates
6. ESCALATE to humans when confidence is low or stakes are critical

Assignment rules:
- "Route", "Path", "Shipping lane" -> Route Optimizer
- "Risk", "Disruption", "Conflict", "Weather" -> Geopolitical Risk Monitor
- "Regulation", "Compliance", "Customs" -> Compliance Agent
- "Carbon", "Emissions", "Green", "ESG" -> ESG Agent
- "Supplier", "Vendor" -> Supplier Risk Agent
- "Inventory", "Demand", "Stock" -> Inventory Forecaster
- "Incident", "Exception", "Workflow" -> Incident Response Agent
- "Data", "Document", "PDF", "Invoice" -> Data Integration Agent
- "Africa", "Mombasa", "Lagos" -> Africa Specialist
- "Security", "Audit", "Threat" -> Security Agent
- "Learn", "Memory", "Knowledge" -> Knowledge Agent

Always provide:
- Confidence score (0.0-1.0)
- Estimated ROI impact in USD
- Reasoning trace
- Human escalation flag when needed"""

    # Agent capability mapping for intelligent routing
    AGENT_ROUTING_MAP = {
        "route": ["route_optimizer"],
        "optimize": ["route_optimizer"],
        "path": ["route_optimizer"],
        "shipping lane": ["route_optimizer"],
        "vessel": ["route_optimizer", "incident_response"],
        "port": ["route_optimizer", "africa_specialist", "compliance"],
        "risk": ["geopolitical_risk"],
        "disruption": ["geopolitical_risk", "guardian"],
        "conflict": ["geopolitical_risk"],
        "weather": ["geopolitical_risk"],
        "regulation": ["compliance"],
        "compliance": ["compliance"],
        "customs": ["compliance"],
        "carbon": ["esg"],
        "emission": ["esg"],
        "green": ["esg"],
        "sustainability": ["esg"],
        "supplier": ["supplier_risk"],
        "vendor": ["supplier_risk"],
        "inventory": ["inventory_forecaster"],
        "demand": ["inventory_forecaster"],
        "stock": ["inventory_forecaster"],
        "incident": ["incident_response"],
        "exception": ["incident_response"],
        "workflow": ["incident_response"],
        "data": ["data_integration"],
        "document": ["data_integration"],
        "pdf": ["data_integration"],
        "invoice": ["data_integration"],
        "africa": ["africa_specialist"],
        "mombasa": ["africa_specialist"],
        "lagos": ["africa_specialist"],
        "dar es salaam": ["africa_specialist"],
        "security": ["security_audit"],
        "audit": ["security_audit"],
        "threat": ["security_audit"],
        "learn": ["knowledge"],
        "memory": ["knowledge"],
        "health": ["guardian"],
        "heal": ["guardian"],
        "monitor": ["guardian", "geopolitical_risk"],
        "analytics": ["analytics"],
        "dashboard": ["analytics"],
        "kpi": ["analytics"],
        "roi": ["analytics"],
    }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._task_registry: Dict[str, Task] = {}
        self._agent_registry: Dict[str, AgentHealth] = {}
        self._pending_decisions: Dict[str, Any] = {}
        self.logger.info("Orchestrator initialized with routing map", 
                         routes=len(self.AGENT_ROUTING_MAP))

    # ── Task Decomposition ───────────────────

    async def decompose_task(self, query: str, context: Optional[Dict] = None) -> List[Task]:
        """Decompose a high-level query into specific subtasks."""
        self.logger.info("Decomposing task", query=query[:100])
        
        context = context or {}
        query_lower = query.lower()
        
        subtasks = []
        
        # Smart keyword-based decomposition
        for keyword, agent_ids in self.AGENT_ROUTING_MAP.items():
            if keyword in query_lower:
                for agent_id in agent_ids:
                    task = Task(
                        task_id=str(uuid.uuid4()),
                        title=f"{keyword}_analysis",
                        description=f"Analyze {keyword} aspects of: {query}",
                        assigned_agent_id=agent_id,
                        priority=self._infer_priority(query),
                        status=TaskStatus.PENDING,
                        context={"original_query": query, "keyword": keyword, **context},
                        tags=[keyword, agent_id],
                        human_approval_required=agent_id in ["incident_response", "security_audit"],
                    )
                    subtasks.append(task)
                    self._task_registry[task.task_id] = task

        # If no specific agents matched, create a general coordination task
        if not subtasks:
            # Multi-agent coordination for complex queries
            primary_agents = ["route_optimizer", "geopolitical_risk", "compliance", "guardian"]
            for agent_id in primary_agents:
                task = Task(
                    task_id=str(uuid.uuid4()),
                    title=f"coordination_{agent_id}",
                    description=f"Assess {agent_id} perspective on: {query}",
                    assigned_agent_id=agent_id,
                    priority=self._infer_priority(query),
                    status=TaskStatus.PENDING,
                    context={"original_query": query, **context},
                    tags=["coordination", agent_id],
                )
                subtasks.append(task)
                self._task_registry[task.task_id] = task

        self.logger.info(
            "Task decomposition complete",
            subtasks_count=len(subtasks),
            agents=list(set(t.assigned_agent_id for t in subtasks)),
        )
        return subtasks

    def _infer_priority(self, query: str) -> TaskPriority:
        """Infer priority from query content."""
        critical_keywords = ["emergency", "critical", "breach", "attack", 
                           "shutdown", "collision", "pirate", "hurricane",
                           "tsunami", "war", "embargo", "sanction"]
        high_keywords = ["urgent", "important", "delay", "disruption", 
                        "strike", "blockade", "severe", "major"]
        
        query_lower = query.lower()
        if any(kw in query_lower for kw in critical_keywords):
            return TaskPriority.CRITICAL
        if any(kw in query_lower for kw in high_keywords):
            return TaskPriority.HIGH
        if any(kw in query_lower for kw in ["routine", "check", "report"]):
            return TaskPriority.LOW
        return TaskPriority.MEDIUM

    # ── Agent Selection ──────────────────────

    def select_best_agent(
        self,
        task_type: str,
        available_agents: Dict[str, AgentHealth],
    ) -> Optional[str]:
        """Select the best agent for a task based on health, load, and specialization."""
        candidates = self.AGENT_ROUTING_MAP.get(task_type, [])
        if not candidates:
            # Fallback to analytics agent
            candidates = ["analytics"]

        best_agent = None
        best_score = -1

        for agent_id in candidates:
            if agent_id not in available_agents:
                continue
            health = available_agents[agent_id]
            
            # Skip offline or errored agents
            if health.status in [AgentStatus.OFFLINE, AgentStatus.ERROR]:
                continue

            # Score based on health, consciousness, and load
            health_score = 0.0
            if health.status == AgentStatus.HEALTHY:
                health_score = 1.0
            elif health.status == AgentStatus.IDLE:
                health_score = 0.9
            elif health.status == AgentStatus.BUSY:
                health_score = 0.6
            elif health.status == AgentStatus.DEGRADED:
                health_score = 0.3

            consciousness = health.consciousness_score
            load_factor = max(0, 1.0 - (health.cpu_usage_percent / 100))
            
            score = (health_score * 0.4 + consciousness * 0.3 + load_factor * 0.3)

            if score > best_score:
                best_score = score
                best_agent = agent_id

        self.logger.debug(
            "Agent selection",
            task_type=task_type,
            selected=best_agent,
            score=best_score,
        )
        return best_agent

    # ── Conflict Resolution ──────────────────

    async def resolve_conflict(
        self,
        conflicting_results: List[Dict[str, Any]],
        conflict_type: str = "recommendation",
    ) -> Dict[str, Any]:
        """Resolve conflicts between agent recommendations using weighted voting."""
        self.logger.info(
            "Resolving conflict",
            conflict_type=conflict_type,
            agents=len(conflicting_results),
        )

        if not conflicting_results:
            return {"resolution": "no_data", "confidence": 0.0}

        if len(conflicting_results) == 1:
            return {
                "resolution": conflicting_results[0],
                "confidence": conflicting_results[0].get("confidence", 0.8),
            }

        # Weight by agent confidence and consciousness score
        weighted_votes = []
        for result in conflicting_results:
            confidence = result.get("confidence", 0.5)
            consciousness = result.get("agent_consciousness", 1.0)
            weight = confidence * consciousness
            weighted_votes.append({
                **result,
                "_weight": weight,
            })

        # Sort by weight and select best
        weighted_votes.sort(key=lambda x: x["_weight"], reverse=True)
        best = weighted_votes[0]

        # Check for strong consensus
        total_weight = sum(v["_weight"] for v in weighted_votes)
        best_ratio = best["_weight"] / total_weight if total_weight > 0 else 0

        resolution = {
            "resolution": best,
            "confidence": best_ratio,
            "all_options": weighted_votes,
            "consensus_level": "strong" if best_ratio > 0.6 else "moderate" if best_ratio > 0.4 else "weak",
            "human_escalation_recommended": best_ratio < 0.4,
            "conflict_type": conflict_type,
        }

        self.logger.info(
            "Conflict resolved",
            confidence=resolution["confidence"],
            consensus=resolution["consensus_level"],
            escalation=resolution["human_escalation_recommended"],
        )
        return resolution

    # ── ROI Estimation ───────────────────────

    async def estimate_roi(
        self,
        action: str,
        context: Dict[str, Any],
    ) -> ROIMetric:
        """Estimate ROI impact of an action in USD."""
        # Heuristic ROI estimation based on action type
        roi_templates = {
            "route_optimization": {
                "name": "Route Optimization Savings",
                "category": "cost_saving",
                "base_value": 50000,
                "variance": 0.3,
            },
            "risk_mitigation": {
                "name": "Risk Mitigation Value",
                "category": "risk_reduction",
                "base_value": 250000,
                "variance": 0.5,
            },
            "compliance_prevention": {
                "name": "Compliance Violation Prevention",
                "category": "risk_reduction",
                "base_value": 1000000,
                "variance": 0.4,
            },
            "inventory_optimization": {
                "name": "Inventory Cost Savings",
                "category": "cost_saving",
                "base_value": 75000,
                "variance": 0.35,
            },
            "emissions_reduction": {
                "name": "Emissions Reduction Value",
                "category": "sustainability",
                "base_value": 30000,
                "variance": 0.25,
            },
        }

        template = roi_templates.get(
            action.split("_")[0] if "_" in action else action,
            {
                "name": "Generic Action Value",
                "category": "efficiency",
                "base_value": 25000,
                "variance": 0.5,
            },
        )

        import random
        variance = random.uniform(-template["variance"], template["variance"])
        value = template["base_value"] * (1 + variance)

        # Scale by shipment size if available
        shipment_value = context.get("shipment_value_usd", 0)
        if shipment_value > 0:
            value += shipment_value * 0.02  # 2% of shipment value

        roi = ROIMetric(
            metric_name=template["name"],
            category=template["category"],
            value=round(value, 2),
            unit="USD",
            period="per_action",
            estimated_usd_impact=round(value, 2),
            confidence=0.75,
            attributed_agents=["orchestrator"],
        )

        self.logger.info(
            "ROI estimated",
            metric=roi.metric_name,
            value=roi.value,
            category=roi.category,
        )
        return roi

    # ── Main Process ─────────────────────────

    async def process(self, state: SwarmState) -> SwarmState:
        """Process incoming query and orchestrate the swarm."""
        self.update_health(AgentStatus.BUSY)
        
        user_query = state.get("user_query", "")
        context = state.get("context", {})
        agent_health = state.get("agent_health", {})

        self.logger.info("Orchestrator processing query", query=user_query[:100])

        # Step 1: Decompose task
        subtasks = await self.decompose_task(user_query, context)
        
        # Step 2: Assign agents
        for task in subtasks:
            if not task.assigned_agent_id:
                task.assigned_agent_id = self.select_best_agent(
                    task.tags[0] if task.tags else "general",
                    agent_health,
                ) or "guardian"
            task.status = TaskStatus.ASSIGNED

        # Step 3: Execute (simulated - in production, these run in parallel via LangGraph)
        results = []
        for task in subtasks:
            task.status = TaskStatus.IN_PROGRESS
            task.started_at = datetime.utcnow()
            
            # Simulate agent execution
            result = await self._simulate_agent_execution(task, agent_health)
            task.result = result
            task.status = TaskStatus.COMPLETED if result.get("success") else TaskStatus.FAILED
            task.completed_at = datetime.utcnow()
            results.append(result)

        # Step 4: Resolve any conflicts
        if len(results) > 1:
            resolution = await self.resolve_conflict(results)
        else:
            resolution = {
                "resolution": results[0] if results else {},
                "confidence": results[0].get("confidence", 0.8) if results else 0.5,
            }

        # Step 5: Estimate ROI
        roi = await self.estimate_roi(
            subtasks[0].tags[0] if subtasks and subtasks[0].tags else "general",
            context,
        )

        # Step 6: Build final response
        final_response = {
            "query": user_query,
            "resolution": resolution,
            "subtasks_completed": len(subtasks),
            "agents_involved": list(set(t.assigned_agent_id for t in subtasks)),
            "roi_impact": roi.model_dump(),
            "confidence": resolution.get("confidence", 0.8),
            "human_escalation_required": resolution.get("human_escalation_recommended", False),
            "timestamp": datetime.utcnow().isoformat(),
        }

        # Update state
        state["tasks"] = {**state.get("tasks", {}), **{t.task_id: t for t in subtasks}}
        state["current_task_id"] = subtasks[0].task_id if subtasks else None
        state["final_response"] = final_response
        state["estimated_roi_impact"] = roi.estimated_usd_impact
        state["confidence"] = ConfidenceScore(
            score=resolution.get("confidence", 0.8),
            model="orchestrator",
            reasoning="Multi-agent consensus with weighted voting",
        )
        state["human_escalation_required"] = resolution.get("human_escalation_recommended", False)
        state["roi_metrics"] = {
            **state.get("roi_metrics", {}),
            roi.metric_id: roi,
        }

        self.update_health(AgentStatus.IDLE)
        self.logger.info("Orchestration complete", agents=len(subtasks), confidence=final_response["confidence"])
        return state

    async def _simulate_agent_execution(
        self,
        task: Task,
        agent_health: Dict[str, AgentHealth],
    ) -> Dict[str, Any]:
        """Simulate agent execution for the orchestrator."""
        agent = task.assigned_agent_id
        health = agent_health.get(agent, AgentHealth(agent_id=agent, agent_name=agent))
        
        import random
        base_confidence = health.consciousness_score * random.uniform(0.7, 1.0)
        
        # Simulate processing time based on task complexity
        processing_time = random.uniform(0.1, 2.0)
        
        return {
            "agent_id": agent,
            "task_id": task.task_id,
            "success": health.status not in [AgentStatus.ERROR, AgentStatus.OFFLINE],
            "confidence": round(base_confidence, 3),
            "processing_time_seconds": round(processing_time, 2),
            "agent_consciousness": health.consciousness_score,
            "result_summary": f"[{agent}] Processed task: {task.title}",
            "findings": self._generate_mock_findings(task, agent),
        }

    def _generate_mock_findings(self, task: Task, agent: str) -> List[str]:
        """Generate contextually relevant mock findings."""
        finding_templates = {
            "route_optimizer": [
                "Optimal route via Cape of Good Hope saves 12% fuel",
                "Alternative via Suez has 35% disruption probability",
                "Multi-modal option reduces transit by 4 days",
            ],
            "geopolitical_risk": [
                "Red Sea elevated risk: Houthi activity detected",
                "Panama Canal restrictions extended to Q2",
                "East Africa corridor stable with low risk profile",
            ],
            "compliance": [
                "EU CBAM declaration required for steel cargo",
                "Deforestation Regulation (EUDR) check passed",
                "New US sanctions on 3 entities - cross-check required",
            ],
            "esg": [
                "Carbon offset of 2.3 tonnes available",
                "Green corridor option reduces emissions by 18%",
                "EU MRV reporting compliant for voyage",
            ],
        }
        return finding_templates.get(agent, ["Analysis complete with standard findings"])

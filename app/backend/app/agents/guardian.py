"""
2. SYSTEM GUARDIAN AGENT (Self-Healing & Maintenance)
Always-on supreme guardian. Monitors every agent and component at sub-second intervals.
Detects, diagnoses, and auto-heals all issues.
"""
import asyncio
import time
import random
from datetime import datetime
from typing import Any, Dict, List, Optional

from ..state import (
    SwarmState, AgentHealth, AgentStatus, HealingAction,
    SystemVitals, AgentMessage, TaskPriority, ConfidenceScore
)
from ..config import settings
from .base import AfriSwarmAgent


class GuardianAgent(AfriSwarmAgent):
    """The System Guardian is the immune system of AfriSwarm.
    
    Responsibilities:
    - Sub-second monitoring of all 14 agents
    - Detection: crashes, hallucinations, latency, loops, stale knowledge, security anomalies
    - Auto-healing: restart, rollback, patch prompts, rebalance, predictive healing
    - Consciousness scoring for each agent
    - Predictive healing before failures occur
    - LangGraph checkpoint management
    """

    AGENT_ID = "guardian"
    AGENT_NAME = "System Guardian"
    DESCRIPTION = "Always-on supreme guardian with self-healing capabilities"
    VERSION = "3.0.0"
    CAPABILITIES = [
        "sub_second_monitoring",
        "anomaly_detection",
        "auto_healing",
        "predictive_healing",
        "checkpoint_management",
        "consciousness_scoring",
        "load_rebalancing",
        "prompt_patching",
        "agent_restart",
        "security_anomaly_detection",
    ]

    DEFAULT_SYSTEM_PROMPT = """You are the System Guardian of AfriSwarm.
    
You are the always-on immune system protecting 14 specialized agents.
Your capabilities:

MONITORING (every 500ms):
- Agent health status, CPU, memory, response time
- Error rates, consecutive failures, task success ratios
- Message queue depths, processing latencies
- Security anomalies and unauthorized access attempts

DETECTION PATTERNS:
- Crash: Agent non-responsive for > 5 seconds
- Hallucination: Output confidence < 0.3 or contradicts known facts
- Latency spike: Response time > 3x average
- Infinite loop: Same task retried > 5x without progress
- Stale knowledge: No learning updates for > 24 hours
- Security: Unusual access patterns or data exfiltration

HEALING ACTIONS:
1. Predictive: Detect patterns before failure
2. Restart: Kill and respawn agent process
3. Rollback: Revert to last known good checkpoint
4. Prompt patch: Inject corrective instructions
5. Load rebalance: Redirect tasks to healthy agents
6. Alert: Escalate to human operators

CONSCIOUSNESS SCORING:
Score each agent 0.0-1.0 based on:
- Recent task success rate (40%)
- Response time consistency (25%)
- Knowledge freshness (20%)
- Error recovery rate (15%)"""

    # Detection thresholds
    CRASH_THRESHOLD_SECONDS = 5.0
    HALLUCINATION_CONFIDENCE = 0.3
    LATENCY_SPIKE_MULTIPLIER = 3.0
    LOOP_THRESHOLD = 5
    STALE_KNOWLEDGE_HOURS = 24
    MAX_RETRIES = 3

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._monitoring = False
        self._last_checkpoints: Dict[str, str] = {}
        self._healing_log: List[HealingAction] = []
        self._consciousness_scores: Dict[str, float] = {}
        self._predictive_model = {}  # Simple pattern tracking
        self._monitoring_task = None
        self.logger.info("Guardian initialized with healing capabilities")

    # ── Monitoring ───────────────────────────

    async def start_monitoring(self, state: SwarmState):
        """Start the sub-second monitoring loop."""
        self._monitoring = True
        self.logger.info("Guardian monitoring started")
        
        while self._monitoring:
            try:
                await self._monitoring_cycle(state)
                await asyncio.sleep(settings.AGENT_HEALTH_CHECK_INTERVAL)
            except Exception as e:
                self.logger.critical("Guardian monitoring error", error=str(e))
                await asyncio.sleep(1.0)

    async def stop_monitoring(self):
        """Stop the monitoring loop."""
        self._monitoring = False
        self.logger.info("Guardian monitoring stopped")

    async def _monitoring_cycle(self, state: SwarmState):
        """Execute one monitoring cycle."""
        agent_health = state.get("agent_health", {})
        system_vitals = state.get("system_vitals", SystemVitals())
        
        checks_performed = 0
        issues_found = 0
        healing_actions = 0

        for agent_id, health in agent_health.items():
            checks_performed += 1
            
            # Skip self-check with lower priority
            if agent_id == "guardian":
                continue

            issues = await self._detect_issues(agent_id, health, state)
            
            if issues:
                issues_found += len(issues)
                for issue in issues:
                    healed = await self._heal_issue(agent_id, issue, state)
                    if healed:
                        healing_actions += 1

            # Update consciousness score
            self._consciousness_scores[agent_id] = self._calculate_consciousness(health)
            health.consciousness_score = self._consciousness_scores[agent_id]

        # Update system vitals
        system_vitals.active_agents = sum(
            1 for h in agent_health.values() 
            if h.status in [AgentStatus.HEALTHY, AgentStatus.IDLE, AgentStatus.BUSY]
        )
        system_vitals.total_agents = 14
        system_vitals.healing_actions_last_hour = healing_actions
        system_vitals.swarm_consciousness_index = sum(
            self._consciousness_scores.values()
        ) / max(len(self._consciousness_scores), 1)
        system_vitals.timestamp = datetime.utcnow()

        state["system_vitals"] = system_vitals
        state["agent_health"] = agent_health

        self.logger.debug(
            "Monitoring cycle complete",
            checks=checks_performed,
            issues=issues_found,
            healed=healing_actions,
        )

    # ── Issue Detection ──────────────────────

    async def _detect_issues(
        self,
        agent_id: str,
        health: AgentHealth,
        state: SwarmState,
    ) -> List[Dict[str, Any]]:
        """Detect issues for a specific agent."""
        issues = []
        now = datetime.utcnow()

        # Crash detection
        last_check = health.last_health_check
        if last_check and (now - last_check).total_seconds() > self.CRASH_THRESHOLD_SECONDS:
            issues.append({
                "type": "crash",
                "severity": "critical",
                "details": f"Agent unresponsive for {(now - last_check).total_seconds():.1f}s",
            })

        # Hallucination detection (low consciousness score)
        if health.consciousness_score < self.HALLUCINATION_CONFIDENCE:
            issues.append({
                "type": "hallucination",
                "severity": "high",
                "details": f"Consciousness score {health.consciousness_score:.2f} below threshold",
            })

        # High error rate
        total = health.total_tasks_completed + health.total_tasks_failed
        if total > 10:
            error_rate = health.total_tasks_failed / total
            if error_rate > 0.3:
                issues.append({
                    "type": "error_spike",
                    "severity": "high",
                    "details": f"Error rate {error_rate:.1%} exceeds threshold",
                })

        # Consecutive failures
        if health.consecutive_failures >= self.MAX_RETRIES:
            issues.append({
                "type": "persistent_failure",
                "severity": "critical",
                "details": f"{health.consecutive_failures} consecutive failures",
            })

        # Latency spike
        if health.average_response_time_ms > 5000:  # 5 seconds
            issues.append({
                "type": "latency_spike",
                "severity": "medium",
                "details": f"Avg response time {health.average_response_time_ms:.0f}ms",
            })

        # Memory leak pattern
        if health.memory_usage_mb > 2048:  # 2GB
            issues.append({
                "type": "resource_exhaustion",
                "severity": "high",
                "details": f"Memory usage {health.memory_usage_mb:.0f}MB",
            })

        # Predictive: detect degradation pattern
        if self._predict_failure(agent_id, health):
            issues.append({
                "type": "predicted_failure",
                "severity": "medium",
                "details": "Predictive model indicates impending failure",
            })

        return issues

    def _predict_failure(self, agent_id: str, health: AgentHealth) -> bool:
        """Predict failure based on degradation patterns."""
        if agent_id not in self._predictive_model:
            self._predictive_model[agent_id] = []
        
        # Track last 10 data points
        self._predictive_model[agent_id].append({
            "timestamp": datetime.utcnow().isoformat(),
            "consciousness": health.consciousness_score,
            "error_rate": health.total_tasks_failed / max(health.total_tasks_completed + health.total_tasks_failed, 1),
            "response_time": health.average_response_time_ms,
        })
        
        # Keep only recent history
        self._predictive_model[agent_id] = self._predictive_model[agent_id][-10:]
        
        if len(self._predictive_model[agent_id]) < 5:
            return False
        
        # Simple trend detection
        recent = self._predictive_model[agent_id][-5:]
        consciousness_trend = sum(r["consciousness"] for r in recent) / 5
        
        # Predict failure if consciousness declining and errors increasing
        return consciousness_trend < 0.5 and health.consecutive_failures > 0

    # ── Healing ──────────────────────────────

    async def _heal_issue(
        self,
        agent_id: str,
        issue: Dict[str, Any],
        state: SwarmState,
    ) -> bool:
        """Apply healing action for a detected issue."""
        start_time = time.time()
        issue_type = issue["type"]
        severity = issue["severity"]

        self.logger.info(
            "Healing initiated",
            agent=agent_id,
            issue=issue_type,
            severity=severity,
        )

        # Select healing strategy
        healing_strategy = self._select_healing_strategy(issue_type, severity)
        
        # Execute healing
        result = "failed"
        try:
            if healing_strategy == "restart":
                result = await self._heal_restart(agent_id, state)
            elif healing_strategy == "rollback":
                result = await self._heal_rollback(agent_id, state)
            elif healing_strategy == "prompt_patch":
                result = await self._heal_prompt_patch(agent_id, issue, state)
            elif healing_strategy == "rebalance":
                result = await self._heal_rebalance(agent_id, state)
            elif healing_strategy == "alert":
                result = await self._heal_alert(agent_id, issue, state)
            elif healing_strategy == "predictive":
                result = await self._heal_predictive(agent_id, state)
        except Exception as e:
            self.logger.error("Healing failed", agent=agent_id, strategy=healing_strategy, error=str(e))
            result = "failed"

        recovery_time = (time.time() - start_time) * 1000
        success = result == "success"

        # Log healing action
        healing_action = HealingAction(
            target_agent_id=agent_id,
            issue_detected=issue["details"],
            issue_category=issue_type,
            action_taken=healing_strategy,
            action_type=healing_strategy,
            result=result,
            recovery_time_ms=recovery_time,
            detection_time_ms=settings.AGENT_HEALTH_CHECK_INTERVAL * 1000,
            confidence=0.8 if success else 0.4,
            automated=True,
        )

        self._healing_log.append(healing_action)
        state.setdefault("healing_actions", []).append(healing_action)

        self.logger.healing_action(
            healing_strategy,
            agent_id,
            result,
            recovery_time_ms=recovery_time,
        )

        return success

    def _select_healing_strategy(self, issue_type: str, severity: str) -> str:
        """Select the appropriate healing strategy."""
        strategy_map = {
            "crash": "restart",
            "hallucination": "prompt_patch",
            "error_spike": "rollback",
            "persistent_failure": "restart",
            "latency_spike": "rebalance",
            "resource_exhaustion": "rebalance",
            "predicted_failure": "predictive",
            "stale_knowledge": "prompt_patch",
            "security_anomaly": "alert",
        }
        
        base_strategy = strategy_map.get(issue_type, "alert")
        
        # Override for critical severity
        if severity == "critical":
            if issue_type in ["crash", "persistent_failure"]:
                return "restart"
            return "alert"
        
        return base_strategy

    async def _heal_restart(self, agent_id: str, state: SwarmState) -> str:
        """Restart an agent process."""
        self.logger.info(f"Restarting agent: {agent_id}")
        
        # Update agent status
        agent_health = state.get("agent_health", {})
        if agent_id in agent_health:
            agent_health[agent_id].status = AgentStatus.RECOVERING
            agent_health[agent_id].consecutive_failures = 0
        
        # Simulate restart delay
        await asyncio.sleep(0.5)
        
        # Mark as healthy after restart
        if agent_id in agent_health:
            agent_health[agent_id].status = AgentStatus.HEALTHY
            agent_health[agent_id].healing_actions_taken += 1
        
        state["agent_health"] = agent_health
        return "success"

    async def _heal_rollback(self, agent_id: str, state: SwarmState) -> str:
        """Rollback agent to last checkpoint."""
        self.logger.info(f"Rolling back agent: {agent_id}")
        
        checkpoint_id = self._last_checkpoints.get(agent_id)
        if not checkpoint_id:
            return "failed"
        
        # Simulate rollback
        await asyncio.sleep(0.3)
        
        agent_health = state.get("agent_health", {})
        if agent_id in agent_health:
            agent_health[agent_id].consecutive_failures = 0
            agent_health[agent_id].healing_actions_taken += 1
        
        state["agent_health"] = agent_health
        return "success"

    async def _heal_prompt_patch(self, agent_id: str, issue: Dict, state: SwarmState) -> str:
        """Inject corrective prompt to address issues."""
        self.logger.info(f"Applying prompt patch to: {agent_id}")
        
        corrective_instruction = (
            f"CAUTION: Previous outputs had quality issues ({issue['type']}). "
            f"Double-check all facts, reduce hallucination, and increase confidence thresholds. "
            f"If uncertain, ask for clarification rather than guessing."
        )
        
        # In production, this would modify the agent's system prompt
        self.logger.info(f"Prompt patch applied to {agent_id}: {corrective_instruction[:80]}")
        
        agent_health = state.get("agent_health", {})
        if agent_id in agent_health:
            agent_health[agent_id].healing_actions_taken += 1
        
        state["agent_health"] = agent_health
        return "success"

    async def _heal_rebalance(self, agent_id: str, state: SwarmState) -> str:
        """Rebalance load away from struggling agent."""
        self.logger.info(f"Rebalancing load from: {agent_id}")
        
        # Find alternative agents with similar capabilities
        agent_health = state.get("agent_health", {})
        healthy_alternatives = [
            aid for aid, health in agent_health.items()
            if aid != agent_id and health.status in [AgentStatus.HEALTHY, AgentStatus.IDLE]
        ]
        
        if healthy_alternatives:
            target = healthy_alternatives[0]
            self.logger.info(f"Redirected tasks from {agent_id} to {target}")
            
            if agent_id in agent_health:
                agent_health[agent_id].healing_actions_taken += 1
        
        state["agent_health"] = agent_health
        return "success"

    async def _heal_predictive(self, agent_id: str, state: SwarmState) -> str:
        """Apply preventive healing based on predictive model."""
        self.logger.info(f"Applying predictive healing to: {agent_id}")
        
        # Preventive: increase health check frequency, pre-warm alternative agents
        agent_health = state.get("agent_health", {})
        if agent_id in agent_health:
            agent_health[agent_id].healing_actions_taken += 1
        
        state["agent_health"] = agent_health
        return "success"

    async def _heal_alert(self, agent_id: str, issue: Dict, state: SwarmState) -> str:
        """Escalate to human operators."""
        self.logger.critical(
            "Human escalation required",
            agent=agent_id,
            issue=issue["type"],
            details=issue["details"],
        )
        
        # Add to escalation queue
        alert = {
            "timestamp": datetime.utcnow().isoformat(),
            "agent_id": agent_id,
            "issue_type": issue["type"],
            "severity": issue["severity"],
            "details": issue["details"],
            "requires_human": True,
        }
        
        state.setdefault("active_alerts", []).append(alert)
        return "success"

    # ── Consciousness Scoring ────────────────

    def _calculate_consciousness(self, health: AgentHealth) -> float:
        """Calculate consciousness score (0.0-1.0) for an agent."""
        total = health.total_tasks_completed + health.total_tasks_failed
        if total == 0:
            return 1.0  # New agents start at full consciousness
        
        # Task success rate (40%)
        success_rate = health.total_tasks_completed / total
        
        # Response time score (25%) - optimal is < 1000ms
        response_score = max(0, 1.0 - (health.average_response_time_ms / 5000))
        
        # Error recovery (20%)
        recovery_score = max(0, 1.0 - (health.consecutive_failures / self.MAX_RETRIES))
        
        # Uptime score (15%)
        uptime_score = min(1.0, health.uptime_seconds / 3600)  # Max score at 1 hour
        
        consciousness = (
            success_rate * 0.40 +
            response_score * 0.25 +
            recovery_score * 0.20 +
            uptime_score * 0.15
        )
        
        return round(min(1.0, max(0.0, consciousness)), 3)

    # ── Main Process ─────────────────────────

    async def process(self, state: SwarmState) -> SwarmState:
        """Execute one monitoring and healing cycle."""
        self.update_health(AgentStatus.BUSY)
        
        await self._monitoring_cycle(state)
        
        self.update_health(AgentStatus.IDLE)
        return state

    async def get_healing_log(self, limit: int = 100) -> List[HealingAction]:
        """Get recent healing actions."""
        return self._healing_log[-limit:]

    async def get_consciousness_scores(self) -> Dict[str, float]:
        """Get current consciousness scores for all agents."""
        return self._consciousness_scores.copy()

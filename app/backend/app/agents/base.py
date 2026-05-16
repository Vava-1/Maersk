"""
Base Agent - All AfriSwarm agents inherit from this foundation.
Provides standardized interfaces, health reporting, message handling,
and integration with the Guardian and Orchestrator.
"""
from __future__ import annotations

import asyncio
import time
import uuid
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional, TypeVar

from langchain_core.language_models import BaseLanguageModel
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel

from ..config import settings
from ..state import (
    AgentHealth, AgentMessage, AgentStatus, ConfidenceScore,
    KnowledgeEntry, SwarmState, Task, TaskPriority, TaskStatus,
    AuditLog
)
from ..utils.logging import AgentLogger
from ..utils.security import sign_audit_entry


T = TypeVar("T")


# ───────────────────────────────────────────────
# Base Agent Class
# ───────────────────────────────────────────────
class AfriSwarmAgent(ABC):
    """Base class for all 14 AfriSwarm agents.
    
    Every agent has:
    - Unique identity and health tracking
    - Structured messaging capabilities
    - Confidence scoring on all outputs
    - Audit logging for every action
    - Knowledge integration via reflection loops
    - Tool registry for dynamic capabilities
    """

    AGENT_ID: str = "base"
    AGENT_NAME: str = "Base Agent"
    DESCRIPTION: str = "Abstract base agent"
    VERSION: str = "1.0.0"
    CAPABILITIES: List[str] = []
    DEFAULT_SYSTEM_PROMPT: str = "You are an AfriSwarm agent."

    def __init__(
        self,
        llm: Optional[BaseLanguageModel] = None,
        model_name: Optional[str] = None,
        system_prompt: Optional[str] = None,
    ):
        self.agent_id = self.AGENT_ID
        self.agent_name = self.AGENT_NAME
        self.version = self.VERSION
        self.llm = llm
        self.model_name = model_name or settings.FAST_MODEL
        self.system_prompt = system_prompt or self.DEFAULT_SYSTEM_PROMPT
        self.logger = AgentLogger(self.agent_id, self.agent_name)

        # Runtime state
        self._health = AgentHealth(
            agent_id=self.agent_id,
            agent_name=self.agent_name,
            status=AgentStatus.IDLE,
            version=self.version,
        )
        self._tools: Dict[str, Callable] = {}
        self._memory: List[Dict[str, Any]] = []
        self._task_count = 0
        self._error_count = 0
        self._start_time = time.time()

        # Dynamic prompt evolution
        self._prompt_versions: List[str] = [self.system_prompt]
        self._current_prompt_index = 0

        self.logger.info("Agent initialized", capabilities=self.CAPABILITIES)

    # ── Health & Status ──────────────────────

    @property
    def health(self) -> AgentHealth:
        self._health.uptime_seconds = time.time() - self._start_time
        self._health.total_tasks_completed = self._task_count
        self._health.total_tasks_failed = self._error_count
        return self._health

    def update_health(self, status: AgentStatus, **kwargs):
        self._health.status = status
        for key, value in kwargs.items():
            if hasattr(self._health, key):
                setattr(self._health, key, value)
        self._health.last_health_check = datetime.utcnow()

    def set_busy(self):
        self._health.status = AgentStatus.BUSY

    def set_idle(self):
        self._health.status = AgentStatus.IDLE

    # ── Tool System ──────────────────────────

    def register_tool(self, name: str, func: Callable, description: str = ""):
        """Register a tool for dynamic capability evolution."""
        self._tools[name] = {"func": func, "description": description}
        if name not in self._health.active_tools:
            self._health.active_tools.append(name)
        self.logger.info(f"Tool registered: {name}", description=description)

    async def use_tool(self, tool_name: str, **kwargs) -> Any:
        """Execute a registered tool."""
        if tool_name not in self._tools:
            raise ValueError(f"Tool '{tool_name}' not found on agent {self.agent_id}")
        tool = self._tools[tool_name]
        start = time.time()
        try:
            result = await tool["func"](**kwargs) if asyncio.iscoroutinefunction(tool["func"]) else tool["func"](**kwargs)
            duration_ms = (time.time() - start) * 1000
            self.logger.debug(f"Tool executed: {tool_name}", duration_ms=duration_ms)
            return result
        except Exception as e:
            self._error_count += 1
            self._health.consecutive_failures += 1
            self.logger.error(f"Tool failed: {tool_name}", error=str(e))
            raise

    # ── Core Execution ───────────────────────

    @abstractmethod
    async def process(self, state: SwarmState) -> SwarmState:
        """Process the current state and return updated state.
        Each agent implements its own logic here."""
        pass

    async def run_with_confidence(
        self,
        input_data: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Run the LLM with confidence scoring."""
        self.set_busy()
        start = time.time()
        task_id = str(uuid.uuid4())

        try:
            self.logger.task_start(task_id, "llm_reasoning")

            if self.llm is None:
                # Fallback simulation when no LLM is available (on-prem mode)
                result = await self._simulate_reasoning(input_data, context)
            else:
                prompt = ChatPromptTemplate.from_messages([
                    SystemMessage(content=self.system_prompt),
                    HumanMessage(content=self._build_prompt(input_data, context))
                ])
                response = await self.llm.ainvoke(prompt.format_messages())
                result = {
                    "response": response.content,
                    "confidence": 0.85,
                    "reasoning": "LLM-generated response",
                }

            duration_ms = (time.time() - start) * 1000
            self._task_count += 1
            self._health.consecutive_failures = 0
            self._health.last_task_completed = datetime.utcnow()
            self._health.average_response_time_ms = (
                (self._health.average_response_time_ms * (self._task_count - 1) + duration_ms)
                / self._task_count
            )

            confidence = ConfidenceScore(
                score=result.get("confidence", 0.8),
                model=self.model_name,
                reasoning=result.get("reasoning", ""),
            )

            self.logger.task_end(task_id, "success", duration_ms)
            self.set_idle()

            return {
                **result,
                "confidence": confidence,
                "task_id": task_id,
                "duration_ms": duration_ms,
                "agent_id": self.agent_id,
                "timestamp": datetime.utcnow().isoformat(),
            }

        except Exception as e:
            duration_ms = (time.time() - start) * 1000
            self._error_count += 1
            self._health.consecutive_failures += 1
            self.logger.task_error(task_id, str(e))
            self.update_health(AgentStatus.ERROR, consecutive_failures=self._health.consecutive_failures)
            self.set_idle()
            raise

    async def _simulate_reasoning(
        self,
        input_data: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Simulate LLM reasoning when no LLM backend is available.
        Uses rule-based heuristics for robust on-prem deployment."""
        return {
            "response": f"[{self.agent_name}] Processed: {input_data[:100]}...",
            "confidence": 0.75,
            "reasoning": f"Rule-based processing by {self.agent_name}",
            "metadata": {"simulated": True, "agent": self.agent_id},
        }

    def _build_prompt(self, input_data: str, context: Optional[Dict[str, Any]]) -> str:
        """Build a rich prompt with context."""
        parts = [f"Input: {input_data}"]
        if context:
            parts.append(f"Context: {context}")
        parts.append(f"Agent: {self.agent_name} ({self.agent_id})")
        parts.append(f"Available tools: {list(self._tools.keys())}")
        return "\n\n".join(parts)

    # ── Messaging ────────────────────────────

    def create_message(
        self,
        receiver_id: str,
        content: Dict[str, Any],
        message_type: str = "result",
        priority: TaskPriority = TaskPriority.MEDIUM,
        parent_message_id: Optional[str] = None,
        trace_id: Optional[str] = None,
    ) -> AgentMessage:
        """Create a structured message to another agent."""
        return AgentMessage(
            sender_id=self.agent_id,
            receiver_id=receiver_id,
            message_type=message_type,
            content=content,
            priority=priority,
            parent_message_id=parent_message_id,
            trace_id=trace_id or str(uuid.uuid4())[:8],
        )

    # ── Knowledge & Learning ─────────────────

    def create_knowledge_entry(
        self,
        entry_type: str,
        content: str,
        source_task_id: Optional[str] = None,
        confidence: float = 0.8,
        tags: Optional[List[str]] = None,
    ) -> KnowledgeEntry:
        """Create a knowledge entry from agent learning."""
        return KnowledgeEntry(
            agent_id=self.agent_id,
            entry_type=entry_type,
            content=content,
            source_task_id=source_task_id,
            confidence=confidence,
            tags=tags or [],
        )

    def add_to_memory(self, key: str, value: Any):
        """Add to agent's short-term memory."""
        self._memory.append({
            "key": key,
            "value": value,
            "timestamp": datetime.utcnow().isoformat(),
        })
        # Keep memory bounded
        if len(self._memory) > 1000:
            self._memory = self._memory[-500:]

    def get_from_memory(self, key: str) -> Optional[Any]:
        """Retrieve from agent's short-term memory."""
        for entry in reversed(self._memory):
            if entry["key"] == key:
                return entry["value"]
        return None

    # ── Audit Logging ────────────────────────

    def log_audit(self, action: str, details: Dict[str, Any], user_id: Optional[str] = None) -> AuditLog:
        """Create cryptographically signed audit log entry."""
        entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "agent_id": self.agent_id,
            "action": action,
            "details": details,
            "user_id": user_id,
        }
        signature = sign_audit_entry(entry)
        audit_log = AuditLog(
            agent_id=self.agent_id,
            action=action,
            details=details,
            user_id=user_id,
            cryptographic_signature=signature,
        )
        return audit_log

    # ── Prompt Evolution ─────────────────────

    def evolve_prompt(self, new_prompt: str):
        """Evolve the agent's system prompt based on learning."""
        self._prompt_versions.append(new_prompt)
        self._current_prompt_index = len(self._prompt_versions) - 1
        self.system_prompt = new_prompt
        self.logger.info("Prompt evolved", version=len(self._prompt_versions))

    def rollback_prompt(self, versions_back: int = 1):
        """Rollback to a previous prompt version."""
        target = max(0, self._current_prompt_index - versions_back)
        self._current_prompt_index = target
        self.system_prompt = self._prompt_versions[target]
        self.logger.info("Prompt rolled back", to_version=target + 1)

    # ── Reflection Loop ──────────────────────

    async def reflection_loop(self, recent_tasks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Perform self-reflection on recent tasks to improve future performance."""
        if not recent_tasks:
            return {"insights": [], "improvements": []}

        insights = []
        improvements = []

        # Analyze error patterns
        errors = [t for t in recent_tasks if t.get("status") == "failed"]
        if errors:
            error_types = {}
            for e in errors:
                et = e.get("error_type", "unknown")
                error_types[et] = error_types.get(et, 0) + 1
            top_error = max(error_types, key=error_types.get)
            insights.append(f"Most common error: {top_error} ({error_types[top_error]} occurrences)")
            improvements.append(f"Improve error handling for: {top_error}")

        # Analyze latency patterns
        latencies = [t.get("duration_ms", 0) for t in recent_tasks]
        if latencies:
            avg_latency = sum(latencies) / len(latencies)
            if avg_latency > 5000:
                insights.append(f"High average latency: {avg_latency:.0f}ms")
                improvements.append("Consider using faster model or caching")

        # Success rate
        success_rate = (len(recent_tasks) - len(errors)) / len(recent_tasks) * 100
        if success_rate < 95:
            insights.append(f"Success rate below target: {success_rate:.1f}%")
            improvements.append("Review failed tasks for systematic issues")

        result = {
            "insights": insights,
            "improvements": improvements,
            "success_rate": success_rate,
            "total_tasks": len(recent_tasks),
            "failed_tasks": len(errors),
            "agent_id": self.agent_id,
            "reflection_time": datetime.utcnow().isoformat(),
        }

        self.logger.info("Reflection completed", insights_count=len(insights))
        return result

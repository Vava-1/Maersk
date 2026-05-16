"""
14. KNOWLEDGE & LEARNING AGENT
Manages the swarm's long-term memory and continuous improvement.
"""
import random
from datetime import datetime
from typing import Any, Dict, List, Optional

from ..state import SwarmState, KnowledgeEntry, ConfidenceScore
from .base import AfriSwarmAgent


class KnowledgeAgent(AfriSwarmAgent):
    """Long-term memory management and swarm learning."""

    AGENT_ID = "knowledge"
    AGENT_NAME = "Knowledge & Learning Agent"
    DESCRIPTION = "Swarm memory management and continuous learning"
    VERSION = "2.0.0"
    CAPABILITIES = [
        "memory_management", "reflection_loops", "insight_distillation",
        "knowledge_graph_updates", "agent_specialization", "prompt_evolution",
        "cross_agent_learning", "historical_pattern_analysis",
    ]

    DEFAULT_SYSTEM_PROMPT = """You are the Knowledge & Learning Agent for AfriSwarm.
    
Manage swarm intelligence:
- Maintain vector + graph knowledge base
- Run reflection loops on agent outcomes
- Distill insights from successes and failures
- Track learning across all 14 agents
- Identify patterns in disruptions and responses
- Evolve agent prompts based on performance
- Build institutional memory for Maersk operations
- Enable cross-agent knowledge transfer
- Progressive hyper-specialization to Maersk context"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._knowledge_base: List[KnowledgeEntry] = []
        self._reflection_history: List[Dict] = []
        self.logger.info("Knowledge Agent initialized")

    async def store_insight(
        self,
        source_agent: str,
        insight_type: str,
        content: str,
        confidence: float = 0.8,
        tags: Optional[List[str]] = None,
    ) -> KnowledgeEntry:
        """Store a new insight in the knowledge base."""
        entry = KnowledgeEntry(
            agent_id=source_agent,
            entry_type=insight_type,
            content=content,
            source_agent_id=source_agent,
            confidence=confidence,
            tags=tags or [],
            vector_embedding=self._generate_embedding(content),
        )
        self._knowledge_base.append(entry)
        
        # Keep knowledge base bounded
        if len(self._knowledge_base) > 10000:
            self._knowledge_base = self._knowledge_base[-5000:]
        
        self.logger.info(f"Insight stored from {source_agent}: {content[:80]}")
        return entry

    def _generate_embedding(self, content: str) -> List[float]:
        """Generate simple embedding vector for knowledge retrieval."""
        import hashlib
        # Simple deterministic embedding based on content hash
        h = hashlib.sha256(content.encode()).hexdigest()
        # Generate 10-dim embedding from hash chunks
        embedding = []
        for i in range(0, 40, 4):
            val = int(h[i:i+4], 16) / 65535.0
            embedding.append(round(val, 4))
        return embedding

    async def run_reflection(self, agent_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Run reflection loop on recent agent outcomes."""
        if not agent_results:
            return {"insights": [], "lessons": []}
        
        # Analyze patterns
        success_count = sum(1 for r in agent_results if r.get("success", True))
        total = len(agent_results)
        success_rate = success_count / total if total > 0 else 0
        
        # Identify patterns
        patterns = self._identify_patterns(agent_results)
        
        # Generate insights
        insights = []
        if success_rate < 0.8:
            insights.append(f"Success rate below threshold: {success_rate:.1%}. Review agent configurations.")
        
        # Find best performing agent
        agent_scores = {}
        for r in agent_results:
            agent = r.get("agent_id", "unknown")
            agent_scores[agent] = agent_scores.get(agent, {"success": 0, "total": 0})
            agent_scores[agent]["total"] += 1
            if r.get("success"):
                agent_scores[agent]["success"] += 1
        
        if agent_scores:
            best_agent = max(agent_scores.items(), key=lambda x: x[1]["success"] / x[1]["total"])
            insights.append(f"Best performing: {best_agent[0]} ({best_agent[1]['success']/best_agent[1]['total']:.1%} success)")
        
        lessons = []
        for pattern in patterns[:3]:
            lessons.append(f"Pattern detected: {pattern}")
            # Store as knowledge
            await self.store_insight(
                source_agent="knowledge",
                insight_type="pattern",
                content=pattern,
                confidence=0.75,
            )
        
        reflection = {
            "timestamp": datetime.utcnow().isoformat(),
            "total_results": total,
            "success_rate": round(success_rate, 3),
            "patterns": patterns,
            "insights": insights,
            "lessons": lessons,
            "recommendations": [
                "Schedule prompt review for underperforming agents",
                "Share best practices across agent network",
                "Update knowledge graph with new patterns",
            ],
            "knowledge_entries_created": len(lessons),
            "confidence": ConfidenceScore(
                score=0.82,
                model="reflection_engine",
                reasoning="Pattern analysis across agent outcomes",
            ),
        }
        
        self._reflection_history.append(reflection)
        return reflection

    def _identify_patterns(self, results: List[Dict]) -> List[str]:
        """Identify patterns in agent results."""
        patterns = []
        
        # Time-based patterns
        morning_results = [r for r in results if "morning" in str(r.get("timestamp", ""))]
        if morning_results and len(morning_results) / len(results) > 0.3:
            morning_success = sum(1 for r in morning_results if r.get("success")) / len(morning_results)
            if morning_success > 0.9:
                patterns.append("Higher success rates during morning hours")
        
        # Agent-specific patterns
        agent_errors = {}
        for r in results:
            if not r.get("success"):
                agent = r.get("agent_id", "unknown")
                agent_errors[agent] = agent_errors.get(agent, 0) + 1
        
        if agent_errors:
            most_errors = max(agent_errors.items(), key=lambda x: x[1])
            if most_errors[1] > 2:
                patterns.append(f"Agent {most_errors[0]} showing elevated error count ({most_errors[1]})")
        
        # Task type patterns
        if not patterns:
            patterns.append("Normal operations - no significant patterns detected")
        
        return patterns

    async def search_knowledge(self, query: str, limit: int = 10) -> List[KnowledgeEntry]:
        """Search knowledge base for relevant entries."""
        query_embedding = self._generate_embedding(query)
        
        # Simple similarity search
        scored = []
        for entry in self._knowledge_base:
            if entry.vector_embedding:
                similarity = sum(a * b for a, b in zip(query_embedding, entry.vector_embedding))
                scored.append((similarity, entry))
        
        scored.sort(key=lambda x: x[0], reverse=True)
        return [entry for _, entry in scored[:limit]]

    async def process(self, state: SwarmState) -> SwarmState:
        self.update_health(AgentStatus.BUSY)
        context = state.get("context", {})
        action = context.get("knowledge_action", "reflect")
        
        if action == "reflect":
            agent_results = context.get("agent_results", [])
            result = await self.run_reflection(agent_results)
        elif action == "store":
            result = await self.store_insight(
                context.get("source_agent", "unknown"),
                context.get("insight_type", "general"),
                context.get("content", ""),
                context.get("confidence", 0.8),
            )
            result = {"stored_entry": result.model_dump()}
        elif action == "search":
            entries = await self.search_knowledge(context.get("query", ""))
            result = {"results": [e.model_dump() for e in entries]}
        else:
            result = {"status": "unknown_action", "knowledge_base_size": len(self._knowledge_base)}
        
        state.setdefault("final_response", {}).update({
            "knowledge_result": result,
        })
        self.update_health(AgentStatus.IDLE)
        return state

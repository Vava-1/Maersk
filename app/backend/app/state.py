"""
AfriSwarm State Schemas - Structured Pydantic models for the multi-agent swarm.
Every message and state object is typed, validated, and auditable.
"""
from __future__ import annotations

from typing import (
    Annotated, Any, Dict, List, Literal, Optional, Sequence, TypedDict, Union
)
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field, validator
import uuid
import operator


# ───────────────────────────────────────────────
# Enums
# ───────────────────────────────────────────────
class AgentStatus(str, Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    ERROR = "error"
    RECOVERING = "recovering"
    OFFLINE = "offline"
    BUSY = "busy"
    IDLE = "idle"


class TaskPriority(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class TaskStatus(str, Enum):
    PENDING = "pending"
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    ESCALATED = "escalated"


class RiskLevel(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    NEGLIGIBLE = "negligible"


class ComplianceStatus(str, Enum):
    COMPLIANT = "compliant"
    NON_COMPLIANT = "non_compliant"
    PENDING_REVIEW = "pending_review"
    EXEMPT = "exempt"


class TransportMode(str, Enum):
    SEA = "sea"
    AIR = "air"
    RAIL = "rail"
    ROAD = "road"
    MULTIMODAL = "multimodal"


# ───────────────────────────────────────────────
# Base Models
# ───────────────────────────────────────────────
class TimestampedModel(BaseModel):
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class ConfidenceScore(BaseModel):
    score: float = Field(ge=0.0, le=1.0)
    model: str
    reasoning: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class AuditLog(BaseModel):
    log_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    agent_id: str
    action: str
    details: Dict[str, Any]
    user_id: Optional[str] = None
    ip_address: Optional[str] = None
    cryptographic_signature: Optional[str] = None


# ───────────────────────────────────────────────
# Agent State
# ───────────────────────────────────────────────
class AgentHealth(BaseModel):
    agent_id: str
    agent_name: str
    status: AgentStatus
    consciousness_score: float = Field(ge=0.0, le=1.0, default=1.0)
    cpu_usage_percent: float = 0.0
    memory_usage_mb: float = 0.0
    last_health_check: datetime = Field(default_factory=datetime.utcnow)
    last_task_completed: Optional[datetime] = None
    consecutive_failures: int = 0
    total_tasks_completed: int = 0
    total_tasks_failed: int = 0
    average_response_time_ms: float = 0.0
    uptime_seconds: float = 0.0
    version: str = "1.0.0"
    active_tools: List[str] = Field(default_factory=list)
    recent_errors: List[str] = Field(default_factory=list)
    healing_actions_taken: int = 0


class AgentMessage(BaseModel):
    message_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    sender_id: str
    receiver_id: str
    message_type: Literal["task", "result", "query", "response", "alert", "heartbeat", "healing"]
    content: Dict[str, Any]
    priority: TaskPriority = TaskPriority.MEDIUM
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    requires_ack: bool = True
    parent_message_id: Optional[str] = None
    confidence: Optional[ConfidenceScore] = None
    trace_id: str = Field(default_factory=lambda: str(uuid.uuid4())[:8])


# ───────────────────────────────────────────────
# Task Models
# ───────────────────────────────────────────────
class Task(BaseModel):
    task_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    parent_task_id: Optional[str] = None
    title: str
    description: str
    assigned_agent_id: Optional[str] = None
    priority: TaskPriority = TaskPriority.MEDIUM
    status: TaskStatus = TaskStatus.PENDING
    created_at: datetime = Field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    due_at: Optional[datetime] = None
    context: Dict[str, Any] = Field(default_factory=dict)
    result: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    estimated_roi_impact: Optional[float] = None  # USD impact
    confidence: Optional[ConfidenceScore] = None
    human_approval_required: bool = False
    approved_by: Optional[str] = None
    approved_at: Optional[datetime] = None
    subtasks: List[str] = Field(default_factory=list)  # task_ids
    tags: List[str] = Field(default_factory=list)


# ───────────────────────────────────────────────
# Domain Models
# ───────────────────────────────────────────────
class Shipment(BaseModel):
    shipment_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    origin: str
    destination: str
    cargo_type: str
    weight_kg: float
    volume_cbm: float
    transport_mode: TransportMode
    customer_id: str
    priority: TaskPriority = TaskPriority.MEDIUM
    status: str = "planned"
    estimated_cost_usd: float = 0.0
    estimated_co2_kg: float = 0.0
    required_documents: List[str] = Field(default_factory=list)
    regulatory_requirements: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    scheduled_departure: Optional[datetime] = None
    scheduled_arrival: Optional[datetime] = None
    current_location: Optional[str] = None
    transit_history: List[Dict[str, Any]] = Field(default_factory=list)


class RouteAlternative(BaseModel):
    route_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    origin: str
    destination: str
    waypoints: List[str] = Field(default_factory=list)
    transport_modes: List[TransportMode] = Field(default_factory=list)
    estimated_cost_usd: float = 0.0
    estimated_duration_hours: float = 0.0
    estimated_co2_kg: float = 0.0
    risk_score: float = Field(ge=0.0, le=1.0)
    disruption_probability: float = Field(ge=0.0, le=1.0)
    carrier_reliability_score: float = Field(ge=0.0, le=1.0)
    compliance_requirements: List[str] = Field(default_factory=list)
    current_status: str = "available"
    advantages: List[str] = Field(default_factory=list)
    disadvantages: List[str] = Field(default_factory=list)


class DisruptionEvent(BaseModel):
    event_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    event_type: str  # geopolitical, weather, port_closure, strike, conflict, etc.
    title: str
    description: str
    affected_regions: List[str] = Field(default_factory=list)
    affected_routes: List[str] = Field(default_factory=list)
    risk_level: RiskLevel
    probability: float = Field(ge=0.0, le=1.0)
    estimated_impact_usd: float = 0.0
    estimated_duration_hours: float = 0.0
    detected_at: datetime = Field(default_factory=datetime.utcnow)
    expected_start: Optional[datetime] = None
    expected_end: Optional[datetime] = None
    source_urls: List[str] = Field(default_factory=list)
    mitigation_recommendations: List[str] = Field(default_factory=list)
    is_active: bool = True
    confidence: Optional[ConfidenceScore] = None


class ComplianceCheck(BaseModel):
    check_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    shipment_id: Optional[str] = None
    regulation_name: str
    regulation_category: str  # customs, trade, environmental, safety, sanctions
    jurisdiction: str
    status: ComplianceStatus
    checked_at: datetime = Field(default_factory=datetime.utcnow)
    checked_by: str  # agent_id
    findings: List[str] = Field(default_factory=list)
    required_actions: List[str] = Field(default_factory=list)
    risk_level: RiskLevel
    next_review_date: Optional[datetime] = None
    reasoning_trace: str = ""
    documents_verified: List[str] = Field(default_factory=list)
    confidence: Optional[ConfidenceScore] = None


class ESGMetric(BaseModel):
    metric_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    metric_type: str  # carbon, water, biodiversity, social, governance
    shipment_id: Optional[str] = None
    supplier_id: Optional[str] = None
    value: float
    unit: str
    benchmark_value: float = 0.0
    reduction_target: float = 0.0
    measured_at: datetime = Field(default_factory=datetime.utcnow)
    methodology: str = ""
    verification_status: str = "unverified"
    improvement_recommendations: List[str] = Field(default_factory=list)
    eu_cbam_applicable: bool = False
    confidence: Optional[ConfidenceScore] = None


class SupplierRiskProfile(BaseModel):
    supplier_id: str
    supplier_name: str
    country: str
    risk_level: RiskLevel
    financial_health_score: float = Field(ge=0.0, le=1.0)
    reliability_score: float = Field(ge=0.0, le=1.0)
    capacity_utilization: float = Field(ge=0.0, le=1.0)
    esg_score: float = Field(ge=0.0, le=1.0)
    geopolitical_risk_exposure: float = Field(ge=0.0, le=1.0)
    alternative_suppliers: List[str] = Field(default_factory=list)
    last_assessed: datetime = Field(default_factory=datetime.utcnow)
    assessment_methodology: str = ""
    diversification_recommendations: List[str] = Field(default_factory=list)
    risk_factors: List[str] = Field(default_factory=list)
    confidence: Optional[ConfidenceScore] = None


# ───────────────────────────────────────────────
# Guardian & Healing Models
# ───────────────────────────────────────────────
class HealingAction(BaseModel):
    action_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    target_agent_id: str
    issue_detected: str
    issue_category: str  # crash, hallucination, latency, loop, stale_knowledge, security
    action_taken: str
    action_type: str  # restart, rollback, patch_prompt, rebalance, alert, predictive
    result: str = "pending"  # pending, success, failed
    recovery_time_ms: float = 0.0
    detection_time_ms: float = 0.0
    confidence: float = Field(ge=0.0, le=1.0)
    automated: bool = True
    approved_by_guardian: bool = True


class SystemVitals(BaseModel):
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    overall_health_score: float = Field(ge=0.0, le=1.0)
    active_agents: int = 0
    total_agents: int = 14
    tasks_in_progress: int = 0
    tasks_completed_last_hour: int = 0
    average_task_latency_ms: float = 0.0
    error_rate_percent: float = 0.0
    memory_usage_mb: float = 0.0
    cpu_usage_percent: float = 0.0
    database_connections: int = 0
    redis_latency_ms: float = 0.0
    kafka_lag: int = 0
    security_alerts_active: int = 0
    healing_actions_last_hour: int = 0
    uptime_hours: float = 0.0
    swarm_consciousness_index: float = Field(ge=0.0, le=1.0)


# ───────────────────────────────────────────────
# Knowledge Models
# ───────────────────────────────────────────────
class KnowledgeEntry(BaseModel):
    entry_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    agent_id: str
    entry_type: str  # insight, lesson, pattern, policy, risk_factor
    content: str
    source_task_id: Optional[str] = None
    source_agent_id: Optional[str] = None
    confidence: float = Field(ge=0.0, le=1.0)
    verified: bool = False
    usage_count: int = 0
    last_accessed: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    tags: List[str] = Field(default_factory=list)
    vector_embedding: Optional[List[float]] = None
    related_entries: List[str] = Field(default_factory=list)


# ───────────────────────────────────────────────
# Analytics Models
# ───────────────────────────────────────────────
class ROIMetric(BaseModel):
    metric_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    metric_name: str
    category: str  # cost_saving, risk_reduction, efficiency, sustainability
    value: float
    unit: str
    period: str  # daily, weekly, monthly, quarterly, yearly
    baseline_value: float = 0.0
    improvement_percent: float = 0.0
    estimated_usd_impact: float = 0.0
    confidence: float = Field(ge=0.0, le=1.0)
    calculated_at: datetime = Field(default_factory=datetime.utcnow)
    attributed_agents: List[str] = Field(default_factory=list)


# ───────────────────────────────────────────────
# Swarm State (LangGraph TypedDict)
# ───────────────────────────────────────────────
class SwarmState(TypedDict, total=False):
    """Core LangGraph state for the AfriSwarm system.
    
    This TypedDict defines the shared state that flows through
    the LangGraph execution graph. All agent nodes read from and
    write to this state.
    """
    # Identity
    session_id: str
    trace_id: str
    timestamp: str

    # Input / Request
    user_query: str
    user_id: str
    priority: str
    context: Dict[str, Any]

    # Agent Registry
    agent_health: Dict[str, AgentHealth]
    active_agents: List[str]
    agent_messages: Annotated[List[AgentMessage], operator.add]

    # Task Management
    tasks: Dict[str, Task]
    current_task_id: Optional[str]
    pending_tasks: List[str]
    completed_tasks: List[str]
    failed_tasks: List[str]

    # Domain Data
    shipments: Dict[str, Shipment]
    route_alternatives: Dict[str, RouteAlternative]
    disruption_events: Dict[str, DisruptionEvent]
    compliance_checks: Dict[str, ComplianceCheck]
    esg_metrics: Dict[str, ESGMetric]
    supplier_risks: Dict[str, SupplierRiskProfile]

    # Guardian & Healing
    system_vitals: SystemVitals
    healing_actions: Annotated[List[HealingAction], operator.add]
    active_alerts: List[Dict[str, Any]]

    # Knowledge
    knowledge_entries: Annotated[List[KnowledgeEntry], operator.add]

    # Analytics
    roi_metrics: Dict[str, ROIMetric]

    # Output
    final_response: Dict[str, Any]
    reasoning_trace: str
    confidence: Optional[ConfidenceScore]
    human_escalation_required: bool
    suggested_actions: List[str]
    estimated_roi_impact: float

    # Security
    audit_logs: Annotated[List[AuditLog], operator.add]
    security_flags: List[Dict[str, Any]]

    # Metadata
    iteration_count: int
    max_iterations: int
    graph_checkpoint_id: Optional[str]

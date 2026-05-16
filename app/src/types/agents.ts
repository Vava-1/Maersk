export type AgentStatus = 'healthy' | 'degraded' | 'error' | 'recovering' | 'offline' | 'busy' | 'idle';

export interface Agent {
  agent_id: string;
  agent_name: string;
  status: AgentStatus;
  consciousness_score: number;
  version: string;
  uptime_seconds: number;
  tasks_completed: number;
  tasks_failed: number;
  avg_response_ms: number;
  active_tools: string[];
  description: string;
  capabilities: string[];
  recent_errors: string[];
  consecutive_failures?: number;
  healing_actions_taken?: number;
  memory_usage_mb?: number;
  cpu_usage_percent?: number;
}

export interface SystemVitals {
  overall_health_score: number;
  active_agents: number;
  total_agents: number;
  tasks_in_progress: number;
  tasks_completed_last_hour: number;
  average_task_latency_ms: number;
  error_rate_percent: number;
  memory_usage_mb: number;
  cpu_usage_percent: number;
  security_alerts_active: number;
  healing_actions_last_hour: number;
  uptime_hours: number;
  swarm_consciousness_index: number;
}

export interface DisruptionEvent {
  event_id: string;
  event_type: string;
  title: string;
  description: string;
  affected_regions: string[];
  affected_routes: string[];
  risk_level: 'critical' | 'high' | 'medium' | 'low' | 'negligible';
  probability: number;
  estimated_impact_usd: number;
  estimated_duration_hours: number;
  mitigation_recommendations: string[];
  is_active: boolean;
}

export interface ComplianceCheck {
  check_id: string;
  regulation_name: string;
  regulation_category: string;
  jurisdiction: string;
  status: 'compliant' | 'non_compliant' | 'pending_review' | 'exempt';
  checked_by?: string;
  risk_level: string;
  findings: string[];
  required_actions: string[];
  next_review_date?: string;
  reasoning_trace?: string;
  documents_verified?: string[];
  confidence?: { score: number };
}

export interface RouteAlternative {
  route_id: string;
  origin: string;
  destination: string;
  waypoints: string[];
  estimated_cost_usd: number;
  estimated_duration_hours: number;
  estimated_co2_kg: number;
  risk_score: number;
  carrier_reliability_score: number;
  advantages: string[];
  disadvantages: string[];
}

export interface ROIMetric {
  metric_name: string;
  category: string;
  value: number;
  unit: string;
  estimated_usd_impact: number;
  confidence: number;
}

export interface ChatMessage {
  id: string;
  role: 'user' | 'agent' | 'system';
  content: string;
  timestamp: string;
  agent_id?: string;
  confidence?: number;
}

export interface HealingAction {
  action_id: string;
  target_agent_id: string;
  issue_category: string;
  action_taken: string;
  result: string;
  recovery_time_ms: number;
  timestamp: string;
}

export interface AnalyticsDashboard {
  cost_savings: {
    route_optimization_usd: number;
    inventory_optimization_usd: number;
    total_cost_savings_usd: number;
  };
  risk_reduction: {
    events_mitigated: number;
    value_protected_usd: number;
    avg_risk_score_reduction: number;
  };
  efficiency: {
    avg_decision_time_seconds: number;
    tasks_automated: number;
    human_hours_saved: number;
    automation_rate: number;
  };
  sustainability: {
    co2_avoided_kg: number;
    fuel_saved_liters: number;
    green_routes_used: number;
  };
  roi_summary: {
    total_return_usd: number;
    roi_ratio: number;
    payback_period_months: number;
  };
  agent_performance: Record<string, {
    tasks_completed: number;
    success_rate: number;
    avg_response_ms: number;
    consciousness_score: number;
  }>;
}

export interface TrendData {
  date: string;
  cost_savings: number;
  risk_events: number;
  tasks_completed: number;
  co2_avoided: number;
  system_health: number;
}

export const AGENT_ICONS: Record<string, string> = {
  orchestrator: 'Brain',
  guardian: 'Shield',
  geopolitical_risk: 'Globe',
  route_optimizer: 'Map',
  compliance: 'Scale',
  esg: 'Leaf',
  supplier_risk: 'Users',
  inventory_forecaster: 'BarChart3',
  incident_response: 'AlertTriangle',
  data_integration: 'Eye',
  analytics: 'LineChart',
  africa_specialist: 'Compass',
  security_audit: 'Lock',
  knowledge: 'Database',
};

export const AGENT_COLORS: Record<string, string> = {
  orchestrator: 'from-blue-500 to-cyan-400',
  guardian: 'from-emerald-500 to-teal-400',
  geopolitical_risk: 'from-orange-500 to-amber-400',
  route_optimizer: 'from-violet-500 to-purple-400',
  compliance: 'from-sky-500 to-blue-400',
  esg: 'from-green-500 to-emerald-400',
  supplier_risk: 'from-yellow-500 to-orange-400',
  inventory_forecaster: 'from-indigo-500 to-blue-400',
  incident_response: 'from-red-500 to-rose-400',
  data_integration: 'from-pink-500 to-fuchsia-400',
  analytics: 'from-cyan-500 to-sky-400',
  africa_specialist: 'from-amber-600 to-yellow-500',
  security_audit: 'from-slate-500 to-gray-400',
  knowledge: 'from-teal-500 to-cyan-400',
};

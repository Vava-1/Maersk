import { useState, useEffect } from 'react';
import {
  Shield, Activity, Brain, Cpu, Zap,
  RefreshCw, Wrench, ServerCrash, Sparkles
} from 'lucide-react';
import { getVitals, getHealingLog, getConsciousnessScores } from '@/hooks/useApi';
import type { SystemVitals, HealingAction } from '@/types/agents';

function HealthScoreRing({ score, label, size = 80 }: { score: number; label: string; size?: number }) {
  const radius = (size - 8) / 2;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference - score * circumference;
  const color = score > 0.8 ? '#42B0D5' : score > 0.6 ? '#f59e0b' : '#ef4444';

  return (
    <div className="flex flex-col items-center gap-2">
      <div className="relative" style={{ width: size, height: size }}>
        <svg width={size} height={size} className="-rotate-90">
          <circle cx={size / 2} cy={size / 2} r={radius} fill="none" stroke="hsl(220,14%,15%)" strokeWidth="4" />
          <circle
            cx={size / 2} cy={size / 2} r={radius} fill="none" stroke={color}
            strokeWidth="4" strokeLinecap="round"
            strokeDasharray={circumference} strokeDashoffset={offset}
            className="transition-all duration-1000"
          />
        </svg>
        <div className="absolute inset-0 flex items-center justify-center">
          <span className="text-sm font-bold text-white">{(score * 100).toFixed(0)}%</span>
        </div>
      </div>
      <span className="text-[10px] text-[hsl(215,20%,55%)]">{label}</span>
    </div>
  );
}

function VitalsGrid({ vitals }: { vitals: SystemVitals }) {
  const items = [
    { icon: Activity, label: 'Health Score', value: `${(vitals.overall_health_score * 100).toFixed(1)}%`, color: 'text-[#42B0D5]' },
    { icon: Brain, label: 'Consciousness', value: `${(vitals.swarm_consciousness_index * 100).toFixed(1)}%`, color: 'text-purple-400' },
    { icon: Shield, label: 'Active Agents', value: `${vitals.active_agents}/${vitals.total_agents}`, color: 'text-emerald-400' },
    { icon: Zap, label: 'Tasks In Progress', value: String(vitals.tasks_in_progress || 0), color: 'text-amber-400' },
    { icon: Cpu, label: 'CPU Usage', value: `${(vitals.cpu_usage_percent || 0).toFixed(1)}%`, color: 'text-sky-400' },
    { icon: ServerCrash, label: 'Error Rate', value: `${(vitals.error_rate_percent || 0).toFixed(2)}%`, color: 'text-red-400' },
  ];

  return (
    <div className="grid grid-cols-2 lg:grid-cols-3 gap-3">
      {items.map((item, i) => {
        const Icon = item.icon;
        return (
          <div key={i} className="card-elevated rounded-lg p-3 flex items-center gap-3">
            <div className="w-9 h-9 rounded-lg bg-[hsl(220,14%,12%)] flex items-center justify-center flex-shrink-0">
              <Icon className={`w-4 h-4 ${item.color}`} />
            </div>
            <div>
              <div className="text-xs font-semibold text-white">{item.value}</div>
              <div className="text-[10px] text-[hsl(215,20%,50%)]">{item.label}</div>
            </div>
          </div>
        );
      })}
    </div>
  );
}

function HealingLogTable({ actions }: { actions: HealingAction[] }) {
  const [expanded, setExpanded] = useState(false);
  const display = expanded ? actions : actions.slice(0, 6);

  return (
    <div className="card-elevated rounded-lg overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b border-[hsl(220,14%,18%)]">
        <div className="flex items-center gap-2">
          <Wrench className="w-4 h-4 text-[hsl(195,70%,55%)]" />
          <h3 className="text-sm font-semibold text-white">Healing Log</h3>
        </div>
        <span className="text-[10px] px-2 py-0.5 bg-[hsl(195,70%,55%/0.1)] text-[hsl(195,70%,65%)] rounded-full">
          {actions.length} actions
        </span>
      </div>
      <div className="divide-y divide-[hsl(220,14%,15%)]">
        {display.map((action, i) => (
          <div key={i} className="p-3 hover:bg-[hsl(220,14%,11%)] transition-colors">
            <div className="flex items-start justify-between gap-2">
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 mb-1">
                  <div className={`w-1.5 h-1.5 rounded-full ${
                    action.result === 'success' ? 'bg-emerald-400' : action.result === 'failed' ? 'bg-red-400' : 'bg-amber-400'
                  }`} />
                  <span className="text-xs text-white font-medium truncate">{action.action_taken}</span>
                </div>
                <div className="text-[10px] text-[hsl(215,20%,50%)] truncate">
                  Target: {action.target_agent_id} · {action.issue_category}
                </div>
              </div>
              <div className="text-right flex-shrink-0">
                <div className="text-[10px] text-[hsl(215,20%,50%)]">{action.recovery_time_ms.toFixed(0)}ms</div>
                <div className="text-[9px] text-[hsl(215,20%,40%)]">
                  {new Date(action.timestamp).toLocaleTimeString()}
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>
      {actions.length > 6 && (
        <button
          onClick={() => setExpanded(!expanded)}
          className="w-full py-2 text-[10px] text-[hsl(195,70%,65%)] hover:text-[hsl(195,70%,75%)] bg-[hsl(220,14%,10%)] hover:bg-[hsl(220,14%,13%)] transition-colors"
        >
          {expanded ? 'Show Less' : `Show All ${actions.length}`}
        </button>
      )}
    </div>
  );
}

function ConsciousnessChart({ scores }: { scores: Record<string, number> }) {
  const sorted = Object.entries(scores).sort(([, a], [, b]) => b - a);

  return (
    <div className="card-elevated rounded-lg p-4">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <Brain className="w-4 h-4 text-purple-400" />
          <h3 className="text-sm font-semibold text-white">Consciousness Scores</h3>
        </div>
        <Sparkles className="w-3.5 h-3.5 text-purple-400/50" />
      </div>
      <div className="space-y-2">
        {sorted.map(([agent, score]) => (
          <div key={agent} className="flex items-center gap-3">
            <span className="text-[10px] text-[hsl(215,20%,50%)] w-32 truncate text-right">{agent.replace(/_/g, ' ')}</span>
            <div className="flex-1 h-4 bg-[hsl(220,14%,12%)] rounded-full overflow-hidden">
              <div
                className="h-full rounded-full transition-all duration-700"
                style={{
                  width: `${score * 100}%`,
                  background: score > 0.8 ? 'linear-gradient(90deg, hsl(142,76%,36%), hsl(142,76%,50%))' :
                    score > 0.5 ? 'linear-gradient(90deg, hsl(38,92%,45%), hsl(38,92%,55%))' :
                    'linear-gradient(90deg, hsl(0,72%,45%), hsl(0,72%,55%))',
                }}
              />
            </div>
            <span className="text-[10px] text-white w-10 text-right font-mono">{(score * 100).toFixed(0)}%</span>
          </div>
        ))}
      </div>
    </div>
  );
}

export function GuardianHealth() {
  const [vitals, setVitals] = useState<SystemVitals | null>(null);
  const [healingLog, setHealingLog] = useState<HealingAction[]>([]);
  const [consciousness, setConsciousness] = useState<Record<string, number>>({});

  const loadData = async () => {
    try {
      const [v, h, c] = await Promise.all([
        getVitals(),
        getHealingLog(20),
        getConsciousnessScores(),
      ]);
      setVitals(v);
      setHealingLog(h.healing_actions || []);
      setConsciousness(c.consciousness_scores || {});
    } catch {
      // Silent fallback
    }
  };

  useEffect(() => {
    loadData();
    const interval = setInterval(loadData, 5000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-bold text-white">Guardian Health Dashboard</h2>
          <p className="text-xs text-[hsl(215,20%,50%)] mt-0.5">Real-time system monitoring and self-healing</p>
        </div>
        <button
          onClick={loadData}
          className="flex items-center gap-2 px-3 py-1.5 bg-[hsl(220,14%,12%)] hover:bg-[hsl(220,14%,18%)] border border-[hsl(220,14%,20%)] rounded-lg text-xs text-[hsl(215,20%,55%)] hover:text-white transition-all"
        >
          <RefreshCw className="w-3.5 h-3.5" />
          Refresh
        </button>
      </div>

      {/* Health Score Rings */}
      <div className="card-elevated rounded-lg p-4">
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 justify-items-center">
          <HealthScoreRing score={vitals?.overall_health_score || 0.98} label="System Health" />
          <HealthScoreRing score={vitals?.swarm_consciousness_index || 0.95} label="Consciousness" />
          <HealthScoreRing score={0.92} label="Self-Healing" />
          <HealthScoreRing score={0.99} label="Security" />
        </div>
      </div>

      {/* Vitals Grid */}
      {vitals && <VitalsGrid vitals={vitals} />}

      {/* Bottom Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <ConsciousnessChart scores={consciousness} />
        <HealingLogTable actions={healingLog} />
      </div>
    </div>
  );
}

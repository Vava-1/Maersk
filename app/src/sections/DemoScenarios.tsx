import { useState, useEffect } from 'react';
import {
  Zap, Play, RotateCcw, ChevronRight, Brain, Shield, Map, Globe, Scale, Clock,
  AlertTriangle, X, CheckCircle, Loader2,
  Leaf, Users, BarChart3, Eye, LineChart, Compass, Lock, Database
} from 'lucide-react';
import { getDemoScenarios, runDemoScenario } from '@/hooks/useApi';

interface Scenario {
  id: string;
  name: string;
  description: string;
  query: string;
  expected_agents: string[];
}

const AGENT_ICONS: Record<string, React.ElementType> = {
  orchestrator: Brain,
  guardian: Shield,
  geopolitical_risk: Globe,
  route_optimizer: Map,
  compliance: Scale,
  esg: Leaf,
  supplier_risk: Users,
  inventory_forecaster: BarChart3,
  incident_response: AlertTriangle,
  data_integration: Eye,
  analytics: LineChart,
  africa_specialist: Compass,
  security_audit: Lock,
  knowledge: Database,
};

function ScenarioCard({ scenario, onRun, isRunning }: {
  scenario: Scenario;
  onRun: (id: string) => void;
  isRunning: boolean;
}) {
  const [expanded, setExpanded] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [running, setRunning] = useState(false);

  const handleRun = async () => {
    setRunning(true);
    onRun(scenario.id);
    try {
      const res = await runDemoScenario(scenario.id);
      setResult(res);
      setExpanded(true);
    } catch (e) {
      console.error(e);
    }
    setRunning(false);
  };

  return (
    <div className="card-elevated rounded-lg overflow-hidden hover:border-[hsl(195,70%,55%/0.3)] transition-all">
      <div className="p-4">
        <div className="flex items-start justify-between mb-3">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-amber-500 to-yellow-600 flex items-center justify-center">
              <Zap className="w-5 h-5 text-white" />
            </div>
            <div>
              <h3 className="text-sm font-semibold text-white">{scenario.name}</h3>
              <p className="text-[10px] text-[hsl(215,20%,55%)] mt-0.5">{scenario.description}</p>
            </div>
          </div>
        </div>

        <div className="bg-[hsl(220,14%,10%)] rounded-lg p-2.5 mb-3 border border-[hsl(220,14%,16%)]">
          <div className="text-[10px] text-[hsl(215,20%,50%)] mb-1">Query:</div>
          <div className="text-xs text-[hsl(210,40%,85%)] italic">&ldquo;{scenario.query}&rdquo;</div>
        </div>

        <div className="flex flex-wrap gap-1 mb-3">
          {scenario.expected_agents.map((agent, i) => {
            const Icon = AGENT_ICONS[agent] || Brain;
            return (
              <span key={i} className="inline-flex items-center gap-1 text-[9px] px-2 py-0.5 bg-[hsl(195,70%,55%/0.08)] text-[hsl(195,70%,65%)] rounded">
                <Icon className="w-2.5 h-2.5" />
                {agent.replace(/_/g, ' ')}
              </span>
            );
          })}
        </div>

        <div className="flex gap-2">
          <button
            onClick={handleRun}
            disabled={running || isRunning}
            className="flex-1 flex items-center justify-center gap-2 py-2 bg-[hsl(195,70%,55%)] hover:bg-[hsl(195,70%,60%)] disabled:opacity-50 rounded-lg text-xs font-medium text-[hsl(220,20%,6%)] transition-all"
          >
            {running ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <Play className="w-3.5 h-3.5" />}
            {running ? 'Running...' : 'Run Scenario'}
          </button>
          {result && (
            <button
              onClick={() => setExpanded(!expanded)}
              className="px-3 py-2 bg-[hsl(220,14%,12%)] hover:bg-[hsl(220,14%,18%)] border border-[hsl(220,14%,20%)] rounded-lg text-xs text-[hsl(215,20%,55%)] hover:text-white transition-all"
            >
              {expanded ? <X className="w-3.5 h-3.5" /> : <ChevronRight className="w-3.5 h-3.5" />}
            </button>
          )}
        </div>

        {expanded && result && (
          <div className="mt-3 pt-3 border-t border-[hsl(220,14%,18%)]">
            <div className="text-[10px] font-semibold text-emerald-400 mb-2 flex items-center gap-1">
              <CheckCircle className="w-3 h-3" /> Execution Complete
            </div>
            <div className="bg-[hsl(220,14%,10%)] rounded-lg p-3 border border-[hsl(220,14%,16%)]">
              <pre className="text-[10px] text-[hsl(215,20%,65%)] whitespace-pre-wrap overflow-auto max-h-60 scrollbar-thin">
                {JSON.stringify(result.result, null, 2)}
              </pre>
            </div>
            <div className="mt-2 flex items-center gap-3 text-[10px] text-[hsl(215,20%,50%)]">
              <span className="flex items-center gap-1">
                <Brain className="w-2.5 h-2.5" />
                {result.agents_involved?.length || 0} agents
              </span>
              <span className="flex items-center gap-1">
                <Clock className="w-2.5 h-2.5" />
                {new Date(result.timestamp).toLocaleTimeString()}
              </span>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export function DemoScenarios() {
  const [scenarios, setScenarios] = useState<Scenario[]>([]);
  const [runningId, setRunningId] = useState<string | null>(null);

  useEffect(() => {
    loadScenarios();
  }, []);

  const loadScenarios = async () => {
    try {
      const data = await getDemoScenarios();
      setScenarios(Object.entries(data.scenarios || {}).map(([id, s]: [string, any]) => ({ id, ...s })));
    } catch {
      // Fallback mock data
      setScenarios([
        {
          id: 'red_sea_crisis',
          name: 'Red Sea Shipping Crisis',
          description: 'Houthi attacks disrupting Red Sea transit - reroute via Cape',
          query: 'Red Sea crisis: Find alternative route from Shanghai to Rotterdam',
          expected_agents: ['orchestrator', 'geopolitical_risk', 'route_optimizer', 'compliance'],
        },
        {
          id: 'eu_cbam_compliance',
          name: 'EU CBAM Compliance Check',
          description: 'Verify CBAM compliance for steel shipment to EU',
          query: 'Check EU CBAM compliance for steel container from Shanghai to Hamburg',
          expected_agents: ['orchestrator', 'compliance', 'esg', 'data_integration'],
        },
        {
          id: 'africa_route_optimization',
          name: 'Africa Route Optimization',
          description: 'Optimize Mombasa to Kampala corridor routing',
          query: 'Optimize shipping route from Mombasa to Kampala for container cargo',
          expected_agents: ['orchestrator', 'route_optimizer', 'africa_specialist', 'geopolitical_risk'],
        },
      ]);
    }
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-bold text-white">Demo Scenarios</h2>
          <p className="text-xs text-[hsl(215,20%,50%)] mt-0.5">Run pre-built scenarios to demonstrate AfriSwarm capabilities</p>
        </div>
        <button
          onClick={loadScenarios}
          className="flex items-center gap-2 px-3 py-1.5 bg-[hsl(220,14%,12%)] hover:bg-[hsl(220,14%,18%)] border border-[hsl(220,14%,20%)] rounded-lg text-xs text-[hsl(215,20%,55%)] hover:text-white transition-all"
        >
          <RotateCcw className="w-3.5 h-3.5" />
          Refresh
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-4">
        {scenarios.map(scenario => (
          <ScenarioCard
            key={scenario.id}
            scenario={scenario}
            onRun={setRunningId}
            isRunning={runningId === scenario.id}
          />
        ))}
      </div>
    </div>
  );
}

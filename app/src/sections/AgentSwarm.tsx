import { useState, useEffect } from 'react';
import {
  Brain, Shield, Globe, Map, Scale, Leaf, Users,
  BarChart3, AlertTriangle, Eye, LineChart, Compass,
  Lock, Database, RefreshCw, MessageSquare, ChevronRight,
  Activity, Sparkles
} from 'lucide-react';
import { AGENT_ICONS, AGENT_COLORS } from '@/types/agents';
import type { Agent as AgentType } from '@/types/agents';
import { getAgents, chatWithAgent } from '@/hooks/useApi';

const iconComponents: Record<string, React.ElementType> = {
  Brain, Shield, Globe, Map, Scale, Leaf, Users,
  BarChart3, AlertTriangle, Eye, LineChart, Compass,
  Lock, Database,
};

function getStatusDot(status: string) {
  const styles: Record<string, string> = {
    healthy: 'status-healthy',
    idle: 'status-idle',
    busy: 'status-busy',
    degraded: 'status-degraded',
    error: 'status-error',
    recovering: 'status-recovering',
    offline: 'status-idle opacity-50',
  };
  return styles[status] || 'status-idle';
}

function AgentCard({ agent, onChat }: { agent: AgentType; onChat: (agent: AgentType) => void }) {
  const iconName = AGENT_ICONS[agent.agent_id] || 'Activity';
  const Icon = iconComponents[iconName] || Activity;
  const colorClass = AGENT_COLORS[agent.agent_id] || 'from-gray-500 to-gray-400';
  const [isHovered, setIsHovered] = useState(false);

  return (
    <div
      className="card-elevated rounded-xl p-4 hover:border-[hsl(195,70%,55%/0.3)] transition-all duration-300 group relative"
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
    >
      {/* Top gradient bar */}
      <div className={`absolute top-0 left-4 right-4 h-0.5 rounded-b-full bg-gradient-to-r ${colorClass} opacity-60`} />

      <div className="flex items-start justify-between mb-3">
        <div className="flex items-center gap-3">
          <div className={`w-10 h-10 rounded-lg bg-gradient-to-br ${colorClass} flex items-center justify-center flex-shrink-0 shadow-lg`}>
            <Icon className="w-5 h-5 text-white" />
          </div>
          <div>
            <h3 className="text-sm font-semibold text-white leading-tight">{agent.agent_name}</h3>
            <div className="flex items-center gap-1.5 mt-0.5">
              <div className={`w-1.5 h-1.5 rounded-full ${getStatusDot(agent.status)}`} />
              <span className="text-[10px] text-[hsl(215,20%,55%)] capitalize">{agent.status}</span>
            </div>
          </div>
        </div>
        <div className="text-right">
          <div className="text-lg font-bold text-gradient leading-none">
            {(agent.consciousness_score * 100).toFixed(0)}
          </div>
          <div className="text-[9px] text-[hsl(215,20%,50%)]">CS Score</div>
        </div>
      </div>

      {/* Metrics */}
      <div className="grid grid-cols-3 gap-2 mb-3">
        <div className="bg-[hsl(220,14%,12%)] rounded-md p-1.5 text-center">
          <div className="text-[10px] text-[hsl(215,20%,50%)]">Tasks</div>
          <div className="text-xs font-semibold text-white">{agent.tasks_completed}</div>
        </div>
        <div className="bg-[hsl(220,14%,12%)] rounded-md p-1.5 text-center">
          <div className="text-[10px] text-[hsl(215,20%,50%)]">Avg ms</div>
          <div className="text-xs font-semibold text-white">{agent.avg_response_ms.toFixed(0)}</div>
        </div>
        <div className="bg-[hsl(220,14%,12%)] rounded-md p-1.5 text-center">
          <div className="text-[10px] text-[hsl(215,20%,50%)]">Uptime</div>
          <div className="text-xs font-semibold text-white">
            {(agent.uptime_seconds / 3600).toFixed(1)}h
          </div>
        </div>
      </div>

      {/* Capabilities */}
      <div className="flex flex-wrap gap-1 mb-3">
        {(agent.capabilities || []).slice(0, 3).map((cap, i) => (
          <span
            key={i}
            className="text-[9px] px-1.5 py-0.5 bg-[hsl(195,70%,55%/0.08)] text-[hsl(195,70%,65%)] rounded"
          >
            {cap}
          </span>
        ))}
        {(agent.capabilities || []).length > 3 && (
          <span className="text-[9px] px-1.5 py-0.5 text-[hsl(215,20%,50%)]">
            +{(agent.capabilities || []).length - 3}
          </span>
        )}
      </div>

      {/* Actions */}
      <div className="flex gap-2">
        <button
          onClick={() => onChat(agent)}
          className="flex-1 flex items-center justify-center gap-1.5 py-1.5 bg-[hsl(195,70%,55%/0.1)] hover:bg-[hsl(195,70%,55%/0.2)] border border-[hsl(195,70%,55%/0.2)] rounded-lg text-xs text-[hsl(195,70%,65%)] transition-all"
        >
          <MessageSquare className="w-3 h-3" />
          Chat
        </button>
        <button className="p-1.5 bg-[hsl(220,14%,12%)] hover:bg-[hsl(220,14%,18%)] rounded-lg text-[hsl(215,20%,50%)] hover:text-white transition-all">
          <Activity className="w-3.5 h-3.5" />
        </button>
      </div>

      {/* Hover details */}
      {isHovered && agent.recent_errors && agent.recent_errors.length > 0 && (
        <div className="mt-2 p-2 bg-[hsl(0,72%,51%/0.05)] border border-[hsl(0,72%,51%/0.1)] rounded-lg">
          <div className="text-[9px] text-[hsl(0,72%,55%)] flex items-center gap-1">
            <AlertTriangle className="w-2.5 h-2.5" />
            Recent Errors
          </div>
          {agent.recent_errors.slice(0, 2).map((err, i) => (
            <div key={i} className="text-[9px] text-[hsl(215,20%,55%)] mt-0.5 truncate">{err}</div>
          ))}
        </div>
      )}
    </div>
  );
}

function AgentChatPanel({ agent, onClose }: { agent: AgentType; onClose: () => void }) {
  const [messages, setMessages] = useState<Array<{role: string; content: string}>>([
    { role: 'agent', content: `Hello! I am ${agent.agent_name}. How can I assist you today?` },
  ]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleSend = async () => {
    if (!input.trim()) return;
    const userMsg = input.trim();
    setMessages(prev => [...prev, { role: 'user', content: userMsg }]);
    setInput('');
    setIsLoading(true);

    try {
      const res = await chatWithAgent(agent.agent_id, userMsg);
      const responseContent = JSON.stringify(res?.response || 'Processing complete.', null, 2);
      setMessages(prev => [...prev, { role: 'agent', content: responseContent }]);
    } catch {
      setMessages(prev => [...prev, { role: 'agent', content: 'I apologize, but I encountered an error processing your request.' }]);
    }
    setIsLoading(false);
  };

  return (
    <div className="fixed inset-y-0 right-0 w-[420px] bg-[hsl(220,20%,7%)] border-l border-[hsl(220,14%,18%)] z-50 flex flex-col shadow-2xl">
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-[hsl(220,14%,18%)]">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-[hsl(195,70%,55%)] to-[hsl(195,70%,40%)] flex items-center justify-center">
            {(() => {
              const Icon = iconComponents[AGENT_ICONS[agent.agent_id] || 'Activity'] || Activity;
              return <Icon className="w-4 h-4 text-white" />;
            })()}
          </div>
          <div>
            <h3 className="text-sm font-semibold text-white">{agent.agent_name}</h3>
            <div className="flex items-center gap-1.5">
              <div className={`w-1.5 h-1.5 rounded-full ${getStatusDot(agent.status)}`} />
              <span className="text-[10px] text-[hsl(215,20%,55%)] capitalize">{agent.status}</span>
            </div>
          </div>
        </div>
        <button onClick={onClose} className="text-[hsl(215,20%,50%)] hover:text-white transition-colors">
          <ChevronRight className="w-5 h-5" />
        </button>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-3 scrollbar-thin">
        {messages.map((msg, i) => (
          <div key={i} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
            <div className={`max-w-[85%] rounded-lg p-3 text-xs leading-relaxed ${
              msg.role === 'user'
                ? 'bg-[hsl(195,70%,55%)] text-[hsl(220,20%,6%)]'
                : 'bg-[hsl(220,14%,12%)] border border-[hsl(220,14%,18%)] text-[hsl(210,40%,90%)]'
            }`}>
              <pre className="whitespace-pre-wrap font-sans">{msg.content}</pre>
            </div>
          </div>
        ))}
        {isLoading && (
          <div className="flex justify-start">
            <div className="bg-[hsl(220,14%,12%)] border border-[hsl(220,14%,18%)] rounded-lg p-3">
              <div className="flex items-center gap-1.5">
                <Sparkles className="w-3 h-3 text-[hsl(195,70%,55%)] animate-pulse" />
                <span className="text-[10px] text-[hsl(215,20%,50%)]">Processing...</span>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Input */}
      <div className="p-4 border-t border-[hsl(220,14%,18%)]">
        <div className="flex gap-2">
          <input
            type="text"
            value={input}
            onChange={e => setInput(e.target.value)}
            onKeyDown={e => e.key === 'Enter' && handleSend()}
            placeholder={`Ask ${agent.agent_name}...`}
            className="flex-1 bg-[hsl(220,14%,12%)] border border-[hsl(220,14%,20%)] rounded-lg px-3 py-2 text-xs text-white placeholder-[hsl(215,20%,45%)] focus:outline-none focus:border-[hsl(195,70%,55%/0.5)] transition-colors"
          />
          <button
            onClick={handleSend}
            disabled={isLoading}
            className="px-3 py-2 bg-[hsl(195,70%,55%)] hover:bg-[hsl(195,70%,60%)] rounded-lg text-[hsl(220,20%,6%)] transition-colors disabled:opacity-50"
          >
            <Sparkles className="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>
  );
}

export function AgentSwarm() {
  const [agents, setAgents] = useState<AgentType[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedAgent, setSelectedAgent] = useState<AgentType | null>(null);

  useEffect(() => {
    loadAgents();
    const interval = setInterval(loadAgents, 10000);
    return () => clearInterval(interval);
  }, []);

  const loadAgents = async () => {
    try {
      const data = await getAgents();
      setAgents(data.agents || []);
    } catch {
      // Use mock data as fallback
      setAgents([]);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <RefreshCw className="w-6 h-6 text-[hsl(195,70%,55%)] animate-spin" />
      </div>
    );
  }

  return (
    <div className="relative">
      <div className="flex items-center justify-between mb-4">
        <div>
          <h2 className="text-xl font-bold text-white">Agent Swarm Control Panel</h2>
          <p className="text-xs text-[hsl(215,20%,50%)] mt-0.5">Monitor and interact with all 14 specialized agents</p>
        </div>
        <button
          onClick={loadAgents}
          className="flex items-center gap-2 px-3 py-1.5 bg-[hsl(220,14%,12%)] hover:bg-[hsl(220,14%,18%)] border border-[hsl(220,14%,20%)] rounded-lg text-xs text-[hsl(215,20%,55%)] hover:text-white transition-all"
        >
          <RefreshCw className="w-3.5 h-3.5" />
          Refresh
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 2xl:grid-cols-4 gap-4">
        {agents.map(agent => (
          <AgentCard key={agent.agent_id} agent={agent} onChat={setSelectedAgent} />
        ))}
      </div>

      {/* Chat Panel Overlay */}
      {selectedAgent && (
        <>
          <div className="fixed inset-0 bg-black/40 z-40" onClick={() => setSelectedAgent(null)} />
          <AgentChatPanel agent={selectedAgent} onClose={() => setSelectedAgent(null)} />
        </>
      )}
    </div>
  );
}

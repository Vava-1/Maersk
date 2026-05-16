import { useState, useRef, useEffect } from 'react';
import {
  Send, Brain, User, Loader2, ChevronRight,
  TrendingUp, Shield
} from 'lucide-react';
import { sendChat } from '@/hooks/useApi';

interface Message {
  id: string;
  role: 'user' | 'agent' | 'system';
  content: string;
  timestamp: string;
  metadata?: Record<string, any>;
}

const SUGGESTIONS = [
  'Optimize route: Shanghai to Mombasa',
  'Assess Red Sea disruption risk',
  'Check EU CBAM compliance for steel shipment',
  'Analyze Northern Corridor infrastructure',
  'Evaluate supplier risk in Lagos',
  'Predict demand for East Africa corridor',
];

export function SwarmChat() {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: 'welcome',
      role: 'system',
      content: 'Welcome to AfriSwarm Command Interface. I am the Orchestrator, coordinating 14 specialized agents. How can I assist with your logistics operations today?',
      timestamp: new Date().toISOString(),
    },
  ]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSend = async (text?: string) => {
    const msg = text || input.trim();
    if (!msg || isLoading) return;

    const userMsg: Message = {
      id: `msg_${Date.now()}`,
      role: 'user',
      content: msg,
      timestamp: new Date().toISOString(),
    };
    setMessages(prev => [...prev, userMsg]);
    setInput('');
    setIsLoading(true);

    try {
      const res = await sendChat(msg);
      const responseData = res?.response || {};
      const agentResponse: Message = {
        id: `resp_${Date.now()}`,
        role: 'agent',
        content: formatResponse(responseData),
        timestamp: new Date().toISOString(),
        metadata: {
          agents_involved: responseData.agents_involved || ['orchestrator'],
          confidence: res?.confidence,
          roi: res?.estimated_roi,
        },
      };
      setMessages(prev => [...prev, agentResponse]);
    } catch {
      const errorMsg: Message = {
        id: `err_${Date.now()}`,
        role: 'system',
        content: 'I apologize, but the swarm is currently experiencing connectivity issues. Please try again in a moment.',
        timestamp: new Date().toISOString(),
      };
      setMessages(prev => [...prev, errorMsg]);
    }
    setIsLoading(false);
  };

  const formatResponse = (data: any): string => {
    if (data.error) return `Error: ${data.error}`;
    if (typeof data === 'string') return data;

    const parts: string[] = [];

    if (data.route_alternatives?.length > 0) {
      parts.push('**Route Alternatives:**');
      data.route_alternatives.forEach((r: any, i: number) => {
        parts.push(`${i + 1}. ${r.origin} -> ${r.destination}`);
        parts.push(`   Cost: $${r.cost_usd?.toLocaleString() || 'N/A'} | Duration: ${r.duration_hours ? `${(r.duration_hours / 24).toFixed(1)} days` : 'N/A'} | CO2: ${r.co2_kg?.toFixed(0) || 'N/A'}kg`);
        if (r.advantages?.length) parts.push(`   Advantages: ${r.advantages.join(', ')}`);
      });
    }

    if (data.compliance_checks?.length > 0) {
      parts.push('\\n**Compliance Checks:**');
      data.compliance_checks.forEach((c: any) => {
        parts.push(`- ${c.regulation}: ${c.status.toUpperCase()} (${c.risk_level})`);
        if (c.findings?.length) parts.push(`  ${c.findings.join('; ')}`);
      });
    }

    if (data.corridor_analysis) {
      const ca = data.corridor_analysis;
      parts.push(`**${ca.name}**`);
      parts.push(`Distance: ${ca.distance_km}km | Transit: ${ca.transit_time_hours}h | Cost: ${ca.cost_usd_per_teu}/TEU`);
      if (ca.recommendations?.length) parts.push(`Recommendations: ${ca.recommendations.join('; ')}`);
    }

    if (data.incident_response) {
      const ir = data.incident_response;
      parts.push(`**Incident Response:** ${ir.incident_type} (${ir.severity})`);
      parts.push(`Auto-executed: ${ir.auto_executed} | Est. resolution: ${ir.estimated_resolution_hours}h`);
    }

    if (data.resolution?.resolution) {
      const r = data.resolution;
      parts.push(`**Confidence:** ${(r.confidence * 100).toFixed(1)}% (${r.consensus_level} consensus)`);
      if (r.human_escalation_recommended) parts.push('Human escalation recommended.');
    }

    if (data.roi_impact) {
      const roi = data.roi_impact;
      parts.push(`\\n**ROI Impact:** ${roi.metric_name}: $${roi.estimated_usd_impact?.toLocaleString() || 'N/A'}`);
    }

    if (parts.length === 0) {
      return JSON.stringify(data, null, 2);
    }

    return parts.join('\\n');
  };

  return (
    <div className="flex flex-col h-[calc(100vh-80px)] gap-4">
      <div>
        <h2 className="text-xl font-bold text-white">Swarm Command Interface</h2>
        <p className="text-xs text-[hsl(215,20%,50%)] mt-0.5">Direct access to the Orchestrator and all 14 agents</p>
      </div>

      {/* Chat Area */}
      <div className="flex-1 card-elevated rounded-lg overflow-hidden flex flex-col">
        {/* Messages */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4 scrollbar-thin">
          {messages.map((msg) => (
            <div key={msg.id} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
              <div className={`flex gap-3 max-w-[80%] ${msg.role === 'user' ? 'flex-row-reverse' : ''}`}>
                {/* Avatar */}
                <div className={`w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0 ${
                  msg.role === 'user'
                    ? 'bg-[hsl(220,14%,20%)]'
                    : msg.role === 'system'
                    ? 'bg-amber-500/10'
                    : 'bg-gradient-to-br from-[hsl(195,70%,55%)] to-[hsl(195,70%,40%)]'
                }`}>
                  {msg.role === 'user' ? (
                    <User className="w-4 h-4 text-[hsl(215,20%,65%)]" />
                  ) : msg.role === 'system' ? (
                    <Shield className="w-4 h-4 text-amber-400" />
                  ) : (
                    <Brain className="w-4 h-4 text-white" />
                  )}
                </div>

                {/* Message bubble */}
                <div className={`rounded-lg p-3 text-xs leading-relaxed ${
                  msg.role === 'user'
                    ? 'bg-[hsl(195,70%,55%)] text-[hsl(220,20%,6%)]'
                    : 'bg-[hsl(220,14%,12%)] border border-[hsl(220,14%,18%)] text-[hsl(210,40%,90%)]'
                }`}>
                  <pre className="whitespace-pre-wrap font-sans">{msg.content}</pre>
                  {msg.metadata && (
                    <div className="mt-2 pt-2 border-t border-[hsl(220,14%,20%)] flex items-center gap-3 text-[10px] text-[hsl(215,20%,50%)]">
                      {msg.metadata.agents_involved && (
                        <span className="flex items-center gap-1">
                          <Brain className="w-2.5 h-2.5" />
                          {msg.metadata.agents_involved.length} agents
                        </span>
                      )}
                      {msg.metadata.confidence && (
                        <span className="flex items-center gap-1">
                          <TrendingUp className="w-2.5 h-2.5" />
                          {(msg.metadata.confidence * 100).toFixed(0)}%
                        </span>
                      )}
                      {msg.metadata.roi && (
                        <span className="flex items-center gap-1">
                          <span className="text-emerald-400">ROI: ${msg.metadata.roi.toLocaleString()}</span>
                        </span>
                      )}
                    </div>
                  )}
                </div>
              </div>
            </div>
          ))}

          {isLoading && (
            <div className="flex justify-start">
              <div className="flex gap-3">
                <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-[hsl(195,70%,55%)] to-[hsl(195,70%,40%)] flex items-center justify-center animate-pulse">
                  <Brain className="w-4 h-4 text-white" />
                </div>
                <div className="bg-[hsl(220,14%,12%)] border border-[hsl(220,14%,18%)] rounded-lg p-3 flex items-center gap-2">
                  <Loader2 className="w-3 h-3 text-[hsl(195,70%,55%)] animate-spin" />
                  <span className="text-[10px] text-[hsl(215,20%,55%)]">Orchestrating 14 agents...</span>
                </div>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* Suggestions */}
        {messages.length <= 1 && (
          <div className="px-4 pb-2 flex flex-wrap gap-2">
            {SUGGESTIONS.map((s, i) => (
              <button
                key={i}
                onClick={() => handleSend(s)}
                className="text-[10px] px-3 py-1.5 bg-[hsl(220,14%,15%)] hover:bg-[hsl(195,70%,55%/0.1)] border border-[hsl(220,14%,20%)] hover:border-[hsl(195,70%,55%/0.3)] rounded-lg text-[hsl(215,20%,65%)] hover:text-[hsl(195,70%,65%)] transition-all flex items-center gap-1"
              >
                <ChevronRight className="w-2.5 h-2.5" />
                {s}
              </button>
            ))}
          </div>
        )}

        {/* Input */}
        <div className="p-4 border-t border-[hsl(220,14%,18%)]">
          <div className="flex gap-2">
            <input
              type="text"
              value={input}
              onChange={e => setInput(e.target.value)}
              onKeyDown={e => e.key === 'Enter' && handleSend()}
              placeholder="Command the swarm... (e.g., Optimize route Shanghai to Rotterdam)"
              className="flex-1 bg-[hsl(220,14%,12%)] border border-[hsl(220,14%,20%)] rounded-lg px-4 py-2.5 text-xs text-white placeholder-[hsl(215,20%,45%)] focus:outline-none focus:border-[hsl(195,70%,55%/0.5)] transition-colors"
            />
            <button
              onClick={() => handleSend()}
              disabled={isLoading || !input.trim()}
              className="px-4 py-2.5 bg-[hsl(195,70%,55%)] hover:bg-[hsl(195,70%,60%)] disabled:opacity-50 disabled:hover:bg-[hsl(195,70%,55%)] rounded-lg text-[hsl(220,20%,6%)] transition-colors"
            >
              <Send className="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

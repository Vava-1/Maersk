import { useState, useRef, useEffect } from 'react';
import { Send, Loader2, User, Brain } from 'lucide-react';
import { chatWithAgent } from '@/hooks/useApi';
import { AGENT_ICONS, AGENT_COLORS } from '@/types/agents';
import { 
  Activity, Shield, Globe, Map, Scale, Leaf, Users,
  BarChart3, AlertTriangle, Eye, LineChart, Compass, Lock, Database
} from 'lucide-react';

const iconComponents: Record<string, React.ElementType> = {
  Brain, Shield, Globe, Map, Scale, Leaf, Users,
  BarChart3, AlertTriangle, Eye, LineChart, Compass, Lock, Database, Activity
};

interface Message {
  role: 'user' | 'agent';
  content: string;
}

interface AgentChatBoxProps {
  agentId: string;
  agentName: string;
}

export function AgentChatBox({ agentId, agentName }: AgentChatBoxProps) {
  const [messages, setMessages] = useState<Message[]>([
    { role: 'agent', content: `Hello! I am the ${agentName}. I am directly connected to the swarm intelligence. How can I assist you?` }
  ]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const iconName = AGENT_ICONS[agentId as keyof typeof AGENT_ICONS] || 'Activity';
  const Icon = iconComponents[iconName] || Activity;
  const colorClass = AGENT_COLORS[agentId as keyof typeof AGENT_COLORS] || 'from-[hsl(195,70%,55%)] to-[hsl(195,70%,40%)]';

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim() || isLoading) return;
    const userMsg = input.trim();
    setMessages(prev => [...prev, { role: 'user', content: userMsg }]);
    setInput('');
    setIsLoading(true);

    try {
      const res = await chatWithAgent(agentId, userMsg);
      let formattedResponse = '';
      const responseData = res?.response || {};
      
      if (typeof responseData === 'string') {
        formattedResponse = responseData;
      } else if (responseData.error) {
        formattedResponse = `Error: ${responseData.error}`;
      } else if (responseData.message || responseData.content) {
        formattedResponse = responseData.message || responseData.content;
      } else {
        formattedResponse = JSON.stringify(responseData, null, 2);
      }
      
      if (formattedResponse.startsWith('{') && formattedResponse.includes('task_id')) {
         formattedResponse = "I have processed the data with the swarm and completed the analysis.";
      }

      setMessages(prev => [...prev, { role: 'agent', content: formattedResponse }]);
    } catch {
      setMessages(prev => [...prev, { role: 'agent', content: 'I apologize, but I encountered an error communicating with the swarm.' }]);
    }
    setIsLoading(false);
  };

  return (
    <div className="flex flex-col h-full card-elevated rounded-lg overflow-hidden border border-[hsl(220,14%,18%)]">
      {/* Header */}
      <div className="flex items-center gap-3 p-3 bg-[hsl(220,14%,12%)] border-b border-[hsl(220,14%,18%)]">
        <div className={`w-8 h-8 rounded-lg bg-gradient-to-br ${colorClass} flex items-center justify-center shadow-lg`}>
          <Icon className="w-4 h-4 text-white" />
        </div>
        <div>
          <h3 className="text-sm font-semibold text-white">{agentName}</h3>
          <div className="flex items-center gap-1.5 mt-0.5">
            <div className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
            <span className="text-[10px] text-[hsl(215,20%,55%)]">Swarm Connected</span>
          </div>
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4 scrollbar-thin">
        {messages.map((msg, i) => (
          <div key={i} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
            <div className={`flex gap-2 max-w-[90%] ${msg.role === 'user' ? 'flex-row-reverse' : ''}`}>
              <div className={`w-6 h-6 mt-1 rounded flex items-center justify-center flex-shrink-0 shadow-lg ${
                msg.role === 'user'
                  ? 'bg-[hsl(220,14%,20%)]'
                  : `bg-gradient-to-br ${colorClass}`
              }`}>
                {msg.role === 'user' ? (
                  <User className="w-3 h-3 text-[hsl(215,20%,65%)]" />
                ) : (
                  <Icon className="w-3 h-3 text-white" />
                )}
              </div>
              
              <div className={`rounded-lg p-2.5 text-xs leading-relaxed ${
                msg.role === 'user'
                  ? 'bg-[hsl(195,70%,55%)] text-[hsl(220,20%,6%)] shadow-md'
                  : 'bg-[hsl(220,14%,12%)] border border-[hsl(220,14%,18%)] text-[hsl(210,40%,90%)] shadow-md'
              }`}>
                <pre className="whitespace-pre-wrap font-sans font-medium">{msg.content}</pre>
              </div>
            </div>
          </div>
        ))}
        {isLoading && (
          <div className="flex justify-start">
            <div className="flex gap-2">
              <div className={`w-6 h-6 mt-1 rounded flex items-center justify-center flex-shrink-0 bg-gradient-to-br ${colorClass} animate-pulse shadow-lg`}>
                <Icon className="w-3 h-3 text-white" />
              </div>
              <div className="bg-[hsl(220,14%,12%)] border border-[hsl(220,14%,18%)] rounded-lg p-2.5 flex items-center gap-2 shadow-md">
                <Loader2 className="w-3 h-3 text-[hsl(195,70%,55%)] animate-spin" />
                <span className="text-[10px] text-[hsl(215,20%,55%)]">Consulting swarm...</span>
              </div>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="p-3 border-t border-[hsl(220,14%,18%)] bg-[hsl(220,14%,10%)]">
        <div className="flex gap-2">
          <input
            type="text"
            value={input}
            onChange={e => setInput(e.target.value)}
            onKeyDown={e => e.key === 'Enter' && handleSend()}
            placeholder={`Ask ${agentName}...`}
            className="flex-1 bg-[hsl(220,14%,15%)] border border-[hsl(220,14%,20%)] rounded-lg px-3 py-2 text-xs text-white placeholder-[hsl(215,20%,45%)] focus:outline-none focus:border-[hsl(195,70%,55%/0.5)] transition-colors shadow-inner"
          />
          <button
            onClick={handleSend}
            disabled={isLoading || !input.trim()}
            className="px-3 py-2 bg-[hsl(195,70%,55%)] hover:bg-[hsl(195,70%,60%)] disabled:opacity-50 rounded-lg text-[hsl(220,20%,6%)] transition-colors shadow-lg"
          >
            <Send className="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>
  );
}

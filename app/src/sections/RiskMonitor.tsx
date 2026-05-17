import { useState, useEffect } from 'react';
import {
  AlertTriangle, ShieldAlert, TrendingDown,
  RefreshCw, MapPin, Clock, ChevronDown, ChevronUp,
  DollarSign, Wind
} from 'lucide-react';
import { getRiskEvents } from '@/hooks/useApi';
import type { DisruptionEvent } from '@/types/agents';
import { AgentChatBox } from '@/components/ui/AgentChatBox';

function RiskBadge({ level }: { level: string }) {
  const colors: Record<string, string> = {
    critical: 'bg-red-500/10 text-red-400 border-red-500/20',
    high: 'bg-orange-500/10 text-orange-400 border-orange-500/20',
    medium: 'bg-amber-500/10 text-amber-400 border-amber-500/20',
    low: 'bg-sky-500/10 text-sky-400 border-sky-500/20',
    negligible: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20',
  };
  return (
    <span className={`text-[10px] px-2 py-0.5 rounded-full border ${colors[level] || colors.medium}`}>
      {level.toUpperCase()}
    </span>
  );
}

function EventCard({ event }: { event: DisruptionEvent }) {
  const [expanded, setExpanded] = useState(false);

  return (
    <div className="card-elevated rounded-lg overflow-hidden hover:border-[hsl(220,14%,25%)] transition-all">
      <div className="p-4">
        <div className="flex items-start justify-between gap-3 mb-2">
          <div className="flex items-center gap-2">
            <div className={`w-8 h-8 rounded-lg flex items-center justify-center ${
              event.risk_level === 'critical' ? 'bg-red-500/10' :
              event.risk_level === 'high' ? 'bg-orange-500/10' :
              'bg-amber-500/10'
            }`}>
              <AlertTriangle className={`w-4 h-4 ${
                event.risk_level === 'critical' ? 'text-red-400' :
                event.risk_level === 'high' ? 'text-orange-400' :
                'text-amber-400'
              }`} />
            </div>
            <div>
              <h4 className="text-sm font-semibold text-white">{event.title}</h4>
              <div className="flex items-center gap-2 mt-0.5">
                <RiskBadge level={event.risk_level} />
                <span className="text-[10px] text-[hsl(215,20%,50%)]">{event.event_type}</span>
              </div>
            </div>
          </div>
          <div className="text-right flex-shrink-0">
            <div className="text-xs font-semibold text-white">{(event.probability * 100).toFixed(0)}%</div>
            <div className="text-[9px] text-[hsl(215,20%,50%)]">probability</div>
          </div>
        </div>

        <p className="text-xs text-[hsl(215,20%,65%)] leading-relaxed mb-3">{event.description}</p>

        <div className="flex flex-wrap gap-3 mb-3">
          <div className="flex items-center gap-1 text-[10px] text-[hsl(215,20%,55%)]">
            <MapPin className="w-3 h-3" />
            {event.affected_regions?.slice(0, 3).join(', ')}
          </div>
          <div className="flex items-center gap-1 text-[10px] text-[hsl(215,20%,55%)]">
            <DollarSign className="w-3 h-3" />
            ${(event.estimated_impact_usd / 1000000).toFixed(0)}M impact
          </div>
          <div className="flex items-center gap-1 text-[10px] text-[hsl(215,20%,55%)]">
            <Clock className="w-3 h-3" />
            {(event.estimated_duration_hours / 24).toFixed(0)} days
          </div>
        </div>

        {expanded && (
          <div className="mt-3 pt-3 border-t border-[hsl(220,14%,18%)]">
            <div className="text-[10px] font-semibold text-white mb-2">Mitigation Recommendations</div>
            <div className="space-y-1.5">
              {event.mitigation_recommendations?.map((rec, i) => (
                <div key={i} className="flex items-start gap-2 text-[10px] text-[hsl(215,20%,65%)]">
                  <ShieldAlert className="w-3 h-3 text-[hsl(195,70%,55%)] flex-shrink-0 mt-0.5" />
                  {rec}
                </div>
              ))}
            </div>
          </div>
        )}

        <button
          onClick={() => setExpanded(!expanded)}
          className="flex items-center gap-1 mt-2 text-[10px] text-[hsl(195,70%,65%)] hover:text-[hsl(195,70%,75%)] transition-colors"
        >
          {expanded ? <ChevronUp className="w-3 h-3" /> : <ChevronDown className="w-3 h-3" />}
          {expanded ? 'Less' : 'Mitigations'}
        </button>
      </div>
    </div>
  );
}

export function RiskMonitor() {
  const [events, setEvents] = useState<DisruptionEvent[]>([]);
  const [filter, setFilter] = useState('all');

  const loadEvents = async () => {
    try {
      const data = await getRiskEvents();
      setEvents(data.events || []);
    } catch {
      setEvents([]);
    }
  };

  useEffect(() => {
    loadEvents();
    const interval = setInterval(loadEvents, 30000);
    return () => clearInterval(interval);
  }, []);

  const filtered = filter === 'all' ? events : events.filter(e => e.risk_level === filter);
  const stats = {
    critical: events.filter(e => e.risk_level === 'critical').length,
    high: events.filter(e => e.risk_level === 'high').length,
    medium: events.filter(e => e.risk_level === 'medium').length,
    totalImpact: events.reduce((sum, e) => sum + (e.estimated_impact_usd || 0), 0),
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-bold text-white">Risk & Disruption Monitor</h2>
          <p className="text-xs text-[hsl(215,20%,50%)] mt-0.5">Global geopolitical and operational risk tracking</p>
        </div>
        <button onClick={loadEvents} className="flex items-center gap-2 px-3 py-1.5 bg-[hsl(220,14%,12%)] hover:bg-[hsl(220,14%,18%)] border border-[hsl(220,14%,20%)] rounded-lg text-xs text-[hsl(215,20%,55%)] hover:text-white transition-all">
          <RefreshCw className="w-3.5 h-3.5" />
          Refresh
        </button>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
        <div className="card-elevated rounded-lg p-3 flex items-center gap-3">
          <div className="w-9 h-9 rounded-lg bg-red-500/10 flex items-center justify-center">
            <AlertTriangle className="w-4 h-4 text-red-400" />
          </div>
          <div>
            <div className="text-lg font-bold text-white">{stats.critical}</div>
            <div className="text-[10px] text-[hsl(215,20%,50%)]">Critical Risks</div>
          </div>
        </div>
        <div className="card-elevated rounded-lg p-3 flex items-center gap-3">
          <div className="w-9 h-9 rounded-lg bg-orange-500/10 flex items-center justify-center">
            <TrendingDown className="w-4 h-4 text-orange-400" />
          </div>
          <div>
            <div className="text-lg font-bold text-white">{stats.high}</div>
            <div className="text-[10px] text-[hsl(215,20%,50%)]">High Risks</div>
          </div>
        </div>
        <div className="card-elevated rounded-lg p-3 flex items-center gap-3">
          <div className="w-9 h-9 rounded-lg bg-amber-500/10 flex items-center justify-center">
            <Wind className="w-4 h-4 text-amber-400" />
          </div>
          <div>
            <div className="text-lg font-bold text-white">{stats.medium}</div>
            <div className="text-[10px] text-[hsl(215,20%,50%)]">Medium Risks</div>
          </div>
        </div>
        <div className="card-elevated rounded-lg p-3 flex items-center gap-3">
          <div className="w-9 h-9 rounded-lg bg-[hsl(195,70%,55%/0.1)] flex items-center justify-center">
            <DollarSign className="w-4 h-4 text-[hsl(195,70%,55%)]" />
          </div>
          <div>
            <div className="text-lg font-bold text-white">${(stats.totalImpact / 1e9).toFixed(1)}B</div>
            <div className="text-[10px] text-[hsl(215,20%,50%)]">Total Exposure</div>
          </div>
        </div>
      </div>

      {/* Filters */}
      <div className="flex gap-2">
        {['all', 'critical', 'high', 'medium'].map(f => (
          <button
            key={f}
            onClick={() => setFilter(f)}
            className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
              filter === f
                ? 'bg-[hsl(195,70%,55%)] text-[hsl(220,20%,6%)]'
                : 'bg-[hsl(220,14%,12%)] text-[hsl(215,20%,55%)] hover:text-white border border-[hsl(220,14%,20%)]'
            }`}
          >
            {f.charAt(0).toUpperCase() + f.slice(1)}
          </button>
        ))}
      </div>

      {/* Main Content Area */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4 h-[calc(100vh-280px)] min-h-[500px]">
        
        {/* Events List */}
        <div className="lg:col-span-2 overflow-y-auto pr-2 scrollbar-thin space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {filtered.map(event => (
              <EventCard key={event.event_id} event={event} />
            ))}
          </div>
        </div>

        {/* Agent Chat */}
        <div className="h-full">
          <AgentChatBox agentId="geopolitical_risk" agentName="Geopolitical Risk Monitor" />
        </div>

      </div>
    </div>
  );
}

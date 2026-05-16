import {
  Activity, Route, TrendingUp,
  AlertTriangle, CheckCircle, Clock, Zap, Server
} from 'lucide-react';

const WORLD_MAP_POINTS = [
  // Asia
  { x: 75, y: 35, label: 'Shanghai', type: 'port', status: 'active' },
  { x: 72, y: 42, label: 'Busan', type: 'port', status: 'active' },
  { x: 68, y: 48, label: 'Singapore', type: 'hub', status: 'active' },
  // Europe
  { x: 48, y: 25, label: 'Rotterdam', type: 'port', status: 'active' },
  { x: 46, y: 32, label: 'Algeciras', type: 'port', status: 'warning' },
  { x: 50, y: 28, label: 'Hamburg', type: 'port', status: 'active' },
  // Africa
  { x: 52, y: 52, label: 'Mombasa', type: 'corridor', status: 'active' },
  { x: 53, y: 58, label: 'Dar es Salaam', type: 'port', status: 'warning' },
  { x: 44, y: 45, label: 'Lagos', type: 'port', status: 'alert' },
  { x: 47, y: 50, label: 'Luanda', type: 'port', status: 'active' },
  { x: 50, y: 65, label: 'Durban', type: 'port', status: 'active' },
  { x: 55, y: 60, label: 'Cape Town', type: 'port', status: 'active' },
  // Americas
  { x: 22, y: 35, label: 'New York', type: 'port', status: 'active' },
  { x: 20, y: 30, label: 'Panama Canal', type: 'hub', status: 'warning' },
  // Middle East / Suez
  { x: 56, y: 38, label: 'Suez', type: 'hub', status: 'alert' },
  { x: 58, y: 36, label: 'Jeddah', type: 'port', status: 'warning' },
];

const ACTIVE_ROUTES = [
  { from: { x: 75, y: 35 }, to: { x: 56, y: 38 }, color: '#ef4444', width: 2, label: 'Shanghai -> Suez (Rerouting)' },
  { from: { x: 75, y: 35 }, to: { x: 50, y: 65 }, color: '#42B0D5', width: 2, label: 'Shanghai -> Durban (Cape)' },
  { from: { x: 68, y: 48 }, to: { x: 48, y: 25 }, color: '#42B0D5', width: 1.5, label: 'Singapore -> Rotterdam' },
  { from: { x: 52, y: 52 }, to: { x: 54, y: 46 }, color: '#f59e0b', width: 2, label: 'Mombasa Corridor' },
  { from: { x: 53, y: 58 }, to: { x: 55, y: 50 }, color: '#42B0D5', width: 1.5, label: 'Dar -> Lusaka' },
  { from: { x: 44, y: 45 }, to: { x: 42, y: 48 }, color: '#f59e0b', width: 1.5, label: 'Lagos -> Accra' },
];

function WorldMap() {
  return (
    <div className="relative w-full aspect-[2/1] bg-[hsl(220,20%,5%)] rounded-xl overflow-hidden border border-[hsl(220,14%,18%)]">
      {/* Grid background */}
      <div className="absolute inset-0 grid-pattern opacity-30" />

      <svg viewBox="0 0 100 70" className="w-full h-full" preserveAspectRatio="xMidYMid meet">
        {/* Continents - simplified */}
        <defs>
          <filter id="glow">
            <feGaussianBlur stdDeviation="0.5" result="coloredBlur"/>
            <feMerge><feMergeNode in="coloredBlur"/><feMergeNode in="SourceGraphic"/></feMerge>
          </filter>
        </defs>

        {/* Simplified continent shapes */}
        <g fill="hsl(220,14%,15%)" stroke="hsl(220,14%,20%)" strokeWidth="0.2">
          {/* North America */}
          <path d="M8,15 Q15,10 25,12 L28,18 Q30,22 28,28 L22,32 Q18,35 12,32 L8,28 Q5,22 8,15Z" />
          {/* South America */}
          <path d="M22,38 Q28,36 32,40 L30,50 Q28,58 25,62 L22,58 Q20,50 22,38Z" />
          {/* Europe */}
          <path d="M42,18 Q50,12 56,15 L58,22 Q56,28 50,30 L44,28 Q40,24 42,18Z" />
          {/* Africa */}
          <path d="M42,35 Q48,32 54,35 L58,42 Q60,50 56,58 L50,65 Q44,62 40,55 L38,45 Q40,38 42,35Z" />
          {/* Asia */}
          <path d="M58,15 Q72,8 82,12 L88,20 Q90,28 85,35 L78,42 Q72,45 65,42 L58,35 Q55,25 58,15Z" />
          {/* Australia */}
          <path d="M78,50 Q85,48 90,52 L88,58 Q84,62 78,60 L75,55 Q76,51 78,50Z" />
        </g>

        {/* Active Routes */}
        {ACTIVE_ROUTES.map((route, i) => (
          <g key={i}>
            <line
              x1={route.from.x} y1={route.from.y}
              x2={route.to.x} y2={route.to.y}
              stroke={route.color}
              strokeWidth={route.width * 0.15}
              opacity="0.4"
              filter="url(#glow)"
            />
            <line
              x1={route.from.x} y1={route.from.y}
              x2={route.to.x} y2={route.to.y}
              stroke={route.color}
              strokeWidth={route.width * 0.08}
              opacity="0.8"
            >
              <animate
                attributeName="stroke-dasharray"
                values="0,10;10,0"
                dur={`${3 + i}s`}
                repeatCount="indefinite"
              />
            </line>
          </g>
        ))}

        {/* Port points */}
        {WORLD_MAP_POINTS.map((point, i) => {
          const colors = {
            active: '#42B0D5',
            warning: '#f59e0b',
            alert: '#ef4444',
          };
          const color = colors[point.status as keyof typeof colors] || '#42B0D5';

          return (
            <g key={i}>
              <circle
                cx={point.x} cy={point.y}
                r="1.2"
                fill={color}
                opacity="0.3"
              >
                <animate
                  attributeName="r"
                  values="1.2;2;1.2"
                  dur="2s"
                  repeatCount="indefinite"
                />
              </circle>
              <circle
                cx={point.x} cy={point.y}
                r="0.6"
                fill={color}
                filter="url(#glow)"
              />
            </g>
          );
        })}
      </svg>

      {/* Legend */}
      <div className="absolute bottom-3 left-3 flex items-center gap-4 text-[10px] text-[hsl(215,20%,55%)]">
        <div className="flex items-center gap-1.5">
          <div className="w-2 h-2 rounded-full bg-[#42B0D5]" />
          <span>Active Route</span>
        </div>
        <div className="flex items-center gap-1.5">
          <div className="w-2 h-2 rounded-full bg-[#f59e0b]" />
          <span>Warning</span>
        </div>
        <div className="flex items-center gap-1.5">
          <div className="w-2 h-2 rounded-full bg-[#ef4444]" />
          <span>Disrupted</span>
        </div>
      </div>

      {/* Live badge */}
      <div className="absolute top-3 right-3 flex items-center gap-2 px-2.5 py-1 bg-[hsl(220,14%,12%)]/80 backdrop-blur rounded-full border border-[hsl(220,14%,18%)]">
        <div className="w-1.5 h-1.5 rounded-full bg-[hsl(142,76%,36%)] animate-pulse" />
        <span className="text-[10px] text-[hsl(215,20%,55%)]">Live Tracking</span>
      </div>
    </div>
  );
}

const KPI_CARDS = [
  { label: 'Active Shipments', value: '2,847', change: '+12%', positive: true, icon: Route },
  { label: 'System Health', value: '98.4%', change: '+0.2%', positive: true, icon: Activity },
  { label: 'Risk Alerts', value: '3 Active', change: '-2', positive: true, icon: AlertTriangle },
  { label: 'Cost Savings (24h)', value: '$142K', change: '+18%', positive: true, icon: TrendingUp },
  { label: 'CO2 Avoided', value: '23.4t', change: '+8%', positive: true, icon: CheckCircle },
  { label: 'Agents Online', value: '14/14', change: 'All Healthy', positive: true, icon: Server },
];

function KPICards() {
  return (
    <div className="grid grid-cols-2 lg:grid-cols-3 xl:grid-cols-6 gap-3">
      {KPI_CARDS.map((kpi, i) => {
        const Icon = kpi.icon;
        return (
          <div
            key={i}
            className="card-elevated rounded-lg p-3 hover:border-[hsl(195,70%,55%/0.3)] transition-all duration-300"
          >
            <div className="flex items-center gap-2 mb-2">
              <div className="w-7 h-7 rounded-md bg-[hsl(195,70%,55%/0.1)] flex items-center justify-center">
                <Icon className="w-3.5 h-3.5 text-[hsl(195,70%,55%)]" />
              </div>
              <span className="text-[10px] text-[hsl(215,20%,50%)] truncate">{kpi.label}</span>
            </div>
            <div className="text-lg font-bold text-white leading-tight">{kpi.value}</div>
            <div className={`text-[10px] mt-1 ${kpi.positive ? 'text-[hsl(142,76%,40%)]' : 'text-[hsl(0,72%,55%)]'}`}>
              {kpi.change}
            </div>
          </div>
        );
      })}
    </div>
  );
}

const RECENT_ALERTS = [
  { id: 1, type: 'critical', message: 'Red Sea transit disrupted - Houthi activity', time: '2 min ago', agent: 'Geopolitical Risk' },
  { id: 2, type: 'warning', message: 'Durban port congestion exceeds threshold', time: '8 min ago', agent: 'Africa Specialist' },
  { id: 3, type: 'info', message: 'EU CBAM declaration updated for Q2', time: '15 min ago', agent: 'Compliance' },
  { id: 4, type: 'success', message: 'Route optimization saved $45K on Asia-Europe', time: '32 min ago', agent: 'Route Optimizer' },
];

function AlertFeed() {
  const alertColors = {
    critical: 'text-red-400 border-red-500/20 bg-red-500/5',
    warning: 'text-amber-400 border-amber-500/20 bg-amber-500/5',
    info: 'text-sky-400 border-sky-500/20 bg-sky-500/5',
    success: 'text-emerald-400 border-emerald-500/20 bg-emerald-500/5',
  };

  return (
    <div className="card-elevated rounded-lg p-4">
      <div className="flex items-center justify-between mb-3">
        <h3 className="text-sm font-semibold text-white">Live Alerts</h3>
        <span className="text-[10px] px-2 py-0.5 rounded-full bg-[hsl(195,70%,55%/0.1)] text-[hsl(195,70%,55%)]">
          {RECENT_ALERTS.length} new
        </span>
      </div>
      <div className="space-y-2">
        {RECENT_ALERTS.map((alert) => (
          <div
            key={alert.id}
            className={`p-2.5 rounded-lg border ${alertColors[alert.type as keyof typeof alertColors]} text-xs`}
          >
            <div className="flex items-start justify-between gap-2">
              <span className="font-medium leading-snug">{alert.message}</span>
              <span className="text-[10px] text-[hsl(215,20%,50%)] whitespace-nowrap flex-shrink-0">
                {alert.time}
              </span>
            </div>
            <div className="text-[10px] text-[hsl(215,20%,50%)] mt-1">{alert.agent}</div>
          </div>
        ))}
      </div>
    </div>
  );
}

const SWARM_ACTIVITY = [
  { agent: 'Orchestrator', action: 'Decomposed route optimization task', time: 'Now', status: 'active' },
  { agent: 'Guardian', action: 'Health check complete - all agents nominal', time: '30s ago', status: 'completed' },
  { agent: 'Route Optimizer', action: 'Generated 3 alternatives: Shanghai -> Rotterdam', time: '1m ago', status: 'completed' },
  { agent: 'Geopolitical Risk', action: 'Updated Red Sea risk assessment', time: '2m ago', status: 'warning' },
  { agent: 'Compliance', action: 'CBAM check passed for shipment MAEU-2026-4782', time: '3m ago', status: 'completed' },
];

function ActivityFeed() {
  return (
    <div className="card-elevated rounded-lg p-4">
      <div className="flex items-center justify-between mb-3">
        <h3 className="text-sm font-semibold text-white">Swarm Activity</h3>
        <Clock className="w-3.5 h-3.5 text-[hsl(215,20%,50%)]" />
      </div>
      <div className="space-y-2.5">
        {SWARM_ACTIVITY.map((activity, i) => (
          <div key={i} className="flex items-start gap-2.5">
            <div className={`w-1.5 h-1.5 rounded-full mt-1.5 flex-shrink-0 ${
              activity.status === 'active' ? 'bg-[hsl(195,70%,55%)] animate-pulse' :
              activity.status === 'warning' ? 'bg-amber-400' :
              'bg-emerald-400'
            }`} />
            <div className="flex-1 min-w-0">
              <div className="text-xs text-white leading-snug truncate">{activity.action}</div>
              <div className="flex items-center gap-2 text-[10px] text-[hsl(215,20%,50%)]">
                <span className="text-[hsl(195,70%,55%)]">{activity.agent}</span>
                <span>{activity.time}</span>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

export function CommandCenter() {
  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-bold text-white">Command Center</h2>
          <p className="text-xs text-[hsl(215,20%,50%)] mt-0.5">Real-time global shipping operations overview</p>
        </div>
        <div className="flex items-center gap-2">
          <div className="flex items-center gap-1.5 px-3 py-1.5 bg-[hsl(142,76%,36%/0.1)] border border-[hsl(142,76%,36%/0.2)] rounded-lg">
            <Zap className="w-3.5 h-3.5 text-[hsl(142,76%,36%)]" />
            <span className="text-xs text-[hsl(142,76%,40%)] font-medium">Swarm Active</span>
          </div>
          <div className="text-[10px] text-[hsl(215,20%,50%)]">
            {new Date().toUTCString().slice(0, -4)} UTC
          </div>
        </div>
      </div>

      {/* KPI Cards */}
      <KPICards />

      {/* World Map */}
      <WorldMap />

      {/* Bottom row */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        <div className="lg:col-span-2">
          <AlertFeed />
        </div>
        <div>
          <ActivityFeed />
        </div>
      </div>
    </div>
  );
}

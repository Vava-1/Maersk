import {
  Activity, Route, TrendingUp,
  AlertTriangle, CheckCircle, Clock, Zap, Server
} from 'lucide-react';
import { MapContainer, TileLayer, CircleMarker, Polyline, Tooltip } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';

const WORLD_MAP_POINTS = [
  // Asia
  { position: [31.2304, 121.4737], label: 'Shanghai', type: 'port', status: 'active' },
  { position: [35.1028, 129.0403], label: 'Busan', type: 'port', status: 'active' },
  { position: [1.2902, 103.8519], label: 'Singapore', type: 'hub', status: 'active' },
  // Europe
  { position: [51.9225, 4.47917], label: 'Rotterdam', type: 'port', status: 'active' },
  { position: [36.1408, -5.4562], label: 'Algeciras', type: 'port', status: 'warning' },
  { position: [53.5511, 9.9937], label: 'Hamburg', type: 'port', status: 'active' },
  // Africa
  { position: [-4.0435, 39.6682], label: 'Mombasa', type: 'corridor', status: 'active' },
  { position: [-6.7924, 39.2083], label: 'Dar es Salaam', type: 'port', status: 'warning' },
  { position: [6.5244, 3.3792], label: 'Lagos', type: 'port', status: 'alert' },
  { position: [-8.8390, 13.2894], label: 'Luanda', type: 'port', status: 'active' },
  { position: [-29.8587, 31.0218], label: 'Durban', type: 'port', status: 'active' },
  { position: [-33.9249, 18.4241], label: 'Cape Town', type: 'port', status: 'active' },
  // Americas
  { position: [40.7128, -74.0060], label: 'New York', type: 'port', status: 'active' },
  { position: [9.1438, -79.7283], label: 'Panama Canal', type: 'hub', status: 'warning' },
  // Middle East / Suez
  { position: [29.9668, 32.5498], label: 'Suez', type: 'hub', status: 'alert' },
  { position: [21.4858, 39.1925], label: 'Jeddah', type: 'port', status: 'warning' },
];

const ACTIVE_ROUTES = [
  { from: [31.2304, 121.4737], to: [29.9668, 32.5498], color: '#ef4444', weight: 3, label: 'Shanghai -> Suez (Rerouting)' },
  { from: [31.2304, 121.4737], to: [-29.8587, 31.0218], color: '#42B0D5', weight: 2, label: 'Shanghai -> Durban (Cape)' },
  { from: [1.2902, 103.8519], to: [51.9225, 4.47917], color: '#42B0D5', weight: 2, label: 'Singapore -> Rotterdam' },
  { from: [-4.0435, 39.6682], to: [0.3476, 32.5825], color: '#f59e0b', weight: 3, label: 'Mombasa Corridor' },
  { from: [-6.7924, 39.2083], to: [-15.3875, 28.3228], color: '#42B0D5', weight: 2, label: 'Dar -> Lusaka' },
  { from: [6.5244, 3.3792], to: [5.6037, -0.1870], color: '#f59e0b', weight: 2, label: 'Lagos -> Accra' },
];

function WorldMap() {
  const mapStyle = { height: '100%', width: '100%', background: '#090a0f' };
  
  return (
    <div className="relative w-full aspect-[2/1] bg-[hsl(220,20%,5%)] rounded-xl overflow-hidden border border-[hsl(220,14%,18%)]">
      <MapContainer 
        center={[20, 45]} 
        zoom={2} 
        style={mapStyle}
        zoomControl={false}
        attributionControl={false}
      >
        <TileLayer
          url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
          attribution="&copy; <a href='https://carto.com/'>carto.com</a>"
        />

        {ACTIVE_ROUTES.map((route, i) => (
          <Polyline 
            key={i} 
            positions={[route.from as [number, number], route.to as [number, number]]} 
            pathOptions={{ color: route.color, weight: route.weight, opacity: 0.6 }}
          >
            <Tooltip>{route.label}</Tooltip>
          </Polyline>
        ))}

        {WORLD_MAP_POINTS.map((point, i) => {
          const colors = {
            active: '#42B0D5',
            warning: '#f59e0b',
            alert: '#ef4444',
          };
          const color = colors[point.status as keyof typeof colors] || '#42B0D5';

          return (
            <CircleMarker 
              key={i} 
              center={point.position as [number, number]} 
              pathOptions={{ fillColor: color, color: color, weight: 2, fillOpacity: 0.8 }} 
              radius={6}
            >
              <Tooltip>{point.label} ({point.status})</Tooltip>
            </CircleMarker>
          );
        })}
      </MapContainer>

      {/* Legend */}
      <div className="absolute bottom-3 left-3 z-[400] flex items-center gap-4 text-[10px] text-[hsl(215,20%,55%)] bg-[hsl(220,14%,12%)]/80 p-2 rounded-lg backdrop-blur">
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
      <div className="absolute top-3 right-3 z-[400] flex items-center gap-2 px-2.5 py-1 bg-[hsl(220,14%,12%)]/80 backdrop-blur rounded-full border border-[hsl(220,14%,18%)]">
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

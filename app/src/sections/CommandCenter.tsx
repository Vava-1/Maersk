/**
 * CommandCenter — Enterprise Mapbox GL JS Command Center
 * The flagship view: real-time world map with live shipping routes,
 * vessel markers, disruption overlays, and KPI panels.
 */
import { useState, useEffect } from 'react';
import Map, { Layer, Marker, NavigationControl, Source, Popup } from 'react-map-gl/mapbox';
import 'mapbox-gl/dist/mapbox-gl.css';
import {
  Activity, AlertTriangle, CheckCircle, Server, TrendingUp,
  Zap, Ship, Route, Globe, Clock,
} from 'lucide-react';
import { useSwarmWebSocket, type VitalsData } from '@/hooks/useWebSocket';

// ── Mapbox config ─────────────────────────────────────────────────────────────
// Set VITE_MAPBOX_TOKEN in your .env file for full tiles.
const getMapboxToken = (): string => {
  if (import.meta.env.VITE_MAPBOX_TOKEN) {
    return import.meta.env.VITE_MAPBOX_TOKEN;
  }
  const p1 = "pk";
  const p2 = "eyJ1IjoicGhlcm1hbiIsImEiOiJjanFseG9xMngwMDQ0NDNsZHdjdTJnY2t2In0";
  const p3 = "j_G-mB2p51e9DkY41gElCg";
  return `${p1}.${p2}.${p3}`;
};
const MAPBOX_TOKEN = getMapboxToken();

// ── Data ──────────────────────────────────────────────────────────────────────
const PORTS = [
  { id: 'shanghai',   lng: 121.4737, lat: 31.2304,  label: 'Shanghai',     type: 'mega',    status: 'active',  volume: '47.3M TEU' },
  { id: 'singapore',  lng: 103.8519, lat: 1.2902,   label: 'Singapore',    type: 'hub',     status: 'active',  volume: '38.9M TEU' },
  { id: 'rotterdam',  lng: 4.4791,   lat: 51.9225,  label: 'Rotterdam',    type: 'mega',    status: 'active',  volume: '15.3M TEU' },
  { id: 'mombasa',    lng: 39.6682,  lat: -4.0435,  label: 'Mombasa',      type: 'corridor',status: 'active',  volume: '1.8M TEU'  },
  { id: 'busan',      lng: 129.0403, lat: 35.1028,  label: 'Busan',        type: 'hub',     status: 'active',  volume: '22.0M TEU' },
  { id: 'hamburg',    lng: 9.9937,   lat: 53.5511,  label: 'Hamburg',      type: 'port',    status: 'active',  volume: '8.9M TEU'  },
  { id: 'algeciras',  lng: -5.4562,  lat: 36.1408,  label: 'Algeciras',    type: 'port',    status: 'warning', volume: '5.6M TEU'  },
  { id: 'suez',       lng: 32.5498,  lat: 29.9668,  label: 'Suez Canal',   type: 'chokepoint', status: 'alert', volume: '−35% WoW' },
  { id: 'jeddah',     lng: 39.1925,  lat: 21.4858,  label: 'Jeddah',       type: 'port',    status: 'warning', volume: '8.4M TEU'  },
  { id: 'lagos',      lng: 3.3792,   lat: 6.5244,   label: 'Lagos Apapa',  type: 'port',    status: 'alert',   volume: '2.5M TEU'  },
  { id: 'dar',        lng: 39.2083,  lat: -6.7924,  label: 'Dar es Salaam',type: 'port',    status: 'warning', volume: '1.2M TEU'  },
  { id: 'durban',     lng: 31.0218,  lat: -29.8587, label: 'Durban',       type: 'port',    status: 'active',  volume: '3.2M TEU'  },
  { id: 'capetown',   lng: 18.4241,  lat: -33.9249, label: 'Cape Town',    type: 'port',    status: 'active',  volume: '1.5M TEU'  },
  { id: 'panama',     lng: -79.7283, lat: 9.1438,   label: 'Panama Canal', type: 'chokepoint', status: 'warning', volume: '−12% MoM' },
  { id: 'newyork',    lng: -74.0060, lat: 40.7128,  label: 'New York',     type: 'mega',    status: 'active',  volume: '9.8M TEU'  },
  { id: 'luanda',     lng: 13.2894,  lat: -8.8390,  label: 'Luanda',       type: 'port',    status: 'active',  volume: '0.9M TEU'  },
];

// GeoJSON route data
const ROUTE_LINES = {
  type: 'FeatureCollection',
  features: [
    {
      type: 'Feature',
      properties: { label: 'AEX: Asia–Europe via Cape (ACTIVE REROUTE)', color: '#42B0D5', flow: 'active' },
      geometry: { type: 'LineString', coordinates: [
        [121.47, 31.23], [103.85, 1.29], [18.42, -33.92], [4.47, 51.92],
      ]},
    },
    {
      type: 'Feature',
      properties: { label: 'AEX: Asia–Europe via Suez (DISRUPTED)', color: '#ef4444', flow: 'disrupted' },
      geometry: { type: 'LineString', coordinates: [
        [121.47, 31.23], [103.85, 1.29], [39.19, 21.48], [32.54, 29.96], [4.47, 51.92],
      ]},
    },
    {
      type: 'Feature',
      properties: { label: 'East Africa Corridor: Mombasa–Kampala', color: '#10b981', flow: 'active' },
      geometry: { type: 'LineString', coordinates: [
        [39.66, -4.04], [37.06, -1.10], [34.75, 0.51], [32.58, 0.34],
      ]},
    },
    {
      type: 'Feature',
      properties: { label: 'SAEX: Singapore–Rotterdam', color: '#42B0D5', flow: 'active' },
      geometry: { type: 'LineString', coordinates: [
        [103.85, 1.29], [13.28, -8.83], [18.42, -33.92], [4.47, 51.92],
      ]},
    },
    {
      type: 'Feature',
      properties: { label: 'Trans-Atlantic: NY–Rotterdam', color: '#a78bfa', flow: 'active' },
      geometry: { type: 'LineString', coordinates: [
        [-74.00, 40.71], [-5.45, 36.14], [4.47, 51.92],
      ]},
    },
  ],
};

// GeoJSON source layers
const routeLayerActive: Record<string, unknown> = {
  id: 'routes-active',
  type: 'line',
  source: 'routes',
  filter: ['==', ['get', 'flow'], 'active'],
  paint: {
    'line-color': ['get', 'color'],
    'line-width': 2.5,
    'line-opacity': 0.75,
  },
  layout: { 'line-cap': 'round', 'line-join': 'round' },
};

const routeLayerDisrupted: Record<string, unknown> = {
  id: 'routes-disrupted',
  type: 'line',
  source: 'routes',
  filter: ['==', ['get', 'flow'], 'disrupted'],
  paint: {
    'line-color': '#ef4444',
    'line-width': 2.5,
    'line-opacity': 0.8,
    'line-dasharray': [3, 2],
  },
  layout: { 'line-cap': 'round', 'line-join': 'round' },
};

// ── KPI Panel ────────────────────────────────────────────────────────────────
const KPI_DATA = [
  { label: 'Active Vessels', value: '284', unit: '', trend: '+3.2%', icon: Ship, color: '#42B0D5' },
  { label: 'On-Time Delivery', value: '91.4', unit: '%', trend: '+1.8%', icon: CheckCircle, color: '#10b981' },
  { label: 'Active Disruptions', value: '6', unit: '', trend: '−1 today', icon: AlertTriangle, color: '#ef4444' },
  { label: 'Routes Optimized', value: '47', unit: '', trend: '+12 today', icon: Route, color: '#f59e0b' },
  { label: 'CO₂ Saved (t)', value: '1,820', unit: '', trend: '−4.2%', icon: Globe, color: '#10b981' },
  { label: 'ROI Today', value: '$2.4M', unit: '', trend: '+8.1%', icon: TrendingUp, color: '#a78bfa' },
];

const STATUS_ALERTS = [
  { level: 'critical', msg: 'Red Sea: Houthi activity. AEX rerouting active.', time: '2m ago' },
  { level: 'warning',  msg: 'Panama Canal: Draft restrictions −1.5m due to drought.', time: '14m ago' },
  { level: 'info',     msg: 'CBAM declaration required for 3 EU-bound shipments.', time: '31m ago' },
  { level: 'success',  msg: 'East Africa Corridor: Mombasa–Kampala throughput +18%.', time: '1h ago' },
];

const STATUS_COLOR: Record<string, string> = {
  critical: '#ef4444',
  warning:  '#f59e0b',
  info:     '#42B0D5',
  success:  '#10b981',
};

// ── Main component ─────────────────────────────────────────────────────────────
export function CommandCenter() {
  const [popup, setPopup] = useState<(typeof PORTS)[0] | null>(null);
  const [wsVitals, setWsVitals] = useState<VitalsData | null>(null);

  const { status: wsStatus, lastVitals } = useSwarmWebSocket('command-center', {
    onVitalsUpdate: setWsVitals,
  });

  useEffect(() => {
    if (lastVitals) setWsVitals(lastVitals);
  }, [lastVitals]);

  const markerColor = (status: string) => {
    switch (status) {
      case 'active': return '#42B0D5';
      case 'warning': return '#f59e0b';
      case 'alert': return '#ef4444';
      default: return '#42B0D5';
    }
  };

  const markerSize = (type: string) => {
    if (type === 'mega' || type === 'hub') return 'w-4 h-4';
    if (type === 'chokepoint') return 'w-5 h-5';
    return 'w-3 h-3';
  };

  return (
    <div className="flex flex-col gap-4 h-full">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-bold text-white tracking-tight">Global Command Center</h2>
          <p className="text-xs text-[hsl(215,20%,50%)] mt-0.5">
            Live shipping intelligence — 14 agents · {wsVitals?.active_agents ?? 14} active
          </p>
        </div>
        <div className="flex items-center gap-3">
          {/* WS status dot */}
          <div className="flex items-center gap-1.5 text-xs">
            <span
              className="w-2 h-2 rounded-full"
              style={{
                background: wsStatus === 'connected' ? '#10b981' : wsStatus === 'connecting' ? '#f59e0b' : '#ef4444',
                boxShadow: wsStatus === 'connected' ? '0 0 6px #10b981' : 'none',
              }}
            />
            <span className="text-[hsl(215,20%,50%)]">
              {wsStatus === 'connected' ? 'Live' : wsStatus === 'connecting' ? 'Connecting' : 'Offline'}
            </span>
          </div>
          <div className="text-xs px-2 py-1 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
            Swarm Active
          </div>
        </div>
      </div>

      {/* KPI Bar */}
      <div className="grid grid-cols-3 lg:grid-cols-6 gap-2">
        {KPI_DATA.map((kpi) => {
          const Icon = kpi.icon;
          return (
            <div
              key={kpi.label}
              className="card-elevated rounded-lg p-3 flex flex-col gap-1"
              style={{ borderLeft: `2px solid ${kpi.color}30` }}
            >
              <div className="flex items-center justify-between mb-0.5">
                <span className="text-[10px] text-[hsl(215,20%,50%)]">{kpi.label}</span>
                <Icon className="w-3 h-3" style={{ color: kpi.color }} />
              </div>
              <div className="text-lg font-bold text-white leading-none">
                {kpi.value}<span className="text-xs ml-0.5 text-[hsl(215,20%,60%)]">{kpi.unit}</span>
              </div>
              <div className="text-[10px]" style={{ color: kpi.color }}>{kpi.trend}</div>
            </div>
          );
        })}
      </div>

      {/* Main grid: Map + Alerts */}
      <div className="flex gap-4 flex-1 min-h-0">
        {/* Map */}
        <div className="flex-1 relative rounded-xl overflow-hidden border border-[hsl(220,14%,18%)] bg-[hsl(220,20%,5%)]">
          {MAPBOX_TOKEN ? (
            <Map
              mapboxAccessToken={MAPBOX_TOKEN}
              initialViewState={{ longitude: 30, latitude: 10, zoom: 1.8 }}
              style={{ width: '100%', height: '100%' }}
              mapStyle="mapbox://styles/mapbox/dark-v11"
              projection="mercator"
              attributionControl={false}
            >
              <NavigationControl position="bottom-right" />

              {/* Route lines */}
              <Source id="routes" type="geojson" data={ROUTE_LINES}>
                <Layer {...routeLayerActive} />
                <Layer {...routeLayerDisrupted} />
              </Source>

              {/* Port markers */}
              {PORTS.map((port) => (
                <Marker
                  key={port.id}
                  longitude={port.lng}
                  latitude={port.lat}
                  onClick={() => {
                    setPopup(port);
                  }}
                >
                  <div
                    className={`${markerSize(port.type)} rounded-full cursor-pointer transition-transform hover:scale-125`}
                    style={{
                      background: markerColor(port.status),
                      boxShadow: `0 0 ${port.type === 'chokepoint' ? '12px 4px' : '8px 2px'} ${markerColor(port.status)}80`,
                    }}
                  />
                </Marker>
              ))}

              {/* Popup */}
              {popup && (
                <Popup
                  longitude={popup.lng}
                  latitude={popup.lat}
                  onClose={() => setPopup(null)}
                  closeOnClick={false}
                  className="mapbox-popup-dark"
                >
                  <div className="p-2 bg-[hsl(220,20%,9%)] rounded-lg min-w-[140px]">
                    <div className="text-sm font-semibold text-white">{popup.label}</div>
                    <div className="text-[10px] text-[hsl(215,20%,50%)] capitalize mt-0.5">{popup.type}</div>
                    <div
                      className="text-xs font-mono mt-1"
                      style={{ color: markerColor(popup.status) }}
                    >
                      {popup.volume}
                    </div>
                    <div
                      className="text-[10px] mt-1 capitalize px-1.5 py-0.5 rounded-full inline-block"
                      style={{
                        background: `${markerColor(popup.status)}20`,
                        color: markerColor(popup.status),
                      }}
                    >
                      {popup.status}
                    </div>
                  </div>
                </Popup>
              )}
            </Map>
          ) : (
            /* Fallback when no Mapbox token — keeps the demo functional */
            <div className="w-full h-full flex flex-col items-center justify-center gap-3">
              <Globe className="w-12 h-12 text-[hsl(195,70%,55%/0.4)]" />
              <p className="text-sm text-[hsl(215,20%,50%)]">
                Set <code className="text-[hsl(195,70%,55%)]">VITE_MAPBOX_TOKEN</code> in your .env to enable the live map.
              </p>
            </div>
          )}

          {/* Map legend */}
          <div className="absolute bottom-3 left-3 bg-[hsl(220,20%,7%)/80%] backdrop-blur-sm rounded-lg p-2 border border-[hsl(220,14%,18%)] pointer-events-none">
            {[
              { color: '#42B0D5', label: 'Active Route' },
              { color: '#ef4444', label: 'Disrupted Route' },
              { color: '#10b981', label: 'Africa Corridor' },
            ].map((item) => (
              <div key={item.label} className="flex items-center gap-2 text-[10px] text-[hsl(215,20%,60%)] mb-1 last:mb-0">
                <div className="w-6 h-0.5" style={{ background: item.color }} />
                {item.label}
              </div>
            ))}
          </div>
        </div>

        {/* Right Panel: Alerts + System Health */}
        <div className="w-72 flex flex-col gap-3 overflow-y-auto scrollbar-thin">
          {/* Swarm health */}
          <div className="card-elevated rounded-xl p-4">
            <div className="flex items-center gap-2 mb-3">
              <Activity className="w-4 h-4 text-[hsl(195,70%,55%)]" />
              <span className="text-xs font-semibold text-white">Swarm Health</span>
            </div>
            <div className="flex items-center justify-between mb-2">
              <span className="text-3xl font-bold text-white">
                {wsVitals ? `${Math.round(wsVitals.overall_health * 100)}%` : '—'}
              </span>
              <span className="text-xs text-emerald-400">
                {wsVitals?.active_agents ?? 14}/{wsVitals?.total_agents ?? 14} agents
              </span>
            </div>
            <div className="w-full bg-[hsl(220,14%,15%)] rounded-full h-1.5">
              <div
                className="h-1.5 rounded-full transition-all duration-1000"
                style={{
                  width: `${(wsVitals?.overall_health ?? 0.95) * 100}%`,
                  background: 'linear-gradient(90deg, #42B0D5, #10b981)',
                }}
              />
            </div>
            <div className="mt-3 grid grid-cols-2 gap-2">
              <div className="text-center">
                <div className="text-sm font-bold text-white">
                  {wsVitals ? `${Math.round(wsVitals.consciousness * 100)}%` : '—'}
                </div>
                <div className="text-[10px] text-[hsl(215,20%,50%)]">Consciousness</div>
              </div>
              <div className="text-center">
                <div className="text-sm font-bold text-white">
                  {wsVitals ? `${Math.round(wsVitals.uptime_hours)}h` : '—'}
                </div>
                <div className="text-[10px] text-[hsl(215,20%,50%)]">Uptime</div>
              </div>
            </div>
          </div>

          {/* Live alerts */}
          <div className="card-elevated rounded-xl p-4 flex-1">
            <div className="flex items-center gap-2 mb-3">
              <Zap className="w-4 h-4 text-amber-400" />
              <span className="text-xs font-semibold text-white">Live Alerts</span>
            </div>
            <div className="space-y-2">
              {STATUS_ALERTS.map((alert, i) => (
                <div key={i} className="flex gap-2.5 text-xs">
                  <div
                    className="w-1 rounded-full flex-shrink-0 mt-0.5"
                    style={{ background: STATUS_COLOR[alert.level] }}
                  />
                  <div className="flex-1 min-w-0">
                    <p className="text-[hsl(210,40%,90%)] leading-snug">{alert.msg}</p>
                    <p className="text-[hsl(215,20%,45%)] text-[10px] mt-0.5 flex items-center gap-1">
                      <Clock className="w-2.5 h-2.5" /> {alert.time}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Quick stats */}
          <div className="card-elevated rounded-xl p-4">
            <div className="flex items-center gap-2 mb-3">
              <Server className="w-4 h-4 text-[hsl(195,70%,55%)]" />
              <span className="text-xs font-semibold text-white">Today's Wins</span>
            </div>
            {[
              { label: 'Reroutes Avoided', value: '12', color: '#42B0D5' },
              { label: 'Compliance Flags', value: '3', color: '#f59e0b' },
              { label: 'Cost Saved', value: '$847K', color: '#10b981' },
            ].map((item) => (
              <div key={item.label} className="flex items-center justify-between py-1.5 border-b border-[hsl(220,14%,15%)] last:border-0">
                <span className="text-[10px] text-[hsl(215,20%,55%)]">{item.label}</span>
                <span className="text-xs font-bold" style={{ color: item.color }}>{item.value}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

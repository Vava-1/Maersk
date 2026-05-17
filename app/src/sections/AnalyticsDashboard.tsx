import { useState } from 'react';
import {
  LineChart, Line, AreaChart, Area, BarChart, Bar,
  XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell
} from 'recharts';
import {
  TrendingUp, DollarSign, Shield, Zap,
  Leaf, BarChart3, Activity, Clock, Award
} from 'lucide-react';

const TREND_DATA = Array.from({ length: 30 }, (_, i) => ({
  date: `Day ${i + 1}`,
  cost_savings: Math.round(15000 + Math.random() * 35000),
  risk_events: Math.round(1 + Math.random() * 7),
  tasks: Math.round(50 + Math.random() * 150),
  co2: Math.round(5000 + Math.random() * 20000),
  health: +(0.85 + Math.random() * 0.14).toFixed(3),
}));

const COST_SAVING_DATA = TREND_DATA.map(d => ({
  date: d.date,
  route: Math.round(d.cost_savings * 0.45),
  inventory: Math.round(d.cost_savings * 0.35),
  incident: Math.round(d.cost_savings * 0.20),
}));

const AGENT_PERF_DATA = [
  { name: 'Orchestrator', tasks: 245, success: 99.2, color: '#42B0D5' },
  { name: 'Guardian', tasks: 1890, success: 99.8, color: '#10b981' },
  { name: 'Risk Monitor', tasks: 456, success: 97.5, color: '#f59e0b' },
  { name: 'Route Opt.', tasks: 312, success: 96.8, color: '#8b5cf6' },
  { name: 'Compliance', tasks: 534, success: 98.5, color: '#0ea5e9' },
  { name: 'ESG', tasks: 178, success: 95.2, color: '#22c55e' },
  { name: 'Analytics', tasks: 89, success: 99.0, color: '#06b6d4' },
  { name: 'Security', tasks: 234, success: 99.9, color: '#64748b' },
];

const ROI_PIE_DATA = [
  { name: 'Route Optimization', value: 45, color: '#42B0D5' },
  { name: 'Risk Mitigation', value: 25, color: '#f59e0b' },
  { name: 'Inventory Opt.', value: 15, color: '#8b5cf6' },
  { name: 'Compliance Prev.', value: 10, color: '#10b981' },
  { name: 'Incident Avoid.', value: 5, color: '#ef4444' },
];

function CustomTooltip({ active, payload, label }: any) {
  if (!active || !payload?.length) return null;
  return (
    <div className="bg-[hsl(220,14%,12%)] border border-[hsl(220,14%,20%)] rounded-lg p-3 shadow-xl">
      <p className="text-[10px] text-[hsl(215,20%,50%)] mb-1">{label}</p>
      {payload.map((entry: any, i: number) => (
        <p key={i} className="text-xs" style={{ color: entry.color }}>
          {entry.name}: {entry.value?.toLocaleString()}
        </p>
      ))}
    </div>
  );
}

const KPI_CARDS = [
  { label: 'Total Savings (MTD)', value: '$2.4M', change: '+22%', positive: true, icon: DollarSign, color: 'text-[#42B0D5]' },
  { label: 'ROI Ratio', value: '4.2x', change: '+0.8x', positive: true, icon: TrendingUp, color: 'text-emerald-400' },
  { label: 'Risk Events Prevented', value: '47', change: '+12', positive: true, icon: Shield, color: 'text-amber-400' },
  { label: 'CO2 Avoided (MTD)', value: '342t', change: '+18%', positive: true, icon: Leaf, color: 'text-emerald-400' },
  { label: 'Tasks Automated', value: '8,432', change: '+34%', positive: true, icon: Zap, color: 'text-purple-400' },
  { label: 'Avg Decision Time', value: '1.2s', change: '-0.4s', positive: true, icon: Clock, color: 'text-sky-400' },
];

export function AnalyticsDashboard() {
  const [period, setPeriod] = useState('30d');

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-bold text-white">Analytics & ROI Dashboard</h2>
          <p className="text-xs text-[hsl(215,20%,50%)] mt-0.5">Performance metrics and business impact quantification</p>
        </div>
        <div className="flex gap-2">
          {['24h', '7d', '30d', '90d'].map(p => (
            <button
              key={p}
              onClick={() => setPeriod(p)}
              className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
                period === p ? 'bg-[hsl(195,70%,55%)] text-[hsl(220,20%,6%)]' :
                  'bg-[hsl(220,14%,12%)] text-[hsl(215,20%,55%)] hover:text-white border border-[hsl(220,14%,20%)]'
              }`}
            >
              {p}
            </button>
          ))}
        </div>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-2 lg:grid-cols-3 xl:grid-cols-6 gap-3">
        {KPI_CARDS.map((kpi, i) => {
          const Icon = kpi.icon;
          return (
            <div key={i} className="card-elevated rounded-lg p-3">
              <div className="flex items-center gap-2 mb-2">
                <Icon className={`w-4 h-4 ${kpi.color}`} />
                <span className="text-[10px] text-[hsl(215,20%,50%)] truncate">{kpi.label}</span>
              </div>
              <div className="text-lg font-bold text-white">{kpi.value}</div>
              <div className={`text-[10px] mt-1 ${kpi.positive ? 'text-emerald-400' : 'text-red-400'}`}>
                {kpi.change}
              </div>
            </div>
          );
        })}
      </div>

      {/* Charts Row 1 */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {/* Cost Savings Trend */}
        <div className="card-elevated rounded-lg p-4">
          <div className="flex items-center gap-2 mb-4">
            <DollarSign className="w-4 h-4 text-[#42B0D5]" />
            <h3 className="text-sm font-semibold text-white">Cost Savings Breakdown</h3>
          </div>
          <ResponsiveContainer width="100%" height={220}>
            <AreaChart data={COST_SAVING_DATA}>
              <CartesianGrid strokeDasharray="3 3" stroke="hsl(220,14%,18%)" />
              <XAxis dataKey="date" tick={{ fontSize: 9, fill: 'hsl(215,20%,50%)' }} interval={4} />
              <YAxis tick={{ fontSize: 9, fill: 'hsl(215,20%,50%)' }} tickFormatter={(v: number) => `$${(v/1000).toFixed(0)}k`} />
              <Tooltip content={<CustomTooltip />} />
              <Area type="monotone" dataKey="route" stackId="1" stroke="#42B0D5" fill="#42B0D5" fillOpacity={0.3} name="Route Opt" />
              <Area type="monotone" dataKey="inventory" stackId="1" stroke="#8b5cf6" fill="#8b5cf6" fillOpacity={0.3} name="Inventory" />
              <Area type="monotone" dataKey="incident" stackId="1" stroke="#f59e0b" fill="#f59e0b" fillOpacity={0.3} name="Incident Avoid" />
            </AreaChart>
          </ResponsiveContainer>
        </div>

        {/* System Health */}
        <div className="card-elevated rounded-lg p-4">
          <div className="flex items-center gap-2 mb-4">
            <Activity className="w-4 h-4 text-emerald-400" />
            <h3 className="text-sm font-semibold text-white">System Health Trend</h3>
          </div>
          <ResponsiveContainer width="100%" height={220}>
            <LineChart data={TREND_DATA}>
              <CartesianGrid strokeDasharray="3 3" stroke="hsl(220,14%,18%)" />
              <XAxis dataKey="date" tick={{ fontSize: 9, fill: 'hsl(215,20%,50%)' }} interval={4} />
              <YAxis domain={[0.7, 1]} tick={{ fontSize: 9, fill: 'hsl(215,20%,50%)' }} tickFormatter={(v: number) => `${(v*100).toFixed(0)}%`} />
              <Tooltip content={<CustomTooltip />} />
              <Line type="monotone" dataKey="health" stroke="#10b981" strokeWidth={2} dot={false} name="Health Score" />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Charts Row 2 */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        {/* Agent Performance */}
        <div className="lg:col-span-2 card-elevated rounded-lg p-4">
          <div className="flex items-center gap-2 mb-4">
            <BarChart3 className="w-4 h-4 text-purple-400" />
            <h3 className="text-sm font-semibold text-white">Agent Performance</h3>
          </div>
          <ResponsiveContainer width="100%" height={220}>
            <BarChart data={AGENT_PERF_DATA} layout="vertical">
              <CartesianGrid strokeDasharray="3 3" stroke="hsl(220,14%,18%)" />
              <XAxis type="number" tick={{ fontSize: 9, fill: 'hsl(215,20%,50%)' }} />
              <YAxis dataKey="name" type="category" tick={{ fontSize: 9, fill: 'hsl(215,20%,50%)' }} width={80} />
              <Tooltip content={<CustomTooltip />} />
              <Bar dataKey="tasks" fill="#42B0D5" radius={[0, 4, 4, 0]} name="Tasks" />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* ROI Distribution */}
        <div className="card-elevated rounded-lg p-4">
          <div className="flex items-center gap-2 mb-4">
            <Award className="w-4 h-4 text-amber-400" />
            <h3 className="text-sm font-semibold text-white">ROI Distribution</h3>
          </div>
          <ResponsiveContainer width="100%" height={200}>
            <PieChart>
              <Pie
                data={ROI_PIE_DATA}
                cx="50%"
                cy="50%"
                innerRadius={50}
                outerRadius={80}
                paddingAngle={3}
                dataKey="value"
              >
                {ROI_PIE_DATA.map((entry, i) => (
                  <Cell key={i} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip content={<CustomTooltip />} />
            </PieChart>
          </ResponsiveContainer>
          <div className="space-y-1.5 mt-2">
            {ROI_PIE_DATA.map((item, i) => (
              <div key={i} className="flex items-center justify-between text-[10px]">
                <div className="flex items-center gap-1.5">
                  <div className="w-2 h-2 rounded-full" style={{ background: item.color }} />
                  <span className="text-[hsl(215,20%,65%)]">{item.name}</span>
                </div>
                <span className="text-white font-medium">{item.value}%</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

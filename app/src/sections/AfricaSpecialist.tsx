import { useState } from 'react';
import {
  TrendingUp, AlertTriangle, Route,
  Info, ChevronRight, Anchor
} from 'lucide-react';

const CORRIDORS = [
  {
    id: 'northern_corridor',
    name: 'Northern Corridor',
    route: 'Mombasa -> Nairobi -> Kampala -> Kigali -> Goma',
    distance: '2,200 km',
    time: '7 days',
    cost: '$2,800/TEU',
    quality: 0.55,
    status: 'active',
    challenges: ['Weightbridges and police checkpoints', 'Mombasa port congestion', 'Road condition variability', 'Multiple customs clearance points'],
    improvements: ['SGR extension to Malaba', 'One-stop border modernization', 'EAC Single Customs Territory', 'Mombasa port automation'],
  },
  {
    id: 'central_corridor',
    name: 'Central Corridor',
    route: 'Dar es Salaam -> Dodoma -> Kigali/Bujumbura',
    distance: '1,800 km',
    time: '6 days',
    cost: '$2,600/TEU',
    quality: 0.50,
    status: 'warning',
    challenges: ['Port capacity constraints', 'Central Tanzania road quality', 'Railway gauge mismatch', 'Burundi instability spillover'],
    improvements: ['Dar port expansion', 'Railway rehabilitation', 'Rwanda logistics hub', 'Electronic cargo tracking'],
  },
  {
    id: 'west_africa_corridor',
    name: 'West Africa Coastal Corridor',
    route: 'Lagos -> Accra -> Abidjan -> Lome',
    distance: '1,200 km',
    time: '3 days',
    cost: '$2,200/TEU',
    quality: 0.58,
    status: 'active',
    challenges: ['Lagos port congestion', 'Multiple border crossings', 'Road quality variance', 'Security concerns'],
    improvements: ['Lekki Deep Sea Port', 'ECOWAS Trade Scheme', 'Abidjan-Lagos highway upgrade', 'Digital customs platforms'],
  },
  {
    id: 'cape_to_cairo',
    name: 'Cape to Cairo Vision',
    route: 'Cape Town -> Gaborone -> Lusaka -> Nairobi',
    distance: '5,200 km',
    time: '14 days',
    cost: '$4,500/TEU',
    quality: 0.45,
    status: 'degraded',
    challenges: ['Multi-country complexity', 'Gauge differences', 'Remote stretches', 'Political instability'],
    improvements: ['Trans-African Highway', 'Tripartite FTA', 'Regional railway links', 'Corridor development authorities'],
  },
];

const PORTS = [
  { name: 'Port of Mombasa', country: 'Kenya', teu: '1.4M', dwell: '6.5 days', congestion: 'High', efficiency: 0.55 },
  { name: 'Port of Dar es Salaam', country: 'Tanzania', teu: '950K', dwell: '8.2 days', congestion: 'Medium-High', efficiency: 0.48 },
  { name: 'Lagos Port Complex', country: 'Nigeria', teu: '1.2M', dwell: '21 days', congestion: 'Critical', efficiency: 0.35 },
  { name: 'Port of Durban', country: 'South Africa', teu: '3.1M', dwell: '4.5 days', congestion: 'Medium', efficiency: 0.72 },
  { name: 'Port of Luanda', country: 'Angola', teu: '850K', dwell: '14 days', congestion: 'High', efficiency: 0.40 },
];

export function AfricaSpecialist() {
  const [selectedCorridor, setSelectedCorridor] = useState<string | null>(null);

  const getStatusColor = (status: string) => {
    const colors: Record<string, string> = {
      active: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20',
      warning: 'bg-amber-500/10 text-amber-400 border-amber-500/20',
      degraded: 'bg-red-500/10 text-red-400 border-red-500/20',
    };
    return colors[status] || colors.active;
  };

  return (
    <div className="space-y-4">
      <div>
        <h2 className="text-xl font-bold text-white">Africa / Emerging Markets Specialist</h2>
        <p className="text-xs text-[hsl(215,20%,50%)] mt-0.5">Deep expertise on African logistics corridors and infrastructure</p>
      </div>

      {/* Corridors */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {CORRIDORS.map(c => (
          <div
            key={c.id}
            className="card-elevated rounded-lg p-4 cursor-pointer hover:border-[hsl(195,70%,55%/0.3)] transition-all"
            onClick={() => setSelectedCorridor(selectedCorridor === c.id ? null : c.id)}
          >
            <div className="flex items-start justify-between mb-3">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-amber-600 to-yellow-500 flex items-center justify-center">
                  <Route className="w-5 h-5 text-white" />
                </div>
                <div>
                  <h3 className="text-sm font-semibold text-white">{c.name}</h3>
                  <p className="text-[10px] text-[hsl(215,20%,55%)]">{c.route}</p>
                </div>
              </div>
              <span className={`text-[10px] px-2 py-0.5 rounded-full border ${getStatusColor(c.status)}`}>
                {c.status.toUpperCase()}
              </span>
            </div>

            <div className="grid grid-cols-4 gap-2 mb-3">
              <div className="bg-[hsl(220,14%,12%)] rounded-md p-2 text-center">
                <div className="text-[10px] text-[hsl(215,20%,50%)]">Distance</div>
                <div className="text-xs font-semibold text-white">{c.distance}</div>
              </div>
              <div className="bg-[hsl(220,14%,12%)] rounded-md p-2 text-center">
                <div className="text-[10px] text-[hsl(215,20%,50%)]">Transit</div>
                <div className="text-xs font-semibold text-white">{c.time}</div>
              </div>
              <div className="bg-[hsl(220,14%,12%)] rounded-md p-2 text-center">
                <div className="text-[10px] text-[hsl(215,20%,50%)]">Cost</div>
                <div className="text-xs font-semibold text-white">{c.cost}</div>
              </div>
              <div className="bg-[hsl(220,14%,12%)] rounded-md p-2 text-center">
                <div className="text-[10px] text-[hsl(215,20%,50%)]">Quality</div>
                <div className="text-xs font-semibold text-white">{(c.quality * 100).toFixed(0)}%</div>
              </div>
            </div>

            {/* Infrastructure quality bar */}
            <div className="mb-3">
              <div className="flex items-center justify-between mb-1">
                <span className="text-[10px] text-[hsl(215,20%,50%)]">Infrastructure Quality</span>
                <span className="text-[10px] text-white font-mono">{(c.quality * 100).toFixed(0)}%</span>
              </div>
              <div className="h-1.5 bg-[hsl(220,14%,12%)] rounded-full overflow-hidden">
                <div
                  className="h-full rounded-full transition-all duration-500"
                  style={{
                    width: `${c.quality * 100}%`,
                    background: c.quality > 0.5 ? 'linear-gradient(90deg, #f59e0b, #eab308)' : 'linear-gradient(90deg, #ef4444, #f59e0b)',
                  }}
                />
              </div>
            </div>

            {selectedCorridor === c.id && (
              <div className="mt-3 pt-3 border-t border-[hsl(220,14%,18%)] space-y-3">
                <div>
                  <div className="text-[10px] font-semibold text-amber-400 mb-1.5 flex items-center gap-1">
                    <AlertTriangle className="w-3 h-3" /> Key Challenges
                  </div>
                  <div className="space-y-1">
                    {c.challenges.map((ch, i) => (
                      <div key={i} className="flex items-start gap-1.5 text-[10px] text-[hsl(215,20%,65%)]">
                        <ChevronRight className="w-2.5 h-2.5 text-red-400 flex-shrink-0 mt-0.5" />
                        {ch}
                      </div>
                    ))}
                  </div>
                </div>
                <div>
                  <div className="text-[10px] font-semibold text-emerald-400 mb-1.5 flex items-center gap-1">
                    <TrendingUp className="w-3 h-3" /> Planned Improvements
                  </div>
                  <div className="space-y-1">
                    {c.improvements.map((imp, i) => (
                      <div key={i} className="flex items-start gap-1.5 text-[10px] text-[hsl(215,20%,65%)]">
                        <ChevronRight className="w-2.5 h-2.5 text-emerald-400 flex-shrink-0 mt-0.5" />
                        {imp}
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            )}

            <div className="text-[10px] text-[hsl(195,70%,65%)] mt-2 flex items-center gap-1">
              <Info className="w-3 h-3" />
              {selectedCorridor === c.id ? 'Click to collapse' : 'Click to expand details'}
            </div>
          </div>
        ))}
      </div>

      {/* Port Table */}
      <div className="card-elevated rounded-lg overflow-hidden">
        <div className="flex items-center gap-2 p-4 border-b border-[hsl(220,14%,18%)]">
          <Anchor className="w-4 h-4 text-[hsl(195,70%,55%)]" />
          <h3 className="text-sm font-semibold text-white">Major African Ports</h3>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-[hsl(220,14%,18%)]">
                <th className="text-left px-4 py-3 text-[10px] font-semibold text-[hsl(215,20%,50%)] uppercase">Port</th>
                <th className="text-left px-4 py-3 text-[10px] font-semibold text-[hsl(215,20%,50%)] uppercase">Country</th>
                <th className="text-left px-4 py-3 text-[10px] font-semibold text-[hsl(215,20%,50%)] uppercase">Annual TEU</th>
                <th className="text-left px-4 py-3 text-[10px] font-semibold text-[hsl(215,20%,50%)] uppercase">Dwell Time</th>
                <th className="text-left px-4 py-3 text-[10px] font-semibold text-[hsl(215,20%,50%)] uppercase">Congestion</th>
                <th className="text-left px-4 py-3 text-[10px] font-semibold text-[hsl(215,20%,50%)] uppercase">Efficiency</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[hsl(220,14%,15%)]">
              {PORTS.map((port, i) => (
                <tr key={i} className="hover:bg-[hsl(220,14%,10%)] transition-colors">
                  <td className="px-4 py-3 text-xs text-white font-medium">{port.name}</td>
                  <td className="px-4 py-3 text-[10px] text-[hsl(215,20%,65%)]">{port.country}</td>
                  <td className="px-4 py-3 text-xs text-white font-mono">{port.teu}</td>
                  <td className="px-4 py-3 text-xs text-white font-mono">{port.dwell}</td>
                  <td className="px-4 py-3">
                    <span className={`text-[10px] px-2 py-0.5 rounded ${
                      port.congestion === 'Critical' ? 'bg-red-500/10 text-red-400' :
                      port.congestion === 'High' ? 'bg-orange-500/10 text-orange-400' :
                      port.congestion === 'Medium-High' ? 'bg-amber-500/10 text-amber-400' :
                      'bg-emerald-500/10 text-emerald-400'
                    }`}>
                      {port.congestion}
                    </span>
                  </td>
                  <td className="px-4 py-3">
                    <div className="flex items-center gap-2">
                      <div className="w-16 h-1.5 bg-[hsl(220,14%,12%)] rounded-full overflow-hidden">
                        <div className="h-full rounded-full bg-gradient-to-r from-amber-500 to-emerald-500 transition-all" style={{ width: `${port.efficiency * 100}%` }} />
                      </div>
                      <span className="text-[10px] text-white font-mono">{(port.efficiency * 100).toFixed(0)}%</span>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

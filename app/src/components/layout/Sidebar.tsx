import { useState } from 'react';
import {
  Brain, Shield, Globe, Map, Scale, Leaf, Users,
  BarChart3, AlertTriangle, Eye, LineChart, Compass,
  Lock, Database, Activity, Command, ChevronLeft, ChevronRight,
  Zap, MessageSquare
} from 'lucide-react';

interface SidebarProps {
  currentView: string;
  onNavigate: (view: string) => void;
  isCollapsed: boolean;
  onToggleCollapse: () => void;
}

const iconMap: Record<string, React.ElementType> = {
  Brain, Shield, Globe, Map, Scale, Leaf, Users,
  BarChart3, AlertTriangle, Eye, LineChart, Compass,
  Lock, Database, Activity, Command, Zap, MessageSquare,
};

const NAV_ITEMS = [
  { id: 'command-center', label: 'Command Center', icon: 'Command', category: 'Core' },
  { id: 'agents', label: 'Agent Swarm', icon: 'Brain', category: 'Core' },
  { id: 'guardian', label: 'Guardian Health', icon: 'Shield', category: 'Core' },
  { id: 'chat', label: 'Swarm Chat', icon: 'MessageSquare', category: 'Core' },
  { id: 'risk', label: 'Risk Monitor', icon: 'Globe', category: 'Operations' },
  { id: 'routes', label: 'Route Optimizer', icon: 'Map', category: 'Operations' },
  { id: 'compliance', label: 'Compliance Tower', icon: 'Scale', category: 'Operations' },
  { id: 'analytics', label: 'Analytics & ROI', icon: 'LineChart', category: 'Intelligence' },
  { id: 'africa', label: 'Africa Specialist', icon: 'Compass', category: 'Intelligence' },
  { id: 'demos', label: 'Demo Scenarios', icon: 'Zap', category: 'Intelligence' },
];

export function Sidebar({ currentView, onNavigate, isCollapsed, onToggleCollapse }: SidebarProps) {
  const [hoveredItem, setHoveredItem] = useState<string | null>(null);

  const grouped = NAV_ITEMS.reduce<Record<string, typeof NAV_ITEMS>>((acc, item) => {
    if (!acc[item.category]) acc[item.category] = [];
    acc[item.category].push(item);
    return acc;
  }, {});

  return (
    <aside
      className={`fixed left-0 top-0 h-screen bg-[hsl(220,20%,7%)] border-r border-[hsl(220,14%,18%)] z-50 transition-all duration-300 flex flex-col ${
        isCollapsed ? 'w-[68px]' : 'w-[260px]'
      }`}
    >
      {/* Header */}
      <div className="flex items-center gap-3 px-4 py-5 border-b border-[hsl(220,14%,18%)]">
        <div className="w-9 h-9 rounded-lg bg-gradient-to-br from-[hsl(195,70%,55%)] to-[hsl(195,70%,40%)] flex items-center justify-center flex-shrink-0">
          <Brain className="w-5 h-5 text-white" />
        </div>
        {!isCollapsed && (
          <div className="overflow-hidden">
            <h1 className="text-sm font-bold text-white whitespace-nowrap">AfriSwarm</h1>
            <p className="text-[10px] text-[hsl(215,20%,55%)] whitespace-nowrap">Maersk Resilience</p>
          </div>
        )}
      </div>

      {/* Navigation */}
      <nav className="flex-1 overflow-y-auto py-3 scrollbar-thin">
        {Object.entries(grouped).map(([category, items]) => (
          <div key={category} className="mb-2">
            {!isCollapsed && (
              <div className="px-4 py-1.5">
                <span className="text-[10px] font-semibold uppercase tracking-wider text-[hsl(215,20%,45%)]">
                  {category}
                </span>
              </div>
            )}
            {items.map((item) => {
              const Icon = iconMap[item.icon] || Activity;
              const isActive = currentView === item.id;
              const isHovered = hoveredItem === item.id;

              return (
                <button
                  key={item.id}
                  onClick={() => onNavigate(item.id)}
                  onMouseEnter={() => setHoveredItem(item.id)}
                  onMouseLeave={() => setHoveredItem(null)}
                  className={`relative w-full flex items-center gap-3 px-4 py-2.5 text-sm transition-all duration-200 group ${
                    isActive
                      ? 'text-white'
                      : 'text-[hsl(215,20%,55%)] hover:text-white'
                  }`}
                >
                  {/* Active indicator */}
                  {isActive && (
                    <div className="absolute left-0 top-1/2 -translate-y-1/2 w-0.5 h-6 bg-[hsl(195,70%,55%)] rounded-r-full" />
                  )}

                  {/* Icon */}
                  <div className={`flex-shrink-0 transition-all duration-200 ${
                    isCollapsed ? 'mx-auto' : ''
                  }`}>
                    <Icon className={`w-[18px] h-[18px] transition-all duration-200 ${
                      isActive
                        ? 'text-[hsl(195,70%,55%)]'
                        : isHovered
                        ? 'text-white'
                        : 'text-[hsl(215,20%,45%)]'
                    }`} />
                  </div>

                  {/* Label */}
                  {!isCollapsed && (
                    <span className="truncate text-[13px] font-medium">{item.label}</span>
                  )}

                  {/* Active background */}
                  {isActive && (
                    <div className="absolute inset-0 bg-[hsl(195,70%,55%/0.08)] -z-10" />
                  )}

                  {/* Tooltip for collapsed */}
                  {isCollapsed && isHovered && (
                    <div className="absolute left-full ml-2 px-2.5 py-1.5 bg-[hsl(220,14%,15%)] border border-[hsl(220,14%,22%)] rounded-md text-xs text-white whitespace-nowrap z-50 shadow-xl">
                      {item.label}
                    </div>
                  )}
                </button>
              );
            })}
          </div>
        ))}
      </nav>

      {/* Footer */}
      <div className="border-t border-[hsl(220,14%,18%)] p-3">
        <div className={`flex items-center gap-2 px-2 py-2 rounded-lg bg-[hsl(220,14%,12%)] ${isCollapsed ? 'justify-center' : ''}`}>
          <div className="w-2 h-2 rounded-full bg-[hsl(142,76%,36%)] animate-pulse" />
          {!isCollapsed && (
            <span className="text-[11px] text-[hsl(215,20%,55%)]">
              Swarm Active · 14 Agents
            </span>
          )}
        </div>
        <button
          onClick={onToggleCollapse}
          className="mt-2 w-full flex items-center justify-center py-1.5 text-[hsl(215,20%,45%)] hover:text-white transition-colors"
        >
          {isCollapsed ? <ChevronRight className="w-4 h-4" /> : <ChevronLeft className="w-4 h-4" />}
        </button>
      </div>
    </aside>
  );
}

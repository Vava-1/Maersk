import { useState, useEffect } from 'react';
import { Sidebar } from '@/components/layout/Sidebar';
import { CommandCenter } from '@/sections/CommandCenter';
import { AgentSwarm } from '@/sections/AgentSwarm';
import { GuardianHealth } from '@/sections/GuardianHealth';
import { RiskMonitor } from '@/sections/RiskMonitor';
import { ComplianceTower } from '@/sections/ComplianceTower';
import { AnalyticsDashboard } from '@/sections/AnalyticsDashboard';
import { AfricaSpecialist } from '@/sections/AfricaSpecialist';
import { SwarmChat } from '@/sections/SwarmChat';
import { DemoScenarios } from '@/sections/DemoScenarios';

function RouteOptimizerFallback() {
  return (
    <div className="flex flex-col items-center justify-center h-96 card-elevated rounded-lg">
      <div className="w-16 h-16 rounded-xl bg-[hsl(195,70%,55%/0.1)] flex items-center justify-center mb-4">
        <span className="text-3xl">🗺️</span>
      </div>
      <h3 className="text-lg font-semibold text-white mb-2">Route & Logistics Optimizer</h3>
      <p className="text-sm text-[hsl(215,20%,55%)] max-w-md text-center">
        Use the Swarm Chat interface to request route optimization.
        Example: &ldquo;Find the best route from Shanghai to Mombasa with low emissions preference&rdquo;
      </p>
    </div>
  );
}

export default function App() {
  const [currentView, setCurrentView] = useState('command-center');
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [isMobile, setIsMobile] = useState(false);
  const [isTransitioning, setIsTransitioning] = useState(false);
  const [isInitializing, setIsInitializing] = useState(true);

  useEffect(() => {
    const check = () => setIsMobile(window.innerWidth < 1024);
    check();
    window.addEventListener('resize', check);
    
    // Simulate power-up sequence
    const timer = setTimeout(() => setIsInitializing(false), 1500);
    
    return () => {
      window.removeEventListener('resize', check);
      clearTimeout(timer);
    };
  }, []);

  const handleNavigate = (view: string) => {
    if (view === currentView) return;
    setIsTransitioning(true);
    setTimeout(() => {
      setCurrentView(view);
      setIsTransitioning(false);
      if (isMobile) setSidebarCollapsed(true);
    }, 300);
  };


  const renderView = () => {
    switch (currentView) {
      case 'command-center': return <CommandCenter />;
      case 'agents': return <AgentSwarm />;
      case 'guardian': return <GuardianHealth />;
      case 'chat': return <SwarmChat />;
      case 'risk': return <RiskMonitor />;
      case 'routes': return <RouteOptimizerFallback />;
      case 'compliance': return <ComplianceTower />;
      case 'analytics': return <AnalyticsDashboard />;
      case 'africa': return <AfricaSpecialist />;
      case 'demos': return <DemoScenarios />;
      default: return <CommandCenter />;
    }
  };

  if (isInitializing) {
    return (
      <div className="min-h-screen bg-[hsl(220,20%,6%)] flex items-center justify-center noise-bg">
        <div className="flex flex-col items-center gap-6 glass-power p-12 rounded-2xl animate-glow">
          <div className="w-24 h-24 rounded-full border-t-4 border-[hsl(195,70%,55%)] border-r-4 border-r-transparent animate-spin" />
          <h1 className="text-3xl font-bold text-gradient tracking-widest">AFRISWARM</h1>
          <p className="text-[hsl(215,20%,55%)] font-mono animate-pulse">Initializing Neural Core...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[hsl(220,20%,6%)] text-[hsl(210,40%,96%)] noise-bg">
      {/* Mobile overlay */}
      {isMobile && !sidebarCollapsed && (
        <div
          className="fixed inset-0 bg-black/50 z-40 lg:hidden"
          onClick={() => setSidebarCollapsed(true)}
        />
      )}

      {/* Sidebar */}
      <div className={`${isMobile ? 'fixed z-50' : 'fixed'} transition-transform duration-300 ${
        isMobile && sidebarCollapsed ? '-translate-x-full' : ''
      }`}>
        <Sidebar
          currentView={currentView}
          onNavigate={handleNavigate}
          isCollapsed={!isMobile && sidebarCollapsed}
          onToggleCollapse={() => setSidebarCollapsed(!sidebarCollapsed)}
        />
      </div>

      {/* Main Content */}
      <main
        className={`transition-all duration-300 ${
          isMobile ? 'ml-0' : sidebarCollapsed ? 'ml-[68px]' : 'ml-[260px]'
        }`}
      >
        {/* Mobile header */}
        {isMobile && (
          <div className="flex items-center gap-3 px-4 py-3 bg-[hsl(220,20%,7%)] border-b border-[hsl(220,14%,18%)]">
            <button
              onClick={() => setSidebarCollapsed(false)}
              className="p-2 rounded-lg bg-[hsl(220,14%,12%)] text-white"
            >
              <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
              </svg>
            </button>
            <span className="text-sm font-semibold text-white">AfriSwarm</span>
          </div>
        )}

        {/* Content */}
        <div className={`p-4 lg:p-6 max-w-[1920px] mx-auto transition-all duration-300 ${isTransitioning ? 'opacity-0 scale-[0.98]' : 'opacity-100 scale-100'}`}>
          {renderView()}
        </div>
      </main>
    </div>
  );
}

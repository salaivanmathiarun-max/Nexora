import React from 'react';
import { useApp } from '../../context/AppContext';
import { 
  Compass, 
  Camera, 
  Building2, 
  Languages, 
  BookHeart, 
  BarChart3, 
  Sliders, 
  User, 
  Accessibility, 
  Sparkles 
} from 'lucide-react';

const Navbar = () => {
  const { 
    activeTab, 
    setActiveTab, 
    profile, 
    setIsProfileOpen, 
    setIsDemoDrawerOpen 
  } = useApp();

  const navItems = [
    { id: 'itinerary', label: 'Itinerary & XAI', icon: Compass },
    { id: 'landmark', label: 'Landmark Vision', icon: Camera },
    { id: 'services', label: 'Travel Services', icon: Building2 },
    { id: 'translate', label: 'Voice & Translate', icon: Languages },
    { id: 'memory', label: 'Memory Book', icon: BookHeart },
    { id: 'benchmarks', label: 'Research Benchmarks', icon: BarChart3 },
  ];

  const hasAccessibility = profile?.accessibility_needs && profile.accessibility_needs.length > 0;

  return (
    <header className="sticky top-0 z-40 w-full glass-panel border-b border-slate-800/80 bg-slate-950/80 backdrop-blur-md">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          
          {/* Logo & Brand */}
          <div className="flex items-center gap-3 cursor-pointer" onClick={() => setActiveTab('itinerary')}>
            <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-teal-500 to-cyan-400 flex items-center justify-center shadow-lg shadow-teal-500/20">
              <Sparkles className="w-5 h-5 text-slate-950 stroke-[2.5]" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="font-extrabold text-xl tracking-tight text-white font-['Outfit']">NEXORA</span>
                <span className="text-[10px] font-semibold tracking-wider uppercase px-2 py-0.5 rounded-full bg-teal-500/10 text-teal-400 border border-teal-500/20">
                  Research AI
                </span>
              </div>
              <p className="text-[11px] text-slate-400 hidden sm:block">Multimodal & Explainable Tourism Framework</p>
            </div>
          </div>

          {/* Navigation Tabs */}
          <nav className="hidden md:flex items-center gap-1 bg-slate-900/60 p-1 rounded-xl border border-slate-800/60">
            {navItems.map((item) => {
              const Icon = item.icon;
              const isActive = activeTab === item.id;
              return (
                <button
                  key={item.id}
                  onClick={() => setActiveTab(item.id)}
                  className={`flex items-center gap-2 px-3 py-1.5 rounded-lg text-xs font-medium transition-all duration-200 ${
                    isActive
                      ? 'bg-teal-500/15 text-teal-300 border border-teal-500/30 shadow-sm'
                      : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/40'
                  }`}
                >
                  <Icon className={`w-3.5 h-3.5 ${isActive ? 'text-teal-400' : 'text-slate-400'}`} />
                  <span>{item.label}</span>
                </button>
              );
            })}
          </nav>

          {/* Actions & Profile */}
          <div className="flex items-center gap-2">
            
            {/* Research Demo Simulator Trigger */}
            <button
              onClick={() => setIsDemoDrawerOpen(true)}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium bg-amber-500/10 text-amber-300 border border-amber-500/30 hover:bg-amber-500/20 transition-colors shadow-sm"
              title="Open Research Simulator to trigger rain or crowd spikes"
            >
              <Sliders className="w-3.5 h-3.5 text-amber-400" />
              <span className="hidden sm:inline">Disruption Simulator</span>
            </button>

            {/* Profile & Accessibility Button */}
            <button
              onClick={() => setIsProfileOpen(true)}
              className="flex items-center gap-2 px-3 py-1.5 rounded-lg text-xs font-medium bg-slate-900 border border-slate-800 hover:border-slate-700 text-slate-200 transition-all hover:bg-slate-800/80"
            >
              <User className="w-3.5 h-3.5 text-teal-400" />
              <span className="hidden sm:inline">{profile?.name || 'Traveler'}</span>
              {hasAccessibility && (
                <span className="flex items-center gap-0.5 px-1.5 py-0.5 rounded-full text-[10px] bg-indigo-500/20 text-indigo-300 border border-indigo-500/30">
                  <Accessibility className="w-2.5 h-2.5" />
                  <span>Access</span>
                </span>
              )}
            </button>

          </div>

        </div>

        {/* Mobile Tab Row */}
        <div className="flex md:hidden overflow-x-auto py-2 gap-1 border-t border-slate-900 scrollbar-none">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = activeTab === item.id;
            return (
              <button
                key={item.id}
                onClick={() => setActiveTab(item.id)}
                className={`flex items-center gap-1.5 px-2.5 py-1 rounded-md text-[11px] font-medium whitespace-nowrap ${
                  isActive
                    ? 'bg-teal-500/20 text-teal-300 border border-teal-500/30'
                    : 'text-slate-400 hover:text-slate-200'
                }`}
              >
                <Icon className="w-3 h-3" />
                <span>{item.label}</span>
              </button>
            );
          })}
        </div>

      </div>
    </header>
  );
};

export default Navbar;

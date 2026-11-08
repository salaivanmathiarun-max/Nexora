import React from 'react';
import { useApp } from '../../context/AppContext';
import api from '../../services/api';
import { 
  X, 
  CloudRain, 
  Users, 
  Car, 
  RotateCcw, 
  Zap, 
  Sparkles, 
  Info 
} from 'lucide-react';

const DemoControlDrawer = () => {
  const { 
    isDemoDrawerOpen, 
    setIsDemoDrawerOpen, 
    activeTrip, 
    setActiveTrip, 
    loadContext, 
    setActiveAdaptation, 
    showToast 
  } = useApp();

  if (!isDemoDrawerOpen) return null;

  const handleSimulateRain = async () => {
    try {
      await api.simulateContext({ weather_condition: 'Rainy' });
      await loadContext('Samarkand');
      showToast('🌧️ Injected sudden heavy rain into context vector.', 'info');

      if (activeTrip) {
        const adaptation = await api.simulateDisruption(activeTrip.id, 'rain_storm');
        setActiveAdaptation(adaptation);
        showToast('Dynamic adaptation proposal generated! Check the adaptation banner.', 'warning');
      }
    } catch (err) {
      console.error(err);
      showToast('Simulation failed', 'error');
    }
  };

  const handleSimulateCrowd = async () => {
    try {
      await api.simulateContext({ crowd_density: 'Peak' });
      await loadContext('Samarkand');
      showToast('👥 Injected peak crowd congestion into context vector.', 'info');

      if (activeTrip) {
        const adaptation = await api.simulateDisruption(activeTrip.id, 'extreme_crowd');
        setActiveAdaptation(adaptation);
        showToast('Dynamic adaptation proposal generated! Check the adaptation banner.', 'warning');
      }
    } catch (err) {
      console.error(err);
      showToast('Simulation failed', 'error');
    }
  };

  const handleSimulateTraffic = async () => {
    try {
      await api.simulateContext({ traffic_level: 'Heavy' });
      await loadContext('Samarkand');
      showToast('🚗 Injected heavy transit congestion into context vector.', 'info');
    } catch (err) {
      console.error(err);
    }
  };

  const handleReset = async () => {
    try {
      await api.resetContext();
      await loadContext('Samarkand');
      setActiveAdaptation(null);
      showToast('Reset to real-time live environmental data.', 'success');
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex justify-end bg-slate-950/70 backdrop-blur-sm animate-fade-in">
      <div className="w-full max-w-md bg-slate-900 border-l border-slate-800 p-6 shadow-2xl flex flex-col justify-between overflow-y-auto">
        
        <div>
          {/* Header */}
          <div className="flex items-center justify-between pb-4 border-b border-slate-800">
            <div className="flex items-center gap-2">
              <div className="p-2 rounded-lg bg-amber-500/10 text-amber-400 border border-amber-500/20">
                <Zap className="w-5 h-5" />
              </div>
              <div>
                <h3 className="text-base font-bold text-white font-['Outfit']">Research Disruption Simulator</h3>
                <p className="text-xs text-slate-400">Evaluate dynamic adaptation ($I^*$) under volatility</p>
              </div>
            </div>
            <button 
              onClick={() => setIsDemoDrawerOpen(false)}
              className="p-1 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800"
            >
              <X className="w-5 h-5" />
            </button>
          </div>

          {/* Research Note */}
          <div className="my-4 p-3 rounded-lg bg-slate-800/60 border border-slate-700/60 text-xs text-slate-300 flex items-start gap-2.5">
            <Info className="w-4 h-4 text-teal-400 shrink-0 mt-0.5" />
            <p>
              In the NEXORA paper, Section 3.6 introduces <strong>Dynamic Itinerary Adaptation</strong>:
              <span className="block font-mono text-[11px] text-teal-300 mt-1">
                I* = argmax [ U(I) - λ1*T(I) - λ2*C(I) - λ3*K(I) ]
              </span>
              Use these controls to inject contextual disruptions and test automated re-routing proposals.
            </p>
          </div>

          {/* Simulation Triggers */}
          <div className="space-y-3 mt-6">
            <h4 className="text-xs font-semibold uppercase tracking-wider text-slate-400">Contextual Injections</h4>
            
            {/* Rain Trigger */}
            <button
              onClick={handleSimulateRain}
              className="w-full flex items-center justify-between p-3.5 rounded-xl bg-slate-800/80 hover:bg-slate-800 border border-slate-700 hover:border-blue-500/40 text-left transition-all group"
            >
              <div className="flex items-center gap-3">
                <div className="p-2.5 rounded-lg bg-blue-500/15 text-blue-400 border border-blue-500/30 group-hover:scale-105 transition-transform">
                  <CloudRain className="w-5 h-5" />
                </div>
                <div>
                  <div className="text-sm font-semibold text-white">Simulate Sudden Heavy Rain</div>
                  <div className="text-xs text-slate-400">Swaps outdoor walks with indoor museums & madrasahs</div>
                </div>
              </div>
              <span className="text-xs font-semibold px-2 py-1 rounded bg-blue-500/20 text-blue-300 border border-blue-500/30">Trigger</span>
            </button>

            {/* Crowd Trigger */}
            <button
              onClick={handleSimulateCrowd}
              className="w-full flex items-center justify-between p-3.5 rounded-xl bg-slate-800/80 hover:bg-slate-800 border border-slate-700 hover:border-rose-500/40 text-left transition-all group"
            >
              <div className="flex items-center gap-3">
                <div className="p-2.5 rounded-lg bg-rose-500/15 text-rose-400 border border-rose-500/30 group-hover:scale-105 transition-transform">
                  <Users className="w-5 h-5" />
                </div>
                <div>
                  <div className="text-sm font-semibold text-white">Simulate Peak Crowd Surge</div>
                  <div className="text-xs text-slate-400">Replaces congested squares with tranquil artisan workshops</div>
                </div>
              </div>
              <span className="text-xs font-semibold px-2 py-1 rounded bg-rose-500/20 text-rose-300 border border-rose-500/30">Trigger</span>
            </button>

            {/* Traffic Trigger */}
            <button
              onClick={handleSimulateTraffic}
              className="w-full flex items-center justify-between p-3.5 rounded-xl bg-slate-800/80 hover:bg-slate-800 border border-slate-700 hover:border-amber-500/40 text-left transition-all group"
            >
              <div className="flex items-center gap-3">
                <div className="p-2.5 rounded-lg bg-amber-500/15 text-amber-400 border border-amber-500/30 group-hover:scale-105 transition-transform">
                  <Car className="w-5 h-5" />
                </div>
                <div>
                  <div className="text-sm font-semibold text-white">Simulate Heavy Transit Delays</div>
                  <div className="text-xs text-slate-400">Recalculates transit buffer time limits</div>
                </div>
              </div>
              <span className="text-xs font-semibold px-2 py-1 rounded bg-amber-500/20 text-amber-300 border border-amber-500/30">Trigger</span>
            </button>
          </div>
        </div>

        {/* Footer / Reset Button */}
        <div className="pt-6 border-t border-slate-800">
          <button
            onClick={handleReset}
            className="w-full flex items-center justify-center gap-2 py-2.5 px-4 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold transition-all border border-slate-700"
          >
            <RotateCcw className="w-4 h-4 text-teal-400" />
            <span>Reset to Live Real-World Context</span>
          </button>
        </div>

      </div>
    </div>
  );
};

export default DemoControlDrawer;

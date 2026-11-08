import React from 'react';
import { useApp } from '../../context/AppContext';
import { 
  X, 
  Sparkles, 
  BarChart, 
  Clock, 
  Accessibility, 
  Sun, 
  Users, 
  CheckCircle2, 
  Info 
} from 'lucide-react';

const XAIModal = () => {
  const { selectedStopForXAI, setSelectedStopForXAI } = useApp();

  if (!selectedStopForXAI) return null;

  const stop = selectedStopForXAI;
  const dest = stop.destination;
  const xai = stop.xai_explanation || {};
  const factors = xai.factors || {
    interest_alignment: 0.95,
    weather_suitability: 0.95,
    accessibility_fit: 1.0,
    crowd_convenience: 0.90,
    time_efficiency: 0.92
  };

  const factorBars = [
    { label: 'Tourist Interest Match', value: factors.interest_alignment, color: 'bg-teal-500', text: 'text-teal-400' },
    { label: 'Real-Time Weather Suitability', value: factors.weather_suitability, color: 'bg-cyan-500', text: 'text-cyan-400' },
    { label: 'Accessibility & Mobility Fit', value: factors.accessibility_fit, color: 'bg-indigo-500', text: 'text-indigo-400' },
    { label: 'Crowd & Queue Avoidance', value: factors.crowd_convenience, color: 'bg-emerald-500', text: 'text-emerald-400' },
    { label: 'Transit & Time Efficiency', value: factors.time_efficiency, color: 'bg-amber-500', text: 'text-amber-400' },
  ];

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-md animate-fade-in">
      <div className="w-full max-w-xl bg-slate-900 border border-slate-800 rounded-2xl shadow-2xl overflow-hidden flex flex-col max-h-[90vh]">
        
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-slate-800 bg-slate-900/90">
          <div className="flex items-center gap-2.5">
            <div className="p-2 rounded-xl bg-gradient-to-tr from-teal-500/20 to-cyan-500/20 text-teal-400 border border-teal-500/30">
              <Sparkles className="w-5 h-5" />
            </div>
            <div>
              <h3 className="text-base font-bold text-white font-['Outfit']">Explainable AI (XAI) Attribution</h3>
              <p className="text-xs text-slate-400">Mathematical formulation E(d) = Σ wi · Fi(d, u, C)</p>
            </div>
          </div>
          <button 
            onClick={() => setSelectedStopForXAI(null)}
            className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Modal Body */}
        <div className="p-6 overflow-y-auto space-y-5 text-xs text-slate-300">
          
          {/* Top Score Summary Banner */}
          <div className="flex items-center justify-between p-4 rounded-xl bg-gradient-to-r from-teal-500/10 via-cyan-500/10 to-indigo-500/10 border border-teal-500/20">
            <div>
              <div className="text-[11px] text-slate-400 font-medium">Evaluated Destination</div>
              <div className="text-base font-bold text-white font-['Outfit']">{dest.name}</div>
              <div className="text-[11px] text-teal-300 mt-0.5">
                Scheduled: {stop.planned_start_time} – {stop.planned_end_time} (+{stop.buffer_minutes}m buffer)
              </div>
            </div>
            <div className="text-right">
              <div className="text-[10px] uppercase font-bold text-slate-400">Composite Score R(d)</div>
              <div className="text-2xl font-extrabold text-teal-400 font-['Outfit']">
                {stop.xai_match_score}%
              </div>
              <span className="text-[10px] text-emerald-400 font-semibold flex items-center gap-1 justify-end">
                <CheckCircle2 className="w-3 h-3" /> Optimal Match
              </span>
            </div>
          </div>

          {/* Quantitative Factor Breakdown Bars */}
          <div className="p-4 rounded-xl bg-slate-800/50 border border-slate-700/60 space-y-3">
            <div className="flex items-center justify-between text-xs font-semibold text-slate-200">
              <span>Decision Factor Breakdown Fi(d, u, C)</span>
              <span className="text-slate-400 text-[10px]">Weight Contribution</span>
            </div>

            <div className="space-y-2.5">
              {factorBars.map((f, i) => (
                <div key={i} className="space-y-1">
                  <div className="flex justify-between text-[11px]">
                    <span className="text-slate-300">{f.label}</span>
                    <span className={`font-mono font-semibold ${f.text}`}>
                      {Math.round(f.value * 100)}%
                    </span>
                  </div>
                  <div className="w-full h-2 rounded-full bg-slate-900 overflow-hidden">
                    <div 
                      className={`h-full rounded-full ${f.color} transition-all duration-500`}
                      style={{ width: `${Math.round(f.value * 100)}%` }}
                    />
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Primary Reason */}
          <div className="p-3.5 rounded-xl bg-teal-500/10 border border-teal-500/20 text-teal-200">
            <span className="font-bold text-teal-400 uppercase tracking-wider text-[10px] block mb-1">
              Primary Recommendation Driver
            </span>
            <p className="text-xs leading-relaxed">
              {xai.primary_reason || "Selected for optimal alignment with your cultural interests and favorable morning sunlight."}
            </p>
          </div>

          {/* Timing Justification */}
          <div className="p-3.5 rounded-xl bg-slate-800/60 border border-slate-700/60 text-slate-300 space-y-1">
            <div className="flex items-center gap-1.5 font-bold text-slate-200 text-[11px]">
              <Clock className="w-3.5 h-3.5 text-cyan-400" />
              <span>Why This Specific Time Slot?</span>
            </div>
            <p className="text-xs text-slate-400 leading-relaxed">
              {xai.timing_justification || "Scheduled at this hour to minimize walking fatigue and avoid peak tourist queue density."}
            </p>
          </div>

          {/* Accessibility Notes */}
          <div className="p-3.5 rounded-xl bg-slate-800/60 border border-slate-700/60 text-slate-300 space-y-1">
            <div className="flex items-center gap-1.5 font-bold text-slate-200 text-[11px]">
              <Accessibility className="w-3.5 h-3.5 text-indigo-400" />
              <span>Mobility & Terrain Assessment</span>
            </div>
            <p className="text-xs text-slate-400 leading-relaxed">
              {xai.accessibility_notes || "Flat paved courtyards with accessible ramped side entries."}
            </p>
          </div>

        </div>

        {/* Footer */}
        <div className="px-6 py-3 border-t border-slate-800 bg-slate-900 flex justify-end">
          <button
            onClick={() => setSelectedStopForXAI(null)}
            className="px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold"
          >
            Close Explanation
          </button>
        </div>

      </div>
    </div>
  );
};

export default XAIModal;

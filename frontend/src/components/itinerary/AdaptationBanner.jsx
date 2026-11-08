import React, { useState } from 'react';
import { useApp } from '../../context/AppContext';
import api from '../../services/api';
import { 
  AlertTriangle, 
  ArrowRight, 
  Check, 
  X, 
  Sparkles, 
  Clock, 
  ShieldCheck, 
  Loader2 
} from 'lucide-react';

const AdaptationBanner = () => {
  const { 
    activeAdaptation, 
    setActiveAdaptation, 
    activeTrip, 
    setActiveTrip, 
    showToast 
  } = useApp();

  const [loading, setLoading] = useState(false);

  if (!activeAdaptation) return null;

  const handleDecision = async (accept) => {
    setLoading(true);
    try {
      await api.confirmAdaptation(activeAdaptation.adaptation_id, accept);
      if (accept && activeTrip) {
        // Reload trip with adapted stops
        const updatedTrip = await api.getItinerary(activeTrip.id);
        setActiveTrip(updatedTrip);
        showToast('Itinerary dynamically adapted based on real-time context!', 'success');
      } else {
        showToast('Adaptation declined. Original itinerary retained.', 'info');
      }
      setActiveAdaptation(null);
    } catch (err) {
      console.error(err);
      showToast('Failed to apply adaptation', 'error');
    } finally {
      setLoading(false);
    }
  };

  const replacements = activeAdaptation.proposed_replacements || [];

  return (
    <div className="w-full rounded-2xl bg-gradient-to-r from-amber-500/15 via-rose-500/15 to-purple-500/15 border border-amber-500/30 p-5 shadow-2xl backdrop-blur-md animate-fade-in mb-6">
      
      {/* Alert Header */}
      <div className="flex flex-wrap items-center justify-between gap-3 pb-3 border-b border-amber-500/20">
        <div className="flex items-center gap-2.5">
          <div className="p-2 rounded-xl bg-amber-500 text-slate-950 shadow-md">
            <AlertTriangle className="w-5 h-5 stroke-[2.5]" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h3 className="text-sm font-bold text-white font-['Outfit']">
                Real-Time Dynamic Itinerary Adaptation Triggered (I*)
              </h3>
              <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-amber-500/20 text-amber-300 border border-amber-500/40">
                Tourist Agency Retained
              </span>
            </div>
            <p className="text-xs text-amber-200/90 mt-0.5">
              {activeAdaptation.disruption_summary}
            </p>
          </div>
        </div>

        {/* Expected Utility Gain */}
        <div className="flex items-center gap-1.5 px-3 py-1 rounded-lg bg-slate-900/80 border border-amber-500/30 text-amber-300 text-xs font-semibold">
          <Sparkles className="w-3.5 h-3.5 text-amber-400" />
          <span>Expected Utility: +{activeAdaptation.expected_utility_delta}%</span>
        </div>
      </div>

      {/* Side-by-side proposed replacements diff */}
      <div className="my-4 space-y-2.5">
        <div className="text-[11px] font-bold uppercase tracking-wider text-slate-400">
          Proposed POI Adjustments:
        </div>

        {replacements.map((rep, idx) => (
          <div key={idx} className="flex flex-col sm:flex-row sm:items-center justify-between p-3 rounded-xl bg-slate-900/90 border border-slate-800 gap-3">
            
            {/* Original Stop */}
            <div className="flex items-center gap-2">
              <span className="text-rose-400 line-through text-xs font-medium">{rep.original_name}</span>
              <span className="text-[10px] px-1.5 py-0.5 rounded bg-rose-500/10 text-rose-300 border border-rose-500/20 capitalize">
                {rep.original_type}
              </span>
            </div>

            {/* Transition Arrow */}
            <ArrowRight className="w-4 h-4 text-slate-500 hidden sm:block shrink-0" />

            {/* Replacement Stop */}
            <div className="flex flex-col sm:items-end">
              <div className="flex items-center gap-2">
                <span className="text-teal-300 font-bold text-xs">{rep.new_name}</span>
                <span className="text-[10px] px-1.5 py-0.5 rounded bg-teal-500/20 text-teal-300 border border-teal-500/30 capitalize">
                  {rep.new_type}
                </span>
              </div>
              <span className="text-[11px] text-slate-400 mt-0.5">{rep.rationale}</span>
            </div>

          </div>
        ))}
      </div>

      {/* Decision Buttons */}
      <div className="flex flex-wrap items-center justify-between gap-3 pt-2">
        <div className="text-[11px] text-slate-400 flex items-center gap-1">
          <ShieldCheck className="w-3.5 h-3.5 text-teal-400" />
          <span>Nexora requires your approval before modifying confirmed schedules.</span>
        </div>

        <div className="flex items-center gap-2.5">
          <button
            onClick={() => handleDecision(false)}
            disabled={loading}
            className="flex items-center gap-1.5 px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-semibold border border-slate-700 transition-all"
          >
            <X className="w-4 h-4" />
            <span>Decline & Keep Plan</span>
          </button>

          <button
            onClick={() => handleDecision(true)}
            disabled={loading}
            className="flex items-center gap-1.5 px-5 py-2 rounded-xl bg-gradient-to-r from-amber-400 to-teal-400 hover:from-amber-300 hover:to-teal-300 text-slate-950 text-xs font-bold shadow-lg shadow-amber-500/20 transition-all hover:scale-105"
          >
            {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Check className="w-4 h-4 stroke-[3]" />}
            <span>Accept Re-Optimization</span>
          </button>
        </div>
      </div>

    </div>
  );
};

export default AdaptationBanner;

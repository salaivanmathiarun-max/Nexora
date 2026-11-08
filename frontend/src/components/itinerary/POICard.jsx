import React from 'react';
import { useApp } from '../../context/AppContext';
import { 
  Clock, 
  MapPin, 
  Accessibility, 
  Sparkles, 
  CheckCircle2, 
  Footprints, 
  Building, 
  SunMedium, 
  DoorClosed, 
  Tag 
} from 'lucide-react';

const POICard = ({ stop }) => {
  const { setSelectedStopForXAI } = useApp();
  const dest = stop.destination;

  if (!dest) return null;

  return (
    <div className="glass-card glass-card-hover rounded-2xl overflow-hidden border border-slate-800 transition-all flex flex-col md:flex-row">
      
      {/* Venue Photo Thumbnail */}
      <div className="relative md:w-56 h-48 md:h-auto shrink-0 overflow-hidden bg-slate-900">
        <img
          src={dest.image_url}
          alt={dest.name}
          className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
          onError={(e) => {
            e.target.src = "https://images.unsplash.com/photo-1548013146-72479768bada?auto=format&fit=crop&w=800&q=80";
          }}
        />
        {/* Category Pill */}
        <span className="absolute top-3 left-3 px-2.5 py-1 rounded-full text-[10px] font-bold uppercase tracking-wider bg-slate-950/80 text-teal-300 backdrop-blur-md border border-teal-500/30">
          {dest.category}
        </span>
        {/* Match Score Badge */}
        <div className="absolute bottom-3 left-3 flex items-center gap-1 px-2.5 py-1 rounded-full text-[11px] font-bold bg-teal-500 text-slate-950 shadow-md">
          <Sparkles className="w-3 h-3 fill-slate-950" />
          <span>{stop.xai_match_score}% Match</span>
        </div>
      </div>

      {/* Content Details */}
      <div className="p-5 flex-1 flex flex-col justify-between">
        
        <div>
          {/* Header Row: Timing & Buffer */}
          <div className="flex flex-wrap items-center justify-between gap-2 mb-2">
            <div className="flex items-center gap-2">
              <span className="flex items-center gap-1.5 px-2.5 py-1 rounded-md bg-teal-500/10 text-teal-300 border border-teal-500/20 text-xs font-semibold">
                <Clock className="w-3.5 h-3.5 text-teal-400" />
                <span>{stop.planned_start_time} – {stop.planned_end_time}</span>
              </span>
              <span className="flex items-center gap-1 px-2 py-1 rounded-md bg-slate-800 text-slate-300 text-[11px] font-medium border border-slate-700/60" title="Buffer time for walking, queue, and photography">
                <Footprints className="w-3 h-3 text-cyan-400" />
                <span>+{stop.buffer_minutes}m buffer</span>
              </span>
            </div>

            {/* Accessibility & Environment Badges */}
            <div className="flex items-center gap-1.5">
              {dest.is_wheelchair_accessible ? (
                <span className="flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] bg-emerald-500/15 text-emerald-300 border border-emerald-500/30" title="Wheelchair and ramp accessible">
                  <Accessibility className="w-3 h-3" />
                  <span>Accessible</span>
                </span>
              ) : (
                <span className="px-2 py-0.5 rounded-full text-[10px] bg-amber-500/15 text-amber-300 border border-amber-500/30">
                  Historic Stairs
                </span>
              )}

              <span className="px-2 py-0.5 rounded-full text-[10px] bg-slate-800 text-slate-300 border border-slate-700 capitalize">
                {dest.indoor_outdoor}
              </span>
            </div>
          </div>

          {/* Destination Title & Description */}
          <h3 className="text-base font-bold text-white font-['Outfit'] mb-1">
            {dest.name}
          </h3>
          <p className="text-xs text-slate-400 line-clamp-2 leading-relaxed mb-3">
            {dest.description}
          </p>

          {/* Tags */}
          {dest.tags && dest.tags.length > 0 && (
            <div className="flex flex-wrap gap-1.5 mb-4">
              {dest.tags.slice(0, 4).map((tag, i) => (
                <span key={i} className="text-[10px] px-2 py-0.5 rounded bg-slate-800/80 text-slate-400 border border-slate-700/50">
                  #{tag}
                </span>
              ))}
            </div>
          )}
        </div>

        {/* Footer: XAI Inspector Trigger */}
        <div className="pt-3 border-t border-slate-800/80 flex items-center justify-between">
          <div className="text-[11px] text-slate-400">
            Avg Duration: <strong className="text-slate-200">{dest.avg_duration_minutes} mins</strong>
          </div>

          <button
            onClick={() => setSelectedStopForXAI(stop)}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-teal-500/10 hover:bg-teal-500/20 text-teal-300 text-xs font-semibold border border-teal-500/30 transition-all hover:scale-105"
          >
            <Sparkles className="w-3.5 h-3.5 text-teal-400" />
            <span>Explain Recommendation (XAI)</span>
          </button>
        </div>

      </div>

    </div>
  );
};

export default POICard;

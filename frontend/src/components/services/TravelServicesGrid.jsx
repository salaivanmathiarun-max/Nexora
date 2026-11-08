import React, { useState, useEffect } from 'react';
import api from '../../services/api';
import { 
  Building2, 
  Hotel, 
  UtensilsCrossed, 
  Bus, 
  ShieldAlert, 
  PhoneCall, 
  Star, 
  Accessibility, 
  MapPin, 
  Check 
} from 'lucide-react';

const TravelServicesGrid = () => {
  const [servicesData, setServicesData] = useState(null);

  useEffect(() => {
    api.getTravelServices('Samarkand')
      .then(d => setServicesData(d))
      .catch(err => console.error(err));
  }, []);

  if (!servicesData) {
    return (
      <div className="w-full glass-panel rounded-2xl p-8 text-center text-slate-400">
        Loading travel services...
      </div>
    );
  }

  const { accommodations, dining, transit_options, emergency_assistance } = servicesData;

  return (
    <div className="w-full space-y-6 animate-fade-in">
      
      {/* Header */}
      <div className="glass-panel rounded-2xl p-6 border border-slate-800">
        <div className="flex items-center gap-3 mb-2">
          <div className="p-2.5 rounded-xl bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
            <Building2 className="w-6 h-6" />
          </div>
          <div>
            <h2 className="text-lg font-bold text-white font-['Outfit']">
              Integrated Travel Services
            </h2>
            <p className="text-xs text-slate-400">
              Coordinated lodging, dining, transit, and emergency support (Paper Section 3.9)
            </p>
          </div>
        </div>
        <p className="text-xs text-slate-300 leading-relaxed max-w-2xl">
          Consolidates fragmented travel logistics into a single intelligent platform, eliminating the need to jump between multiple independent apps during your journey.
        </p>
      </div>

      {/* Grid: 4 Pillars */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        
        {/* 1. Accommodations */}
        <div className="glass-panel rounded-2xl p-5 border border-slate-800 space-y-4">
          <div className="flex items-center gap-2 text-sm font-bold text-white font-['Outfit']">
            <Hotel className="w-4 h-4 text-teal-400" />
            <span>Curated Accommodations</span>
          </div>

          <div className="space-y-3">
            {accommodations.map((hotel, idx) => (
              <div key={idx} className="p-3.5 rounded-xl bg-slate-900/80 border border-slate-800 space-y-2">
                <div className="flex items-start justify-between gap-2">
                  <div>
                    <h4 className="text-xs font-bold text-white">{hotel.name}</h4>
                    <span className="text-[11px] text-teal-300 font-medium">{hotel.type}</span>
                  </div>
                  <div className="flex items-center gap-1 text-[11px] font-bold text-amber-400 bg-amber-500/10 px-2 py-0.5 rounded-md border border-amber-500/20">
                    <Star className="w-3 h-3 fill-amber-400" />
                    <span>{hotel.rating}</span>
                  </div>
                </div>

                <div className="text-[11px] text-slate-400 flex items-center gap-1">
                  <MapPin className="w-3 h-3 text-slate-500" />
                  <span>{hotel.distance}</span>
                </div>

                <div className="flex flex-wrap gap-1 pt-1">
                  {hotel.perks.map((perk, i) => (
                    <span key={i} className="text-[10px] px-2 py-0.5 rounded-md bg-slate-800 text-slate-300 border border-slate-700/60">
                      ✓ {perk}
                    </span>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* 2. Dining by Dietary Profile */}
        <div className="glass-panel rounded-2xl p-5 border border-slate-800 space-y-4">
          <div className="flex items-center gap-2 text-sm font-bold text-white font-['Outfit']">
            <UtensilsCrossed className="w-4 h-4 text-amber-400" />
            <span>Dining & Cuisine (Profile Aligned)</span>
          </div>

          <div className="space-y-3">
            {dining.map((rest, idx) => (
              <div key={idx} className="p-3.5 rounded-xl bg-slate-900/80 border border-slate-800 space-y-2">
                <div className="flex items-start justify-between gap-2">
                  <div>
                    <h4 className="text-xs font-bold text-white">{rest.name}</h4>
                    <span className="text-[11px] text-amber-300 font-medium">{rest.cuisine}</span>
                  </div>
                  <div className="flex items-center gap-1 text-[11px] font-bold text-amber-400 bg-amber-500/10 px-2 py-0.5 rounded-md border border-amber-500/20">
                    <Star className="w-3 h-3 fill-amber-400" />
                    <span>{rest.rating}</span>
                  </div>
                </div>

                <div className="text-[11px] text-slate-300 font-medium">
                  Signature: <span className="text-teal-300">{rest.signature_dish}</span>
                </div>

                <div className="flex flex-wrap gap-1 pt-1">
                  {rest.dietary.map((d, i) => (
                    <span key={i} className="text-[10px] px-2 py-0.5 rounded-md bg-amber-500/10 text-amber-300 border border-amber-500/20">
                      {d}
                    </span>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* 3. Local Transit & Mobility */}
        <div className="glass-panel rounded-2xl p-5 border border-slate-800 space-y-4">
          <div className="flex items-center gap-2 text-sm font-bold text-white font-['Outfit']">
            <Bus className="w-4 h-4 text-cyan-400" />
            <span>Local Transit & Route Options</span>
          </div>

          <div className="space-y-3">
            {transit_options.map((transit, idx) => (
              <div key={idx} className="p-3.5 rounded-xl bg-slate-900/80 border border-slate-800 space-y-1.5">
                <div className="flex items-center justify-between">
                  <h4 className="text-xs font-bold text-white">{transit.mode}</h4>
                  <span className="text-[10px] px-2 py-0.5 rounded bg-cyan-500/15 text-cyan-300 border border-cyan-500/30 font-mono">
                    {transit.cost}
                  </span>
                </div>
                <div className="text-[11px] text-slate-400">Coverage: {transit.coverage}</div>
                <div className="text-[10px] text-teal-300 flex items-center gap-1">
                  <Accessibility className="w-3 h-3" />
                  <span>{transit.accessibility}</span>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* 4. Emergency SOS & Tourist Police */}
        <div className="glass-panel rounded-2xl p-5 border border-slate-800 space-y-4">
          <div className="flex items-center gap-2 text-sm font-bold text-white font-['Outfit']">
            <ShieldAlert className="w-4 h-4 text-rose-400" />
            <span>Emergency Assistance & Tourist Police</span>
          </div>

          <div className="space-y-2.5">
            {emergency_assistance.map((sos, idx) => (
              <div key={idx} className="flex items-center justify-between p-3 rounded-xl bg-slate-900/80 border border-slate-800">
                <div>
                  <div className="text-xs font-bold text-slate-200">{sos.service}</div>
                  {sos.address && <div className="text-[10px] text-slate-400">{sos.address}</div>}
                </div>
                <a
                  href={`tel:${sos.phone}`}
                  className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-rose-500/15 text-rose-300 border border-rose-500/30 text-xs font-bold hover:bg-rose-500/25 transition-colors"
                >
                  <PhoneCall className="w-3.5 h-3.5" />
                  <span>{sos.phone}</span>
                </a>
              </div>
            ))}
          </div>
        </div>

      </div>

    </div>
  );
};

export default TravelServicesGrid;

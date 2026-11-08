import React, { useState } from 'react';
import { useApp } from '../../context/AppContext';
import api from '../../services/api';
import POICard from './POICard';
import AdaptationBanner from './AdaptationBanner';
import { 
  Calendar, 
  MapPin, 
  Clock, 
  Sparkles, 
  Share2, 
  Download, 
  Compass 
} from 'lucide-react';

const ItineraryTimeline = () => {
  const { activeTrip, setActiveTrip, profile, showToast } = useApp();
  const [selectedDay, setSelectedDay] = useState(1);
  const [loadingDemo, setLoadingDemo] = useState(false);

  const handleQuickDemo = async () => {
    setLoadingDemo(true);
    try {
      const newTrip = await api.generateItinerary({
        destination_city: 'Samarkand',
        start_date: '2026-11-01',
        total_days: 2,
        travel_style: profile?.travel_style || 'balanced',
        custom_interests: ['historical', 'monument', 'cultural'],
        accessibility_needs: profile?.accessibility_needs || []
      });
      setActiveTrip(newTrip);
      showToast('Loaded 2-Day Samarkand Silk Road Tour with XAI attribution!', 'success');
    } catch (err) {
      console.error(err);
      showToast('Failed to load demo itinerary', 'error');
    } finally {
      setLoadingDemo(false);
    }
  };

  if (!activeTrip || !activeTrip.stops || activeTrip.stops.length === 0) {
    return (
      <div className="w-full glass-panel rounded-2xl p-12 text-center border border-slate-800">
        <div className="w-16 h-16 rounded-2xl bg-teal-500/10 border border-teal-500/20 text-teal-400 flex items-center justify-center mx-auto mb-4">
          <Compass className="w-8 h-8 animate-spin-slow" />
        </div>
        <h3 className="text-lg font-bold text-white font-['Outfit'] mb-2">No Active Itinerary Yet</h3>
        <p className="text-xs text-slate-400 max-w-md mx-auto mb-6 leading-relaxed">
          Use the Multimodal Travel Query bar above to speak, type, or upload an image to generate an explainable, context-aware itinerary.
        </p>
        <button
          onClick={handleQuickDemo}
          disabled={loadingDemo}
          className="inline-flex items-center gap-2 px-6 py-2.5 rounded-xl bg-gradient-to-r from-teal-500 to-cyan-500 hover:from-teal-400 hover:to-cyan-400 text-slate-950 font-bold text-xs shadow-lg shadow-teal-500/20 transition-all hover:scale-105"
        >
          <Sparkles className="w-4 h-4 fill-slate-950" />
          <span>{loadingDemo ? 'Generating...' : 'Load 2-Day Silk Road Demo Itinerary'}</span>
        </button>
      </div>
    );
  }

  const daysCount = activeTrip.total_days || 1;
  const currentDayStops = activeTrip.stops.filter(s => s.day_number === selectedDay);

  return (
    <div className="w-full space-y-6">
      
      {/* Dynamic Adaptation Proposal if active */}
      <AdaptationBanner />

      {/* Itinerary Header & Controls */}
      <div className="glass-panel rounded-2xl p-5 border border-slate-800 flex flex-wrap items-center justify-between gap-4">
        
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="text-xs font-semibold px-2.5 py-0.5 rounded-full bg-teal-500/10 text-teal-400 border border-teal-500/20">
              Personalized Trip Plan
            </span>
            <span className="text-xs text-slate-400">
              {activeTrip.start_date} – {activeTrip.end_date}
            </span>
          </div>
          <h2 className="text-xl font-extrabold text-white font-['Outfit']">
            {activeTrip.title}
          </h2>
          <div className="flex items-center gap-2 text-xs text-slate-400 mt-1">
            <MapPin className="w-3.5 h-3.5 text-teal-400" />
            <span>{activeTrip.destination_city} • {activeTrip.stops.length} Optimized Stops</span>
          </div>
        </div>

        {/* Day Selector Tabs */}
        <div className="flex items-center gap-1.5 bg-slate-900 p-1.5 rounded-xl border border-slate-800">
          {Array.from({ length: daysCount }, (_, i) => i + 1).map((day) => (
            <button
              key={day}
              onClick={() => setSelectedDay(day)}
              className={`flex items-center gap-1.5 px-4 py-2 rounded-lg text-xs font-bold transition-all ${
                selectedDay === day
                  ? 'bg-gradient-to-r from-teal-500 to-cyan-500 text-slate-950 shadow-md shadow-teal-500/20'
                  : 'text-slate-400 hover:text-white hover:bg-slate-800'
              }`}
            >
              <Calendar className="w-3.5 h-3.5" />
              <span>Day {day}</span>
            </button>
          ))}
        </div>

      </div>

      {/* Stops Timeline for Selected Day */}
      <div className="space-y-4">
        <div className="flex items-center justify-between text-xs font-semibold text-slate-400 px-1">
          <span>DAY {selectedDay} CHRONOLOGICAL SCHEDULE</span>
          <span>Buffer times calculated for walking, ticketing & queue flow</span>
        </div>

        <div className="space-y-4">
          {currentDayStops.map((stop) => (
            <POICard key={stop.id} stop={stop} />
          ))}
        </div>
      </div>

    </div>
  );
};

export default ItineraryTimeline;

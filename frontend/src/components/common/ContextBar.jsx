import React from 'react';
import { useApp } from '../../context/AppContext';
import { 
  MapPin, 
  Sun, 
  CloudRain, 
  Cloud, 
  Users, 
  Car, 
  AlertTriangle, 
  Clock 
} from 'lucide-react';

const ContextBar = () => {
  const { contextVector } = useApp();

  if (!contextVector) return null;

  const weather = contextVector.weather || {};
  const isRain = weather.weather_condition === 'Rainy' || weather.is_indoor_preferred;
  const isCrowdHigh = contextVector.crowd_density === 'High' || contextVector.crowd_density === 'Peak';

  return (
    <div className="w-full bg-slate-900/70 border-b border-slate-800/80 px-4 py-2 backdrop-blur-sm">
      <div className="max-w-7xl mx-auto flex flex-wrap items-center justify-between gap-3 text-xs">
        
        {/* Context Parameters C = [L, T, W, Tr, Cr, O, P] */}
        <div className="flex flex-wrap items-center gap-3">
          
          {/* Location L */}
          <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-md bg-slate-800/80 text-slate-300 border border-slate-700/60">
            <MapPin className="w-3.5 h-3.5 text-teal-400" />
            <span className="font-semibold text-slate-200">{contextVector.location_name}</span>
          </div>

          {/* Time T */}
          <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-md bg-slate-800/80 text-slate-300 border border-slate-700/60">
            <Clock className="w-3.5 h-3.5 text-slate-400" />
            <span>Local Time: <strong className="text-slate-200">{contextVector.current_time}</strong></span>
          </div>

          {/* Weather W */}
          <div className={`flex items-center gap-1.5 px-2.5 py-1 rounded-md border ${
            isRain 
              ? 'bg-blue-500/15 border-blue-500/30 text-blue-300' 
              : 'bg-slate-800/80 border-slate-700/60 text-slate-300'
          }`}>
            {isRain ? (
              <CloudRain className="w-3.5 h-3.5 text-blue-400" />
            ) : weather.weather_condition === 'Partly Cloudy' ? (
              <Cloud className="w-3.5 h-3.5 text-cyan-400" />
            ) : (
              <Sun className="w-3.5 h-3.5 text-amber-400" />
            )}
            <span>
              {weather.weather_condition}, <strong className="text-slate-100">{weather.temperature_c}°C</strong>
              {weather.precipitation_probability > 0 && ` (${weather.precipitation_probability}% precip)`}
            </span>
          </div>

          {/* Crowd Cr */}
          <div className={`flex items-center gap-1.5 px-2.5 py-1 rounded-md border ${
            isCrowdHigh 
              ? 'bg-rose-500/15 border-rose-500/30 text-rose-300' 
              : 'bg-slate-800/80 border-slate-700/60 text-slate-300'
          }`}>
            <Users className={`w-3.5 h-3.5 ${isCrowdHigh ? 'text-rose-400' : 'text-slate-400'}`} />
            <span>Crowd Index: <strong className="text-slate-200">{contextVector.crowd_density}</strong></span>
          </div>

          {/* Traffic Tr */}
          <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-md bg-slate-800/80 text-slate-300 border border-slate-700/60">
            <Car className="w-3.5 h-3.5 text-slate-400" />
            <span>Transit Flow: <strong className="text-slate-200">{contextVector.traffic_level}</strong></span>
          </div>

        </div>

        {/* Live Vector Indicator */}
        <div className="flex items-center gap-2">
          <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
          <span className="text-[11px] font-mono text-slate-400">Context Vector: C Active</span>
        </div>

      </div>

      {/* Real-time Alerts Banner if any */}
      {contextVector.active_alerts && contextVector.active_alerts.length > 0 && (
        <div className="max-w-7xl mx-auto mt-2">
          {contextVector.active_alerts.map((alert, idx) => (
            <div key={idx} className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-amber-500/15 border border-amber-500/30 text-amber-300 text-xs animate-pulse-subtle">
              <AlertTriangle className="w-4 h-4 text-amber-400 shrink-0" />
              <span>{alert}</span>
            </div>
          ))}
        </div>
      )}

    </div>
  );
};

export default ContextBar;

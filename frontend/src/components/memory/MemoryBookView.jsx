import React, { useState, useEffect } from 'react';
import { useApp } from '../../context/AppContext';
import api from '../../services/api';
import { 
  BookHeart, 
  Sparkles, 
  Calendar, 
  MapPin, 
  Download, 
  Share2, 
  PenTool, 
  Image as ImageIcon, 
  Loader2 
} from 'lucide-react';

const MemoryBookView = () => {
  const { activeTrip, showToast } = useApp();
  const [memoryBook, setMemoryBook] = useState(null);
  const [loading, setLoading] = useState(false);
  const [userNotes, setUserNotes] = useState('');

  const loadMemory = async (tripId) => {
    try {
      const res = await api.getMemoryBook(tripId);
      if (res && res.entry) {
        setMemoryBook(res.entry);
      }
    } catch (err) {
      console.error(err);
    }
  };

  useEffect(() => {
    if (activeTrip) {
      loadMemory(activeTrip.id);
    }
  }, [activeTrip]);

  const handleGenerate = async () => {
    if (!activeTrip) {
      showToast('Please generate an itinerary first to build your Memory Book.', 'info');
      return;
    }

    setLoading(true);
    try {
      const res = await api.generateMemoryBook(activeTrip.id, userNotes);
      setMemoryBook(res);
      showToast('AI Memory Book generated successfully!', 'success');
    } catch (err) {
      console.error(err);
      showToast('Failed to generate Memory Book', 'error');
    } finally {
      setLoading(false);
    }
  };

  const handlePrint = () => {
    window.print();
  };

  return (
    <div className="w-full space-y-6 animate-fade-in">
      
      {/* Header */}
      <div className="glass-panel rounded-2xl p-6 border border-slate-800">
        <div className="flex items-center gap-3 mb-2">
          <div className="p-2.5 rounded-xl bg-rose-500/10 text-rose-400 border border-rose-500/20">
            <BookHeart className="w-6 h-6" />
          </div>
          <div>
            <h2 className="text-lg font-bold text-white font-['Outfit']">
              AI Travel Memory Book
            </h2>
            <p className="text-xs text-slate-400">
              Automated journey synthesis and digital keepsake (Paper Section 3.10)
            </p>
          </div>
        </div>
        <p className="text-xs text-slate-300 leading-relaxed max-w-2xl">
          Nexora compiles your visited destinations, photos, timelines, and personal reflections into a curated digital travelogue upon trip completion.
        </p>
      </div>

      {memoryBook ? (
        /* Render Generated Digital Keepsake Scrapbook */
        <div className="glass-panel rounded-3xl p-8 border border-slate-800 shadow-2xl space-y-8 bg-gradient-to-b from-slate-900/90 to-slate-950/90 relative overflow-hidden">
          
          <div className="flex flex-wrap items-center justify-between gap-4 pb-6 border-b border-slate-800">
            <div>
              <span className="text-[10px] font-bold uppercase tracking-widest px-3 py-1 rounded-full bg-rose-500/15 text-rose-300 border border-rose-500/30">
                AI Travel Keepsake Journal
              </span>
              <h3 className="text-2xl font-extrabold text-white font-['Outfit'] mt-2">
                {memoryBook.entry_title}
              </h3>
              <div className="flex items-center gap-2 text-xs text-slate-400 mt-1">
                <Calendar className="w-3.5 h-3.5 text-teal-400" />
                <span>Captured on {new Date(memoryBook.created_at).toLocaleDateString()}</span>
              </div>
            </div>

            <div className="flex items-center gap-2">
              <button
                onClick={handlePrint}
                className="flex items-center gap-1.5 px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold border border-slate-700 transition-all"
              >
                <Download className="w-4 h-4 text-teal-400" />
                <span>Export / Print Keepsake</span>
              </button>
            </div>
          </div>

          {/* AI Narrative Chapter */}
          <div className="p-6 rounded-2xl bg-slate-900/70 border border-slate-800 space-y-3">
            <div className="flex items-center gap-2 text-xs font-bold text-teal-300 font-['Outfit'] uppercase tracking-wider">
              <Sparkles className="w-4 h-4 text-teal-400" />
              <span>Journey Narrative</span>
            </div>
            <p className="text-sm text-slate-200 leading-relaxed italic font-serif">
              "{memoryBook.story_narrative}"
            </p>
          </div>

          {/* Photo Gallery Grid */}
          <div className="space-y-3">
            <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider">Visual Highlights</h4>
            <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4">
              {memoryBook.photos.map((photoUrl, idx) => (
                <div key={idx} className="h-48 rounded-2xl overflow-hidden border border-slate-800 shadow-md group">
                  <img
                    src={photoUrl}
                    alt={`Memory photo ${idx}`}
                    className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
                  />
                </div>
              ))}
            </div>
          </div>

          {/* Trip Milestones / Highlights */}
          <div className="space-y-3">
            <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider">Cherished Moments</h4>
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
              {memoryBook.highlights.map((item, idx) => (
                <div key={idx} className="p-4 rounded-xl bg-slate-900/60 border border-slate-800 text-xs text-slate-300 flex items-start gap-2">
                  <span className="w-1.5 h-1.5 rounded-full bg-teal-400 mt-1.5 shrink-0" />
                  <span>{item}</span>
                </div>
              ))}
            </div>
          </div>

        </div>
      ) : (
        /* Prompt to Generate */
        <div className="glass-panel rounded-2xl p-8 border border-slate-800 text-center space-y-4 max-w-xl mx-auto">
          <div className="w-16 h-16 rounded-2xl bg-rose-500/10 text-rose-400 border border-rose-500/20 flex items-center justify-center mx-auto">
            <BookHeart className="w-8 h-8" />
          </div>
          <h3 className="text-base font-bold text-white font-['Outfit']">Ready to Chronicle Your Trip?</h3>
          <p className="text-xs text-slate-400 leading-relaxed">
            Add optional personal travel notes or reflections, and Nexora's AI will craft your personalized journey story and photo scrapbook.
          </p>

          <textarea
            value={userNotes}
            onChange={(e) => setUserNotes(e.target.value)}
            rows={3}
            placeholder="Add personal reflections, favorite bazaar discoveries, or memorable encounters..."
            className="w-full bg-slate-900 border border-slate-700 rounded-xl p-3 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-rose-500"
          />

          <button
            onClick={handleGenerate}
            disabled={loading}
            className="flex items-center gap-2 px-6 py-2.5 rounded-xl bg-gradient-to-r from-rose-500 to-teal-500 hover:from-rose-400 hover:to-teal-400 text-white font-bold text-xs shadow-lg shadow-rose-500/20 transition-all mx-auto"
          >
            {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Sparkles className="w-4 h-4" />}
            <span>Compile AI Memory Book</span>
          </button>
        </div>
      )}

    </div>
  );
};

export default MemoryBookView;

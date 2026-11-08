import React, { useState, useRef } from 'react';
import { useApp } from '../../context/AppContext';
import api from '../../services/api';
import { 
  Sparkles, 
  Mic, 
  MicOff, 
  Image as ImageIcon, 
  MapPin, 
  Calendar, 
  Send, 
  X, 
  Compass, 
  Loader2 
} from 'lucide-react';

const MultimodalInput = () => {
  const { setActiveTrip, profile, showToast } = useApp();

  const [textQuery, setTextQuery] = useState('');
  const [voiceTranscript, setVoiceTranscript] = useState('');
  const [isRecording, setIsRecording] = useState(false);
  const [selectedImage, setSelectedImage] = useState(null);
  const [destinationCity, setDestinationCity] = useState('Samarkand');
  const [durationDays, setDurationDays] = useState(2);
  const [isGenerating, setIsGenerating] = useState(false);

  const fileInputRef = useRef(null);
  const recognitionRef = useRef(null);

  // Web Speech API Voice Recognition
  const toggleVoiceRecording = () => {
    if (isRecording) {
      if (recognitionRef.current) {
        recognitionRef.current.stop();
      }
      setIsRecording(false);
      return;
    }

    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) {
      showToast('Speech recognition not supported in this browser. Please type your query.', 'error');
      return;
    }

    try {
      const recognition = new SpeechRecognition();
      recognition.continuous = false;
      recognition.interimResults = false;
      recognition.lang = profile?.language === 'uz' ? 'uz-UZ' : 'en-US';

      recognition.onstart = () => {
        setIsRecording(true);
        showToast('Listening... Speak your travel request now.', 'info');
      };

      recognition.onresult = (event) => {
        const transcript = event.results[0][0].transcript;
        setVoiceTranscript(transcript);
        setTextQuery(prev => prev ? `${prev} [Spoken: ${transcript}]` : transcript);
        showToast(`Captured: "${transcript}"`, 'success');
      };

      recognition.onerror = (event) => {
        console.error('Speech recognition error:', event.error);
        setIsRecording(false);
        showToast(`Voice error: ${event.error}`, 'error');
      };

      recognition.onend = () => {
        setIsRecording(false);
      };

      recognitionRef.current = recognition;
      recognition.start();
    } catch (err) {
      console.error(err);
      setIsRecording(false);
    }
  };

  // Image Upload Handler
  const handleImageUpload = (e) => {
    const file = e.target.files[0];
    if (file) {
      const reader = new FileReader();
      reader.onloadend = () => {
        setSelectedImage(reader.result);
        showToast('Image uploaded as multimodal reference.', 'info');
      };
      reader.readAsDataURL(file);
    }
  };

  // GPS Location Handler
  const handleGetLocation = () => {
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (pos) => {
          showToast(`GPS Captured: ${pos.coords.latitude.toFixed(4)}, ${pos.coords.longitude.toFixed(4)}`, 'success');
        },
        (err) => {
          showToast('GPS unavailable, using destination defaults.', 'info');
        }
      );
    }
  };

  // Generate Itinerary Execution
  const handleSubmit = async (e) => {
    if (e) e.preventDefault();
    setIsGenerating(true);

    try {
      // 1. Process Multimodal Query via Gemini (or rule-based parser)
      const parsedIntent = await api.processQuery({
        text_query: textQuery,
        voice_transcript: voiceTranscript,
        image_base64: selectedImage,
        destination_city: destinationCity,
        duration_days: durationDays,
      });

      // 2. Generate personalized itinerary with XAI attribution & buffer times
      const newTrip = await api.generateItinerary({
        destination_city: parsedIntent.destination_city || destinationCity,
        start_date: parsedIntent.start_date || '2026-11-01',
        total_days: parsedIntent.duration_days || durationDays,
        travel_style: parsedIntent.travel_style || profile?.travel_style || 'balanced',
        custom_interests: parsedIntent.primary_interests,
        accessibility_needs: parsedIntent.accessibility_flags.length > 0 ? parsedIntent.accessibility_flags : profile?.accessibility_needs
      });

      setActiveTrip(newTrip);
      showToast(`Personalized ${newTrip.total_days}-Day Itinerary with XAI Attribution generated!`, 'success');
    } catch (err) {
      console.error('Itinerary generation error:', err);
      showToast('Failed to generate itinerary. Check backend connectivity.', 'error');
    } finally {
      setIsGenerating(false);
    }
  };

  return (
    <div className="w-full glass-panel rounded-2xl p-5 border border-slate-800 shadow-xl relative overflow-hidden">
      
      {/* Background ambient gradient glow */}
      <div className="absolute top-0 right-0 -mr-16 -mt-16 w-64 h-64 rounded-full bg-teal-500/10 blur-3xl pointer-events-none"></div>

      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          <Sparkles className="w-4 h-4 text-teal-400" />
          <h2 className="text-sm font-bold text-white font-['Outfit'] uppercase tracking-wider">
            Multimodal Travel Query Fusion (Hm = αtHt + αsHs + αiHi)
          </h2>
        </div>
        <span className="text-[11px] text-slate-400">Natural language, spoken voice & photo prompts</span>
      </div>

      <form onSubmit={handleSubmit} className="space-y-4">
        
        {/* Main Text Input Bar */}
        <div className="relative flex items-center">
          <input
            type="text"
            value={textQuery}
            onChange={(e) => setTextQuery(e.target.value)}
            placeholder="E.g., Plan a 2-day historical and culinary journey exploring Samarkand's grand madrasahs and bazaars..."
            className="w-full pl-4 pr-32 py-3.5 rounded-xl bg-slate-900/90 border border-slate-700/80 text-white placeholder-slate-500 text-xs sm:text-sm focus:outline-none focus:border-teal-500 focus:ring-1 focus:ring-teal-500 transition-all shadow-inner"
          />

          {/* Inline Action Controls */}
          <div className="absolute right-2 flex items-center gap-1.5">
            
            {/* Microphone Button */}
            <button
              type="button"
              onClick={toggleVoiceRecording}
              className={`p-2 rounded-lg transition-all ${
                isRecording 
                  ? 'bg-rose-500 text-white animate-pulse' 
                  : 'text-slate-400 hover:text-teal-300 hover:bg-slate-800'
              }`}
              title={isRecording ? 'Stop recording voice' : 'Speak your travel request'}
            >
              {isRecording ? <MicOff className="w-4 h-4" /> : <Mic className="w-4 h-4" />}
            </button>

            {/* Photo Upload Button */}
            <button
              type="button"
              onClick={() => fileInputRef.current?.click()}
              className="p-2 rounded-lg text-slate-400 hover:text-teal-300 hover:bg-slate-800 transition-all"
              title="Upload reference photo of destination or architectural monument"
            >
              <ImageIcon className="w-4 h-4" />
            </button>
            <input
              type="file"
              ref={fileInputRef}
              onChange={handleImageUpload}
              accept="image/*"
              className="hidden"
            />

            {/* GPS Geolocation Button */}
            <button
              type="button"
              onClick={handleGetLocation}
              className="p-2 rounded-lg text-slate-400 hover:text-teal-300 hover:bg-slate-800 transition-all"
              title="Use current GPS location"
            >
              <MapPin className="w-4 h-4" />
            </button>

          </div>
        </div>

        {/* Selected Image Preview Pill */}
        {selectedImage && (
          <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-teal-500/10 border border-teal-500/30 text-teal-300 text-xs w-max animate-fade-in">
            <img src={selectedImage} alt="Ref preview" className="w-5 h-5 rounded object-cover" />
            <span>Photo reference attached for visual feature extraction</span>
            <button type="button" onClick={() => setSelectedImage(null)} className="hover:text-white">
              <X className="w-3.5 h-3.5" />
            </button>
          </div>
        )}

        {/* Query Controls: Destination, Duration, & Submit Button */}
        <div className="flex flex-wrap items-center justify-between gap-3 pt-1">
          
          <div className="flex flex-wrap items-center gap-3">
            
            {/* Destination Selector */}
            <div className="flex items-center gap-2 bg-slate-900 px-3 py-1.5 rounded-lg border border-slate-800 text-xs">
              <Compass className="w-3.5 h-3.5 text-teal-400" />
              <span className="text-slate-400">Destination:</span>
              <select
                value={destinationCity}
                onChange={(e) => setDestinationCity(e.target.value)}
                className="bg-transparent text-white font-semibold focus:outline-none cursor-pointer"
              >
                <option value="Samarkand" className="bg-slate-900">Samarkand, Uzbekistan</option>
              </select>
            </div>

            {/* Duration Selector */}
            <div className="flex items-center gap-2 bg-slate-900 px-3 py-1.5 rounded-lg border border-slate-800 text-xs">
              <Calendar className="w-3.5 h-3.5 text-cyan-400" />
              <span className="text-slate-400">Duration:</span>
              <div className="flex items-center gap-1">
                {[1, 2, 3].map((d) => (
                  <button
                    key={d}
                    type="button"
                    onClick={() => setDurationDays(d)}
                    className={`px-2 py-0.5 rounded text-xs font-semibold transition-all ${
                      durationDays === d
                        ? 'bg-teal-500 text-slate-950 shadow-sm'
                        : 'text-slate-400 hover:text-white hover:bg-slate-800'
                    }`}
                  >
                    {d}D
                  </button>
                ))}
              </div>
            </div>

          </div>

          {/* Submit Button */}
          <button
            type="submit"
            disabled={isGenerating}
            className="flex items-center gap-2 px-6 py-2.5 rounded-xl bg-gradient-to-r from-teal-500 via-cyan-500 to-teal-400 hover:from-teal-400 hover:to-cyan-400 text-slate-950 font-bold text-xs shadow-lg shadow-teal-500/20 transition-all hover:scale-[1.02] active:scale-[0.98] disabled:opacity-50"
          >
            {isGenerating ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin" />
                <span>Computing XAI Itinerary...</span>
              </>
            ) : (
              <>
                <Send className="w-4 h-4" />
                <span>Generate Explainable Itinerary</span>
              </>
            )}
          </button>

        </div>

      </form>
    </div>
  );
};

export default MultimodalInput;

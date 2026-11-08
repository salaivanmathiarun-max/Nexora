import React, { useState, useRef } from 'react';
import api from '../../services/api';
import { 
  Camera, 
  Upload, 
  CheckCircle2, 
  BookOpen, 
  Building2, 
  Lightbulb, 
  Loader2,
  AlertTriangle,
  MapPin,
  Trophy,
  Info
} from 'lucide-react';

const LandmarkScanner = () => {
  const [selectedImage, setSelectedImage] = useState(null);
  const [analyzing, setAnalyzing] = useState(false);
  const [result, setResult] = useState(null);
  const fileInputRef = useRef(null);

  // Sample landmark image buttons for effortless testing
  const sampleLandmarks = [
    {
      name: "Registan Ensemble",
      url: "https://images.unsplash.com/photo-1548013146-72479768bada?auto=format&fit=crop&w=800&q=80"
    },
    {
      name: "Gur-e-Amir Mausoleum",
      url: "https://images.unsplash.com/photo-1596178065887-1198b6148b2b?auto=format&fit=crop&w=800&q=80"
    },
    {
      name: "Shah-i-Zinda Necropolis",
      url: "https://images.unsplash.com/photo-1528728329032-2972f65dfb3f?auto=format&fit=crop&w=800&q=80"
    }
  ];

  const handleSelectSample = (sample) => {
    setSelectedImage(sample.url);
    runAnalysis(sample.url);
  };

  const handleFileUpload = (e) => {
    const file = e.target.files[0];
    if (file) {
      const reader = new FileReader();
      reader.onloadend = () => {
        setSelectedImage(reader.result);
        runAnalysis(reader.result);
      };
      reader.readAsDataURL(file);
    }
  };

  const runAnalysis = async (imgData) => {
    setAnalyzing(true);
    setResult(null);
    try {
      const res = await api.recognizeLandmark(imgData, "Samarkand landmark exploration");
      setResult(res);
    } catch (err) {
      console.error(err);
    } finally {
      setAnalyzing(false);
    }
  };

  return (
    <div className="w-full space-y-6 animate-fade-in">
      
      {/* Header */}
      <div className="glass-panel rounded-2xl p-6 border border-slate-800">
        <div className="flex items-center gap-3 mb-2">
          <div className="p-2.5 rounded-xl bg-teal-500/10 text-teal-400 border border-teal-500/20">
            <Camera className="w-6 h-6" />
          </div>
          <div>
            <h2 className="text-lg font-bold text-white font-['Outfit']">
              Multimodal Landmark Recognition & Cultural Guide
            </h2>
            <p className="text-xs text-slate-400">
              Powered by Gemini Vision (Paper Section 3.7 & Eq. 5–6)
            </p>
          </div>
        </div>
        <p className="text-xs text-slate-300 leading-relaxed max-w-2xl">
          Upload any photo of a monument, shrine, or ancient facade. Nexora extracts visual features, identifies the landmark, and synthesizes historical, architectural, and visiting guidance.
        </p>
      </div>

      {/* Main Scanner Section */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        
        {/* Left Column: Image Upload & Sample Selector */}
        <div className="lg:col-span-5 space-y-4">
          <div 
            onClick={() => fileInputRef.current?.click()}
            className="w-full h-72 rounded-2xl border-2 border-dashed border-slate-700 hover:border-teal-500/60 bg-slate-900/60 flex flex-col items-center justify-center cursor-pointer p-4 transition-all overflow-hidden relative group"
          >
            {selectedImage ? (
              <img 
                src={selectedImage} 
                alt="Selected Landmark" 
                className="w-full h-full object-cover rounded-xl"
              />
            ) : (
              <div className="text-center space-y-2">
                <div className="w-12 h-12 rounded-xl bg-slate-800 text-teal-400 flex items-center justify-center mx-auto group-hover:scale-110 transition-transform">
                  <Upload className="w-6 h-6" />
                </div>
                <div className="text-sm font-semibold text-white">Click or Drop Photo to Scan</div>
                <div className="text-xs text-slate-400">Supports JPG, PNG, WEBP</div>
              </div>
            )}
            <input 
              type="file" 
              ref={fileInputRef} 
              onChange={handleFileUpload} 
              accept="image/*" 
              className="hidden" 
            />
          </div>

          {/* Sample Photos */}
          <div>
            <div className="text-[11px] font-bold uppercase tracking-wider text-slate-400 mb-2">
              Or Test with Sample Landmark:
            </div>
            <div className="grid grid-cols-3 gap-2">
              {sampleLandmarks.map((sample, idx) => (
                <button
                  key={idx}
                  onClick={() => handleSelectSample(sample)}
                  className="rounded-xl overflow-hidden border border-slate-800 hover:border-teal-500/50 bg-slate-900 text-left transition-all group"
                >
                  <img src={sample.url} alt={sample.name} className="w-full h-16 object-cover group-hover:scale-105 transition-transform" />
                  <div className="p-1.5 text-[10px] font-semibold text-slate-300 truncate">
                    {sample.name}
                  </div>
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Right Column: AI Recognition Output */}
        <div className="lg:col-span-7">
          {analyzing ? (
            <div className="h-full min-h-[300px] glass-panel rounded-2xl border border-slate-800 flex flex-col items-center justify-center p-8 text-center">
              <Loader2 className="w-8 h-8 text-teal-400 animate-spin mb-3" />
              <div className="text-sm font-bold text-white font-['Outfit']">Analyzing Visual Features...</div>
              <div className="text-xs text-slate-400 mt-1">Running EfficientNet-B0 classifier → Gemini enrichment</div>
            </div>
          ) : result ? (
            <div className="glass-panel rounded-2xl p-6 border border-slate-800 space-y-5 animate-fade-in">

              {/* Recognition Header */}
              <div className="flex flex-wrap items-center justify-between gap-3 pb-4 border-b border-slate-800">
                <div className="flex-1 min-w-[200px]">
                  {/* Classifier & Hierarchy Badges */}
                  <div className="flex flex-wrap items-center gap-2 mb-1.5">
                    <span className="text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded-full bg-teal-500/10 text-teal-400 border border-teal-500/20">
                      EfficientNet-B0 Classifier
                    </span>

                    {/* Hierarchy badge */}
                    {result.hierarchy_level === 'complex' && (
                      <span className="text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded-full bg-purple-500/15 text-purple-300 border border-purple-500/30">
                        Architectural Ensemble
                      </span>
                    )}
                    {result.hierarchy_level === 'sub_monument' && (
                      <span className="text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded-full bg-cyan-500/15 text-cyan-300 border border-cyan-500/30">
                        Individual Monument
                      </span>
                    )}

                    {result.confidence_level === 'uncertain' && (
                      <span className="text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded-full bg-amber-500/10 text-amber-400 border border-amber-500/20">
                        Low Confidence
                      </span>
                    )}
                    {result.confidence_level === 'medium' && (
                      <span className="text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded-full bg-blue-500/10 text-blue-400 border border-blue-500/20">
                        Medium Confidence
                      </span>
                    )}
                    {result.confidence_level === 'high' && (
                      <span className="text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                        High Confidence
                      </span>
                    )}
                  </div>

                  {/* Parent Landmark Breadcrumb if Child Monument */}
                  {result.parent_landmark && (
                    <div className="text-[11px] font-semibold text-teal-400 tracking-wide flex items-center gap-1 mb-0.5">
                      <span>{result.parent_landmark}</span>
                      <span className="text-slate-500">&rsaquo;</span>
                    </div>
                  )}

                  <h3 className={`text-xl font-extrabold font-['Outfit'] mt-0.5 ${result.is_recognized ? 'text-white' : 'text-amber-300'}`}>
                    {result.predicted_landmark}
                  </h3>

                  {/* Sub-Landmarks Chips for Complex Ensembles */}
                  {result.hierarchy_level === 'complex' && result.sub_landmarks && result.sub_landmarks.length > 0 && (
                    <div className="flex flex-wrap items-center gap-1.5 mt-2">
                      <span className="text-[10px] text-slate-400 font-medium">Includes:</span>
                      {result.sub_landmarks.map((sub, i) => (
                        <span key={i} className="text-[10px] font-medium px-2 py-0.5 rounded-md bg-slate-800 text-slate-300 border border-slate-700">
                          {sub}
                        </span>
                      ))}
                    </div>
                  )}

                  {result.location && result.location !== 'Unknown' && (
                    <div className="flex items-center gap-1 mt-1.5">
                      <MapPin className="w-3 h-3 text-slate-500" />
                      <span className="text-xs text-slate-400">{result.location}</span>
                    </div>
                  )}
                </div>

                {/* Confidence badge */}
                <div className={`flex flex-col items-center gap-1 px-3 py-2 rounded-xl border ${
                  result.confidence_level === 'high'
                    ? 'bg-emerald-500/10 border-emerald-500/30 text-emerald-300'
                    : result.confidence_level === 'medium'
                    ? 'bg-blue-500/10 border-blue-500/30 text-blue-300'
                    : 'bg-amber-500/10 border-amber-500/30 text-amber-300'
                }`}>
                  {result.is_recognized
                    ? <CheckCircle2 className="w-4 h-4" />
                    : <AlertTriangle className="w-4 h-4" />
                  }
                  <span className="text-xs font-bold font-mono">
                    {Math.round((result.confidence_score ?? 0) * 100)}%
                  </span>
                </div>
              </div>

              {/* Confidence bar */}
              <div className="space-y-1">
                <div className="flex justify-between text-[10px] text-slate-500">
                  <span>Classifier Confidence</span>
                  <span className="font-mono">{Math.round((result.confidence_score ?? 0) * 100)}%</span>
                </div>
                <div className="w-full h-1.5 bg-slate-800 rounded-full overflow-hidden">
                  <div
                    className={`h-full rounded-full transition-all ${
                      result.confidence_level === 'high'
                        ? 'bg-emerald-400'
                        : result.confidence_level === 'medium'
                        ? 'bg-blue-400'
                        : 'bg-amber-400'
                    }`}
                    style={{ width: `${Math.round((result.confidence_score ?? 0) * 100)}%` }}
                  />
                </div>
              </div>

              {/* Top candidates (only when uncertain or multiple close candidates) */}
              {result.top_candidates && result.top_candidates.length > 1 && (
                <div className="space-y-1.5">
                  <div className="flex items-center gap-1.5 text-xs font-bold text-slate-200">
                    <Trophy className="w-4 h-4 text-purple-400" />
                    <span>Top Candidates</span>
                  </div>
                  <div className="space-y-1.5">
                    {result.top_candidates.map((candidate, idx) => (
                      <div key={idx} className="flex items-center gap-3 bg-slate-900/60 px-3 py-2 rounded-xl border border-slate-800/80">
                        <span className="text-[10px] font-mono text-slate-500 w-4 shrink-0">#{idx + 1}</span>
                        <div className="flex-1 min-w-0">
                          <div className="text-xs font-semibold text-slate-200 truncate">{candidate.display_name}</div>
                          <div className="w-full h-1 bg-slate-800 rounded-full mt-1 overflow-hidden">
                            <div
                              className="h-full bg-teal-500/60 rounded-full"
                              style={{ width: `${Math.round(candidate.confidence * 100)}%` }}
                            />
                          </div>
                        </div>
                        <span className="text-[10px] font-mono text-slate-400 shrink-0">
                          {Math.round(candidate.confidence * 100)}%
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Uncertainty notice */}
              {!result.is_recognized && (
                <div className="flex items-start gap-2.5 p-3.5 rounded-xl bg-amber-500/5 border border-amber-500/20">
                  <Info className="w-4 h-4 text-amber-400 shrink-0 mt-0.5" />
                  <p className="text-xs text-amber-200 leading-relaxed">{result.message}</p>
                </div>
              )}

              {/* Historical Context */}
              <div className="space-y-1.5">
                <div className="flex items-center gap-1.5 text-xs font-bold text-slate-200">
                  <BookOpen className="w-4 h-4 text-cyan-400" />
                  <span>Historical Significance</span>
                </div>
                <p className="text-xs text-slate-300 leading-relaxed bg-slate-900/60 p-3.5 rounded-xl border border-slate-800/80">
                  {result.historical_background}
                </p>
              </div>

              {/* Architectural Notes */}
              <div className="space-y-1.5">
                <div className="flex items-center gap-1.5 text-xs font-bold text-slate-200">
                  <Building2 className="w-4 h-4 text-teal-400" />
                  <span>Architectural Details</span>
                </div>
                <p className="text-xs text-slate-300 leading-relaxed bg-slate-900/60 p-3.5 rounded-xl border border-slate-800/80">
                  {result.architectural_characteristics}
                </p>
              </div>

              {/* Practical Visiting Tips */}
              <div className="space-y-1.5">
                <div className="flex items-center gap-1.5 text-xs font-bold text-slate-200">
                  <Lightbulb className="w-4 h-4 text-amber-400" />
                  <span>Visiting Advice</span>
                </div>
                <p className="text-xs text-slate-300 leading-relaxed bg-slate-900/60 p-3.5 rounded-xl border border-slate-800/80">
                  {result.visiting_tips}
                </p>
              </div>

            </div>
          ) : (
            <div className="h-full min-h-[300px] glass-panel rounded-2xl border border-slate-800 flex flex-col items-center justify-center p-8 text-center text-slate-400">
              <Camera className="w-10 h-10 text-slate-600 mb-3" />
              <div className="text-sm font-semibold text-slate-300">Ready to Scan</div>
              <p className="text-xs text-slate-500 max-w-xs mt-1">
                Upload a photo or select one of the test samples to view AI landmark recognition.
              </p>
            </div>
          )}
        </div>

      </div>

    </div>
  );
};

export default LandmarkScanner;

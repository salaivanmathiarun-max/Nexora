import React, { useState, useRef, useEffect } from 'react';
import api from '../../services/api';
import {
  Languages,
  Volume2,
  ArrowRightLeft,
  Sparkles,
  Mic,
  Square,
  Check,
  Copy,
  Camera,
  Upload,
  FileText,
  X,
  Loader2,
  Info,
  Radio,
  FileAudio,
  CheckCircle2,
  AlertCircle,
  RefreshCw,
  Edit3
} from 'lucide-react';

const TranslatorCard = () => {
  const [activeMode, setActiveMode] = useState('text'); // 'text' | 'camera'

  // Text & Voice state
  const [inputText, setInputText] = useState('Can you please tell me the historical significance of the azure tilework in Samarkand, and where I can find authentic local bread?');
  const [sourceLang, setSourceLang] = useState('auto');
  const [targetLang, setTargetLang] = useState('uz');
  const [translationResult, setTranslationResult] = useState(null);
  const [translating, setTranslating] = useState(false);
  const [copied, setCopied] = useState(false);
  const [errorMsg, setErrorMsg] = useState(null);

  // Whisper Speech-to-Text State
  const [isRecording, setIsRecording] = useState(false);
  const [recordingSeconds, setRecordingSeconds] = useState(0);
  const [isTranscribing, setIsTranscribing] = useState(false);
  const [whisperTranscript, setWhisperTranscript] = useState(null);
  const [engineStatus, setEngineStatus] = useState(null);

  // Camera / OCR translation state
  const [cameraImage, setCameraImage] = useState(null);
  const [ocrTranslating, setOcrTranslating] = useState(false);
  const [ocrResult, setOcrResult] = useState(null);

  // Refs
  const fileInputRef = useRef(null);
  const audioFileInputRef = useRef(null);
  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);
  const timerIntervalRef = useRef(null);

  // Supported Multilingual Catalog
  const languages = [
    { code: 'uz', name: "Uzbek (O'zbekcha)", script: 'Latin' },
    { code: 'ru', name: 'Russian (Русский)', script: 'Cyrillic' },
    { code: 'en', name: 'English', script: 'Latin' },
    { code: 'hi', name: 'Hindi (हिन्दी)', script: 'Devanagari' },
    { code: 'ar', name: 'Arabic (العربية)', script: 'Arabic' },
    { code: 'zh', name: 'Chinese (简体中文)', script: 'Hanzi' },
    { code: 'fr', name: 'French (Français)', script: 'Latin' },
    { code: 'de', name: 'German (Deutsch)', script: 'Latin' },
    { code: 'es', name: 'Spanish (Español)', script: 'Latin' },
    { code: 'tr', name: 'Turkish (Türkçe)', script: 'Latin' },
    { code: 'fa', name: 'Persian / Tajik (فارسی)', script: 'Perso-Arabic' },
    { code: 'ja', name: 'Japanese (日本語)', script: 'Kanji/Kana' }
  ];

  // Fetch engine readiness on load
  useEffect(() => {
    fetchStatus();
    return () => {
      if (timerIntervalRef.current) clearInterval(timerIntervalRef.current);
      stopMediaStream();
    };
  }, []);

  const fetchStatus = async () => {
    try {
      const res = await api.getTranslationStatus();
      setEngineStatus(res);
    } catch (err) {
      console.warn('Could not fetch translation service status:', err);
    }
  };

  const stopMediaStream = () => {
    if (mediaRecorderRef.current && mediaRecorderRef.current.stream) {
      mediaRecorderRef.current.stream.getTracks().forEach(track => track.stop());
    }
  };

  // =========================================================================
  // 1. DYNAMIC TEXT TRANSLATION (GEMINI API)
  // =========================================================================
  const handleTranslate = async (overrideText = null) => {
    const textToTranslate = overrideText !== null ? overrideText : inputText;
    if (!textToTranslate || !textToTranslate.trim()) {
      setErrorMsg('Please enter, speak, or upload text to translate.');
      return;
    }

    setErrorMsg(null);
    setTranslating(true);
    try {
      const res = await api.translate(textToTranslate.trim(), sourceLang, targetLang);
      setTranslationResult(res);
      // Auto-sync source language selector if auto-detected
      if (sourceLang === 'auto' && res.source_language) {
        // Keep auto in dropdown but inform user via detection badge
      }
    } catch (err) {
      console.error(err);
      const detail = err.response?.data?.detail || err.message || 'Translation request failed.';
      setErrorMsg(`Translation failed: ${detail}`);
    } finally {
      setTranslating(false);
    }
  };

  // =========================================================================
  // 2. MULTILINGUAL SPEECH TRANSCRIPTION (OPENAI WHISPER)
  // =========================================================================
  const startRecording = async () => {
    setErrorMsg(null);
    audioChunksRef.current = [];

    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
      setErrorMsg('Audio recording is not supported in this browser. Please upload an audio file or type text.');
      return;
    }

    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        audio: {
          channelCount: 1,
          sampleRate: 16000,
          echoCancellation: true,
          noiseSuppression: true
        }
      });

      const mimeType = MediaRecorder.isTypeSupported('audio/webm;codecs=opus')
        ? 'audio/webm;codecs=opus'
        : (MediaRecorder.isTypeSupported('audio/webm') ? 'audio/webm' : 'audio/mp4');

      const mediaRecorder = new MediaRecorder(stream, { mimeType });
      mediaRecorderRef.current = mediaRecorder;

      mediaRecorder.ondataavailable = (event) => {
        if (event.data && event.data.size > 0) {
          audioChunksRef.current.push(event.data);
        }
      };

      mediaRecorder.onstop = () => {
        const audioBlob = new Blob(audioChunksRef.current, { type: mimeType });
        stopMediaStream();
        processAudioBlob(audioBlob, `speech_${Date.now()}.webm`);
      };

      mediaRecorder.start(250);
      setIsRecording(true);
      setRecordingSeconds(0);

      timerIntervalRef.current = setInterval(() => {
        setRecordingSeconds(prev => prev + 1);
      }, 1000);

    } catch (err) {
      console.error('Microphone access error:', err);
      if (err.name === 'NotAllowedError' || err.name === 'PermissionDeniedError') {
        setErrorMsg('Microphone access was denied. Please allow microphone permissions in your browser or upload an audio file.');
      } else {
        setErrorMsg(`Unable to start microphone: ${err.message}`);
      }
      setIsRecording(false);
    }
  };

  const stopRecording = () => {
    if (timerIntervalRef.current) {
      clearInterval(timerIntervalRef.current);
      timerIntervalRef.current = null;
    }
    if (mediaRecorderRef.current && mediaRecorderRef.current.state !== 'inactive') {
      mediaRecorderRef.current.stop();
    }
    setIsRecording(false);
  };

  const processAudioBlob = async (blob, filename) => {
    if (blob.size < 100) {
      setErrorMsg('Recording was too short. Please speak clearly into your microphone.');
      return;
    }

    setIsTranscribing(true);
    setErrorMsg(null);

    const reader = new FileReader();
    reader.onloadend = async () => {
      try {
        const base64Data = reader.result;
        // Call backend Whisper STT
        const sttRes = await api.transcribeAudio(base64Data, filename, sourceLang);

        if (sttRes && sttRes.text) {
          setWhisperTranscript(sttRes);
          setInputText(sttRes.text);
          if (sttRes.language && sttRes.language !== 'unknown') {
            // If user had set 'auto', reflect detected spoken language
            setSourceLang(sttRes.language);
          }
          // Automatically translate transcription with Gemini
          await handleTranslate(sttRes.text);
        } else {
          setErrorMsg('No speech was detected in the audio. Please try speaking again.');
        }
      } catch (err) {
        console.error('Whisper transcription error:', err);
        const detail = err.response?.data?.detail || err.message || 'Speech recognition failed.';
        setErrorMsg(`Whisper Speech Recognition error: ${detail}`);
      } finally {
        setIsTranscribing(false);
      }
    };
    reader.readAsDataURL(blob);
  };

  // Upload Pre-recorded Audio File (.mp3, .wav, .m4a, .webm, .ogg)
  const handleAudioFileUpload = async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setIsTranscribing(true);
    setErrorMsg(null);

    try {
      const res = await api.transcribeAudioFile(file, sourceLang);
      if (res && res.text) {
        setWhisperTranscript(res);
        setInputText(res.text);
        if (res.language && res.language !== 'unknown') {
          setSourceLang(res.language);
        }
        await handleTranslate(res.text);
      } else {
        setErrorMsg('Could not transcribe audio file. Please ensure speech is clearly audible.');
      }
    } catch (err) {
      console.error(err);
      const detail = err.response?.data?.detail || err.message || 'Failed to process audio file.';
      setErrorMsg(`Audio file transcription failed: ${detail}`);
    } finally {
      setIsTranscribing(false);
      if (audioFileInputRef.current) audioFileInputRef.current.value = '';
    }
  };

  // =========================================================================
  // 3. CAMERA / SIGNBOARD OCR TRANSLATION (GEMINI VISION)
  // =========================================================================
  const handleImageUpload = (e) => {
    const file = e.target.files?.[0];
    if (file) {
      const reader = new FileReader();
      reader.onloadend = () => {
        setCameraImage(reader.result);
        runImageTranslation(reader.result);
      };
      reader.readAsDataURL(file);
    }
  };

  const runImageTranslation = async (imgData) => {
    setOcrTranslating(true);
    setOcrResult(null);
    setErrorMsg(null);
    try {
      const res = await api.translateImage(imgData, targetLang);
      setOcrResult(res);
    } catch (err) {
      console.error(err);
      const detail = err.response?.data?.detail || 'Camera sign translation failed.';
      setErrorMsg(`Camera OCR error: ${detail}`);
    } finally {
      setOcrTranslating(false);
    }
  };

  // =========================================================================
  // 4. UTILITIES (SWAP, PLAYBACK, COPY)
  // =========================================================================
  const handleSwap = () => {
    const newSource = targetLang;
    const newTarget = sourceLang === 'auto' ? (translationResult?.source_language || 'en') : sourceLang;

    setSourceLang(newSource);
    setTargetLang(newTarget);

    if (translationResult?.translated_text) {
      const prevTranslated = translationResult.translated_text;
      setInputText(prevTranslated);
      setTranslationResult(null);
      setWhisperTranscript(null);
    }
  };

  const handleSpeak = (text, langCode) => {
    if (!('speechSynthesis' in window)) {
      setErrorMsg('Speech synthesis (audio playback) is not supported in this browser.');
      return;
    }
    window.speechSynthesis.cancel();
    const utterance = new SpeechSynthesisUtterance(text);
    // Language mapping for browser TTS
    const langMap = {
      uz: 'ru-RU', // Fallback for browsers lacking native uz-UZ voice
      ru: 'ru-RU',
      en: 'en-US',
      hi: 'hi-IN',
      ar: 'ar-SA',
      zh: 'zh-CN',
      fr: 'fr-FR',
      de: 'de-DE',
      es: 'es-ES',
      tr: 'tr-TR',
      ja: 'ja-JP'
    };
    utterance.lang = langMap[langCode] || langCode;
    utterance.rate = 0.95;
    window.speechSynthesis.speak(utterance);
  };

  const handleCopy = (text) => {
    navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const formatTimer = (secs) => {
    const m = Math.floor(secs / 60).toString().padStart(2, '0');
    const s = (secs % 60).toString().padStart(2, '0');
    return `${m}:${s}`;
  };

  return (
    <div className="w-full space-y-6 animate-fade-in">

      {/* Header Panel with Research Paper Citation & Pipeline Status */}
      <div className="glass-panel rounded-2xl p-6 border border-slate-800">
        <div className="flex flex-wrap items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <div className="p-2.5 rounded-xl bg-purple-500/10 text-purple-400 border border-purple-500/20">
              <Languages className="w-6 h-6" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h2 className="text-lg font-bold text-white font-['Outfit']">
                  Translation Assistance & Voice Intelligence
                </h2>
                <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-purple-500/20 text-purple-300 border border-purple-500/30">
                  Paper Section 3.8
                </span>
              </div>
              <p className="text-xs text-slate-400">
                Multilingual communication pipeline: <strong>OpenAI Whisper</strong> (Speech-to-Text) + <strong>Gemini AI</strong> (Context-Aware Translation)
              </p>
            </div>
          </div>

          {/* Mode Switcher Tabs */}
          <div className="flex items-center gap-1 bg-slate-900 p-1 rounded-xl border border-slate-800">
            <button
              onClick={() => setActiveMode('text')}
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${activeMode === 'text'
                  ? 'bg-purple-500/20 text-purple-300 border border-purple-500/30'
                  : 'text-slate-400 hover:text-white'
                }`}
            >
              <FileText className="w-3.5 h-3.5" />
              <span>Voice & Text Translation</span>
            </button>
            <button
              onClick={() => setActiveMode('camera')}
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${activeMode === 'camera'
                  ? 'bg-purple-500/20 text-purple-300 border border-purple-500/30'
                  : 'text-slate-400 hover:text-white'
                }`}
            >
              <Camera className="w-3.5 h-3.5" />
              <span>Camera Signboard OCR</span>
            </button>
          </div>
        </div>

        {/* Engine Status Indicators */}
        <div className="mt-4 pt-3 border-t border-slate-800/80 flex flex-wrap items-center justify-between gap-3 text-[11px]">
          <div className="flex items-center gap-3">
            <div className="flex items-center gap-1.5 text-slate-300">
              <Radio className={`w-3.5 h-3.5 ${engineStatus?.whisper?.available ? 'text-emerald-400' : 'text-amber-400'}`} />
              <span>Whisper STT:</span>
              <strong className="text-slate-200">
                {engineStatus?.whisper?.engine === 'openai_whisper_api' ? 'OpenAI Whisper API' : 'Local Whisper Engine'}
              </strong>
            </div>

            <div className="flex items-center gap-1.5 text-slate-300">
              <Sparkles className="w-3.5 h-3.5 text-purple-400" />
              <span>Translation Engine:</span>
              <strong className="text-slate-200">
                Gemini AI ({engineStatus?.gemini?.active_model || 'gemini-3.5-flash'})
              </strong>
            </div>
          </div>

          <div className="text-slate-400">
            Silk Road Hub: <span className="text-teal-300 font-medium">Samarkand Multilingual Bridge (Uzbek • Russian • English)</span>
          </div>
        </div>

        {/* Error Notification Banner */}
        {errorMsg && (
          <div className="mt-4 p-3 rounded-xl bg-rose-500/15 border border-rose-500/30 text-rose-300 text-xs flex items-center justify-between animate-fade-in">
            <div className="flex items-center gap-2">
              <AlertCircle className="w-4 h-4 shrink-0 text-rose-400" />
              <span>{errorMsg}</span>
            </div>
            <button onClick={() => setErrorMsg(null)} className="hover:text-white ml-2">
              <X className="w-4 h-4" />
            </button>
          </div>
        )}
      </div>

      {activeMode === 'text' ? (
        /* ================= MODE 1: DYNAMIC MULTILINGUAL VOICE & TEXT TRANSLATION ================= */
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">

          {/* Source Input Column */}
          <div className="glass-panel rounded-2xl p-5 border border-slate-800 flex flex-col justify-between space-y-4">

            {/* Source Header Controls */}
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <span className="text-xs font-bold text-slate-400 uppercase tracking-wider">Source Language</span>
                {translationResult?.source_language_name && (
                  <span className="text-[10px] px-2 py-0.5 rounded-md bg-teal-500/15 text-teal-300 border border-teal-500/30 font-medium">
                    Detected: {translationResult.source_language_name} ({translationResult.source_language})
                  </span>
                )}
              </div>

              <select
                value={sourceLang}
                onChange={(e) => setSourceLang(e.target.value)}
                className="bg-slate-900 text-xs text-white border border-slate-700 rounded-lg px-2.5 py-1.5 focus:outline-none focus:border-purple-500 cursor-pointer"
              >
                <option value="auto">✨ Auto Detect (AI)</option>
                {languages.map((l) => (
                  <option key={l.code} value={l.code}>{l.name} — {l.script}</option>
                ))}
              </select>
            </div>

            {/* Source Text Area */}
            <div className="relative">
              <textarea
                value={inputText}
                onChange={(e) => setInputText(e.target.value)}
                rows={6}
                placeholder="Enter any sentence, question, paragraph, or speak in Uzbek, Russian, English, or any language..."
                className="w-full bg-slate-900/90 border border-slate-700/80 rounded-xl p-3.5 text-xs sm:text-sm text-white placeholder-slate-500 focus:outline-none focus:border-purple-500 transition-all leading-relaxed"
              />
              <div className="flex items-center justify-between text-[10px] text-slate-500 mt-1">
                <span>Supports arbitrary text, directions, questions, and non-travel vocabulary</span>
                <span>{inputText.length} characters</span>
              </div>
            </div>

            {/* Whisper Transcription Separate Inspector */}
            {whisperTranscript && (
              <div className="p-3.5 rounded-xl bg-purple-500/10 border border-purple-500/25 text-xs space-y-1.5 animate-fade-in">
                <div className="flex items-center justify-between">
                  <span className="font-bold text-purple-400 text-[10px] uppercase tracking-wider flex items-center gap-1.5">
                    <Radio className="w-3 h-3 text-purple-400" />
                    OpenAI Whisper Speech Transcription:
                  </span>
                  <div className="flex items-center gap-1.5 text-[10px] text-slate-400">
                    <span className="px-1.5 py-0.5 rounded bg-purple-900/50 text-purple-300 border border-purple-700/50">
                      Lang: {whisperTranscript.language_name || whisperTranscript.language}
                    </span>
                    {whisperTranscript.duration_seconds > 0 && (
                      <span>{whisperTranscript.duration_seconds}s</span>
                    )}
                  </div>
                </div>
                <div className="text-slate-200 italic font-medium bg-slate-950/40 p-2 rounded-lg border border-purple-500/15">
                  "{whisperTranscript.text}"
                </div>
                <div className="text-[10px] text-slate-400 flex items-center gap-1">
                  <Edit3 className="w-3 h-3 text-purple-400" />
                  <span>You can edit the text in the box above before translating if desired.</span>
                </div>
              </div>
            )}

            {/* Source Footer Actions: Voice Recording, Audio Upload, & Translate */}
            <div className="flex flex-wrap items-center justify-between gap-2 pt-3 border-t border-slate-800">

              <div className="flex items-center gap-2">
                {/* Whisper Microphone Recording Button */}
                <button
                  type="button"
                  onClick={isRecording ? stopRecording : startRecording}
                  disabled={isTranscribing}
                  className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${isRecording
                      ? 'bg-rose-500 hover:bg-rose-600 text-white animate-pulse shadow-md shadow-rose-500/30'
                      : 'bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700'
                    }`}
                  title={isRecording ? 'Click to finish recording speech' : 'Record voice for Whisper transcription'}
                >
                  {isRecording ? (
                    <>
                      <Square className="w-3.5 h-3.5 fill-current" />
                      <span>Stop ({formatTimer(recordingSeconds)})</span>
                    </>
                  ) : (
                    <>
                      <Mic className="w-3.5 h-3.5 text-purple-400" />
                      <span>Record Voice</span>
                    </>
                  )}
                </button>

                {/* Audio File Upload Button */}
                <button
                  type="button"
                  onClick={() => audioFileInputRef.current?.click()}
                  disabled={isRecording || isTranscribing}
                  className="flex items-center gap-1 px-2.5 py-1.5 rounded-lg text-xs bg-slate-800/80 hover:bg-slate-700 text-slate-300 border border-slate-700 transition-colors"
                  title="Upload audio file (.webm, .wav, .mp3, .m4a)"
                >
                  <FileAudio className="w-3.5 h-3.5 text-teal-400" />
                  <span>Upload Audio</span>
                </button>
                <input
                  type="file"
                  ref={audioFileInputRef}
                  onChange={handleAudioFileUpload}
                  accept="audio/*,.webm,.wav,.mp3,.m4a,.ogg,.flac"
                  className="hidden"
                />

                {inputText && (
                  <button
                    type="button"
                    onClick={() => { setInputText(''); setWhisperTranscript(null); setTranslationResult(null); }}
                    className="text-xs text-slate-500 hover:text-slate-300 px-1"
                  >
                    Clear
                  </button>
                )}
              </div>

              {/* Translate Action Button */}
              <button
                type="button"
                onClick={() => handleTranslate()}
                disabled={translating || isRecording || isTranscribing}
                className="flex items-center gap-2 px-5 py-2 rounded-xl bg-gradient-to-r from-purple-500 to-indigo-500 hover:from-purple-400 hover:to-indigo-400 text-white font-bold text-xs shadow-lg shadow-purple-500/20 transition-all hover:scale-[1.02] active:scale-[0.98] disabled:opacity-50"
              >
                {translating ? (
                  <>
                    <Loader2 className="w-4 h-4 animate-spin" />
                    <span>Translating via Gemini...</span>
                  </>
                ) : isTranscribing ? (
                  <>
                    <Loader2 className="w-4 h-4 animate-spin text-purple-200" />
                    <span>Whisper Transcribing...</span>
                  </>
                ) : (
                  <>
                    <Languages className="w-4 h-4" />
                    <span>Translate Text</span>
                  </>
                )}
              </button>

            </div>

          </div>

          {/* Target Output Column */}
          <div className="glass-panel rounded-2xl p-5 border border-slate-800 flex flex-col justify-between space-y-4 bg-slate-900/50">

            {/* Target Header Controls */}
            <div className="flex items-center justify-between">
              <span className="text-xs font-bold text-purple-400 uppercase tracking-wider">Target Language</span>

              <div className="flex items-center gap-2">
                <button
                  type="button"
                  onClick={handleSwap}
                  className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition-colors flex items-center gap-1 text-xs"
                  title="Swap source and target languages"
                >
                  <ArrowRightLeft className="w-3.5 h-3.5" />
                  <span className="text-[10px] hidden sm:inline">Swap</span>
                </button>

                <select
                  value={targetLang}
                  onChange={(e) => {
                    const newTarget = e.target.value;
                    setTargetLang(newTarget);
                    if (inputText.trim()) {
                      api.translate(inputText.trim(), sourceLang, newTarget)
                        .then(res => setTranslationResult(res))
                        .catch(err => console.error(err));
                    }
                  }}
                  className="bg-slate-900 text-xs text-white border border-slate-700 rounded-lg px-2.5 py-1.5 focus:outline-none focus:border-purple-500 cursor-pointer"
                >
                  {languages.map((l) => (
                    <option key={l.code} value={l.code}>{l.name} — {l.script}</option>
                  ))}
                </select>
              </div>
            </div>

            {/* Translation Output Box */}
            <div className="min-h-[180px] p-4 rounded-xl bg-slate-900/90 border border-slate-800 flex flex-col justify-between space-y-3">
              {translating ? (
                <div className="flex flex-col items-center justify-center py-12 space-y-2 text-slate-400">
                  <Loader2 className="w-7 h-7 text-purple-400 animate-spin" />
                  <span className="text-xs font-medium">Translating dynamically with Gemini AI...</span>
                  <span className="text-[10px] text-slate-500">Preserving grammatical nuance & local cultural context</span>
                </div>
              ) : isTranscribing ? (
                <div className="flex flex-col items-center justify-center py-12 space-y-2 text-purple-300">
                  <Radio className="w-7 h-7 text-purple-400 animate-pulse" />
                  <span className="text-xs font-medium">Transcribing speech with OpenAI Whisper...</span>
                  <span className="text-[10px] text-slate-400">Detecting spoken language automatically</span>
                </div>
              ) : translationResult ? (
                <div className="space-y-3.5">
                  <div className="text-base sm:text-lg font-semibold text-teal-300 font-['Outfit'] leading-relaxed">
                    {translationResult.translated_text}
                  </div>

                  {translationResult.phonetic_pronunciation && (
                    <div className="text-xs text-slate-300 italic bg-slate-950/70 p-2.5 rounded-lg border border-slate-800/80">
                      <span className="font-semibold text-slate-400 not-italic block text-[10px] uppercase mb-0.5 tracking-wider">
                        Phonetic Pronunciation:
                      </span>
                      {translationResult.phonetic_pronunciation}
                    </div>
                  )}

                  {translationResult.context_notes && (
                    <div className="text-[11px] text-purple-300/90 flex items-start gap-1.5 pt-1 bg-purple-950/20 p-2 rounded-lg border border-purple-500/20">
                      <Sparkles className="w-3.5 h-3.5 text-purple-400 shrink-0 mt-0.5" />
                      <span>{translationResult.context_notes}</span>
                    </div>
                  )}
                </div>
              ) : (
                <div className="text-slate-500 text-xs flex flex-col items-center justify-center py-12 space-y-1">
                  <span>Enter or record speech on the left, then click Translate to view output.</span>
                  <span className="text-[10px] text-slate-600">Supports bidirectional translations between Uzbek, Russian, English, Hindi, Arabic, and more.</span>
                </div>
              )}

              {/* Action Buttons: Speak Aloud & Copy */}
              {translationResult && (
                <div className="flex items-center justify-between pt-3 border-t border-slate-800/80 text-xs">
                  <div className="text-[10px] text-slate-400">
                    Tone: <strong className="text-slate-200 capitalize">{translationResult.detected_tone || 'polite'}</strong>
                  </div>

                  <div className="flex items-center gap-1.5">
                    <button
                      type="button"
                      onClick={() => handleSpeak(translationResult.translated_text, targetLang)}
                      className="flex items-center gap-1 px-2.5 py-1 rounded-lg text-slate-300 hover:text-teal-300 hover:bg-slate-800 transition-colors"
                      title="Listen to pronunciation via speech synthesis"
                    >
                      <Volume2 className="w-3.5 h-3.5" />
                      <span>Listen</span>
                    </button>

                    <button
                      type="button"
                      onClick={() => handleCopy(translationResult.translated_text)}
                      className="flex items-center gap-1 px-2.5 py-1 rounded-lg text-slate-300 hover:text-teal-300 hover:bg-slate-800 transition-colors"
                      title="Copy translated text"
                    >
                      {copied ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
                      <span>{copied ? 'Copied' : 'Copy'}</span>
                    </button>
                  </div>
                </div>
              )}
            </div>

            <div className="text-[11px] text-slate-400 flex items-center gap-1.5">
              <Info className="w-3.5 h-3.5 text-purple-400 shrink-0" />
              <span>Full semantic context, scripts (Latin, Cyrillic, Arabic, Devanagari), and proper nouns preserved.</span>
            </div>

          </div>

        </div>
      ) : (
        /* ================= MODE 2: CAMERA / SIGNBOARD OCR TRANSLATION ================= */
        <div className="glass-panel rounded-2xl p-6 border border-slate-800 space-y-6">
          <div className="flex items-center justify-between flex-wrap gap-4">
            <div>
              <h3 className="text-sm font-bold text-white font-['Outfit']">
                Camera Signboard & Menu OCR Translation (Section 3.8)
              </h3>
              <p className="text-xs text-slate-400">
                Upload or capture a photo of written signs, directional plaques, menus, or monuments in Samarkand
              </p>
            </div>

            <div className="flex items-center gap-2">
              <span className="text-xs text-slate-400">Translate to:</span>
              <select
                value={targetLang}
                onChange={(e) => {
                  const newT = e.target.value;
                  setTargetLang(newT);
                  if (cameraImage) runImageTranslation(cameraImage);
                }}
                className="bg-slate-900 text-xs text-white border border-slate-700 rounded-lg px-2.5 py-1 cursor-pointer"
              >
                {languages.map((l) => (
                  <option key={l.code} value={l.code}>{l.name}</option>
                ))}
              </select>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">

            {/* Image Upload Box */}
            <div
              onClick={() => fileInputRef.current?.click()}
              className="w-full h-64 rounded-xl border-2 border-dashed border-slate-700 hover:border-purple-500/60 bg-slate-900/60 flex flex-col items-center justify-center cursor-pointer p-4 transition-all overflow-hidden relative group"
            >
              {cameraImage ? (
                <div className="relative w-full h-full">
                  <img src={cameraImage} alt="Signboard" className="w-full h-full object-contain rounded-lg" />
                  <div className="absolute bottom-2 right-2 px-2 py-1 bg-slate-900/90 text-[10px] text-slate-300 rounded border border-slate-700">
                    Click to change photo
                  </div>
                </div>
              ) : (
                <div className="text-center space-y-2">
                  <div className="w-12 h-12 rounded-xl bg-slate-800 text-purple-400 flex items-center justify-center mx-auto group-hover:scale-110 transition-transform">
                    <Camera className="w-6 h-6" />
                  </div>
                  <div className="text-sm font-semibold text-white">Click or Drop Photo of Sign/Menu</div>
                  <div className="text-xs text-slate-400">Extracts Cyrillic, Latin, or Arabic scripts automatically via Gemini Vision</div>
                </div>
              )}
              <input
                type="file"
                ref={fileInputRef}
                onChange={handleImageUpload}
                accept="image/*"
                className="hidden"
              />
            </div>

            {/* OCR Translation Result */}
            <div className="p-5 rounded-xl bg-slate-900/90 border border-slate-800 flex flex-col justify-between">
              {ocrTranslating ? (
                <div className="flex flex-col items-center justify-center h-full space-y-2 text-slate-400 py-16">
                  <Loader2 className="w-6 h-6 text-purple-400 animate-spin" />
                  <span className="text-xs">Extracting text and translating via Gemini Vision OCR...</span>
                </div>
              ) : ocrResult ? (
                <div className="space-y-4">
                  {ocrResult.is_text_found ? (
                    <>
                      <div>
                        <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400 block mb-1">
                          Detected Text ({ocrResult.detected_script_or_language || 'Extracted Script'}):
                        </span>
                        <div className="text-xs text-slate-300 font-mono bg-slate-950 p-2.5 rounded-lg border border-slate-800">
                          {ocrResult.extracted_text}
                        </div>
                      </div>

                      <div>
                        <span className="text-[10px] font-bold uppercase tracking-wider text-teal-400 block mb-1">
                          Translated Meaning:
                        </span>
                        <div className="text-sm font-bold text-teal-300 font-['Outfit'] bg-teal-500/10 p-3 rounded-lg border border-teal-500/20">
                          {ocrResult.translated_text}
                        </div>
                      </div>

                      {ocrResult.phonetic_pronunciation && (
                        <div className="text-xs text-slate-400 italic bg-slate-950/60 p-2 rounded">
                          <span className="font-semibold text-slate-300 not-italic block text-[10px] uppercase mb-0.5">
                            Phonetic Reading:
                          </span>
                          {ocrResult.phonetic_pronunciation}
                        </div>
                      )}

                      {ocrResult.context_notes && (
                        <div className="text-xs text-slate-400">
                          Sign Category: <strong className="text-slate-200">{ocrResult.context_notes}</strong>
                        </div>
                      )}
                    </>
                  ) : (
                    <div className="text-center py-10 space-y-1 text-slate-400">
                      <div className="text-sm font-semibold text-amber-300">No Inscription Detected</div>
                      <p className="text-xs text-slate-500">
                        Please upload a clearer image focusing on the written text or signboard.
                      </p>
                    </div>
                  )}
                </div>
              ) : (
                <div className="text-center py-16 text-xs text-slate-500">
                  Upload an image of a signboard, menu, or plaque to view OCR translation.
                </div>
              )}
            </div>

          </div>
        </div>
      )}

    </div>
  );
};

export default TranslatorCard;

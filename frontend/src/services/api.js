import axios from 'axios';

const API_BASE = 'http://127.0.0.1:8000/api';

const client = axios.create({
  baseURL: API_BASE,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const api = {
  // Profile
  getProfile: () => client.get('/profile').then(r => r.data),
  updateProfile: (data) => client.post('/profile', data).then(r => r.data),

  // Multimodal Query
  processQuery: (data) => client.post('/query/process', data).then(r => r.data),

  // Context & Real-Time Environment
  getCurrentContext: (city = 'Samarkand') => client.get(`/context/current?city=${encodeURIComponent(city)}`).then(r => r.data),
  simulateContext: (data) => client.post('/context/simulate', data).then(r => r.data),
  resetContext: () => client.post('/context/reset').then(r => r.data),

  // Itinerary & Dynamic Adaptation
  generateItinerary: (payload) => client.post('/itinerary/generate', payload).then(r => r.data),
  getItinerary: (tripId) => client.get(`/itinerary/${tripId}`).then(r => r.data),
  simulateDisruption: (tripId, disruptionType) => client.post('/itinerary/simulate-disruption', {
    trip_id: tripId,
    disruption_type: disruptionType
  }).then(r => r.data),
  confirmAdaptation: (adaptationId, accept) => client.post(`/itinerary/confirm-adaptation?adaptation_id=${adaptationId}&accept=${accept}`).then(r => r.data),

  // Section 3.7: Landmark Recognition & Benchmarks
  recognizeLandmark: (imageBase64, contextNotes = '') => client.post('/landmark/recognize', {
    image_base64: imageBase64,
    context_notes: contextNotes
  }).then(r => r.data),
  classifyLandmark: (imageBase64) => client.post('/landmark/classify', {
    image_base64: imageBase64
  }).then(r => r.data),
  getLandmarkClasses: () => client.get('/landmark/classes').then(r => r.data),
  getBenchmarks: () => client.get('/landmark/benchmarks').then(r => r.data),

  // Travel Services
  getTravelServices: (city = 'Samarkand') => client.get(`/services/nearby?city=${encodeURIComponent(city)}`).then(r => r.data),

  // Section 3.8: Translation Assistance
  getTranslationStatus: () => client.get('/translate/status').then(r => r.data),
  translate: (text, source = 'auto', target = 'uz') => client.post('/translate', {
    text,
    source_language: source,
    target_language: target
  }).then(r => r.data),
  transcribeAudio: (audioBase64, filename = 'recording.webm', sourceLang = 'auto') => client.post('/translate/transcribe', {
    audio_base64: audioBase64,
    filename,
    source_language: sourceLang
  }).then(r => r.data),
  translateVoice: (audioBase64, filename = 'recording.webm', sourceLang = 'auto', targetLang = 'uz') => client.post('/translate/voice', {
    audio_base64: audioBase64,
    filename,
    source_language: sourceLang,
    target_language: targetLang
  }).then(r => r.data),
  transcribeAudioFile: (file, sourceLang = 'auto') => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('source_language', sourceLang);
    return client.post('/translate/transcribe-file', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    }).then(r => r.data);
  },
  translateImage: (imageBase64, target = 'en') => client.post('/translate/image', {
    image_base64: imageBase64,
    target_language: target
  }).then(r => r.data),

  // AI Memory Book
  generateMemoryBook: (tripId, userNotes = '', photos = []) => client.post('/memory/generate', {
    trip_id: tripId,
    user_notes: userNotes,
    uploaded_photos: photos
  }).then(r => r.data),
  getMemoryBook: (tripId) => client.get(`/memory/${tripId}`).then(r => r.data),
};

export default api;

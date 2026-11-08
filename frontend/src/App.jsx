
import React from 'react';
import { AppProvider, useApp } from './context/AppContext';
import Navbar from './components/common/Navbar';
import ContextBar from './components/common/ContextBar';
import DemoControlDrawer from './components/common/DemoControlDrawer';
import ProfileModal from './components/profile/ProfileModal';
import MultimodalInput from './components/query/MultimodalInput';
import ItineraryTimeline from './components/itinerary/ItineraryTimeline';
import XAIModal from './components/itinerary/XAIModal';
import LandmarkScanner from './components/landmark/LandmarkScanner';
import BenchmarkModal from './components/landmark/BenchmarkModal';
import TravelServicesGrid from './components/services/TravelServicesGrid';
import TranslatorCard from './components/translation/TranslatorCard';
import MemoryBookView from './components/memory/MemoryBookView';
import { AlertCircle, CheckCircle, Info } from 'lucide-react';

const MainLayout = () => {
  const { activeTab, toastMessage } = useApp();

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col relative selection:bg-teal-500 selection:text-slate-950">

      {/* Toast Notification */}
      {toastMessage && (
        <div className="fixed top-20 right-4 z-50 flex items-center gap-2 px-4 py-3 rounded-xl bg-slate-900 border border-slate-700 shadow-2xl text-xs font-semibold text-white animate-fade-in backdrop-blur-md">
          {toastMessage.type === 'success' ? (
            <CheckCircle className="w-4 h-4 text-emerald-400" />
          ) : toastMessage.type === 'warning' ? (
            <AlertCircle className="w-4 h-4 text-amber-400" />
          ) : (
            <Info className="w-4 h-4 text-teal-400" />
          )}
          <span>{toastMessage.message}</span>
        </div>
      )}

      {/* Navigation */}
      <Navbar />

      {/* Real-time Context Bar C = [L, T, W, Tr, Cr, O, P] */}
      <ContextBar />

      {/* Main Container */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">

        {activeTab === 'itinerary' && (
          <div className="space-y-8">
            <MultimodalInput />
            <ItineraryTimeline />
          </div>
        )}

        {activeTab === 'landmark' && <LandmarkScanner />}

        {activeTab === 'services' && <TravelServicesGrid />}

        {activeTab === 'translate' && <TranslatorCard />}

        {activeTab === 'memory' && <MemoryBookView />}

        {activeTab === 'benchmarks' && <BenchmarkModal />}

      </main>

      {/* Footer */}
      <footer className="w-full border-t border-slate-900 py-6 px-4 text-center text-xs text-slate-500 bg-slate-950/60">
        <div className="max-w-7xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-2">
          <span>NEXORA © 2026 • Multimodal & Explainable Smart Tourism Framework</span>
          <span className="font-mono text-[11px] text-slate-600">
            Based on Research Paper by Rachna et al. • Powered by Gemini Vision
          </span>
        </div>
      </footer>

      {/* Modals & Overlays */}
      <ProfileModal />
      <DemoControlDrawer />
      <XAIModal />

    </div>
  );
};

export default function App() {
  return (
    <AppProvider>
      <MainLayout />
    </AppProvider>
  );
}

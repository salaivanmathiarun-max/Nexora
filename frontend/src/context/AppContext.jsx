import React, { createContext, useContext, useState, useEffect } from 'react';
import api from '../services/api';

const AppContext = createContext();

export const AppProvider = ({ children }) => {
  const [profile, setProfile] = useState(null);
  const [activeTrip, setActiveTrip] = useState(null);
  const [contextVector, setContextVector] = useState(null);
  const [activeTab, setActiveTab] = useState('itinerary'); // 'itinerary' | 'landmark' | 'services' | 'translate' | 'memory' | 'benchmarks'
  const [isProfileOpen, setIsProfileOpen] = useState(false);
  const [isDemoDrawerOpen, setIsDemoDrawerOpen] = useState(false);
  const [selectedStopForXAI, setSelectedStopForXAI] = useState(null);
  const [activeAdaptation, setActiveAdaptation] = useState(null);
  const [loading, setLoading] = useState(false);
  const [toastMessage, setToastMessage] = useState(null);

  const showToast = (message, type = 'info') => {
    setToastMessage({ message, type });
    setTimeout(() => setToastMessage(null), 4000);
  };

  const loadProfile = async () => {
    try {
      const data = await api.getProfile();
      setProfile(data);
    } catch (err) {
      console.error('Failed to load profile:', err);
    }
  };

  const loadContext = async (city = 'Samarkand') => {
    try {
      const data = await api.getCurrentContext(city);
      setContextVector(data);
    } catch (err) {
      console.error('Failed to load context:', err);
    }
  };

  // Initial load
  useEffect(() => {
    loadProfile();
    loadContext('Samarkand');
  }, []);

  return (
    <AppContext.Provider
      value={{
        profile,
        setProfile,
        loadProfile,
        activeTrip,
        setActiveTrip,
        contextVector,
        loadContext,
        activeTab,
        setActiveTab,
        isProfileOpen,
        setIsProfileOpen,
        isDemoDrawerOpen,
        setIsDemoDrawerOpen,
        selectedStopForXAI,
        setSelectedStopForXAI,
        activeAdaptation,
        setActiveAdaptation,
        loading,
        setLoading,
        toastMessage,
        showToast,
      }}
    >
      {children}
    </AppContext.Provider>
  );
};

export const useApp = () => useContext(AppContext);

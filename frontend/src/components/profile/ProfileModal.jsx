import React, { useState, useEffect } from 'react';
import { useApp } from '../../context/AppContext';
import api from '../../services/api';
import { 
  X, 
  Accessibility, 
  Heart, 
  DollarSign, 
  Compass, 
  Utensils, 
  Check, 
  Save 
} from 'lucide-react';

const ProfileModal = () => {
  const { isProfileOpen, setIsProfileOpen, profile, setProfile, showToast } = useApp();

  const [name, setName] = useState('');
  const [language, setLanguage] = useState('en');
  const [accessibility, setAccessibility] = useState([]);
  const [interests, setInterests] = useState([]);
  const [travelStyle, setTravelStyle] = useState('balanced');
  const [budgetTier, setBudgetTier] = useState('moderate');
  const [dietary, setDietary] = useState([]);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    if (profile) {
      setName(profile.name || 'Traveler');
      setLanguage(profile.language || 'en');
      setAccessibility(profile.accessibility_needs || []);
      setInterests(profile.preferred_activities || ['historical', 'cultural']);
      setTravelStyle(profile.travel_style || 'balanced');
      setBudgetTier(profile.budget_tier || 'moderate');
      setDietary(profile.dietary_preferences || []);
    }
  }, [profile, isProfileOpen]);

  if (!isProfileOpen) return null;

  const toggleItem = (list, setList, item) => {
    if (list.includes(item)) {
      setList(list.filter(i => i !== item));
    } else {
      setList([...list, item]);
    }
  };

  const handleSave = async () => {
    setSaving(true);
    try {
      const updated = await api.updateProfile({
        name,
        language,
        accessibility_needs: accessibility,
        preferred_activities: interests,
        travel_style: travelStyle,
        budget_tier: budgetTier,
        dietary_preferences: dietary
      });
      setProfile(updated);
      showToast('Profile preference vector P updated successfully!', 'success');
      setIsProfileOpen(false);
    } catch (err) {
      console.error(err);
      showToast('Failed to save profile', 'error');
    } finally {
      setSaving(false);
    }
  };

  const allInterests = [
    { id: 'historical', label: 'Historical & Ancient' },
    { id: 'cultural', label: 'Cultural & Art' },
    { id: 'monument', label: 'Monuments & Architecture' },
    { id: 'culinary', label: 'Food & Bazaars' },
    { id: 'scenic', label: 'Gardens & Scenic Nature' },
    { id: 'craft', label: 'Silk & Paper Workshops' }
  ];

  const allDietary = [
    { id: 'halal', label: 'Halal Cuisine' },
    { id: 'vegetarian', label: 'Vegetarian' },
    { id: 'vegan', label: 'Vegan' },
    { id: 'gluten_free', label: 'Gluten-Free' }
  ];

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/75 backdrop-blur-sm animate-fade-in">
      <div className="w-full max-w-2xl bg-slate-900 border border-slate-800 rounded-2xl shadow-2xl overflow-hidden flex flex-col max-h-[90vh]">
        
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-slate-800 bg-slate-900/80">
          <div className="flex items-center gap-2">
            <div className="p-2 rounded-xl bg-teal-500/10 text-teal-400 border border-teal-500/20">
              <Accessibility className="w-5 h-5" />
            </div>
            <div>
              <h3 className="text-base font-bold text-white font-['Outfit']">Tourist Profile & Accessibility</h3>
              <p className="text-xs text-slate-400">Formalizes user preference vector P = [P1, P2, ... Pn]</p>
            </div>
          </div>
          <button 
            onClick={() => setIsProfileOpen(false)}
            className="p-1 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Form Body */}
        <div className="p-6 overflow-y-auto space-y-6 text-xs text-slate-300">
          
          {/* Basic Info */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="block text-slate-400 font-medium mb-1.5">Traveler Name</label>
              <input
                type="text"
                value={name}
                onChange={(e) => setName(e.target.value)}
                className="w-full px-3 py-2 rounded-lg bg-slate-800 border border-slate-700 text-white focus:outline-none focus:border-teal-500"
              />
            </div>
            <div>
              <label className="block text-slate-400 font-medium mb-1.5">Primary Language</label>
              <select
                value={language}
                onChange={(e) => setLanguage(e.target.value)}
                className="w-full px-3 py-2 rounded-lg bg-slate-800 border border-slate-700 text-white focus:outline-none focus:border-teal-500"
              >
                <option value="en">English (US)</option>
                <option value="uz">Uzbek (O'zbek tili)</option>
                <option value="ru">Russian (Русский)</option>
                <option value="fr">French (Français)</option>
                <option value="es">Spanish (Español)</option>
                <option value="de">German (Deutsch)</option>
              </select>
            </div>
          </div>

          {/* Accessibility Requirements */}
          <div className="p-4 rounded-xl bg-indigo-500/5 border border-indigo-500/20">
            <div className="flex items-center gap-2 mb-2 text-indigo-300 font-semibold">
              <Accessibility className="w-4 h-4 text-indigo-400" />
              <span>Accessibility Requirements (Paper Section 3.1)</span>
            </div>
            <p className="text-slate-400 mb-3 text-[11px]">
              Active accessibility flags automatically filter and penalize non-accessible historic stairways (e.g., steep necropolis climbs).
            </p>
            <div className="flex flex-wrap gap-2">
              {[
                { id: 'wheelchair', label: 'Wheelchair / Ramp Access Required' },
                { id: 'step_free', label: 'Step-Free Paved Pathways' },
                { id: 'elevator', label: 'Elevator / Ground-Level Only' },
                { id: 'audio_guide', label: 'Visual Assistance / Audio Guide' }
              ].map((acc) => {
                const active = accessibility.includes(acc.id);
                return (
                  <button
                    key={acc.id}
                    type="button"
                    onClick={() => toggleItem(accessibility, setAccessibility, acc.id)}
                    className={`flex items-center gap-2 px-3 py-2 rounded-lg border text-xs font-medium transition-all ${
                      active
                        ? 'bg-indigo-500/20 border-indigo-500 text-indigo-200'
                        : 'bg-slate-800/80 border-slate-700 text-slate-300 hover:border-slate-600'
                    }`}
                  >
                    <div className={`w-3.5 h-3.5 rounded flex items-center justify-center border ${
                      active ? 'bg-indigo-500 border-indigo-400 text-white' : 'border-slate-600'
                    }`}>
                      {active && <Check className="w-2.5 h-2.5 stroke-[3]" />}
                    </div>
                    <span>{acc.label}</span>
                  </button>
                );
              })}
            </div>
          </div>

          {/* Preferred Activities / Interests */}
          <div>
            <div className="flex items-center gap-2 mb-2 text-slate-300 font-semibold">
              <Heart className="w-4 h-4 text-rose-400" />
              <span>Destination Interests & Activity Preferences</span>
            </div>
            <div className="grid grid-cols-2 sm:grid-cols-3 gap-2">
              {allInterests.map((interest) => {
                const active = interests.includes(interest.id);
                return (
                  <button
                    key={interest.id}
                    type="button"
                    onClick={() => toggleItem(interests, setInterests, interest.id)}
                    className={`px-3 py-2 rounded-lg border text-left font-medium transition-all ${
                      active
                        ? 'bg-teal-500/20 border-teal-500 text-teal-200'
                        : 'bg-slate-800/80 border-slate-700 text-slate-300 hover:border-slate-600'
                    }`}
                  >
                    <span>{interest.label}</span>
                  </button>
                );
              })}
            </div>
          </div>

          {/* Travel Style & Budget */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <div className="flex items-center gap-2 mb-2 text-slate-300 font-semibold">
                <Compass className="w-4 h-4 text-cyan-400" />
                <span>Travel Style</span>
              </div>
              <div className="grid grid-cols-3 gap-1.5">
                {['relaxed', 'balanced', 'fast_paced'].map((style) => (
                  <button
                    key={style}
                    type="button"
                    onClick={() => setTravelStyle(style)}
                    className={`py-2 px-1 text-center rounded-lg border text-[11px] capitalize font-medium transition-all ${
                      travelStyle === style
                        ? 'bg-cyan-500/20 border-cyan-500 text-cyan-200'
                        : 'bg-slate-800 border-slate-700 text-slate-400'
                    }`}
                  >
                    {style.replace('_', ' ')}
                  </button>
                ))}
              </div>
            </div>

            <div>
              <div className="flex items-center gap-2 mb-2 text-slate-300 font-semibold">
                <DollarSign className="w-4 h-4 text-emerald-400" />
                <span>Budget Tier</span>
              </div>
              <div className="grid grid-cols-3 gap-1.5">
                {['budget', 'moderate', 'luxury'].map((b) => (
                  <button
                    key={b}
                    type="button"
                    onClick={() => setBudgetTier(b)}
                    className={`py-2 px-1 text-center rounded-lg border text-[11px] capitalize font-medium transition-all ${
                      budgetTier === b
                        ? 'bg-emerald-500/20 border-emerald-500 text-emerald-200'
                        : 'bg-slate-800 border-slate-700 text-slate-400'
                    }`}
                  >
                    {b}
                  </button>
                ))}
              </div>
            </div>
          </div>

          {/* Dietary Preferences */}
          <div>
            <div className="flex items-center gap-2 mb-2 text-slate-300 font-semibold">
              <Utensils className="w-4 h-4 text-amber-400" />
              <span>Dietary Requirements</span>
            </div>
            <div className="flex flex-wrap gap-2">
              {allDietary.map((d) => {
                const active = dietary.includes(d.id);
                return (
                  <button
                    key={d.id}
                    type="button"
                    onClick={() => toggleItem(dietary, setDietary, d.id)}
                    className={`px-3 py-1.5 rounded-lg border text-xs font-medium transition-all ${
                      active
                        ? 'bg-amber-500/20 border-amber-500 text-amber-200'
                        : 'bg-slate-800 border-slate-700 text-slate-300 hover:border-slate-600'
                    }`}
                  >
                    {d.label}
                  </button>
                );
              })}
            </div>
          </div>

        </div>

        {/* Footer */}
        <div className="px-6 py-4 border-t border-slate-800 bg-slate-900 flex justify-end gap-3">
          <button
            onClick={() => setIsProfileOpen(false)}
            className="px-4 py-2 rounded-xl text-slate-400 hover:text-white hover:bg-slate-800 text-xs font-semibold"
          >
            Cancel
          </button>
          <button
            onClick={handleSave}
            disabled={saving}
            className="flex items-center gap-2 px-5 py-2 rounded-xl bg-gradient-to-r from-teal-500 to-cyan-500 hover:from-teal-400 hover:to-cyan-400 text-slate-950 text-xs font-bold shadow-lg shadow-teal-500/20"
          >
            <Save className="w-4 h-4" />
            <span>{saving ? 'Saving...' : 'Save Preferences'}</span>
          </button>
        </div>

      </div>
    </div>
  );
};

export default ProfileModal;

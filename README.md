# NEXORA: Multimodal & Explainable AI Framework for Intelligent Tourism Assistance

Based on the research paper:
> **"Nexora: A Multi modal Explainable AI Framework for Intelligent Smart Tourism Assistance Using Context-Aware Recommendation"**  
> *R. Rachna, A. Salai Vanmathi, VB. Rithik Balaji, and Kavya Sree.A*

---

## 🌟 Overview & Key Contributions

NEXORA addresses the fragmentation, lack of transparency, and vulnerability to real-world volatility in modern smart tourism applications. It provides a unified, single-platform framework covering the entire travel lifecycle:

1. **Multimodal Query Fusion ($H_m$):** Seamlessly interprets natural language text, spoken voice input (via Web Speech API), reference images, and GPS coordinates.
2. **Context-Aware Modeling ($C = [L, T, W, Tr, Cr, O, P]$):** Combines real-time meteorology (Open-Meteo), crowd density indices, transit flow, and operating schedules.
3. **Explainable AI (XAI) Attribution ($E(d)$):** Calculates quantitative decision-factor weight breakdowns (interest alignment, weather suitability, accessibility fit, crowd avoidance) alongside transparent natural language justifications.
4. **Realistic Buffer Time Calculations:** Allocates realistic walking, ticketing, photography, and queue intervals (+20m to +30m) into chronological schedules.
5. **Dynamic Itinerary Adaptation ($I^*$):** Automatically detects environmental shifts (e.g. sudden rainstorms, crowd spikes) and proposes re-optimized itineraries while strictly preserving the tourist's final decision agency.
6. **Gemini Vision Landmark Recognition:** Identifies monuments and historical sites from photos and generates rich architectural, cultural, and visiting guidance.
7. **Samarkand v2 Quantitative Benchmark Dashboard:** Interactive reproduction of the paper's 96.40% Accuracy benchmark, comparison table, and confusion matrix.
8. **Integrated Travel Services:** Curated lodging, dietary-filtered dining (Halal, Vegetarian), transit options, and emergency SOS contacts.
9. **Multilingual Translation & Voice:** Real-time cross-language assistance with pronunciation guides and speech synthesis.
10. **AI Memory Book:** Automatically synthesizes a post-trip digital travelogue, highlights, and photo keepsake.

---

## 🚀 Running Locally

Both the backend and frontend development servers are configured and running:

- **Frontend Application:** [http://127.0.0.1:3000](http://127.0.0.1:3000)
- **FastAPI Backend & Swagger Docs:** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **Backend Health Check:** [http://127.0.0.1:8000/](http://127.0.0.1:8000/)

### Manual Launch Commands (if restarted)

#### 1. Backend Server
```bash
python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload
```

#### 2. Frontend Server
```bash
cd frontend
npm run dev -- --host 127.0.0.1 --port 3000
```

---

## 🧭 Live Demonstration Walkthrough

1. **User Profile & Accessibility ($P$):**
   - Click the profile button in the top right corner.
   - Configure accessibility flags (e.g. *Wheelchair / Ramp Access Required*) or dietary preferences.
   - Save preferences to update the profile vector $P$.
2. **Multimodal Query Fusion:**
   - In the search bar, click the microphone button to test spoken voice input, or click the photo icon to upload a reference image.
   - Click **"Generate Explainable Itinerary"**.
3. **Itinerary & Buffer Times:**
   - Switch between **Day 1** and **Day 2** tabs.
   - Observe scheduled timestamps and realistic buffer intervals (e.g., `+20m buffer for walking/queue`).
4. **Explainable AI (XAI) Inspector:**
   - Click **"Explain Recommendation (XAI)"** on any POI card.
   - View the mathematical formulation $E(d)$, percentage progress bars for all 5 factors, and transparent justifications for venue and timing selection.
5. **Dynamic Disruption Simulator ($I^*$ Adaptation):**
   - Click the **"Disruption Simulator"** button in the top bar.
   - Click **"Simulate Sudden Heavy Rain"**.
   - Notice the reactive adaptation banner proposing an indoor replacement (e.g., swapping outdoor necropolis stairs with covered museums).
   - Click **"Accept Re-Optimization"** to update the schedule.
6. **Landmark Vision Recognition:**
   - Navigate to the **"Landmark Vision"** tab.
   - Upload any monument photo or click one of the preset sample landmarks (e.g. *Registan Ensemble*).
   - Review the AI-generated historical provenance, architectural details, and visiting tips.
7. **Research Benchmarks & Confusion Matrix:**
   - Navigate to the **"Research Benchmarks"** tab.
   - Inspect the quantitative performance comparison table, comparative bar chart, and 4×4 confusion matrix from Section 4 of the paper.
8. **Supporting Tourism Services:**
   - Visit **"Travel Services"** for hotels, dining by dietary needs, transit routes, and emergency SOS contacts.
   - Visit **"Voice & Translate"** for speech-synthesized translations and Silk Road phrasebooks.
   - Visit **"Memory Book"** to generate the digital keepsake journal.

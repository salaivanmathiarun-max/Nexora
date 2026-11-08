import os
import json
import base64
import logging
from typing import Dict, Any, Optional, List
import requests
from google import genai
from google.genai import types
from ..config import settings

logger = logging.getLogger("nexora.gemini")

class GeminiService:
    def __init__(self):
        self.api_key = settings.GEMINI_API_KEY
        self.model_name = settings.GEMINI_MODEL or "gemini-3.5-flash"
        self.client = None
        self._init_client()

    def _init_client(self):
        # Refresh API key from settings or environment
        key = settings.GEMINI_API_KEY or os.getenv("GEMINI_API_KEY", "")
        if key and key.strip():
            try:
                self.client = genai.Client(api_key=key.strip().strip('"').strip("'"))
                self.api_key = key
                logger.info(f"Gemini client initialized successfully with model: {self.model_name}")
            except Exception as e:
                logger.warning(f"Failed to initialize Gemini client: {e}")
                self.client = None

    def is_available(self) -> bool:
        if self.client is None:
            self._init_client()
        return self.client is not None

    def _generate_with_fallback(self, contents, config=None):
        """Attempts generation with primary model and handles transient demand spikes with backoff."""
        import time
        if not self.is_available():
            raise RuntimeError("Gemini AI client is not initialized. Please configure GEMINI_API_KEY in backend/.env.")

        candidate_models = [self.model_name]
        for m in ["gemini-3.5-flash", "gemini-3.5-flash-lite"]:
            if m not in candidate_models:
                candidate_models.append(m)

        last_error = None
        for model in candidate_models:
            for attempt in range(3):
                try:
                    response = self.client.models.generate_content(
                        model=model,
                        contents=contents,
                        config=config
                    )
                    self.model_name = model
                    return response
                except Exception as e:
                    err_str = str(e)
                    last_error = e
                    # If 503 spike, wait briefly and retry
                    if "503" in err_str or "unavailable" in err_str.lower():
                        logger.warning(f"Gemini model '{model}' 503 spike on attempt {attempt+1}, waiting 1.5s...")
                        time.sleep(1.5)
                        continue
                    elif "404" in err_str or "not found" in err_str.lower():
                        break # try next model
                    else:
                        raise
        raise RuntimeError(f"All Gemini models failed. Last error: {last_error}")

    def _extract_image_bytes(self, image_input: str) -> Optional[bytes]:
        """Helper to extract raw JPEG/PNG bytes from base64, data URL, local path, or HTTP URL."""
        if not image_input:
            return None

        # 1. Check if it's an HTTP/HTTPS URL
        if image_input.startswith("http://") or image_input.startswith("https://"):
            try:
                headers = {"User-Agent": "NexoraBot/1.0 (academic.research@nexora.dev)"}
                resp = requests.get(image_input, headers=headers, timeout=12)
                if resp.status_code == 200:
                    return resp.content
            except Exception as e:
                logger.warning(f"Failed to fetch image from URL {image_input}: {e}")
                return None

        # 2. Check if it's a relative local path in public/ or data/
        if image_input.startswith("/landmarks/") or "landmarks" in image_input:
            # Check local public folder
            possible_paths = [
                os.path.join(os.getcwd(), "frontend", "public", image_input.lstrip("/")),
                os.path.join(os.getcwd(), "backend", "app", "data", "sample_landmarks", os.path.basename(image_input)),
                os.path.join(os.path.dirname(__file__), "..", "data", "sample_landmarks", os.path.basename(image_input))
            ]
            for p in possible_paths:
                if os.path.exists(p):
                    with open(p, "rb") as f:
                        return f.read()

        # 3. Base64 or Data URL
        try:
            raw_b64 = image_input.split(",")[-1] if "," in image_input else image_input
            return base64.b64decode(raw_b64)
        except Exception as e:
            logger.warning(f"Failed to decode base64 image: {e}")
            return None

    # =========================================================================
    # Section 3.8: Multilingual Translation Assistance
    # =========================================================================
    def translate_text(
        self,
        text: str,
        source_language: str = "auto",
        target_language: str = "uz"
    ) -> Dict[str, Any]:
        """
        Research Paper Section 3.8 – Translation Assistance.
        Dynamic AI-powered translation preserving meaning, tone, and sentence structure.
        Supports arbitrary sentences, long paragraphs, auto-detect, and phonetics.
        """
        if not text or not text.strip():
            raise ValueError("Input text to translate cannot be empty.")

        lang_instruction = (
            f"from '{source_language}'"
            if source_language and source_language != "auto"
            else "with automatic source language detection"
        )
        prompt = f"""You are the NEXORA Multilingual Translation Engine (Section 3.8 of the research paper: Translation Assistance).
Translate the input text accurately into target language '{target_language}' {lang_instruction}.

Core Requirements:
1. Translate accurately between any language pair (e.g. Uzbek, Russian, English, Hindi, Arabic, Chinese Simplified, French, German, Spanish, Turkish, etc.).
2. Automatic source language detection: Identify the source language ISO code (e.g. 'uz', 'ru', 'en', 'hi', 'ar', 'zh', 'fr', 'de', 'es', 'tr') and full English language name.
3. Preserve the original meaning, grammatical structure, semantic nuance, and communicative tone (e.g. polite, conversational, formal, inquisitive, urgent, descriptive).
4. Preserve proper names, addresses, historical monuments in Samarkand (Registan, Gur-e-Amir, Bibi-Khanym, Shah-i Zinda, Siab Bazaar), and numbers faithfully.
5. Writing scripts:
   - For Uzbek target: use standard modern Uzbek Latin script (e.g. O'zbekcha) unless Cyrillic is specifically requested.
   - For Russian target: use Russian Cyrillic script.
   - For Arabic target: use Arabic script.
   - For Chinese target: use Simplified Chinese characters.
   - For Hindi target: use Devanagari script.
   - For English/French/German/Spanish/Turkish: use respective standard Latin scripts.
6. Provide an accurate phonetic pronunciation guide (romanized) to help tourists and locals read or pronounce the translation aloud.
7. Provide a concise context note explaining any cultural nuance, polite conventions (e.g. Uzbek 'Assalomu alaykum', 'Rahmat', 'Iltimos'), or geographical context.

Input text:
\"\"\"{text}\"\"\"

Respond ONLY with a valid JSON object matching this schema:
{{
  "original_text": {json.dumps(text)},
  "source_language": "2-letter ISO code of detected source language (e.g. uz, ru, en, hi, ar, zh, fr, de, es, tr)",
  "source_language_name": "Full name of source language in English (e.g. Uzbek, Russian, English, Hindi, Arabic, Chinese)",
  "target_language": "{target_language}",
  "target_language_name": "Full name of target language in English",
  "translated_text": "Accurate, complete, and fluent translation into target language in proper script",
  "phonetic_pronunciation": "Phonetic pronunciation guide for oral communication",
  "detected_tone": "e.g. Polite / Conversational / Inquisitive / Formal / Urgent / Informative",
  "context_notes": "Helpful notes on cultural nuance or local conventions in Samarkand, Uzbekistan"
}}"""

        try:
            response = self._generate_with_fallback(
                contents=prompt,
                config=types.GenerateContentConfig(response_mime_type="application/json")
            )
            raw_text = response.text or ""
            if raw_text.startswith("```"):
                lines = raw_text.splitlines()
                if lines[0].startswith("```"):
                    lines = lines[1:]
                if lines and lines[-1].startswith("```"):
                    lines = lines[:-1]
                raw_text = "\n".join(lines).strip()
            
            res = json.loads(raw_text)
            res["original_text"] = text
            return res
        except Exception as e:
            logger.error(f"Gemini translation failed: {e}")
            raise RuntimeError(f"Translation failed: {str(e)}")

    def translate_image_text(
        self,
        image_data: str,
        target_language: str = "en"
    ) -> Dict[str, Any]:
        """
        Camera-based sign/menu/inscription translation (Section 3.8).
        Extracts visible text using Gemini Vision and translates it.
        """
        img_bytes = self._extract_image_bytes(image_data)
        if not img_bytes:
            raise ValueError("Failed to read image data. Please upload a clear photo.")

        prompt = f"""You are the NEXORA Multimodal Camera Translator (Section 3.8 of the research paper: Translation Assistance).
1. Perform OCR to read all visible written text from this photograph (e.g. street signs, museum plaques, restaurant menus, architectural inscriptions in Samarkand).
2. Identify the detected script and language (e.g. Uzbek Latin, Uzbek Cyrillic, Russian Cyrillic, Arabic calligraphy, English).
3. Translate all extracted text accurately into '{target_language}'.
4. Provide phonetic pronunciation and sign category notes.

Respond ONLY with a valid JSON object matching this schema:
{{
  "is_text_found": true,
  "detected_script_or_language": "e.g. Uzbek Latin / Russian Cyrillic / Arabic Calligraphy",
  "source_language": "ISO code if identifiable (e.g. uz, ru, en, ar)",
  "source_language_name": "Full name of detected language",
  "extracted_text": "Original text exactly as seen in the image",
  "target_language": "{target_language}",
  "translated_text": "Faithful translation into target language",
  "phonetic_pronunciation": "Phonetic reading guide",
  "context_notes": "Sign category (e.g. Historical Monument Plaque, Directional Signpost, Restaurant Menu, Transit Notice)"
}}
If no readable text is found in the photo, set "is_text_found": false, "extracted_text": "", and "translated_text": "No readable inscription or signboard detected in the image."
"""
        try:
            response = self._generate_with_fallback(
                contents=[
                    types.Part.from_bytes(data=img_bytes, mime_type="image/jpeg"),
                    prompt
                ],
                config=types.GenerateContentConfig(response_mime_type="application/json")
            )
            raw_text = response.text or ""
            if raw_text.startswith("```"):
                lines = raw_text.splitlines()
                if lines[0].startswith("```"):
                    lines = lines[1:]
                if lines and lines[-1].startswith("```"):
                    lines = lines[:-1]
                raw_text = "\n".join(lines).strip()
            
            res = json.loads(raw_text)
            return res
        except Exception as e:
            logger.error(f"Gemini image OCR translation failed: {e}")
            raise RuntimeError(f"Camera translation failed: {str(e)}")

    # =========================================================================
    # Section 3.7: Multimodal Landmark Recognition
    # =========================================================================
    def recognize_landmark(
        self,
        image_data: str,
        context_notes: str = "",
        landmark_hint: Optional[str] = None,
        classifier_confidence: Optional[float] = None,
        hierarchy_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Research Paper Section 3.7 – Landmark Recognition (Eq. 5 & 6).
        Synthesizes deep architectural, historical, cultural, and visiting guidance
        for the landmark identified by the PyTorch classifier.
        Supports Phase 1 Hierarchical Visual-Scope Disambiguation for Registan Square.
        """
        img_bytes = self._extract_image_bytes(image_data)
        if not img_bytes:
            return {
                "is_recognized": False,
                "confidence_score": 0.0,
                "confidence_level": "unrecognized",
                "predicted_landmark": "Unrecognized",
                "location": "Unknown",
                "message": "Invalid or unreadable image data. Please upload a valid image file.",
                "historical_background": "",
                "cultural_significance": "",
                "architectural_characteristics": "",
                "interesting_facts": [],
                "visiting_tips": "",
                "scope_determination": "uncertain",
                "hierarchy_level": "monument",
                "parent_landmark": None
            }

        if self.is_available():
            try:
                is_registan_domain = bool(hierarchy_context and hierarchy_context.get("is_registan_domain"))

                if is_registan_domain:
                    domain_prob = hierarchy_context.get("registan_domain_probability", 0.0)
                    top_candidates = [c.get("display_name") for c in hierarchy_context.get("top_candidates", [])]
                    hint_instruction = f"""
PRIMARY IDENTIFICATION & HIERARCHICAL VISUAL-SCOPE DISAMBIGUATION:
The initial PyTorch classifier detected architectural features characteristic of the Registan Square domain (cumulative domain signal: {domain_prob:.1%}, candidate signals: {', '.join(top_candidates)}).
Because Registan Square consists of three distinct madrasahs surrounding a central public plaza, you must perform visual spatial-scope analysis:

Determine which of the following three categories best describes this photograph:
1. 'full_complex': The image is a wide-angle, panoramic, or general view showing the whole public plaza / Registan square or multiple madrasahs simultaneously.
2. 'individual_monument': The image focuses primarily (>60% of frame) on ONE specific madrasah. Identify precisely which one:
   - 'Sher-Dor Madrasah' (East madrasah, famous for the twin lion/tiger and rising sun mosaic portal)
   - 'Tilya-Kori Madrasah & Mosque' (Central/North madrasah, distinguished by its gold-gilded prayer hall and azure dome)
   - 'Ulugh Beg Madrasah' (West madrasah, 15th-century astronomical star-pattern mosaics and vaulted iwan)
3. 'uncertain': The visual evidence is insufficient, blurry, ambiguous, or shows an unfamiliar non-Registan scene.
"""
                elif landmark_hint and landmark_hint != "Uncertain / Unfamiliar Landmark":
                    hint_instruction = f"""
PRIMARY IDENTIFICATION:
The trained PyTorch classifier has identified this monument as: '{landmark_hint}' with confidence {classifier_confidence or 0.0:.1%}.
Generate accurate, rich historical provenance, cultural significance, architectural highlights, and tourist visiting advice specifically tailored to {landmark_hint}.
"""
                else:
                    hint_instruction = """
Analyze the visual characteristics and architectural details of this monument photo.
Identify the historical monument within Samarkand or designate it as uncertain if unidentifiable.
"""

                prompt = f"""You are the NEXORA Landmark Recognition System (Section 3.7 of the research paper: Landmark Recognition).
Analyze the visual characteristics and architectural details of the provided monument photo.
{hint_instruction}
Context notes: {context_notes or 'Samarkand tourism exploration'}

Respond ONLY with a valid JSON object matching this schema:
{{
  "is_recognized": true,
  "confidence_score": {classifier_confidence or 0.95},
  "confidence_level": "high",
  "scope_determination": "full_complex | individual_monument | uncertain",
  "predicted_landmark": "{landmark_hint or 'Precise Landmark Name'}",
  "parent_landmark": "Registan Complex if individual madrasah, otherwise null",
  "hierarchy_level": "complex | sub_monument | monument",
  "location": "Location within Samarkand (street / district / hills)",
  "historical_background": "Detailed 2-3 sentence historical background, founding era, and rulers involved",
  "cultural_significance": "Cultural, religious, and civilizational importance for Uzbekistan and the Silk Road",
  "architectural_characteristics": "Distinctive architectural features (majolica tiles, azure domes, pishtaq portals, geometric mosaics)",
  "interesting_facts": [
    "Interesting historical or architectural fact 1",
    "Interesting historical or architectural fact 2",
    "Interesting historical or architectural fact 3"
  ],
  "visiting_tips": "Practical visiting advice for tourists (best photo spots, ticketing, dress code, buffer times)"
}}"""
                response = self._generate_with_fallback(
                    contents=[
                        types.Part.from_bytes(data=img_bytes, mime_type="image/jpeg"),
                        prompt
                    ],
                    config=types.GenerateContentConfig(response_mime_type="application/json")
                )
                raw_text = response.text or ""
                if raw_text.startswith("```"):
                    lines = raw_text.splitlines()
                    if lines[0].startswith("```"):
                        lines = lines[1:]
                    if lines and lines[-1].startswith("```"):
                        lines = lines[:-1]
                    raw_text = "\n".join(lines).strip()

                res = json.loads(raw_text)
                # Respect Gemini's visual-scope determination if in Registan domain
                scope = res.get("scope_determination", "")
                if is_registan_domain:
                    if scope == "full_complex":
                        res["predicted_landmark"] = "Registan Complex"
                        res["hierarchy_level"] = "complex"
                        res["parent_landmark"] = None
                    elif scope == "individual_monument":
                        # If Gemini identified the specific madrasah, use it
                        if res.get("predicted_landmark") not in [None, "", "Registan Complex"]:
                            res["hierarchy_level"] = "sub_monument"
                            res["parent_landmark"] = "Registan Complex"
                        elif landmark_hint:
                            res["predicted_landmark"] = landmark_hint
                            res["hierarchy_level"] = "sub_monument"
                            res["parent_landmark"] = "Registan Complex"
                elif landmark_hint:
                    res["predicted_landmark"] = landmark_hint
                if classifier_confidence is not None:
                    res["confidence_score"] = classifier_confidence
                if "interesting_facts" not in res or not isinstance(res["interesting_facts"], list):
                    res["interesting_facts"] = []
                return res
            except Exception as e:
                logger.error(f"Gemini landmark explanation failed: {e}")

        # Resilient fallback with curated knowledge if network is unavailable
        meta_name = landmark_hint or "Samarkand Historical Landmark"
        return {
            "is_recognized": bool(landmark_hint),
            "confidence_score": classifier_confidence or 0.85,
            "confidence_level": "medium" if (classifier_confidence and classifier_confidence < 0.7) else "high",
            "predicted_landmark": meta_name,
            "location": "Samarkand, Uzbekistan",
            "message": f"Classified by NEXORA PyTorch model as {meta_name}.",
            "historical_background": f"{meta_name} is one of the celebrated historical and cultural architectural monuments of ancient Samarkand.",
            "cultural_significance": "A masterpiece of Silk Road Islamic architecture and Timurid cultural heritage registered under UNESCO World Heritage.",
            "architectural_characteristics": "Characterized by glazed turquoise majolica tilework, ribbed cupolas, monumental vaulted portals, and intricate geometric muqarnas.",
            "interesting_facts": [
                f"{meta_name} stands as an enduring emblem of 14th-17th century Silk Road master craftsmanship.",
                "Its preservation and restoration continue under UNESCO cultural heritage guidelines."
            ],
            "visiting_tips": "Recommended visiting time is morning or golden hour for photography. Modest dress is advised when visiting sacred shrines."
        }

    # =========================================================================
    # Section 3.2: Multimodal User Query Processing
    # =========================================================================
    def parse_multimodal_query(
        self,
        text_query: str = "",
        voice_transcript: str = "",
        image_base64: Optional[str] = None,
        city_hint: Optional[str] = None
    ) -> Dict[str, Any]:
        combined_text = f"Typed query: {text_query}\nSpoken voice input: {voice_transcript}".strip()
        if not combined_text and not image_base64:
            combined_text = f"Explore {city_hint or 'Samarkand'} for 2 days"

        if self.is_available():
            try:
                prompt = f"""
You are the NEXORA Multimodal Travel Query Parser (Section 3.2 of the research paper: Hm = alpha_t*Ht + alpha_s*Hs + alpha_i*Hi).
Extract structured travel intent from the tourist's inputs:
Input:
{combined_text}
City Hint: {city_hint or 'Samarkand'}

Respond ONLY with a valid JSON object matching this schema:
{{
  "destination_city": "City Name (e.g. Samarkand)",
  "start_date": "YYYY-MM-DD (default to 2026-11-01 if unspecified)",
  "duration_days": 1,
  "travel_style": "balanced", // "relaxed", "balanced", "fast_paced"
  "primary_interests": ["historical", "cultural", "scenic"],
  "accessibility_flags": [], // e.g. ["wheelchair"] if mentioned
  "special_requests": "optional notes",
  "needs_clarification": false,
  "clarification_question": null
}}
"""
                response = self.client.models.generate_content(
                    model=self.model_name,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json"
                    )
                )
                if response.text:
                    return json.loads(response.text)
            except Exception as e:
                logger.warning(f"Gemini query parsing failed, using rule-based fallback: {e}")

        # Deterministic fallback
        dest = city_hint or "Samarkand"
        lower_text = combined_text.lower()
        if "samarkand" in lower_text:
            dest = "Samarkand"
        
        days = 2
        for num_word, n in [("1", 1), ("one", 1), ("2", 2), ("two", 2), ("3", 3), ("three", 3), ("4", 4)]:
            if f"{num_word} day" in lower_text:
                days = n
                break

        interests = []
        if any(w in lower_text for w in ["history", "historic", "ancient", "monument"]):
            interests.append("historical")
        if any(w in lower_text for w in ["culture", "craft", "art", "museum"]):
            interests.append("cultural")
        if any(w in lower_text for w in ["food", "bazaar", "eat", "dining", "cuisine"]):
            interests.append("culinary")
        if any(w in lower_text for w in ["relax", "garden", "nature", "scenic"]):
            interests.append("scenic")
        if not interests:
            interests = ["historical", "cultural", "scenic"]

        accessibility = []
        if "wheelchair" in lower_text or "accessible" in lower_text or "step free" in lower_text:
            accessibility.append("wheelchair")

        return {
            "destination_city": dest,
            "start_date": "2026-11-01",
            "duration_days": days,
            "travel_style": "balanced",
            "primary_interests": interests,
            "accessibility_flags": accessibility,
            "special_requests": combined_text,
            "needs_clarification": False,
            "clarification_question": None
        }

    # =========================================================================
    # Section 3.5: Explainable AI (XAI) Attribution
    # =========================================================================
    def generate_xai_reasoning(
        self,
        destination_name: str,
        factors: Dict[str, float],
        context: Dict[str, Any],
        user_profile: Dict[str, Any]
    ) -> Dict[str, str]:
        if self.is_available():
            try:
                prompt = f"""
You are the NEXORA Explainable AI (XAI) Engine (Section 3.5 of the research paper: E(d) = sum(wi * Fi(d, u, C))).
Explain why destination '{destination_name}' is recommended for this traveler.

Context:
- Weather: {context.get('weather', {}).get('weather_condition', 'Pleasant')}, Temp: {context.get('weather', {}).get('temperature_c', 22)}°C
- Crowd Level: {context.get('crowd_density', 'Moderate')}
- User Accessibility: {user_profile.get('accessibility_needs', [])}
- Factor Scores: Interest Match={factors.get('interest_alignment', 0.9):.2f}, Weather Suitability={factors.get('weather_suitability', 0.9):.2f}, Accessibility Fit={factors.get('accessibility_fit', 0.9):.2f}

Generate a concise, transparent explanation JSON:
{{
  "primary_reason": "One clear sentence stating why this POI was chosen",
  "detailed_justification": "2-3 sentences explaining the trade-offs and factor weights",
  "timing_justification": "Why this stop is scheduled at this specific hour",
  "accessibility_notes": "Note on mobility access and comfort"
}}
"""
                response = self.client.models.generate_content(
                    model=self.model_name,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json"
                    )
                )
                if response.text:
                    return json.loads(response.text)
            except Exception as e:
                logger.warning(f"Gemini XAI reasoning fallback: {e}")

        # Deterministic XAI Rationale Generator
        primary = f"Selected for strong alignment with your travel style and optimal current weather conditions."
        detailed = (
            f"The recommendation engine weighted user interest at {int(factors.get('interest_alignment', 0.9)*100)}% "
            f"and weather suitability at {int(factors.get('weather_suitability', 0.9)*100)}%. "
            f"Scheduled during a moderate crowd window to minimize queue delays."
        )
        timing = "Scheduled in the morning/midday block when lighting and visitor flow are most favorable."
        access = "Wheelchair accessible with paved pathways and ramped thresholds." if factors.get("accessibility_fit", 1.0) > 0.8 else "Moderate mobility required due to historic steps."

        return {
            "primary_reason": primary,
            "detailed_justification": detailed,
            "timing_justification": timing,
            "accessibility_notes": access
        }

gemini_service = GeminiService()

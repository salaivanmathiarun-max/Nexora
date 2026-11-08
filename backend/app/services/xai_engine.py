from typing import Dict, Any
from .gemini_service import gemini_service
from ..schemas.xai import XAIExplanation, XAIFactors

class XAIEngine:
    def generate_explanation(
        self,
        destination_name: str,
        rec_data: Dict[str, Any],
        context_dict: Dict[str, Any],
        user_profile: Dict[str, Any]
    ) -> XAIExplanation:
        """
        Derives Explainable AI attribution E(d) and synthesizes transparent rationales.
        """
        feature_scores = rec_data.get("feature_scores", {})
        weights = rec_data.get("weights", {})
        match_score = rec_data.get("match_score_pct", 92.0)

        factors = XAIFactors(
            interest_alignment=feature_scores.get("interest_alignment", 0.9),
            weather_suitability=feature_scores.get("weather_suitability", 0.9),
            crowd_convenience=feature_scores.get("crowd_convenience", 0.9),
            accessibility_fit=feature_scores.get("accessibility_fit", 1.0),
            time_efficiency=feature_scores.get("time_efficiency", 0.92)
        )

        # Synthesize reasoning text via Gemini (or rule-based fallback)
        reasoning = gemini_service.generate_xai_reasoning(
            destination_name=destination_name,
            factors=feature_scores,
            context=context_dict,
            user_profile=user_profile
        )

        return XAIExplanation(
            match_score=match_score,
            factors=factors,
            factor_weights=weights,
            primary_reason=reasoning.get("primary_reason", "High compatibility with user profile and context."),
            detailed_justification=reasoning.get("detailed_justification", ""),
            timing_justification=reasoning.get("timing_justification", ""),
            accessibility_notes=reasoning.get("accessibility_notes", "Accessible pathways available.")
        )

xai_engine = XAIEngine()

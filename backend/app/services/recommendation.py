import json
from typing import Dict, Any, List
from ..models.destination import Destination
from ..schemas.context import ContextVector

class RecommendationEngine:
    def __init__(self):
        # Weights wi defined in paper for scoring
        self.weights = {
            "interest": 0.35,
            "accessibility": 0.25,
            "weather": 0.20,
            "crowd": 0.10,
            "cost": 0.10
        }

    def compute_profile_score(self, destination: Destination, user_profile: Dict[str, Any]) -> float:
        """
        Calculates Profile Matching Score: Sp(u,d) = sum(wi * pi(u) * fi(d))
        """
        user_interests = [i.lower() for i in user_profile.get("preferred_activities", ["historical", "cultural"])]
        tags = json.loads(destination.tags) if isinstance(destination.tags, str) else destination.tags
        dest_category = destination.category.lower()

        # Check interest match
        match_count = 0
        if dest_category in user_interests:
            match_count += 2
        for t in tags:
            if t.lower() in user_interests:
                match_count += 1

        interest_score = min(1.0, 0.4 + (match_count * 0.2))

        # Check accessibility
        access_needs = user_profile.get("accessibility_needs", [])
        if "wheelchair" in access_needs:
            access_score = 1.0 if destination.is_wheelchair_accessible else 0.1
        else:
            access_score = 1.0

        # Cost match
        user_budget = user_profile.get("budget_tier", "moderate").lower()
        dest_cost = destination.cost_tier.lower()
        cost_score = 1.0 if user_budget == dest_cost else 0.85

        return (0.5 * interest_score) + (0.35 * access_score) + (0.15 * cost_score)

    def compute_recommendation_score(
        self,
        destination: Destination,
        user_profile: Dict[str, Any],
        context: ContextVector
    ) -> Dict[str, Any]:
        """
        Calculates Overall Recommendation Score: R(d) = sum(wi * Fi(d, u, C))
        Also returns individual Fi scores for XAI module E(d).
        """
        # 1. Interest Score Fi(interest)
        user_interests = [i.lower() for i in user_profile.get("preferred_activities", ["historical", "cultural"])]
        tags = json.loads(destination.tags) if isinstance(destination.tags, str) else destination.tags
        dest_category = destination.category.lower()

        matched = any(i in dest_category for i in user_interests) or any(t.lower() in user_interests for t in tags)
        f_interest = 0.95 if matched else 0.65

        # 2. Accessibility Fit Fi(access)
        access_needs = user_profile.get("accessibility_needs", [])
        if "wheelchair" in access_needs:
            f_access = 1.0 if destination.is_wheelchair_accessible else 0.15
        else:
            f_access = 1.0

        # 3. Weather Suitability Fi(weather)
        f_weather = 1.0
        if context.weather.is_indoor_preferred:
            if destination.indoor_outdoor == "indoor":
                f_weather = 1.0
            elif destination.indoor_outdoor == "hybrid":
                f_weather = 0.75
            else: # outdoor
                f_weather = 0.25
        else:
            # Sunny/pleasant weather makes outdoor/hybrid venues very attractive
            f_weather = 0.95 if destination.indoor_outdoor in ["outdoor", "hybrid"] else 0.90

        # 4. Crowd Convenience Fi(crowd)
        f_crowd = 0.90
        if context.crowd_density in ["High", "Peak"] and destination.typical_crowd_level == "high":
            f_crowd = 0.55
        elif destination.typical_crowd_level == "low":
            f_crowd = 0.98

        # 5. Cost Fit Fi(cost)
        user_budget = user_profile.get("budget_tier", "moderate").lower()
        f_cost = 1.0 if user_budget == destination.cost_tier.lower() else 0.85

        # Weighted combination R(d)
        total_score = (
            (self.weights["interest"] * f_interest) +
            (self.weights["accessibility"] * f_access) +
            (self.weights["weather"] * f_weather) +
            (self.weights["crowd"] * f_crowd) +
            (self.weights["cost"] * f_cost)
        )

        match_score_pct = round(total_score * 100.0, 1)

        feature_scores = {
            "interest_alignment": round(f_interest, 2),
            "accessibility_fit": round(f_access, 2),
            "weather_suitability": round(f_weather, 2),
            "crowd_convenience": round(f_crowd, 2),
            "time_efficiency": 0.92
        }

        return {
            "destination": destination,
            "total_score": total_score,
            "match_score_pct": match_score_pct,
            "feature_scores": feature_scores,
            "weights": self.weights
        }

recommendation_engine = RecommendationEngine()

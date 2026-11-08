from typing import Dict, List
from pydantic import BaseModel

class XAIFactors(BaseModel):
    interest_alignment: float   # 0 to 1.0 (e.g. 0.95 = 95%)
    weather_suitability: float  # 0 to 1.0
    crowd_convenience: float    # 0 to 1.0
    accessibility_fit: float    # 0 to 1.0
    time_efficiency: float      # 0 to 1.0

class XAIExplanation(BaseModel):
    match_score: float                          # e.g. 94.2%
    factors: XAIFactors
    factor_weights: Dict[str, float]            # e.g. {"interest": 0.35, "weather": 0.25, ...}
    primary_reason: str                         # Concise primary justification
    detailed_justification: str                 # In-depth transparent reasoning
    timing_justification: str                   # Why this venue at this specific hour
    accessibility_notes: str                    # Details on ramps, elevators, terrain

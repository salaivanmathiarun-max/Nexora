from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from datetime import date
from .xai import XAIExplanation

class DestinationBrief(BaseModel):
    id: str
    name: str
    category: str
    city: str
    latitude: float
    longitude: float
    opening_time: str
    closing_time: str
    avg_duration_minutes: int
    cost_tier: str
    is_wheelchair_accessible: bool
    indoor_outdoor: str
    typical_crowd_level: str
    description: str
    image_url: str
    tags: List[str]

    class Config:
        from_attributes = True

class ItineraryStopResponse(BaseModel):
    id: str
    day_number: int
    stop_order: int
    planned_start_time: str
    planned_end_time: str
    buffer_minutes: int
    visit_status: str
    xai_match_score: float
    xai_explanation: Optional[Dict[str, Any]] = None
    destination: DestinationBrief

    class Config:
        from_attributes = True

class TripResponse(BaseModel):
    id: str
    title: str
    destination_city: str
    start_date: date
    end_date: date
    total_days: int
    status: str
    stops: List[ItineraryStopResponse] = []

    class Config:
        from_attributes = True

class ItineraryGenerateRequest(BaseModel):
    user_id: Optional[str] = None
    destination_city: str
    start_date: str # YYYY-MM-DD
    total_days: int = 1
    travel_style: Optional[str] = "balanced"
    custom_interests: Optional[List[str]] = None
    accessibility_needs: Optional[List[str]] = None

class DisruptionSimulationRequest(BaseModel):
    trip_id: str
    disruption_type: str # "rain_storm", "extreme_crowd", "venue_closed", "traffic_gridlock"
    day_number: int = 1

class AdaptationProposal(BaseModel):
    adaptation_id: str
    trip_id: str
    disruption_type: str
    disruption_summary: str
    affected_stops: List[str]
    proposed_replacements: List[Dict[str, Any]]
    expected_utility_delta: float
    recommendation_rationale: str

from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

class UserProfileBase(BaseModel):
    name: str = "Traveler"
    language: str = "en"
    accessibility_needs: List[str] = []       # e.g. ["wheelchair", "step_free"]
    preferred_activities: List[str] = ["historical", "cultural", "scenic"]
    budget_tier: str = "moderate"             # "budget", "moderate", "luxury"
    travel_style: str = "balanced"            # "relaxed", "balanced", "fast_paced"
    dietary_preferences: List[str] = []       # e.g. ["vegetarian", "halal"]

class UserProfileCreate(UserProfileBase):
    pass

class UserProfileUpdate(BaseModel):
    name: Optional[str] = None
    language: Optional[str] = None
    accessibility_needs: Optional[List[str]] = None
    preferred_activities: Optional[List[str]] = None
    budget_tier: Optional[str] = None
    travel_style: Optional[str] = None
    dietary_preferences: Optional[List[str]] = None

class UserProfileResponse(UserProfileBase):
    id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Text
from ..database import Base

class UserProfile(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(100), default="Traveler")
    language = Column(String(10), default="en")
    
    # Serialized JSON preferences matching vector P = [P1, P2, ... Pn]
    accessibility_needs = Column(Text, default="[]")       # e.g. ["wheelchair", "step_free"]
    preferred_activities = Column(Text, default="[\"historical\", \"cultural\", \"scenic\"]")
    budget_tier = Column(String(20), default="moderate")   # "budget", "moderate", "luxury"
    travel_style = Column(String(30), default="balanced")  # "relaxed", "balanced", "fast_paced"
    dietary_preferences = Column(Text, default="[]")       # e.g. ["vegetarian", "halal"]
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

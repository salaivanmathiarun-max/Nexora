import uuid
from sqlalchemy import Column, String, Float, Integer, Boolean, Text
from ..database import Base

class Destination(Base):
    __tablename__ = "destinations"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(150), nullable=False)
    category = Column(String(50), nullable=False) # "monument", "museum", "nature", "heritage", "dining"
    city = Column(String(100), nullable=False)
    country = Column(String(100), nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    
    opening_time = Column(String(5), default="09:00")
    closing_time = Column(String(5), default="18:00")
    avg_duration_minutes = Column(Integer, default=90)
    cost_tier = Column(String(20), default="moderate") # "free", "budget", "moderate", "luxury"
    
    # Contextual & accessibility parameters
    is_wheelchair_accessible = Column(Boolean, default=True)
    indoor_outdoor = Column(String(10), default="outdoor") # "indoor", "outdoor", "hybrid"
    typical_crowd_level = Column(String(20), default="moderate") # "low", "moderate", "high"
    
    description = Column(Text, default="")
    image_url = Column(String(500), default="")
    tags = Column(Text, default="[]") # JSON list of string tags

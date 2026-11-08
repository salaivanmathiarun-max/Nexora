import uuid
from datetime import datetime, date
from sqlalchemy import Column, String, Integer, Float, Boolean, Text, ForeignKey, Date, DateTime
from sqlalchemy.orm import relationship
from ..database import Base

class Trip(Base):
    __tablename__ = "trips"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=True)
    title = Column(String(150), nullable=False)
    destination_city = Column(String(100), nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    total_days = Column(Integer, default=1)
    status = Column(String(20), default="active") # "planning", "active", "completed"
    created_at = Column(DateTime, default=datetime.utcnow)

    stops = relationship("ItineraryStop", back_populates="trip", cascade="all, delete-orphan", order_by="ItineraryStop.day_number, ItineraryStop.stop_order")
    adaptations = relationship("ItineraryAdaptation", back_populates="trip", cascade="all, delete-orphan")


class ItineraryStop(Base):
    __tablename__ = "itinerary_stops"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    trip_id = Column(String(36), ForeignKey("trips.id", ondelete="CASCADE"), nullable=False)
    destination_id = Column(String(36), ForeignKey("destinations.id"), nullable=False)
    
    day_number = Column(Integer, nullable=False, default=1)
    stop_order = Column(Integer, nullable=False, default=1)
    planned_start_time = Column(String(5), nullable=False) # e.g. "09:30"
    planned_end_time = Column(String(5), nullable=False)   # e.g. "11:00"
    buffer_minutes = Column(Integer, default=20)           # Walking, queue, photo buffer
    
    visit_status = Column(String(20), default="scheduled") # "scheduled", "visited", "skipped", "replaced"
    
    # Explainable AI (XAI) Attribution & Metrics
    xai_match_score = Column(Float, default=90.0)          # Overall match score (0-100)
    xai_explanation = Column(Text, default="{}")           # JSON object: factor contributions and textual rationale
    
    created_at = Column(DateTime, default=datetime.utcnow)

    trip = relationship("Trip", back_populates="stops")
    destination = relationship("Destination")


class ItineraryAdaptation(Base):
    __tablename__ = "itinerary_adaptations"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    trip_id = Column(String(36), ForeignKey("trips.id", ondelete="CASCADE"), nullable=False)
    trigger_type = Column(String(50), nullable=False) # "weather_rain", "crowd_surge", "traffic_delay", "user_change"
    trigger_description = Column(Text, nullable=False)
    proposed_changes = Column(Text, nullable=False)   # JSON diff of old stops vs proposed stops
    status = Column(String(20), default="pending")    # "pending", "accepted", "rejected"
    created_at = Column(DateTime, default=datetime.utcnow)

    trip = relationship("Trip", back_populates="adaptations")

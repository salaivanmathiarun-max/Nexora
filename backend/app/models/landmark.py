import uuid
from datetime import datetime
from sqlalchemy import Column, String, Float, Text, Boolean, DateTime
from ..database import Base

class LandmarkLog(Base):
    __tablename__ = "landmark_logs"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), nullable=True)
    image_preview = Column(Text, nullable=True)
    is_recognized = Column(Boolean, default=True)
    confidence_score = Column(Float, nullable=False, default=0.96)
    confidence_level = Column(String(20), default="high") # "high", "medium", "unrecognized"
    predicted_landmark = Column(String(150), nullable=False)
    location = Column(String(150), default="Samarkand, Uzbekistan")
    history_summary = Column(Text, default="")
    cultural_significance = Column(Text, default="")
    architectural_notes = Column(Text, default="")
    interesting_facts = Column(Text, default="[]") # JSON list of strings
    visiting_tips = Column(Text, default="")
    created_at = Column(DateTime, default=datetime.utcnow)

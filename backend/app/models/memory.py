import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, DateTime, ForeignKey
from ..database import Base

class MemoryBookEntry(Base):
    __tablename__ = "memory_book_entries"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    trip_id = Column(String(36), ForeignKey("trips.id", ondelete="CASCADE"), nullable=False)
    entry_title = Column(String(150), nullable=False)
    story_narrative = Column(Text, default="")
    highlights = Column(Text, default="[]") # JSON list of strings
    photos = Column(Text, default="[]")     # JSON list of photo URLs or previews
    created_at = Column(DateTime, default=datetime.utcnow)

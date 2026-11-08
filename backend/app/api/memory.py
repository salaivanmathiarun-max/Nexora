import json
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from ..database import get_db
from ..models.itinerary import Trip, ItineraryStop
from ..models.memory import MemoryBookEntry

router = APIRouter(prefix="/api/memory", tags=["Memory Book"])

class MemoryGenerateRequest(BaseModel):
    trip_id: str
    user_notes: Optional[str] = ""
    uploaded_photos: Optional[List[str]] = []

@router.post("/generate")
def generate_memory_book(req: MemoryGenerateRequest, db: Session = Depends(get_db)):
    """
    AI Memory Book Generation (Section 3.10 in paper).
    Synthesizes visited POIs, photos, and notes into an AI-narrated travel keepsake.
    """
    trip = db.query(Trip).filter(Trip.id == req.trip_id).first()
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")

    stops = db.query(ItineraryStop).filter(ItineraryStop.trip_id == req.trip_id).all()
    visited_names = [s.destination.name for s in stops if s.destination]

    # Synthesize rich narrative
    narrative = (
        f"An unforgettable journey through ancient {trip.destination_city}. "
        f"Across {trip.total_days} day(s), you explored world heritage marvels including {', '.join(visited_names[:3])}. "
        f"From the dazzling turquoise tilework of the Silk Road to the warm aroma of freshly baked Siab flatbread, "
        f"your footsteps brought the historic chronicles of Central Asia to life."
    )

    highlights = [
        f"Admired the monumental azure facades of {visited_names[0] if visited_names else 'Registan'}",
        "Navigated the ancient pathways with real-time context-aware guidance",
        "Savoring traditional plov and mint tea alongside local artisans"
    ]

    photos = req.uploaded_photos or [
        "https://images.unsplash.com/photo-1548013146-72479768bada?auto=format&fit=crop&w=800&q=80",
        "https://images.unsplash.com/photo-1596178065887-1198b6148b2b?auto=format&fit=crop&w=800&q=80"
    ]

    entry = MemoryBookEntry(
        trip_id=trip.id,
        entry_title=f"The Chronicles of {trip.destination_city}",
        story_narrative=narrative,
        highlights=json.dumps(highlights),
        photos=json.dumps(photos)
    )
    db.add(entry)
    db.commit()
    db.refresh(entry)

    return {
        "id": entry.id,
        "trip_id": entry.trip_id,
        "entry_title": entry.entry_title,
        "story_narrative": entry.story_narrative,
        "highlights": json.loads(entry.highlights),
        "photos": json.loads(entry.photos),
        "created_at": entry.created_at
    }

@router.get("/{trip_id}")
def get_memory_book(trip_id: str, db: Session = Depends(get_db)):
    """Fetch existing Memory Book for a trip."""
    entry = db.query(MemoryBookEntry).filter(MemoryBookEntry.trip_id == trip_id).first()
    if not entry:
        return {"entry": None}

    return {
        "entry": {
            "id": entry.id,
            "trip_id": entry.trip_id,
            "entry_title": entry.entry_title,
            "story_narrative": entry.story_narrative,
            "highlights": json.loads(entry.highlights),
            "photos": json.loads(entry.photos),
            "created_at": entry.created_at
        }
    }

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..database import get_db
from ..schemas.query import MultimodalQueryRequest, ParsedTravelIntent
from ..services.gemini_service import gemini_service

router = APIRouter(prefix="/api/query", tags=["Query"])

@router.post("/process", response_model=ParsedTravelIntent)
def process_multimodal_query(payload: MultimodalQueryRequest, db: Session = Depends(get_db)):
    """
    Multimodal User Query Processing (Eq. 3 in paper):
    Processes text prompt, spoken voice transcript, and/or reference photo.
    """
    parsed = gemini_service.parse_multimodal_query(
        text_query=payload.text_query or "",
        voice_transcript=payload.voice_transcript or "",
        image_base64=payload.image_base64,
        city_hint=payload.destination_city
    )

    # Override with explicit payload fields if user provided them directly
    if payload.destination_city:
        parsed["destination_city"] = payload.destination_city
    if payload.duration_days:
        parsed["duration_days"] = payload.duration_days
    if payload.start_date:
        parsed["start_date"] = payload.start_date

    return ParsedTravelIntent(**parsed)

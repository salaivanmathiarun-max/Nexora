from typing import List, Optional
from pydantic import BaseModel

class MultimodalQueryRequest(BaseModel):
    text_query: Optional[str] = ""
    voice_transcript: Optional[str] = ""
    image_base64: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    destination_city: Optional[str] = None
    duration_days: Optional[int] = None
    start_date: Optional[str] = None

class ParsedTravelIntent(BaseModel):
    destination_city: str
    start_date: str
    duration_days: int
    travel_style: str
    primary_interests: List[str]
    accessibility_flags: List[str]
    special_requests: Optional[str] = None
    needs_clarification: bool = False
    clarification_question: Optional[str] = None

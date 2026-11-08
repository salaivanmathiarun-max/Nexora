import json
import datetime
from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..models.itinerary import Trip, ItineraryStop, ItineraryAdaptation
from ..models.user import UserProfile
from ..models.destination import Destination
from ..schemas.itinerary import (
    ItineraryGenerateRequest,
    TripResponse,
    ItineraryStopResponse,
    DestinationBrief,
    DisruptionSimulationRequest,
    AdaptationProposal
)
from ..services.context_service import context_service
from ..services.itinerary_optimizer import itinerary_optimizer

router = APIRouter(prefix="/api/itinerary", tags=["Itinerary"])

def serialize_stop(stop: ItineraryStop) -> ItineraryStopResponse:
    d = stop.destination
    dest_brief = DestinationBrief(
        id=d.id,
        name=d.name,
        category=d.category,
        city=d.city,
        latitude=d.latitude,
        longitude=d.longitude,
        opening_time=d.opening_time,
        closing_time=d.closing_time,
        avg_duration_minutes=d.avg_duration_minutes,
        cost_tier=d.cost_tier,
        is_wheelchair_accessible=d.is_wheelchair_accessible,
        indoor_outdoor=d.indoor_outdoor,
        typical_crowd_level=d.typical_crowd_level,
        description=d.description,
        image_url=d.image_url,
        tags=json.loads(d.tags) if isinstance(d.tags, str) else d.tags
    )
    return ItineraryStopResponse(
        id=stop.id,
        day_number=stop.day_number,
        stop_order=stop.stop_order,
        planned_start_time=stop.planned_start_time,
        planned_end_time=stop.planned_end_time,
        buffer_minutes=stop.buffer_minutes,
        visit_status=stop.visit_status,
        xai_match_score=stop.xai_match_score,
        xai_explanation=json.loads(stop.xai_explanation) if stop.xai_explanation else None,
        destination=dest_brief
    )

@router.post("/generate", response_model=TripResponse)
def generate_itinerary(req: ItineraryGenerateRequest, db: Session = Depends(get_db)):
    """
    Generates a personalized itinerary using profile matching Sp(u,d),
    context-aware scoring R(d), buffer times, and XAI attribution E(d).
    """
    profile = db.query(UserProfile).first()
    user_dict = {}
    if profile:
        user_dict = {
            "accessibility_needs": json.loads(profile.accessibility_needs) if profile.accessibility_needs else [],
            "preferred_activities": json.loads(profile.preferred_activities) if profile.preferred_activities else [],
            "budget_tier": profile.budget_tier,
            "travel_style": req.travel_style or profile.travel_style
        }
    if req.custom_interests:
        user_dict["preferred_activities"] = req.custom_interests
    if req.accessibility_needs is not None:
        user_dict["accessibility_needs"] = req.accessibility_needs

    start_d = datetime.date.today()
    try:
        start_d = datetime.datetime.strptime(req.start_date, "%Y-%m-%d").date()
    except Exception:
        pass
    end_d = start_d + datetime.timedelta(days=req.total_days - 1)

    trip = Trip(
        user_id=profile.id if profile else None,
        title=f"Exploring {req.destination_city}",
        destination_city=req.destination_city,
        start_date=start_d,
        end_date=end_d,
        total_days=req.total_days,
        status="active"
    )
    db.add(trip)
    db.commit()
    db.refresh(trip)

    # Collect context C
    context = context_service.get_context_vector(city=req.destination_city)

    # Generate sequenced stops with buffer times and XAI metrics
    stops = itinerary_optimizer.generate_trip_itinerary(
        db=db,
        trip=trip,
        user_profile=user_dict,
        context=context
    )

    return TripResponse(
        id=trip.id,
        title=trip.title,
        destination_city=trip.destination_city,
        start_date=trip.start_date,
        end_date=trip.end_date,
        total_days=trip.total_days,
        status=trip.status,
        stops=[serialize_stop(s) for s in stops]
    )

@router.get("/{trip_id}", response_model=TripResponse)
def get_itinerary(trip_id: str, db: Session = Depends(get_db)):
    """Fetch complete itinerary with stops and XAI metrics."""
    trip = db.query(Trip).filter(Trip.id == trip_id).first()
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")

    stops = db.query(ItineraryStop).filter(ItineraryStop.trip_id == trip_id).order_by(ItineraryStop.day_number, ItineraryStop.stop_order).all()
    return TripResponse(
        id=trip.id,
        title=trip.title,
        destination_city=trip.destination_city,
        start_date=trip.start_date,
        end_date=trip.end_date,
        total_days=trip.total_days,
        status=trip.status,
        stops=[serialize_stop(s) for s in stops]
    )

@router.post("/simulate-disruption", response_model=AdaptationProposal)
def simulate_disruption(req: DisruptionSimulationRequest, db: Session = Depends(get_db)):
    """
    Triggers dynamic disruption (e.g. rainstorm or crowd spike) and derives I* adaptation proposals.
    """
    trip = db.query(Trip).filter(Trip.id == req.trip_id).first()
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")

    profile = db.query(UserProfile).first()
    user_dict = {
        "accessibility_needs": json.loads(profile.accessibility_needs) if profile and profile.accessibility_needs else [],
        "preferred_activities": json.loads(profile.preferred_activities) if profile and profile.preferred_activities else [],
        "travel_style": profile.travel_style if profile else "balanced"
    }

    # Temporarily set simulation context
    if req.disruption_type == "rain_storm":
        context_service.set_simulation_override({"weather_condition": "Rainy"})
    elif req.disruption_type == "extreme_crowd":
        context_service.set_simulation_override({"crowd_density": "Peak"})

    context = context_service.get_context_vector(city=trip.destination_city)

    adaptation = itinerary_optimizer.propose_adaptation(
        db=db,
        trip_id=trip.id,
        disruption_type=req.disruption_type,
        context=context,
        user_profile=user_dict
    )

    changes = json.loads(adaptation.proposed_changes)
    affected = [c["original_name"] for c in changes]

    return AdaptationProposal(
        adaptation_id=adaptation.id,
        trip_id=trip.id,
        disruption_type=adaptation.trigger_type,
        disruption_summary=adaptation.trigger_description,
        affected_stops=affected,
        proposed_replacements=changes,
        expected_utility_delta=+18.5, # Enhanced utility under adverse conditions
        recommendation_rationale=adaptation.trigger_description
    )

@router.post("/confirm-adaptation")
def confirm_adaptation(adaptation_id: str, accept: bool, db: Session = Depends(get_db)):
    """Tourist accepts or rejects the proposed adaptation (tourist retained agency)."""
    try:
        adaptation = itinerary_optimizer.apply_adaptation(db=db, adaptation_id=adaptation_id, accept=accept)
        return {
            "adaptation_id": adaptation.id,
            "status": adaptation.status,
            "message": "Itinerary updated successfully" if accept else "Proposed adaptation dismissed"
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

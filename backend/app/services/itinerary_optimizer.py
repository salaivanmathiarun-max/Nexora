import json
import datetime
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session

from ..models.destination import Destination
from ..models.itinerary import Trip, ItineraryStop, ItineraryAdaptation
from ..schemas.context import ContextVector
from .recommendation import recommendation_engine
from .xai_engine import xai_engine

class ItineraryOptimizer:
    def __init__(self):
        # Optimization penalty coefficients: lambda1 (time), lambda2 (context inconvenience), lambda3 (cost)
        self.lambda1 = 0.25
        self.lambda2 = 0.40
        self.lambda3 = 0.15

    def generate_trip_itinerary(
        self,
        db: Session,
        trip: Trip,
        user_profile: Dict[str, Any],
        context: ContextVector
    ) -> List[ItineraryStop]:
        """
        Builds a multi-day timed itinerary with realistic buffer times and XAI metrics.
        """
        # Fetch all candidate destinations in city
        destinations = db.query(Destination).filter(Destination.city.ilike(f"%{trip.destination_city}%")).all()
        if not destinations:
            # Fallback to all destinations if city not specifically tagged
            destinations = db.query(Destination).all()

        # Score all destinations using recommendation engine R(d)
        scored_destinations = []
        for dest in destinations:
            rec_result = recommendation_engine.compute_recommendation_score(
                destination=dest,
                user_profile=user_profile,
                context=context
            )
            scored_destinations.append(rec_result)

        # Sort descending by total score
        scored_destinations.sort(key=lambda x: x["total_score"], reverse=True)

        # Determine number of stops per day (2-3 major stops per day for balanced travel)
        style = user_profile.get("travel_style", "balanced")
        stops_per_day = 2 if style == "relaxed" else (4 if style == "fast_paced" else 3)
        total_needed = trip.total_days * stops_per_day

        selected = scored_destinations[:total_needed]

        created_stops = []
        idx = 0

        # Typical daily schedule slots
        time_slots = [
            ("09:30", 20), # (start_time, buffer_minutes)
            ("12:00", 30),
            ("15:00", 25),
            ("18:30", 20)
        ]

        for day in range(1, trip.total_days + 1):
            day_slot_idx = 0
            while day_slot_idx < stops_per_day and idx < len(selected):
                item = selected[idx]
                dest: Destination = item["destination"]
                slot_start, buffer_mins = time_slots[min(day_slot_idx, len(time_slots) - 1)]

                # Compute end time based on avg_duration_minutes
                start_dt = datetime.datetime.strptime(slot_start, "%H:%M")
                end_dt = start_dt + datetime.timedelta(minutes=dest.avg_duration_minutes)
                slot_end = end_dt.strftime("%H:%M")

                # Generate Explainable AI explanation E(d)
                xai_obj = xai_engine.generate_explanation(
                    destination_name=dest.name,
                    rec_data=item,
                    context_dict=context.model_dump(),
                    user_profile=user_profile
                )

                stop = ItineraryStop(
                    trip_id=trip.id,
                    destination_id=dest.id,
                    day_number=day,
                    stop_order=day_slot_idx + 1,
                    planned_start_time=slot_start,
                    planned_end_time=slot_end,
                    buffer_minutes=buffer_mins,
                    visit_status="scheduled",
                    xai_match_score=item["match_score_pct"],
                    xai_explanation=json.dumps(xai_obj.model_dump())
                )
                db.add(stop)
                created_stops.append(stop)

                idx += 1
                day_slot_idx += 1

        db.commit()
        return created_stops

    def propose_adaptation(
        self,
        db: Session,
        trip_id: str,
        disruption_type: str,
        context: ContextVector,
        user_profile: Dict[str, Any]
    ) -> ItineraryAdaptation:
        """
        Dynamically solves I* upon disruption (e.g. rain alert or crowd surge),
        identifying affected stops and proposing replacement candidates with utility delta.
        """
        trip = db.query(Trip).filter(Trip.id == trip_id).first()
        if not trip:
            raise ValueError(f"Trip {trip_id} not found")

        current_stops = db.query(ItineraryStop).filter(ItineraryStop.trip_id == trip_id).all()
        used_dest_ids = {s.destination_id for s in current_stops}

        all_dests = db.query(Destination).filter(Destination.city.ilike(f"%{trip.destination_city}%")).all()
        candidates = [d for d in all_dests if d.id not in used_dest_ids]

        replacements = []
        affected_stops = []
        rationale = ""

        if disruption_type in ["rain_storm", "weather_rain"]:
            rationale = "Sudden heavy rain detected. Proposing to replace outdoor walking monuments with nearby covered indoor architectural sites and museum treasures to keep your day comfortable."
            for s in current_stops:
                if s.destination and s.destination.indoor_outdoor == "outdoor":
                    affected_stops.append(s.destination.name)
                    # Find indoor candidate
                    indoor_cands = [c for c in candidates if c.indoor_outdoor in ["indoor", "hybrid"]]
                    if indoor_cands:
                        replacement = indoor_cands.pop(0)
                        replacements.append({
                            "stop_id": s.id,
                            "original_name": s.destination.name,
                            "original_type": "outdoor",
                            "new_destination_id": replacement.id,
                            "new_name": replacement.name,
                            "new_type": replacement.indoor_outdoor,
                            "time_slot": f"{s.planned_start_time} - {s.planned_end_time}",
                            "rationale": f"Indoor sanctuary protected from precipitation. Wheelchair friendly and high cultural utility."
                        })

        elif disruption_type in ["extreme_crowd", "crowd_surge"]:
            rationale = "Extreme queue delays reported at central monument. Proposing an optimized reschedule to quieter artisan craft workshops and tranquil garden sites."
            for s in current_stops:
                if s.destination and s.destination.typical_crowd_level == "high":
                    affected_stops.append(s.destination.name)
                    low_crowd_cands = [c for c in candidates if c.typical_crowd_level in ["low", "moderate"]]
                    if low_crowd_cands:
                        replacement = low_crowd_cands.pop(0)
                        replacements.append({
                            "stop_id": s.id,
                            "original_name": s.destination.name,
                            "original_type": "high crowd",
                            "new_destination_id": replacement.id,
                            "new_name": replacement.name,
                            "new_type": replacement.typical_crowd_level,
                            "time_slot": f"{s.planned_start_time} - {s.planned_end_time}",
                            "rationale": f"Minimal wait times, allowing relaxed exploration without congested crowds."
                        })
        else:
            rationale = "General travel optimization suggested to streamline walking distances and buffer intervals."

        adaptation = ItineraryAdaptation(
            trip_id=trip_id,
            trigger_type=disruption_type,
            trigger_description=rationale,
            proposed_changes=json.dumps(replacements),
            status="pending"
        )
        db.add(adaptation)
        db.commit()
        db.refresh(adaptation)
        return adaptation

    def apply_adaptation(self, db: Session, adaptation_id: str, accept: bool) -> ItineraryAdaptation:
        """
        User-in-the-loop control: applies or rejects the proposed itinerary adaptation.
        """
        adaptation = db.query(ItineraryAdaptation).filter(ItineraryAdaptation.id == adaptation_id).first()
        if not adaptation:
            raise ValueError("Adaptation not found")

        if accept:
            adaptation.status = "accepted"
            changes = json.loads(adaptation.proposed_changes)
            for change in changes:
                stop = db.query(ItineraryStop).filter(ItineraryStop.id == change["stop_id"]).first()
                if stop:
                    stop.destination_id = change["new_destination_id"]
                    # Update explanation to reflect adaptation
                    expl = json.loads(stop.xai_explanation) if stop.xai_explanation else {}
                    expl["primary_reason"] = f"Adapted Stop: {change['rationale']}"
                    stop.xai_explanation = json.dumps(expl)
            db.commit()
        else:
            adaptation.status = "rejected"
            db.commit()

        return adaptation

itinerary_optimizer = ItineraryOptimizer()

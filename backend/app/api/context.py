from typing import Optional, Dict, Any
from fastapi import APIRouter
from pydantic import BaseModel
from ..schemas.context import ContextVector
from ..services.context_service import context_service

router = APIRouter(prefix="/api/context", tags=["Context"])

class ContextSimulationPayload(BaseModel):
    weather_condition: Optional[str] = None # "Sunny", "Rainy", "Overcast"
    crowd_density: Optional[str] = None     # "Low", "Moderate", "High", "Peak"
    traffic_level: Optional[str] = None     # "Light", "Moderate", "Heavy"

@router.get("/current", response_model=ContextVector)
def get_current_context(city: str = "Samarkand", lat: float = 39.6548, lon: float = 66.9757):
    """Retrieve real-time environmental context C = [L, T, W, Tr, Cr, O, P]."""
    return context_service.get_context_vector(city=city, lat=lat, lon=lon)

@router.post("/simulate")
def set_simulation_context(payload: ContextSimulationPayload):
    """Research demo tool: manually inject weather or crowd conditions."""
    overrides = {}
    if payload.weather_condition is not None:
        overrides["weather_condition"] = payload.weather_condition
    if payload.crowd_density is not None:
        overrides["crowd_density"] = payload.crowd_density
    if payload.traffic_level is not None:
        overrides["traffic_level"] = payload.traffic_level

    context_service.set_simulation_override(overrides)
    return {"message": "Simulation overrides updated", "active_overrides": context_service.simulation_override}

@router.post("/reset")
def reset_simulation():
    """Reset simulation overrides back to live real-world conditions."""
    context_service.reset_simulation()
    return {"message": "Simulation reset to live environmental data"}

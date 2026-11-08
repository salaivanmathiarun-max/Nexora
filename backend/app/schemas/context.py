from typing import Optional, List
from pydantic import BaseModel

class WeatherContext(BaseModel):
    temperature_c: float
    weather_condition: str # "Sunny", "Partly Cloudy", "Rainy", "Overcast"
    precipitation_probability: int # 0-100%
    uv_index: float
    is_indoor_preferred: bool = False

class ContextVector(BaseModel):
    location_name: str
    latitude: float
    longitude: float
    current_time: str
    weather: WeatherContext
    traffic_level: str # "Light", "Moderate", "Heavy"
    crowd_density: str # "Low", "Moderate", "High", "Peak"
    active_alerts: List[str] = []

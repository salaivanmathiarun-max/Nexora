import requests
import datetime
from typing import Dict, Any, Optional
from ..schemas.context import ContextVector, WeatherContext
from ..config import settings

class ContextService:
    def __init__(self):
        # Simulation override state for research demonstration
        self.simulation_override: Dict[str, Any] = {}

    def set_simulation_override(self, overrides: Dict[str, Any]):
        """Allows demo controls to simulate sudden rain, extreme crowd, or traffic spikes."""
        self.simulation_override.update(overrides)

    def reset_simulation(self):
        self.simulation_override = {}

    def fetch_live_weather(self, lat: float, lon: float) -> WeatherContext:
        """Fetches live meteorological data from Open-Meteo free API."""
        try:
            url = f"{settings.WEATHER_API_BASE}?latitude={lat}&longitude={lon}&current=temperature_2m,precipitation,weather_code,uv_index"
            resp = requests.get(url, timeout=4)
            if resp.status_code == 200:
                data = resp.json().get("current", {})
                temp = data.get("temperature_2m", 22.0)
                precip = data.get("precipitation", 0.0)
                uv = data.get("uv_index", 3.0)
                code = data.get("weather_code", 0)

                # WMO Weather interpretation codes
                if code in [0, 1]:
                    condition = "Sunny"
                elif code in [2, 3]:
                    condition = "Partly Cloudy"
                elif code in [51, 53, 55, 61, 63, 65, 80, 81, 82]:
                    condition = "Rainy"
                elif code in [71, 73, 75]:
                    condition = "Snowy"
                else:
                    condition = "Overcast"

                return WeatherContext(
                    temperature_c=float(temp),
                    weather_condition=condition,
                    precipitation_probability=int(precip * 30) if precip > 0 else 5,
                    uv_index=float(uv),
                    is_indoor_preferred=(condition == "Rainy" or precip > 1.0)
                )
        except Exception:
            pass

        # Fallback pleasant weather for Samarkand (autumn/spring season)
        return WeatherContext(
            temperature_c=21.5,
            weather_condition="Sunny",
            precipitation_probability=5,
            uv_index=3.8,
            is_indoor_preferred=False
        )

    def get_context_vector(
        self,
        city: str = "Samarkand",
        lat: float = 39.6548,
        lon: float = 66.9757
    ) -> ContextVector:
        """
        Builds Context Vector C = [L, T, W, Tr, Cr, O, P].
        """
        now = datetime.datetime.now()
        current_time_str = now.strftime("%H:%M")
        
        # Weather
        weather = self.fetch_live_weather(lat, lon)
        
        # Default crowd density heuristics (peaking between 11:00-15:00)
        hour = now.hour
        if 11 <= hour <= 15:
            crowd = "High"
            traffic = "Moderate"
        elif 9 <= hour < 11 or 15 < hour <= 18:
            crowd = "Moderate"
            traffic = "Moderate"
        else:
            crowd = "Low"
            traffic = "Light"

        alerts = []

        # Apply simulation overrides if set by research demo controls
        if "weather_condition" in self.simulation_override:
            cond = self.simulation_override["weather_condition"]
            weather.weather_condition = cond
            if cond == "Rainy":
                weather.precipitation_probability = 85
                weather.is_indoor_preferred = True
                alerts.append("Weather Alert: Sudden heavy rain detected in city area.")

        if "crowd_density" in self.simulation_override:
            crowd = self.simulation_override["crowd_density"]
            if crowd in ["High", "Peak"]:
                alerts.append("Crowd Alert: Peak tourist congestion near primary monument squares.")

        if "traffic_level" in self.simulation_override:
            traffic = self.simulation_override["traffic_level"]
            if traffic == "Heavy":
                alerts.append("Traffic Advisory: Road works causing 20+ min transit delays on main avenues.")

        return ContextVector(
            location_name=city,
            latitude=lat,
            longitude=lon,
            current_time=current_time_str,
            weather=weather,
            traffic_level=traffic,
            crowd_density=crowd,
            active_alerts=alerts
        )

context_service = ContextService()

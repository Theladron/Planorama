from typing import Optional, Dict
from app.external_services.weather_api import get_weather_forecast


class WeatherApiConnector:
    def __init__(self):
        pass

    def get_weather_forecast(self, lat: float, lon: float) -> Optional[Dict]:
        return get_weather_forecast(lat, lon)
"""Weather API connector for forecast data."""
from typing import Optional, Dict
from app.external_services.weather_api import get_weather_forecast


class WeatherApiConnector:
    """Connector for Open-Meteo weather API."""
    
    def __init__(self):
        """Initialize the Weather API connector."""

    def get_weather_forecast(self, lat: float, lon: float) -> Optional[Dict]:
        """Get weather forecast for a location.
        
        Args:
            lat: Latitude coordinate.
            lon: Longitude coordinate.
            
        Returns:
            Dictionary with current weather and forecast data, or None if failed.
        """
        return get_weather_forecast(lat, lon)
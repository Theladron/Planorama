"""AI connector for fetching suggestions and transport options."""
from typing import List, Optional
from app.external_services import ai_suggestions


class AiConnector:
    """Connector for AI-powered suggestions using Perplexity API."""
    
    def __init__(self, api_key: str):
        """Initialize the AI connector.
        
        Args:
            api_key: Perplexity API key.
        """
        self.api_key = api_key

    def fetch_suggestions(self, town_name: str,
        lat: float,
        lon: float,
        language: str,
        content_type: str) -> Optional[List]:
        """Fetch local item suggestions for a location.
        
        Args:
            town_name: Name of the town or location.
            lat: Latitude coordinate.
            lon: Longitude coordinate.
            language: Language code ('en' or 'de').
            content_type: Type of content to fetch (e.g., 'campsites', 'hotels').
            
        Returns:
            List of suggestion dictionaries or None if failed.
        """
        return ai_suggestions.fetch_local_items(self.api_key, town_name, lat, lon,
                                                language, content_type)

    def fetch_public_transport(self, start_city: str,
        start_lat: float,
        start_lon: float,
        end_city: str,
        end_lat: float,
        end_lon: float,
        language: str) -> Optional[List]:
        """Fetch public transport options between two cities.
        
        Args:
            start_city: Starting city name.
            start_lat: Starting latitude.
            start_lon: Starting longitude.
            end_city: Destination city name.
            end_lat: Destination latitude.
            end_lon: Destination longitude.
            language: Language code ('en' or 'de').
            
        Returns:
            List of transport route dictionaries or None if failed.
        """
        return ai_suggestions.fetch_public_transport(self.api_key, start_city, start_lat, start_lon,
                                                    end_city, end_lat, end_lon, language)
"""OpenRouteService connector for geocoding and routing."""
import openrouteservice
from typing import List, Optional
from app.external_services import openroute


class OpenRouteConnector:
    """Connector for OpenRouteService API."""
    
    def __init__(self, api_key: str):
        """Initialize the OpenRoute connector.
        
        Args:
            api_key: OpenRouteService API key.
        """
        self.client = openrouteservice.Client(key=api_key)

    def get_location_info(self, town_name: str) -> Optional[dict]:
        """Get location information (coordinates and country) for a town.
        
        Args:
            town_name: Name of the town to geocode.
            
        Returns:
            Dictionary with 'lat', 'lon', and 'country' keys, or None if not found.
        """
        return openroute.geocode_town(self.client, town_name)

    def get_route_info(self, start_town: str, end_town: str) -> Optional[tuple[list[str], str]]:
        """Get driving directions between two towns.
        
        Args:
            start_town: Starting town name.
            end_town: Destination town name.
            
        Returns:
            Tuple of (directions_list, readable_duration) or None if failed.
        """
        return openroute.get_route_directions(self.client, start_town, end_town)

    def get_full_route_by_coords(
            self,
            start_lat: float, start_lon: float,
            end_lat: float, end_lon: float) -> Optional[dict]:
        """Get full route data including polyline coordinates.
        
        Args:
            start_lat: Starting latitude.
            start_lon: Starting longitude.
            end_lat: Destination latitude.
            end_lon: Destination longitude.
            
        Returns:
            Dictionary with polyline, duration, and directions, or None if failed.
        """
        return openroute.get_full_route_data_by_coords(
            self.client,
            start_lat, start_lon,
            end_lat, end_lon
        )
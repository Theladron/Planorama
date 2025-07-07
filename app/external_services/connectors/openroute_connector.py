import openrouteservice
from typing import List, Optional
from app.external_services import openroute


class OpenRouteConnector:
    def __init__(self, api_key: str):
        self.client = openrouteservice.Client(key=api_key)

    def get_location_info(self, town_name: str) -> Optional[dict]:
        return openroute.geocode_town(self.client, town_name)

    def get_route_info(self, start_town: str, end_town: str) -> Optional[tuple[list[str], str]]:
        return openroute.get_route_directions(self.client, start_town, end_town)

    def get_full_route_by_coords(
            self,
            start_lat: float, start_lon: float,
            end_lat: float, end_lon: float) -> Optional[dict]:
        return openroute.get_full_route_data_by_coords(
            self.client,
            start_lat, start_lon,
            end_lat, end_lon
        )
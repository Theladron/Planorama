import openrouteservice
from typing import List, Optional
from app.external_services import openroute


class OpenRouteConnector:
    def __init__(self, api_key: str):
        self.client = openrouteservice.Client(key=api_key)

    def get_coordinates_for_town(self, town_name: str) -> Optional[dict]:
        return openroute.geocode_town(self.client, town_name)

    def get_turn_by_turn_directions(self, start_town: str, end_town: str) -> Optional[List[str]]:
        return openroute.get_route_directions(self.client, start_town, end_town)
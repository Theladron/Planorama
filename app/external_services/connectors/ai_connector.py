from typing import List, Optional
from app.external_services import ai_suggestions


class AiConnector:
    def __init__(self, api_key: str):
        self.api_key = api_key

    def fetch_suggestions(self, town_name: str,
        lat: float,
        lon: float,
        language: str,
        content_type: str) -> Optional[List]:
        return ai_suggestions.fetch_local_items(self.api_key, town_name, lat, lon,
                                                language, content_type)
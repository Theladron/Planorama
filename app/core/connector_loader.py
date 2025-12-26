"""External service connector initialization."""
from app.core.config_loader import settings
from app.external_services.connectors.openroute_connector import OpenRouteConnector
from app.external_services.connectors.googletrans_connector import GoogleTranslateConnector
from app.external_services.connectors.weather_api_connector import WeatherApiConnector
from app.external_services.connectors.ai_connector import AiConnector
openroute_connector = OpenRouteConnector(api_key=settings.ORS_API_KEY)

googletrans_connector = GoogleTranslateConnector()

weather_api_connector = WeatherApiConnector()

ai_connector = AiConnector(settings.AI_API_KEY)
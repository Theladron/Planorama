from app.core.config_loader import settings
from app.external_services.connectors.openroute_connector import OpenRouteConnector
from app.external_services.connectors.googletrans_connector import GoogleTranslateConnector
from app.external_services.connectors.weather_api_connector import WeatherApiConnector

openroute_connector = OpenRouteConnector(api_key=settings.ORS_API_KEY)

googletrans_connector = GoogleTranslateConnector()

weather_api_connector = WeatherApiConnector()
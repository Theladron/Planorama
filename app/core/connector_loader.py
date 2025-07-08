from app.core.config_loader import settings
from app.external_services.connectors.openroute_connector import OpenRouteConnector
from app.external_services.connectors.googletrans_connector import GoogleTranslateConnector

openroute_connector = OpenRouteConnector(api_key=settings.ORS_API_KEY)

googletrans_connector = GoogleTranslateConnector()
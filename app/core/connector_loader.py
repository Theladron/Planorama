from app.core.config_loader import settings
from app.external_services.connectors.openroute_connector import OpenRouteConnector

openroute_connector = OpenRouteConnector(api_key=settings.ORS_API_KEY)
from fastapi import APIRouter, Depends, Query
from fastapi.exceptions import HTTPException
from app.core.connector_loader import openroute_connector, weather_api_connector, ai_connector
from app.auth.services import get_current_active_user
from app.users.models import User

frontend_router = APIRouter(tags=["OpenRoute"])

@frontend_router.get("/full-route-by-coords",
                     summary="Get full route data using coordinates",
                     include_in_schema=False)
def get_full_route_by_coords(
    start_lat: float = Query(...),
    start_lon: float = Query(...),
    end_lat: float = Query(...),
    end_lon: float = Query(...),
    current_user: User = Depends(get_current_active_user)
):
    data = openroute_connector.get_full_route_by_coords(
        start_lat, start_lon, end_lat, end_lon
    )
    if not data:
        raise HTTPException(status_code=404, detail="Route data could not be retrieved.")
    return data


@frontend_router.get("/weather",
                     summary="Get weather forecast for a location",
                     include_in_schema=False)
def get_weather_forecast(
    lat: float = Query(...),
    lon: float = Query(...),
    current_user: User = Depends(get_current_active_user)
):
    data = weather_api_connector.get_weather_forecast(lat, lon)
    if not data:
        raise HTTPException(status_code=404, detail="Weather data could not be retrieved.")
    return data


@frontend_router.get("/ai-suggestions",
                     summary="Get AI-powered location-based suggestions",
                     include_in_schema=False)
def get_ai_suggestions(
    town_name: str = Query(..., description="Name of the town or city"),
    lat: float = Query(..., description="Latitude of the location"),
    lon: float = Query(..., description="Longitude of the location"),
    language: str = Query("en", description="Language for the result, e.g., 'en' or 'de'"),
    content_type: str = Query(..., description="Type of content to fetch, e.g., 'campsites', 'hotels', 'activities'"),
    current_user: User = Depends(get_current_active_user)
):
    suggestions = ai_connector.fetch_suggestions(
        town_name=town_name,
        lat=lat,
        lon=lon,
        language=language,
        content_type=content_type
    )

    if not suggestions:
        raise HTTPException(status_code=404, detail="No suggestions could be generated.")

    return suggestions
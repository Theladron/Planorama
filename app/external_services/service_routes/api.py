from fastapi import APIRouter, Depends, Query
from fastapi.exceptions import HTTPException
from app.core.connector_loader import openroute_connector
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
    current_user: User = Depends(get_current_active_user)   # <--- hier Auth erzwingen
):
    data = openroute_connector.get_full_route_by_coords(
        start_lat, start_lon, end_lat, end_lon
    )
    if not data:
        raise HTTPException(status_code=404, detail="Route data could not be retrieved.")
    return data
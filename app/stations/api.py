from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.auth.services import get_current_active_user
from app.core.database import get_db
from app.users.models import User
from app.stations.schemas import (
    StationCreate,
    StationSchema,
    StationReorderItem,
    StationsReorderRequest
)
from app.stations.services import (
    get_all_stations,
    create_station,
    reorder_stations,
    delete_station,
    admin_delete_station,
    get_station,
    get_stations_by_trip
)

station_router = APIRouter(prefix="/stations", tags=["Stations"])
admin_station_router = APIRouter(prefix="/admin/stations", tags=["Admin"])


@station_router.post(
    "/",
    response_model=StationSchema,
    summary="Create a new station for a user's trip",
    description=(
        "Creates a new station and links it to one of the current user's trips via the linking table. "
        "Each trip day can only have one station assigned, so you cannot add multiple stations with the same day_number. "
        "The day_number and trip_id provided are stored in the linking table, not directly on the station. "
        "The station's day_number must fall within the trip's duration. "
        "Coordinates are automatically retrieved from an external service."
    )
)
async def create_new_station(
    station: StationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    if station.trip_id <= 0:
        raise HTTPException(status_code=400, detail="Invalid trip_id")
    return await create_station(db, station, current_user.id)


@station_router.get(
    "/by-trip/{trip_id}",
    response_model=list[StationSchema],
    summary="Get all stations for a trip",
    description=(
            "Returns all stations linked to a trip belonging to the current user, "
            "ordered by day_number as stored in the linking table."
    )
)
def list_stations_for_trip(
    trip_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    if trip_id <= 0:
        raise HTTPException(status_code=400, detail="Invalid trip_id")
    stations = get_stations_by_trip(db, trip_id, current_user.id)
    if stations is None:
        raise HTTPException(status_code=404, detail="Trip not found or not authorized")
    return stations


@station_router.put(
    "/reorder",
    response_model=list[StationSchema],
    summary="Bulk reorder stations by updating their day_numbers",
    description=(
            "Reorders multiple stations within a specified trip owned by the current user "
            "by updating their day_numbers in the linking table. "
            "Each station must have a unique day_number within the trip. "
            "Consecutive duplicate station names will be handled automatically."
    ),
)
def put_reorder_stations(
    reorder_request: StationsReorderRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    if not reorder_request.stations:
        raise HTTPException(status_code=400, detail="Station list cannot be empty")
    if reorder_request.trip_id <= 0:
        raise HTTPException(status_code=400, detail="Invalid trip_id")

    try:
        return reorder_stations(
            db=db,
            trip_id=reorder_request.trip_id,
            reorder_items=reorder_request.stations,
            user_id=current_user.id,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@station_router.delete(
    "/{station_id}",
    summary="Delete a station owned by the user",
    description="Deletes a station if it belongs to one of the current user's trips."
)
def user_delete_station(
    station_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    if station_id <= 0:
        raise HTTPException(status_code=400, detail="Invalid station_id")
    success = delete_station(db, station_id, current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="Station not found or not authorized")
    return {"message": "Station deleted"}


@admin_station_router.get(
    "/",
    response_model=list[StationSchema],
    summary="Admin: List all stations",
    description="Returns a list of all stations in the system. Admin access required."
)
def admin_list_all_stations(db: Session = Depends(get_db)):
    return get_all_stations(db)


@admin_station_router.delete(
    "/{station_id}",
    summary="Admin: Delete any station by ID",
    description="Allows an admin to delete any station by its ID."
)
def admin_delete_station_by_id(station_id: int, db: Session = Depends(get_db)):
    if station_id <= 0:
        raise HTTPException(status_code=400, detail="Invalid station_id")
    success = admin_delete_station(db, station_id)
    if not success:
        raise HTTPException(status_code=404, detail="Station not found")
    return {"message": "Station deleted"}

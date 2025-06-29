from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.auth.services import get_current_active_user
from app.core.database import get_db
from app.users.models import User
from app.stations.schemas import StationCreate, StationSchema, StationUpdate
from app.stations.services import (
    get_all_stations, create_station, update_station,
    delete_station, admin_delete_station, get_station
)

station_router = APIRouter(prefix="/stations", tags=["Stations"])
admin_station_router = APIRouter(prefix="/admin/stations", tags=["Admin"])


@station_router.post(
    "/",
    response_model=StationSchema,
    summary="Create a new station for a user's trip",
    description=(
        "Creates a new station linked to one of the current user's trips. "
        "Validates that the station's day_number fits within the trip duration and "
        "retrieves coordinates from an external service."
    )
)
async def create_new_station(
    station: StationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    return await create_station(db, station, current_user.id)


@station_router.patch(
    "/{station_id}",
    response_model=StationSchema,
    summary="Update a station's day number",
    description=(
        "Allows the owner of the station's trip to update the day_number of the station. "
        "Validates the new day_number is within the trip's duration."
    )
)
def patch_station(
    station_id: int,
    update: StationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    return update_station(db, station_id, update, current_user.id)


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
    delete_station(db, station_id, current_user.id)
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
    admin_delete_station(db, station_id)
    return {"message": "Station deleted"}

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.auth.services import get_current_active_user, get_current_admin_user
from app.users.models import User
from app.trips.schemas import TripCreate, TripSchema, TripUpdate
from app.trips.services import (
    get_trips, get_trip,
    get_user_trips, create_trip,
    delete_trip, update_trip
)

trip_router = APIRouter(
    prefix="/trips",
    tags=["Trips"]
)

admin_trip_router = APIRouter(
    prefix="/admin/trips",
    tags=["Admin"]
)


@trip_router.get(
    "/me",
    response_model=list[TripSchema],
    summary="List trips for current user",
    description="Returns a list of trips that belong to the currently authenticated user."
)
def list_user_trips(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    return get_user_trips(db, current_user.id)


@trip_router.get(
    "/{trip_id}",
    response_model=TripSchema,
    summary="Get trip by ID",
    description="Fetches details of a specific trip. Only the owner can access it."
)
def trip_detail(
    trip_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    trip = get_trip(db, trip_id)
    if not trip or trip.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Trip not found or access denied")
    return trip


@trip_router.post(
    "/",
    response_model=TripSchema,
    summary="Create a new trip for current user",
    description="Creates a new trip assigned to the current user."
)
def create_new_trip(
    trip_data: TripCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    try:
        return create_trip(db, trip_data, current_user.id)
    except Exception as error:
        raise HTTPException(status_code=400, detail=str(error))


@trip_router.put(
    "/{trip_id}",
    response_model=TripSchema,
    summary="Update a user's trip",
    description="Only the trip owner can update the trip. Dates must still fit existing stations."
)
def update_user_trip(
    trip_id: int,
    trip_update: TripUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    trip = get_trip(db, trip_id)
    if not trip or trip.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Trip not found or unauthorized")
    try:
        return update_trip(db, trip_id, trip_update)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))


@trip_router.delete(
    "/{trip_id}",
    summary="Delete a user's trip",
    description="Only the trip owner can delete it."
)
def delete_trip_by_id(
    trip_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    trip = get_trip(db, trip_id)
    if not trip or trip.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Trip not found or unauthorized")
    delete_trip(db, trip_id)
    return {"message": "Trip deleted"}


@admin_trip_router.get(
    "/",
    response_model=list[TripSchema],
    summary="Admin: List all trips",
    description="Returns a list of all trips in the system. Requires admin privileges."
)
def list_all_trips(
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin_user)
):
    return get_trips(db)


@admin_trip_router.delete(
    "/{trip_id}",
    summary="Admin: Delete any trip by ID",
    description="Allows an admin user to delete any trip."
)
def admin_delete_trip_by_id(
    trip_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin_user)
):
    trip = get_trip(db, trip_id)
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")
    delete_trip(db, trip_id)
    return {"message": "Trip deleted by admin"}

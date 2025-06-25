from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.auth.services import get_current_active_user
from app.users.models import User
from app.trips.schemas import TripCreate, TripSchema
from app.trips.services import get_trips, get_trip, get_user_trips, create_trip, delete_trip

trip_router = APIRouter(
    prefix="/trips",
    tags=["Trips"]
)
admin_trip_router = APIRouter(
    prefix="/admin/trips",
    tags=["Admin"]
)

@admin_trip_router.get("/", response_model=list[TripSchema])
def list_trips(db: Session = Depends(get_db)):
    return get_trips(db)


@trip_router.get("/me", response_model=list[TripSchema])
def list_user_trips(current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    return get_user_trips(db, current_user.id)


@trip_router.get("/{trip_id}", response_model=TripSchema)
def trip_detail(trip_id: int, db: Session = Depends(get_db)):
    db_trip = get_trip(db, trip_id)
    if not db_trip:
        raise HTTPException(status_code=404, detail="Trip not found")
    return db_trip


@trip_router.post("/", response_model=TripSchema)
def create_new_trip(trip: TripCreate, db: Session = Depends(get_db)):
    return create_trip(db, trip)


@trip_router.delete("/{trip_id}")
def delete_trip_by_id(trip_id: int, db: Session = Depends(get_db)):
    db_trip = get_trip(db, trip_id)
    if not db_trip:
        raise HTTPException(status_code=404, detail="Trip not found")
    delete_trip(db, trip_id)
    return {"message": "Trip deleted"}

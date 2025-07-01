from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.auth.services import get_current_active_user
from app.users.models import User
from app.travel.schemas import TravelSchema
from app.travel.services import (
    get_user_travel_for_trip,
    get_user_travel_by_day
)

travel_router = APIRouter(
    prefix="/travel",
    tags=["Travel"]
)

@travel_router.get("/trip/{trip_id}", response_model=list[TravelSchema],
                   summary="Get all travel routes for a trip")
def get_travel_routes_for_trip(
    trip_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    return get_user_travel_for_trip(db, trip_id, current_user.id)


@travel_router.get("/trip/{trip_id}/day/{day_number}", response_model=TravelSchema,
                   summary="Get travel route for a specific day")
def get_travel_by_trip_and_day(
    trip_id: int,
    day_number: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    travel = get_user_travel_by_day(db, trip_id, day_number, current_user.id)
    if not travel:
        raise HTTPException(status_code=404, detail="Travel not found")
    return travel

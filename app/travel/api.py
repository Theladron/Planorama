from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.auth.services import get_current_active_user, get_current_admin_user
from app.users.models import User
from app.travel.schemas import TravelSchema, TravelCreate
from app.travel.services import (
    create_travel,
    get_user_travel_for_trip,
    delete_travel,
    get_travel_by_id,
    get_travels_by_user,
    update_transport_method
)

travel_router = APIRouter(
    prefix="/travel",
    tags=["Travel"]
)

admin_travel_router = APIRouter(
    prefix="/admin/travel",
    tags=["Admin"]
)


@travel_router.post("/", response_model=TravelSchema, summary="Create a travel route", description="""
Creates a travel route between two stations in one of the user's trips.  
- Requires: `trip_id`, `from_station_id`, `to_station_id`  
- Automatically fetches directions from external_services.  
- Will attempt fallback to alternate transportation if routing fails.
""")
def create_user_travel(
    travel: TravelCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    return create_travel(db, travel, current_user.id)


@travel_router.get("/trip/{trip_id}", response_model=list[TravelSchema], summary="Get all travels for a trip", description="""
Returns all travel segments for a given trip.  
- Only accessible if the trip belongs to the current user.
""")
def get_travel_routes_for_trip(
    trip_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    return get_user_travel_for_trip(db, trip_id, current_user.id)


@travel_router.patch("/{travel_id}", response_model=TravelSchema, summary="Request alternate travel option", description="""
Requests a new alternate travel option (e.g. public transport, flight) between the existing route.  
- Updates `method_of_transport` and `cost_euros` using external_services.
""")
def update_travel_option(
    travel_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    return update_transport_method(db, travel_id, current_user.id)


@travel_router.delete("/{travel_id}", summary="Delete travel", description="""
Deletes a travel route if it belongs to a trip owned by the user.
""")
def delete_user_travel(
    travel_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    db_travel = get_travel_by_id(db, travel_id)
    if not db_travel or db_travel.trip.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Travel not found or unauthorized")

    delete_travel(db, travel_id)
    return {"message": "Travel deleted"}


@admin_travel_router.get("/user/{user_id}", response_model=list[TravelSchema], summary="Admin: Get travels by user", description="""
Returns all travel segments for a specific user.  
Admin access required.
""")
def admin_get_user_travels(
    user_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin_user)
):
    return get_travels_by_user(db, user_id)


@admin_travel_router.delete("/{travel_id}", summary="Admin: Delete travel", description="""
Deletes a travel segment by ID.  
Admin access required.
""")
def admin_delete_travel(
    travel_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin_user)
):
    db_travel = get_travel_by_id(db, travel_id)
    if not db_travel:
        raise HTTPException(status_code=404, detail="Travel not found")

    delete_travel(db, travel_id)
    return {"message": "Travel deleted"}

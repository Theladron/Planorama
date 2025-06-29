from typing import TYPE_CHECKING, List, Optional, Any, cast

from sqlalchemy.orm import Session, joinedload
from fastapi import HTTPException

from app.travel.schemas import TravelCreate
from app.travel.models import Travel
from app.trips.services import get_trip

if TYPE_CHECKING:
    from app.trips.models import Trip

def create_travel(db: Session, travel_data: TravelCreate, user_id: int) -> Travel:
    pass

def get_user_travel_for_trip(db: Session, trip_id: int, user_id: int) -> List[Travel]:
    trip = get_trip(db, trip_id)
    if not trip or trip.user_id != user_id:
        raise HTTPException(status_code=403, detail="Unauthorized trip")

    travels = cast(List[Travel], (
        db.query(Travel)
        .options(joinedload(Travel.trip))
        .filter(Travel.trip_id == trip_id)
        .all()
    ))
    return travels


def get_travel_by_id(db: Session, travel_id: int) -> Optional[Travel]:
    return db.query(Travel).filter_by(id=travel_id).first()


def delete_travel(db: Session, travel_id: int):
    travel = get_travel_by_id(db, travel_id)
    if travel:
        db.delete(travel)
        db.commit()


def update_transport_method(db: Session, travel_id: int, user_id: int) -> Travel:
    travel = cast(Optional[Travel], (
        db.query(Travel)
        .options(joinedload(Travel.trip))
        .filter(Travel.id == travel_id)
        .first()
    ))

    if not travel or not travel.trip:
        raise HTTPException(status_code=403, detail="Unauthorized travel update")

    trip = cast("Trip", travel.trip)  # cast the relationship attribute explicitly

    if trip.user_id != user_id:
        raise HTTPException(status_code=403, detail="Unauthorized travel update")

    alt = get_alternative_transport(travel.from_station_id, travel.to_station_id)
    if not alt:
        raise HTTPException(status_code=502, detail="Could not retrieve alternate transport")

    travel.method_of_transport = alt["method"]
    travel.cost_euros = alt.get("estimated_cost")
    travel.travel_route_description = alt["route"]
    db.commit()
    db.refresh(travel)
    return travel


def get_travels_by_user(db: Session, user_id: int) -> List[Travel]:
    travels = cast(List[Travel], (
        db.query(Travel)
        .join(Travel.trip)
        .options(joinedload(Travel.trip))
        .filter(Travel.trip.has(user_id=user_id))
        .all()
    ))
    return travels

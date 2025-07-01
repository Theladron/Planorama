from typing import List, Optional, cast
from sqlalchemy.orm import Session, joinedload
from fastapi import HTTPException
from app.core.connector_loader import openroute_connector
from app.travel.models import Travel
from app.trips.services import get_trip
from app.stations.models import Station


def get_user_travel_for_trip(db: Session, trip_id: int, user_id: int) -> List[Travel]:
    trip = get_trip(db, trip_id)
    if not trip or trip.user_id != user_id:
        raise HTTPException(status_code=403, detail="Unauthorized trip access")

    travels = cast(List[Travel], (
        db.query(Travel)
        .filter(Travel.trip_id == trip_id)
        .order_by(Travel.id)
        .all()
    ))
    return travels


def get_user_travel_by_day(db: Session, trip_id: int,
                           day_number: int, user_id: int) -> Optional[Travel]:
    trip = get_trip(db, trip_id)
    if not trip or trip.user_id != user_id:
        raise HTTPException(status_code=403, detail="Unauthorized trip access")

    station = db.query(Station).filter_by(trip_id=trip_id, day_number=day_number).first()
    if not station:
        return None

    travel = db.query(Travel).filter_by(trip_id=trip_id, to_station_id=station.id).first()
    return travel

def create_travel_entry(
    db: Session,
    trip_id: int,
    from_station_id: int,
    to_station_id: int,
    from_town: str,
    to_town: str,
    connector: openroute_connector
) -> Travel:
    try:
        route_data = connector.get_route_info(from_town, to_town)
    except Exception:

        route_data = None

    # Validate town names
    if not from_town or not to_town:
        raise ValueError("Both from_town and to_town must be provided")

    if route_data and isinstance(route_data, tuple) and len(route_data) == 2:
        directions, duration = route_data
        travel = Travel(
            trip_id=trip_id,
            from_station_id=from_station_id,
            to_station_id=to_station_id,
            method_of_transport="car",
            cost_euros=None,
            travel_route_description={"directions": directions},
            time_estimated=duration
        )
    else:
        # Fallback scenario: route data missing or malformed
        travel = Travel(
            trip_id=trip_id,
            from_station_id=from_station_id,
            to_station_id=to_station_id,
            method_of_transport="plane",
            cost_euros=None,
            travel_route_description=None,
            time_estimated=None
        )

    try:
        db.add(travel)
        db.commit()
        db.refresh(travel)
    except Exception as db_err:
        db.rollback()
        raise db_err

    return travel

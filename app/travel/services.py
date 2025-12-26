"""Travel route management service functions."""
from typing import List, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.core.connector_loader import openroute_connector
from app.travel.models import Travel
from app.trips.services import get_trip
from app.trip_stations.models import TripStation


def get_user_travel_for_trip(db: Session, trip_id: int, user_id: int) -> List[Travel]:
    """Retrieve all travel routes for a specific trip.
    
    Args:
        db: Database session.
        trip_id: Unique trip identifier.
        user_id: Unique user identifier for authorization.
        
    Returns:
        List of Travel objects for the trip.
        
    Raises:
        HTTPException: If user is unauthorized to access the trip.
    """
    trip = get_trip(db, trip_id)
    if not trip or trip.user_id != user_id:
        raise HTTPException(status_code=403, detail="Unauthorized trip access")

    return (
        db.query(Travel)
        .filter(Travel.trip_id == trip_id)
        .order_by(Travel.id)
        .all()
    )


def get_user_travel_by_day(db: Session, trip_id: int,
                           day_number: int, user_id: int) -> Optional[Travel]:
    """Retrieve travel route for a specific day within a trip.
    
    Args:
        db: Database session.
        trip_id: Unique trip identifier.
        day_number: Day number within the trip.
        user_id: Unique user identifier for authorization.
        
    Returns:
        Travel object if found, None otherwise.
        
    Raises:
        HTTPException: If user is unauthorized to access the trip.
    """
    trip = get_trip(db, trip_id)
    if not trip or trip.user_id != user_id:
        raise HTTPException(status_code=403, detail="Unauthorized trip access")

    trip_station = db.query(TripStation).filter_by(trip_id=trip_id, day_number=day_number).first()
    if not trip_station:
        return None

    travel = db.query(Travel).filter_by(trip_id=trip_id, to_station_id=trip_station.station_id).first()
    return travel


def create_travel_entry(
    db: Session,
    trip_id: int,
    from_station_id: int,
    to_station_id: int,
    from_town: str,
    to_town: str,
) -> Travel:
    """Create a travel entry between two stations.
    
    Attempts to fetch route information from OpenRouteService API.
    Falls back to a placeholder entry if routing fails.
    
    Args:
        db: Database session.
        trip_id: Unique trip identifier.
        from_station_id: Source station ID.
        to_station_id: Destination station ID.
        from_town: Source town name for routing.
        to_town: Destination town name for routing.
        
    Returns:
        Created Travel object.
        
    Raises:
        ValueError: If town names are not provided.
        Exception: If database operation fails.
    """
    if not from_town or not to_town:
        raise ValueError("Both from_town and to_town must be provided")

    try:
        route_data = openroute_connector.get_route_info(from_town, to_town)
    except Exception:
        route_data = None

    if (
        route_data
        and isinstance(route_data, tuple)
        and len(route_data) == 2
        and isinstance(route_data[0], list)
        and isinstance(route_data[1], str)
    ):
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

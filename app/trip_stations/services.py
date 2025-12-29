"""TripStation relationship management service functions."""
from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.trip_stations.models import TripStation
from app.trip_stations.schemas import TripStationCreate, TripStationReorderItem
from app.trips.models import Trip
from app.travel.services import create_travel_entry
from app.travel.models import Travel
from app.stations.models import Station
from typing import List


def get_trip_station_by_trip_and_day(db: Session, trip_id: int, day_number: int) -> TripStation | None:
    """Retrieve a TripStation by trip ID and day number.
    
    Args:
        db: Database session.
        trip_id: Unique trip identifier.
        day_number: Day number within the trip.
        
    Returns:
        TripStation object if found, None otherwise.
    """
    return db.query(TripStation)\
        .filter_by(trip_id=trip_id, day_number=day_number)\
        .first()


def get_trip_stations_for_trip(db: Session, trip_id: int) -> List[TripStation]:
    """Retrieve all TripStations for a specific trip.
    
    Args:
        db: Database session.
        trip_id: Unique trip identifier.
        
    Returns:
        List of TripStation objects ordered by day_number.
    """
    return db.query(TripStation)\
        .filter_by(trip_id=trip_id)\
        .order_by(TripStation.day_number)\
        .all()


def create_trip_station(db: Session, data: TripStationCreate) -> TripStation:
    """Create a new TripStation link between a trip and station.
    
    Args:
        db: Database session.
        data: TripStationCreate schema with trip, station, and day information.
        
    Returns:
        Created TripStation object.
        
    Raises:
        HTTPException: If trip or station not found, or link already exists.
    """
    trip = db.query(Trip).filter_by(id=data.trip_id).first()
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")

    station = db.query(Station).filter_by(id=data.station_id).first()
    if not station:
        raise HTTPException(status_code=404, detail="Station not found")

    existing = db.query(TripStation).filter_by(
        trip_id=data.trip_id,
        station_id=data.station_id,
        day_number=data.day_number
    ).first()

    if existing:
        raise HTTPException(status_code=400, detail="TripStation entry already exists")

    trip_station = TripStation(**data.model_dump())
    db.add(trip_station)
    db.commit()
    db.refresh(trip_station)

    sync_travel_routes_for_trip_stations(db, data.trip_id)

    return trip_station



def delete_trip_station(db: Session, trip_id: int, day_number: int, user_id: str):
    """Delete a TripStation link and clean up orphaned stations.
    
    Args:
        db: Database session.
        trip_id: Unique trip identifier.
        day_number: Day number of the station to remove.
        user_id: Auth0 user identifier for authorization.
        
    Returns:
        Dictionary with success message.
        
    Raises:
        HTTPException: If validation fails, trip/station not found, or unauthorized.
    """
    from app.stations.services import _remove_country_if_unused

    if day_number <= 0:
        raise HTTPException(status_code=400, detail="Invalid day number")

    trip = db.query(Trip).filter_by(id=trip_id).first()
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")

    if trip.user_id != user_id:
        raise HTTPException(status_code=403, detail="Unauthorized")

    trip_station = get_trip_station_by_trip_and_day(db, trip_id, day_number)
    if not trip_station:
        raise HTTPException(status_code=404, detail="TripStation not found")

    station = trip_station.station
    country_to_check = station.country

    db.delete(trip_station)
    db.commit()

    other_links = db.query(TripStation).filter_by(station_id=station.id).count()
    if other_links == 0:
        db.delete(station)
        db.commit()
        _remove_country_if_unused(db, trip, country_to_check)

    trip_stations = (
        db.query(TripStation)
        .filter_by(trip_id=trip_id)
        .order_by(TripStation.day_number)
        .all()
    )

    to_delete = []
    previous_name = None
    for ts in trip_stations:
        current_name = ts.station.station_name
        if current_name == previous_name:
            to_delete.append(ts)
        else:
            previous_name = current_name

    for ts in to_delete:
        db.delete(ts)
    db.commit()

    sync_travel_routes_for_trip_stations(db, trip_id)

    return {"detail": "Station unlinked from trip successfully"}


def sync_travel_routes_for_trip_stations(db: Session, trip_id: int):
    """Synchronize travel routes with current trip station configuration.
    
    Creates travel entries for consecutive station pairs and removes
    travel entries for station pairs that no longer exist.
    
    Args:
        db: Database session.
        trip_id: Unique trip identifier.
    """
    trip_stations = (
        db.query(TripStation)
        .filter_by(trip_id=trip_id)
        .order_by(TripStation.day_number)
        .all()
    )

    existing_travel_segments = db.query(Travel).filter_by(trip_id=trip_id).all()

    expected_station_pairs = [
        (
            trip_stations[i].station_id,
            trip_stations[i + 1].station_id
        )
        for i in range(len(trip_stations) - 1)
    ]

    expected_pair_set = set(expected_station_pairs)

    for travel_segment in existing_travel_segments:
        if (travel_segment.from_station_id, travel_segment.to_station_id) not in expected_pair_set:
            db.delete(travel_segment)

    for from_station_id, to_station_id in expected_station_pairs:
        segment_exists = any(
            travel_segment.from_station_id == from_station_id and
            travel_segment.to_station_id == to_station_id
            for travel_segment in existing_travel_segments
        )
        if not segment_exists:
            from_station = db.query(Station).filter_by(id=from_station_id).first()
            to_station = db.query(Station).filter_by(id=to_station_id).first()
            
            if not from_station or not to_station:
                raise ValueError(f"Station not found: from={from_station_id}, to={to_station_id}")

            create_travel_entry(
                db=db,
                trip_id=trip_id,
                from_station_id=from_station_id,
                to_station_id=to_station_id,
                from_town=from_station.station_name,
                to_town=to_station.station_name
            )

    db.commit()



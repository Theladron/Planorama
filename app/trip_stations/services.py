from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.trip_stations.models import TripStation
from app.trip_stations.schemas import TripStationCreate, TripStationReorderItem
from app.trips.models import Trip
from app.stations.models import Station
from typing import List


def get_trip_station_by_id(db: Session, trip_station_id: int) -> TripStation | None:
    return db.query(TripStation).filter_by(id=trip_station_id).first()


def get_trip_stations_for_trip(db: Session, trip_id: int) -> List[TripStation]:
    return db.query(TripStation)\
        .filter_by(trip_id=trip_id)\
        .order_by(TripStation.day_number)\
        .all()


def create_trip_station(db: Session, data: TripStationCreate) -> TripStation:
    trip = db.query(Trip).filter_by(id=data.trip_id).first()
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")

    station = db.query(Station).filter_by(id=data.station_id).first()
    if not station:
        raise HTTPException(status_code=404, detail="Station not found")

    # Check for duplicate constraint manually to fail early
    existing = db.query(TripStation).filter_by(
        trip_id=data.trip_id,
        station_id=data.station_id,
        day_number=data.day_number
    ).first()

    if existing:
        raise HTTPException(status_code=400, detail="TripStation entry already exists")

    trip_station = TripStation(**data.dict())
    db.add(trip_station)
    db.commit()
    db.refresh(trip_station)
    return trip_station


def delete_trip_station(db: Session, trip_station_id: int):
    trip_station = get_trip_station_by_id(db, trip_station_id)
    if not trip_station:
        raise HTTPException(status_code=404, detail="TripStation not found")

    db.delete(trip_station)
    db.commit()
    return {"detail": "TripStation deleted successfully"}


def get_trip_station_by_trip_and_day(db: Session, trip_id: int, day_number: int) -> TripStation | None:
    return db.query(TripStation)\
        .filter_by(trip_id=trip_id, day_number=day_number)\
        .first()


def bulk_update_trip_station_days(
    db: Session,
    trip_id: int,
    reorder_items: List[TripStationReorderItem]
) -> List[TripStation]:
    # Map station_id -> new day_number
    id_to_day = {item.station_id: item.day_number for item in reorder_items}

    # Fetch all TripStation entries for the trip & stations being reordered
    trip_stations = db.query(TripStation).filter(
        TripStation.trip_id == trip_id,
        TripStation.station_id.in_(id_to_day.keys())
    ).all()

    # Update their day_number without checking for individual conflicts
    for trip_station in trip_stations:
        new_day = id_to_day.get(trip_station.station_id)
        if new_day is not None:
            trip_station.day_number = new_day

    db.flush()
    return trip_stations
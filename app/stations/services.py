from sqlalchemy.orm import Session, joinedload
from app.stations.models import Station
from app.trips.models import Trip
from app.stations.schemas import StationCreate, StationUpdate
from fastapi import HTTPException
from typing import cast
from app.core.connector_loader import openroute_connector

def get_station(db: Session, station_id: int):
    return db.query(Station)\
        .options(joinedload(Station.trip))\
        .filter(Station.id == station_id)\
        .first()

def get_trip(db: Session, trip_id: int):
    return db.query(Trip).filter_by(id=trip_id).first()

def get_all_stations(db: Session):
    return db.query(Station).all()

async def create_station(db: Session, station_data: StationCreate, user_id: int):
    trip = get_trip(db, station_data.trip_id)
    if not trip or trip.user_id != user_id:
        raise HTTPException(status_code=403, detail="Trip not found or unauthorized")

    duration_days = (trip.end_date - trip.start_date).days + 1
    if not (1 <= station_data.day_number <= duration_days):
        raise HTTPException(status_code=400, detail="Day number is out of trip range")

    coords = openroute_connector.get_coordinates_for_town(station_data.location_name)
    if not coords:
        raise HTTPException(status_code=400, detail="Location lookup failed")

    station = Station(
        trip_id=station_data.trip_id,
        day_number=station_data.day_number,
        station_name=station_data.station_name,
        latitude=coords["lat"],
        longitude=coords["lon"]
    )
    db.add(station)

    # === Add country to trip if it's not there already ===
    country = coords.get("country")
    if country:
        if trip.trip_countries is None:
            trip.trip_countries = []
        if country not in trip.trip_countries:
            trip.trip_countries.append(country) # type: ignore[attr-defined]
            db.add(trip)
    db.commit()
    db.refresh(station)
    return station

def update_station(db: Session, station_id: int, update_data: StationUpdate, user_id: int):
    station = get_station(db, station_id)
    if not station:
        raise HTTPException(status_code=404, detail="Station not found")

    trip = cast(Trip, station.trip)
    if trip.user_id != user_id:
        raise HTTPException(status_code=403, detail="Unauthorized")

    if update_data.day_number is not None:
        duration_days = (trip.end_date - trip.start_date).days + 1
        if not (1 <= update_data.day_number <= duration_days):
            raise HTTPException(status_code=400, detail="Day number is out of trip range")
        station.day_number = update_data.day_number

    db.commit()
    db.refresh(station)
    return station

def delete_station(db: Session, station_id: int, user_id: int):
    station = get_station(db, station_id)
    if not station:
        raise HTTPException(status_code=404, detail="Station not found")

    trip = cast(Trip, station.trip)
    if trip.user_id != user_id:
        raise HTTPException(status_code=403, detail="Unauthorized")

    db.delete(station)
    db.commit()

def admin_delete_station(db: Session, station_id: int):
    station = get_station(db, station_id)
    if not station:
        raise HTTPException(status_code=404, detail="Station not found")
    db.delete(station)
    db.commit()

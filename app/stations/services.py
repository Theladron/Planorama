from sqlalchemy.orm import Session, joinedload
from app.stations.models import Station
from app.travel.models import Travel
from app.trips.models import Trip
from app.stations.schemas import StationCreate, StationReorderItem
from fastapi import HTTPException
from typing import cast
from app.core.connector_loader import openroute_connector
from app.travel.services import create_travel_entry


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
    if station_data.trip_id <= 0 or station_data.day_number <= 0:
        raise HTTPException(status_code=400,
                            detail="Trip ID and day number must be positive integers")

    trip = get_trip(db, station_data.trip_id)
    if not trip or trip.user_id != user_id:
        raise HTTPException(status_code=403,
                            detail="Trip not found or unauthorized")

    duration_days = (trip.end_date - trip.start_date).days + 1
    if station_data.day_number > duration_days:
        raise HTTPException(status_code=400,
                            detail="Day number is out of trip range")

    existing_station = db.query(Station).filter(
        Station.trip_id == station_data.trip_id,
        Station.day_number == station_data.day_number
    ).first()
    if existing_station:
        raise HTTPException(
            status_code=400,
            detail=f"A station already exists on day {station_data.day_number}."
        )

    stations = (db.query(Station).filter(Station.trip_id == station_data.trip_id)
                .order_by(Station.day_number).all())

    prev_station = None
    for s in reversed(stations):
        if s.day_number < station_data.day_number:
            prev_station = s
            break

    next_station = None
    for s in stations:
        if s.day_number > station_data.day_number:
            next_station = s
            break

    # Check if same station_name is adjacent (prev or next)
    if prev_station and prev_station.station_name == station_data.station_name:
        raise HTTPException(
            status_code=400,
            detail=f"Station '{station_data.station_name}' "
                   f"already exists adjacent before day {prev_station.day_number}."
        )
    if next_station and next_station.station_name == station_data.station_name:
        raise HTTPException(
            status_code=400,
            detail=f"Station '{station_data.station_name}' "
                   f"already exists adjacent after day {next_station.day_number}."
        )

    coords = openroute_connector.get_location_info(station_data.station_name)
    if not coords:
        raise HTTPException(status_code=400, detail="Location lookup failed")

    country = coords.get("country")
    station = Station(
        trip_id=station_data.trip_id,
        day_number=station_data.day_number,
        station_name=station_data.station_name,
        latitude=coords["lat"],
        longitude=coords["lon"],
        country=country
    )
    db.add(station)
    db.flush()

    # Update trip countries if needed
    if country:
        current_countries = set(trip.trip_countries or [])
        if country not in current_countries:
            trip.trip_countries = list(current_countries.union({country}))
            db.add(trip)

    db.commit()
    db.refresh(station)
    sync_travel_routes_for_trip(db, trip.id)

    return station


def delete_station(db: Session, station_id: int, user_id: int):
    if station_id <= 0:
        raise HTTPException(status_code=400, detail="Invalid station ID")

    station = get_station(db, station_id)
    if not station:
        raise HTTPException(status_code=404, detail="Station not found")

    trip = cast(Trip, station.trip)
    if trip.user_id != user_id:
        raise HTTPException(status_code=403, detail="Unauthorized")

    country_to_check = station.country

    db.delete(station)
    db.commit()
    db.refresh(trip)

    # Remove country if no other stations from this country exist
    _remove_country_if_unused(db, trip, country_to_check)

    # Remove adjacent duplicates after deletion
    stations = (db.query(Station).filter(Station.trip_id == trip.id)
                .order_by(Station.day_number).all())

    to_delete = []
    previous_name = None
    for station in stations:
        if station.station_name == previous_name:
            to_delete.append(station)
        else:
            previous_name = station.station_name

    for station in to_delete:
        db.delete(station)

    db.commit()

    sync_travel_routes_for_trip(db, trip.id)

    return {"detail": "Station deleted successfully"}


def admin_delete_station(db: Session, station_id: int):
    if station_id <= 0:
        raise HTTPException(status_code=400, detail="Invalid station ID")

    station = get_station(db, station_id)
    if not station:
        raise HTTPException(status_code=404, detail="Station not found")

    trip = cast(Trip, station.trip)
    country_to_check = station.country

    db.delete(station)
    db.commit()
    db.refresh(trip)

    # Remove country if no other stations from this country exist
    _remove_country_if_unused(db, trip, country_to_check)

    # Remove adjacent duplicates after deletion
    stations = (db.query(Station).filter(Station.trip_id == trip.id)
                .order_by(Station.day_number).all())

    to_delete = []
    previous_name = None
    for s in stations:
        if s.station_name == previous_name:
            to_delete.append(s)
        else:
            previous_name = s.station_name

    for s in to_delete:
        db.delete(s)

    db.commit()

    sync_travel_routes_for_trip(db, trip.id)


def reorder_stations(
    db: Session,
    trip_id: int,
    reorder_items: list[StationReorderItem],
    user_id: int
):
    if trip_id <= 0:
        raise HTTPException(status_code=400, detail="Invalid trip ID")

    trip = get_trip(db, trip_id)
    if not trip or trip.user_id != user_id:
        raise HTTPException(status_code=403, detail="Unauthorized or trip not found")

    duration_days = (trip.end_date - trip.start_date).days + 1
    seen_days = set()

    for item in reorder_items:
        if item.day_number <= 0:
            raise HTTPException(status_code=400,
                                detail="Day numbers must be positive integers")
        if item.day_number > duration_days:
            raise HTTPException(status_code=400,
                                detail=f"Day number {item.day_number} exceeds trip range")
        if item.day_number in seen_days:
            raise HTTPException(status_code=400,
                                detail="Duplicate day_numbers not allowed")
        seen_days.add(item.day_number)

    # Validate stations exist & belong to trip
    station_ids = [item.station_id for item in reorder_items]
    stations_to_reorder = db.query(Station).filter(Station.id.in_(station_ids)).all()
    if len(stations_to_reorder) != len(station_ids):
        raise HTTPException(status_code=404,
                            detail="One or more stations not found")
    if any(s.trip_id != trip_id for s in stations_to_reorder):
        raise HTTPException(status_code=400,
                            detail="All stations must belong to the specified trip")

    # Update day_number of reordered stations
    id_to_day = {item.station_id: item.day_number for item in reorder_items}
    for station in stations_to_reorder:
        station.day_number = id_to_day[station.id]

    db.flush()

    all_stations = (db.query(Station).filter(Station.trip_id == trip_id)
                    .order_by(Station.day_number).all())

    # Remove adjacent duplicates
    to_delete = []
    previous_name = None
    for station in all_stations:
        if station.station_name == previous_name:
            to_delete.append(station)
        else:
            previous_name = station.station_name

    for station in to_delete:
        db.delete(station)

    db.commit()
    sync_travel_routes_for_trip(db, trip_id)

    # Return all remaining stations sorted by day_number
    remaining_stations = [s for s in all_stations if s not in to_delete]
    remaining_stations.sort(key=lambda s: s.day_number)
    return remaining_stations


def get_stations_by_trip(db: Session, trip_id: int, user_id: int):
    if trip_id <= 0:
        raise HTTPException(status_code=400, detail="Invalid trip ID")

    trip = get_trip(db, trip_id)
    if not trip or trip.user_id != user_id:
        raise HTTPException(status_code=403, detail="Unauthorized or trip not found")

    return db.query(Station).filter_by(trip_id=trip_id).order_by(Station.day_number).all()


def sync_travel_routes_for_trip(db: Session, trip_id: int):
    stations = db.query(Station).filter_by(trip_id=trip_id).order_by(Station.day_number).all()
    existing_travels = db.query(Travel).filter_by(trip_id=trip_id).all()

    expected_pairs = [
        (stations[i].id, stations[i + 1].id)
        for i in range(len(stations) - 1)
    ]

    expected_set = set(expected_pairs)
    for travel in existing_travels:
        if (travel.from_station_id, travel.to_station_id) not in expected_set:
            db.delete(travel)

    for from_id, to_id in expected_pairs:
        exists = any(
            t for t in existing_travels
            if t.from_station_id == from_id and t.to_station_id == to_id
        )
        if not exists:
            from_station = db.query(Station).get(from_id)
            to_station = db.query(Station).get(to_id)
            create_travel_entry(
                db=db,
                trip_id=trip_id,
                from_station_id=from_id,
                to_station_id=to_id,
                from_town=from_station.station_name,
                to_town=to_station.station_name,
                connector=openroute_connector
            )

    db.commit()


def _remove_country_if_unused(db: Session, trip: Trip, country: str | None):
    if not country or not trip.trip_countries:
        return

    db.refresh(trip)

    # Check if any station with this country remains in DB
    still_exists = db.query(Station).filter(
        Station.trip_id == trip.id,
        Station.country == country
    ).first()

    if not still_exists and country in trip.trip_countries:
        # Use set for safer removal
        current_countries = set(trip.trip_countries)
        current_countries.discard(country)
        trip.trip_countries = list(current_countries)
        db.add(trip)
        db.commit()

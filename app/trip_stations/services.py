from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.trip_stations.models import TripStation
from app.trip_stations.schemas import TripStationCreate, TripStationReorderItem
from app.trips.models import Trip
from app.travel.services import create_travel_entry
from app.travel.models import Travel
from app.stations.models import Station
from typing import List


def get_trip_station_by_id(db: Session, trip_station_id: int) -> TripStation | None:
    return db.query(TripStation).filter_by(id=trip_station_id).first()


def get_trip_station_by_trip_and_day(db: Session, trip_id: int, day_number: int) -> TripStation | None:
    return db.query(TripStation)\
        .filter_by(trip_id=trip_id, day_number=day_number)\
        .first()


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



def delete_trip_station(db: Session, trip_id: int, day_number: int, user_id: int):
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

    # Clean up adjacent duplicates safely
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

    # Delete duplicates one by one to keep integrity
    for ts in to_delete:
        db.delete(ts)
    db.commit()

    sync_travel_routes_for_trip_stations(db, trip_id)

    return {"detail": "Station unlinked from trip successfully"}



def bulk_update_trip_station_days(
    db: Session,
    trip_id: int,
    reorder_items: List[TripStationReorderItem]
) -> List[TripStation]:
    # Map trip_station_id -> new day_number
    id_to_day = {item.id: item.day_number for item in reorder_items}

    trip_station_ids = list(id_to_day.keys())
    trip_stations = db.query(TripStation).filter(
        TripStation.trip_id == trip_id,
        TripStation.id.in_(trip_station_ids)
    ).all()

    for trip_station in trip_stations:
        new_day = id_to_day.get(trip_station.id)
        if new_day is not None:
            trip_station.day_number = new_day

    db.flush()

    sync_travel_routes_for_trip_stations(db, trip_id)

    return trip_stations



def sync_travel_routes_for_trip_stations(db: Session, trip_id: int):
    trip_station_links = (
        db.query(TripStation)
        .filter_by(trip_id=trip_id)
        .order_by(TripStation.day_number)
        .all()
    )

    existing_travel_segments = db.query(Travel).filter_by(trip_id=trip_id).all()

    expected_station_pairs = [
        (
            trip_station_links[current_index].station_id,
            trip_station_links[current_index + 1].station_id
        )
        for current_index in range(len(trip_station_links) - 1)
    ]

    expected_pair_set = set(expected_station_pairs)

    # Delete travel segments no longer valid
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
            from_station = db.query(Station).get(from_station_id)
            to_station = db.query(Station).get(to_station_id)

            create_travel_entry(
                db=db,
                trip_id=trip_id,
                from_station_id=from_station_id,
                to_station_id=to_station_id,
                from_town=from_station.station_name,
                to_town=to_station.station_name
            )

    db.commit()



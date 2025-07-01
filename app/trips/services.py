from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from app.trips.models import Trip
from app.trips.schemas import TripCreate, TripUpdate
from app.stations.models import Station
from datetime import timedelta


def get_trips(db: Session):
    return db.query(Trip).all()


def get_trip(db: Session, trip_id: int):
    return db.query(Trip).filter_by(id=trip_id).first()


def get_user_trips(db: Session, user_id: int):
    return db.query(Trip).filter_by(user_id=user_id).all()


def create_trip(db: Session, trip_data: TripCreate, user_id: int):
    try:
        trip_dict = trip_data.model_dump()
        trip_dict['user_id'] = user_id
        db_trip = Trip(**trip_dict)
        db.add(db_trip)
        db.commit()
        db.refresh(db_trip)
        return db_trip
    except SQLAlchemyError as e:
        db.rollback()
        raise Exception("Trip creation failed: " + str(e))


def delete_trip(db: Session, trip_id: int):
    trip = get_trip(db, trip_id)
    if trip:
        db.delete(trip)
        db.commit()


def update_trip(db: Session, trip_id: int, trip_update: TripUpdate):
    trip = get_trip(db, trip_id)
    if not trip:
        raise ValueError("Trip not found")

    update_data = trip_update.model_dump(exclude_unset=True)

    # Validate: check stations for day bounds
    new_start = update_data.get("start_date", trip.start_date)
    new_end = update_data.get("end_date", trip.end_date)

    stations = db.query(Station).filter_by(trip_id=trip_id).all()
    for station in stations:
        if station.day < 1:
            raise ValueError(f"Invalid day {station.day} in trip")
        station_date = new_start + timedelta(days=station.day - 1)
        if station_date < new_start or station_date > new_end:
            raise ValueError(f"Station on day {station.day} falls outside the new trip range")

    # Apply updates
    for key, value in update_data.items():
        setattr(trip, key, value)

    db.commit()
    db.refresh(trip)
    return trip

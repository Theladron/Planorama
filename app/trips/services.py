from sqlalchemy.orm import Session
from app.trips.models import Trip
from app.trips.schemas import TripCreate, TripUpdate


def get_trips(db: Session):
    return db.query(Trip).all()


def get_trip(db: Session, trip_id: int):
    return db.query(Trip).filter_by(id=trip_id).first()


def get_user_trips(db: Session, user_id: int):
    return db.query(Trip).filter_by(user_id=user_id).all()


def create_trip(db: Session, trip: TripCreate):
    db_trip = Trip(**trip.model_dump())
    db.add(db_trip)
    db.commit()
    db.refresh(db_trip)
    return db_trip


def delete_trip(db: Session, trip_id: int):
    trip = get_trip(db, trip_id)
    if trip:
        db.delete(trip)
        db.commit()
    return


def update_trip(db: Session, trip_id: int, trip_update: TripUpdate):
    trip = get_trip(db, trip_id)
    if not trip:
        return None

    update_data = trip_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(trip, key, value)

    db.commit()
    db.refresh(trip)
    return trip

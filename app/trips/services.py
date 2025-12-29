"""Trip management service functions."""
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from app.trips.models import Trip
from app.trips.schemas import TripCreate, TripUpdate
from app.trip_stations.models import TripStation
from datetime import timedelta


def get_trips(db: Session):
    """Retrieve all trips from the database.
    
    Args:
        db: Database session.
        
    Returns:
        List of all Trip objects.
    """
    return db.query(Trip).all()


def get_trip(db: Session, trip_id: int):
    """Retrieve a trip by its ID.
    
    Args:
        db: Database session.
        trip_id: Unique trip identifier.
        
    Returns:
        Trip object if found, None otherwise.
    """
    return db.query(Trip).filter_by(id=trip_id).first()


def get_user_trips(db: Session, user_id: str):
    """Retrieve all trips belonging to a specific user.
    
    Args:
        db: Database session.
        user_id: Auth0 user identifier.
        
    Returns:
        List of Trip objects for the specified user.
    """
    return db.query(Trip).filter_by(user_id=user_id).all()


def create_trip(db: Session, trip_data: TripCreate, user_id: str):
    """Create a new trip in the database.
    
    Args:
        db: Database session.
        trip_data: TripCreate schema with trip information.
        user_id: Auth0 ID of the user creating the trip.
        
    Returns:
        Created Trip object.
        
    Raises:
        Exception: If trip creation fails.
    """
    try:
        trip_dict = trip_data.model_dump()
        trip_dict['user_id'] = user_id
        db_trip = Trip(**trip_dict)
        db.add(db_trip)
        db.commit()
        db.refresh(db_trip)
        return db_trip
    except SQLAlchemyError as error:
        db.rollback()
        raise Exception("Trip creation failed: " + str(error))


def delete_trip(db: Session, trip_id: int):
    """Delete a trip from the database.
    
    Args:
        db: Database session.
        trip_id: Unique trip identifier.
    """
    trip = get_trip(db, trip_id)
    if trip:
        db.delete(trip)
        db.commit()


def update_trip(db: Session, trip_id: int, trip_update: TripUpdate):
    """Update an existing trip.
    
    Args:
        db: Database session.
        trip_id: Unique trip identifier.
        trip_update: TripUpdate schema with fields to update.
        
    Returns:
        Updated Trip object.
        
    Raises:
        ValueError: If trip not found or station dates fall outside trip range.
    """
    trip = get_trip(db, trip_id)
    if not trip:
        raise ValueError("Trip not found")

    update_data = trip_update.model_dump(exclude_unset=True)

    new_start = update_data.get("start_date", trip.start_date)
    new_end = update_data.get("end_date", trip.end_date)

    trip_stations = db.query(TripStation).filter_by(trip_id=trip_id).all()
    for trip_station in trip_stations:
        if trip_station.day_number < 1:
            raise ValueError(f"Invalid day {trip_station.day_number} in trip")
        station_date = new_start + timedelta(days=trip_station.day_number - 1)
        if station_date < new_start or station_date > new_end:
            raise ValueError(f"Station on day {trip_station.day_number} falls outside the new trip range")

    for key, value in update_data.items():
        setattr(trip, key, value)

    db.commit()
    db.refresh(trip)
    return trip

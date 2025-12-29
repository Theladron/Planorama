"""Unit tests for trip service functions."""
import pytest
from datetime import date, timedelta
from sqlalchemy.exc import SQLAlchemyError
from app.trips.services import (
    get_trips, get_trip, get_user_trips, create_trip,
    delete_trip, update_trip
)
from app.trips.schemas import TripCreate, TripUpdate


@pytest.mark.unit
class TestTripServices:
    """Test trip service functions with real database."""

    def test_get_trips_empty(self, test_db):
        """Test getting all trips when database is empty."""
        trips = get_trips(test_db)
        assert trips == []

    def test_get_trips_with_data(self, test_db, test_trip):
        """Test getting all trips."""
        trips = get_trips(test_db)
        assert len(trips) == 1
        assert trips[0].id == test_trip.id
        assert trips[0].trip_name == test_trip.trip_name

    def test_get_trip_exists(self, test_db, test_trip):
        """Test getting a trip by ID when trip exists."""
        trip = get_trip(test_db, test_trip.id)
        assert trip is not None
        assert trip.id == test_trip.id
        assert trip.trip_name == test_trip.trip_name

    def test_get_trip_not_exists(self, test_db):
        """Test getting a trip by ID when trip doesn't exist."""
        trip = get_trip(test_db, 999)
        assert trip is None

    def test_get_user_trips_empty(self, test_db, test_user):
        """Test getting trips for a user with no trips."""
        trips = get_user_trips(test_db, test_user.id)
        assert trips == []

    def test_get_user_trips_with_data(self, test_db, test_user, test_trip):
        """Test getting trips for a specific user."""
        trips = get_user_trips(test_db, test_user.id)
        assert len(trips) == 1
        assert trips[0].id == test_trip.id
        assert trips[0].user_id == test_user.id

    def test_get_user_trips_wrong_user(self, test_db, test_user):
        """Test getting trips for a user that doesn't own any trips."""
        from app.users.models import User
        other_user = User(
            id="auth0|otheruser123",
            username="otheruser",
            email="other@example.com",
            is_active=True
        )
        test_db.add(other_user)
        test_db.commit()
        trips = get_user_trips(test_db, other_user.id)
        assert trips == []

    def test_create_trip_success(self, test_db, test_user):
        """Test creating a new trip."""
        trip_data = TripCreate(
            trip_name="New Trip",
            start_date=date(2025, 7, 1),
            end_date=date(2025, 7, 10),
            trip_countries=["France"]
        )
        trip = create_trip(test_db, trip_data, test_user.id)
        assert trip is not None
        assert trip.id is not None
        assert trip.trip_name == "New Trip"
        assert trip.user_id == test_user.id
        assert trip.start_date == date(2025, 7, 1)
        assert trip.end_date == date(2025, 7, 10)
        assert trip.trip_countries == ["France"]

    def test_delete_trip_exists(self, test_db, test_trip):
        """Test deleting an existing trip."""
        trip_id = test_trip.id
        delete_trip(test_db, trip_id)
        deleted_trip = get_trip(test_db, trip_id)
        assert deleted_trip is None

    def test_delete_trip_not_exists(self, test_db):
        """Test deleting a non-existent trip (should not raise error)."""
        delete_trip(test_db, 999)
        assert True

    def test_update_trip_trip_name(self, test_db, test_trip):
        """Test updating trip name."""
        update_data = TripUpdate(trip_name="Updated Trip Name")
        updated_trip = update_trip(test_db, test_trip.id, update_data)
        assert updated_trip.trip_name == "Updated Trip Name"
        assert updated_trip.start_date == test_trip.start_date
        assert updated_trip.end_date == test_trip.end_date

    def test_update_trip_dates(self, test_db, test_trip):
        """Test updating trip dates."""
        new_start = date(2025, 6, 5)
        new_end = date(2025, 6, 15)
        update_data = TripUpdate(
            start_date=new_start,
            end_date=new_end
        )
        updated_trip = update_trip(test_db, test_trip.id, update_data)
        assert updated_trip.start_date == new_start
        assert updated_trip.end_date == new_end

    def test_update_trip_not_exists(self, test_db):
        """Test updating a non-existent trip raises ValueError."""
        update_data = TripUpdate(trip_name="Updated Name")
        with pytest.raises(ValueError, match="Trip not found"):
            update_trip(test_db, 999, update_data)

    def test_update_trip_countries(self, test_db, test_trip):
        """Test updating trip countries."""
        update_data = TripUpdate(trip_countries=["France", "Spain"])
        updated_trip = update_trip(test_db, test_trip.id, update_data)
        assert updated_trip.trip_countries == ["France", "Spain"]



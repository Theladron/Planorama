"""Unit tests for travel service functions."""
import pytest
from fastapi import HTTPException
from app.travel.services import (
    get_user_travel_for_trip, get_user_travel_by_day, create_travel_entry
)


@pytest.mark.unit
class TestTravelServices:
    """Test travel service functions with real database."""

    def test_get_user_travel_for_trip_empty(self, test_db, test_user, test_trip):
        """Test getting travel routes for a trip with no routes."""
        travels = get_user_travel_for_trip(test_db, test_trip.id, test_user.id)
        assert travels == []

    def test_get_user_travel_for_trip_unauthorized(self, test_db, test_trip):
        """Test getting travel routes for trip owned by different user raises HTTPException."""
        from app.users.models import User
        other_user = User(
            username="otheruser",
            email="other@example.com",
            password_hash="hash",
            is_active=True
        )
        test_db.add(other_user)
        test_db.commit()
        
        with pytest.raises(HTTPException, match="Unauthorized"):
            get_user_travel_for_trip(test_db, test_trip.id, other_user.id)

    def test_get_user_travel_by_day_not_found(self, test_db, test_user, test_trip):
        """Test getting travel route by day when it doesn't exist."""
        travel = get_user_travel_by_day(test_db, test_trip.id, 1, test_user.id)
        assert travel is None

    def test_get_user_travel_by_day_unauthorized(self, test_db, test_trip):
        """Test getting travel route by day for unauthorized user raises HTTPException."""
        from app.users.models import User
        other_user = User(
            username="otheruser",
            email="other@example.com",
            password_hash="hash",
            is_active=True
        )
        test_db.add(other_user)
        test_db.commit()
        
        with pytest.raises(HTTPException, match="Unauthorized"):
            get_user_travel_by_day(test_db, test_trip.id, 1, other_user.id)

    def test_create_travel_entry_success(self, test_db, test_trip, test_station):
        """Test creating a travel entry."""
        from app.stations.models import Station
        station2 = Station(
            station_name="Munich",
            station_name_de="München",
            latitude=48.1351,
            longitude=11.5820,
            country="Germany"
        )
        test_db.add(station2)
        test_db.commit()
        test_db.refresh(station2)
        
        travel = create_travel_entry(
            test_db,
            test_trip.id,
            test_station.id,
            station2.id,
            "Berlin",
            "Munich"
        )
        assert travel is not None
        assert travel.trip_id == test_trip.id
        assert travel.from_station_id == test_station.id
        assert travel.to_station_id == station2.id

    def test_create_travel_entry_missing_towns(self, test_db, test_trip, test_station):
        """Test creating travel entry with missing town names raises ValueError."""
        with pytest.raises(ValueError, match="Both from_town and to_town must be provided"):
            create_travel_entry(
                test_db,
                test_trip.id,
                test_station.id,
                test_station.id,
                "",
                "Munich"
            )



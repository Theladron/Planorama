"""Unit tests for trip_stations service functions."""
import pytest
from fastapi import HTTPException
from app.trip_stations.services import (
    get_trip_station_by_trip_and_day,
    get_trip_stations_for_trip, create_trip_station,
    delete_trip_station, sync_travel_routes_for_trip_stations
)
from app.trip_stations.schemas import TripStationCreate


@pytest.mark.unit
class TestTripStationServices:
    """Test trip_station service functions with real database."""

    def test_get_trip_station_by_trip_and_day_exists(self, test_db, test_trip, test_station):
        """Test getting a trip station by trip and day when it exists."""
        from app.trip_stations.models import TripStation
        trip_station = TripStation(
            trip_id=test_trip.id,
            station_id=test_station.id,
            day_number=1
        )
        test_db.add(trip_station)
        test_db.commit()
        
        result = get_trip_station_by_trip_and_day(test_db, test_trip.id, 1)
        assert result is not None
        assert result.day_number == 1

    def test_get_trip_station_by_trip_and_day_not_exists(self, test_db, test_trip):
        """Test getting a trip station by trip and day when it doesn't exist."""
        result = get_trip_station_by_trip_and_day(test_db, test_trip.id, 99)
        assert result is None

    def test_get_trip_stations_for_trip_empty(self, test_db, test_trip):
        """Test getting trip stations for a trip with no stations."""
        stations = get_trip_stations_for_trip(test_db, test_trip.id)
        assert stations == []

    def test_get_trip_stations_for_trip_with_data(self, test_db, test_trip, test_station):
        """Test getting trip stations for a trip."""
        from app.trip_stations.models import TripStation
        trip_station1 = TripStation(
            trip_id=test_trip.id,
            station_id=test_station.id,
            day_number=1
        )
        trip_station2 = TripStation(
            trip_id=test_trip.id,
            station_id=test_station.id,
            day_number=2
        )
        test_db.add(trip_station1)
        test_db.add(trip_station2)
        test_db.commit()
        
        stations = get_trip_stations_for_trip(test_db, test_trip.id)
        assert len(stations) == 2
        assert stations[0].day_number == 1
        assert stations[1].day_number == 2

    def test_create_trip_station_success(self, test_db, test_trip, test_station):
        """Test creating a new trip station."""
        data = TripStationCreate(
            trip_id=test_trip.id,
            station_id=test_station.id,
            day_number=1
        )
        trip_station = create_trip_station(test_db, data)
        assert trip_station is not None
        assert trip_station.trip_id == test_trip.id
        assert trip_station.station_id == test_station.id
        assert trip_station.day_number == 1

    def test_create_trip_station_trip_not_found(self, test_db, test_station):
        """Test creating trip station with non-existent trip raises HTTPException."""
        data = TripStationCreate(
            trip_id=999,
            station_id=test_station.id,
            day_number=1
        )
        with pytest.raises(HTTPException, match="Trip not found"):
            create_trip_station(test_db, data)

    def test_create_trip_station_station_not_found(self, test_db, test_trip):
        """Test creating trip station with non-existent station raises HTTPException."""
        data = TripStationCreate(
            trip_id=test_trip.id,
            station_id=999,
            day_number=1
        )
        with pytest.raises(HTTPException, match="Station not found"):
            create_trip_station(test_db, data)

    def test_delete_trip_station_success(self, test_db, test_user, test_trip, test_station):
        """Test deleting a trip station."""
        from app.trip_stations.models import TripStation
        trip_station = TripStation(
            trip_id=test_trip.id,
            station_id=test_station.id,
            day_number=1
        )
        test_db.add(trip_station)
        test_db.commit()
        test_db.refresh(trip_station)
        
        result = delete_trip_station(test_db, test_trip.id, 1, test_user.id)
        assert "detail" in result
        
        from app.trip_stations.models import TripStation
        deleted = test_db.query(TripStation).filter_by(id=trip_station.id).first()
        assert deleted is None

    def test_delete_trip_station_invalid_day_number(self, test_db, test_user, test_trip):
        """Test deleting trip station with invalid day number raises HTTPException."""
        with pytest.raises(HTTPException, match="Invalid day number"):
            delete_trip_station(test_db, test_trip.id, 0, test_user.id)

    def test_delete_trip_station_trip_not_found(self, test_db, test_user):
        """Test deleting trip station for non-existent trip raises HTTPException."""
        with pytest.raises(HTTPException, match="Trip not found"):
            delete_trip_station(test_db, 999, 1, test_user.id)

    def test_delete_trip_station_unauthorized(self, test_db, test_user, test_trip, test_station):
        """Test deleting trip station for trip owned by different user raises HTTPException."""
        from app.users.models import User
        from app.trip_stations.models import TripStation
        other_user = User(
            username="otheruser",
            email="other@example.com",
            password_hash="hash",
            is_active=True
        )
        test_db.add(other_user)
        test_db.commit()
        
        trip_station = TripStation(
            trip_id=test_trip.id,
            station_id=test_station.id,
            day_number=1
        )
        test_db.add(trip_station)
        test_db.commit()
        
        with pytest.raises(HTTPException, match="Unauthorized"):
            delete_trip_station(test_db, test_trip.id, 1, other_user.id)

    def test_sync_travel_routes_for_trip_stations(self, test_db, test_trip, test_station):
        """Test syncing travel routes for trip stations."""
        from app.trip_stations.models import TripStation
        from app.stations.models import Station
        from app.travel.models import Travel
        
        # Create a second station
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
        
        trip_station1 = TripStation(
            trip_id=test_trip.id,
            station_id=test_station.id,
            day_number=1
        )
        trip_station2 = TripStation(
            trip_id=test_trip.id,
            station_id=station2.id,
            day_number=2
        )
        test_db.add(trip_station1)
        test_db.add(trip_station2)
        test_db.commit()
        
        # Sync should succeed
        sync_travel_routes_for_trip_stations(test_db, test_trip.id)
        
        # Verify travel entry was created
        travel = test_db.query(Travel).filter_by(trip_id=test_trip.id).first()
        assert travel is not None
        assert travel.from_station_id == test_station.id
        assert travel.to_station_id == station2.id



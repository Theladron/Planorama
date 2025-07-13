import sys
import os

# Patch datetime.fromisoformat to accept space or 'T' as separator
import datetime as dt

_original_fromisoformat = dt.datetime.fromisoformat

def patched_fromisoformat(date_string):
    # Replace space with T before parsing to avoid ValueError
    fixed = date_string.replace(" ", "T")
    return _original_fromisoformat(fixed)

dt.datetime.fromisoformat = patched_fromisoformat


# Ensure we can import from the main app package
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

import pytest
from datetime import date, datetime
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from fastapi import HTTPException
from sqlalchemy.engine import Engine

from app.core.database import Base, import_all_models
from app.stations.models import Station
from app.trips.models import Trip
from app.users.models import User
from app.trip_stations.schemas import TripStationCreate, TripStationReorderItem
from app.stations.schemas import StationCreate
from app.stations.services import create_station, delete_station, get_stations_by_trip, reorder_stations
from app.trip_stations.services import create_trip_station

TEST_DB_URL = "sqlite:///:memory:"


# ------------------ Fixtures ------------------ #

@pytest.fixture(scope="function")
def db_session():
    engine = create_engine(TEST_DB_URL)

    # Register a custom SQL function "now" with ISO 8601 format (T separator)
    @event.listens_for(engine, "connect")
    def connect(dbapi_connection, connection_record):
        dbapi_connection.create_function("now", 0, lambda: datetime.utcnow().isoformat(sep="T"))

    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    import_all_models()
    Base.metadata.create_all(bind=engine)

    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture
def test_user(db_session):
    user = User(
        id=1,
        email="test@example.com",
        username="Test User",
        password_hash="hashedpassword123",
        language_preference="en"
    )
    db_session.add(user)
    db_session.commit()
    return user


@pytest.fixture
def test_trip(db_session, test_user):
    trip = Trip(
        id=1,
        trip_name="Test Trip",
        user_id=test_user.id,
        start_date=date(2025, 1, 1),
        end_date=date(2025, 1, 5),
        trip_countries=[]
    )
    db_session.add(trip)
    db_session.commit()
    return trip


@pytest.fixture
def sample_station(db_session):
    station = Station(
        station_name="TestCity",
        station_name_de="TestStadt",
        latitude=10.0,
        longitude=10.0,
        country="TestLand"
    )
    db_session.add(station)
    db_session.commit()
    return station


# ------------------ Tests ------------------ #

def test_create_station_success(monkeypatch, db_session, test_user, test_trip):
    def fake_get_location_info(name, lang):
        return {"lat": 10.0, "lon": 10.0, "country": "TestLand"}

    def fake_get_town_name_by_coords(lat, lon, lang):
        return "TestCity" if lang == "en" else "TestStadt"

    monkeypatch.setattr(
        "app.core.connector_loader.openroute_connector.openroute_connector.get_location_info",
        fake_get_location_info
    )
    monkeypatch.setattr(
        "app.core.connector_loader.openroute_connector.openroute_connector.get_town_name_by_coords",
        fake_get_town_name_by_coords
    )

    station_data = StationCreate(
        station_name="TestCity",
        latitude=0,
        longitude=0,
        country="",
        trip_id=test_trip.id,
        day_number=1,
    )

    created_station = create_station(db_session, station_data, test_user.id)

    assert created_station.station_name == "TestCity"
    assert created_station.station_name_de == "TestStadt"
    assert created_station.country == "TestLand"


def test_create_station_invalid_day(db_session, test_user, test_trip):
    station_data = StationCreate(
        station_name="City",
        latitude=0,
        longitude=0,
        country="",
        trip_id=test_trip.id,
        day_number=10,
    )

    with pytest.raises(HTTPException) as excinfo:
        create_station(db_session, station_data, test_user.id)
    assert excinfo.value.status_code == 400


def test_delete_station(db_session, test_user, test_trip, sample_station):
    create_trip_station(
        db_session,
        data=TripStationCreate(
            trip_id=test_trip.id,
            station_id=sample_station.id,
            day_number=1
        )
    )

    response = delete_station(db_session, sample_station.id, test_user.id)
    assert response["detail"] == "Station deleted successfully"

    station_after = db_session.query(Station).filter_by(id=sample_station.id).first()
    assert station_after is None


def test_reorder_stations(db_session, test_user, test_trip, sample_station):
    station2 = Station(
        station_name="City2",
        station_name_de="Stadt2",
        latitude=11,
        longitude=11,
        country="TestLand"
    )
    db_session.add(station2)
    db_session.commit()

    create_trip_station(db_session, TripStationCreate(trip_id=test_trip.id, station_id=sample_station.id, day_number=1))
    create_trip_station(db_session, TripStationCreate(trip_id=test_trip.id, station_id=station2.id, day_number=2))

    reorder_items = [
        TripStationReorderItem(station_id=sample_station.id, day_number=2),
        TripStationReorderItem(station_id=station2.id, day_number=1),
    ]

    reordered = reorder_stations(db_session, test_trip.id, reorder_items, test_user.id)
    assert [ts.day_number for ts in reordered] == [1, 2]
    assert reordered[0].station_id == station2.id
    assert reordered[1].station_id == sample_station.id


def test_get_stations_by_trip(db_session, test_user, test_trip, sample_station):
    create_trip_station(
        db_session,
        data=TripStationCreate(
            trip_id=test_trip.id,
            station_id=sample_station.id,
            day_number=1
        )
    )

    stations = get_stations_by_trip(db_session, test_trip.id, test_user.id)

    assert len(stations) == 1
    assert stations[0].station_name == sample_station.station_name


# ------------------ Run tests directly ------------------ #

if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])

"""Shared pytest fixtures for backend tests."""
import pytest
from unittest.mock import Mock, MagicMock, patch
from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session, sessionmaker
from datetime import datetime, date
from app.core.database import Base, get_db, import_all_models
from app.core.security import hash_password
from app.users.models import User
from app.trips.models import Trip
from app.stations.models import Station
from app.trip_stations.models import TripStation
from app.travel.models import Travel

import_all_models()


@pytest.fixture(scope="function")
def test_db():
    """Create an in-memory SQLite database for testing."""
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    
    # Register SQLite functions to handle now() and datetime functions
    @event.listens_for(engine, "connect")
    def register_sqlite_functions(dbapi_conn, connection_record):
        """Register custom SQLite functions for PostgreSQL compatibility."""
        def sqlite_now():
            """SQLite-compatible now() function that returns current datetime as ISO string."""
            # SQLite stores datetimes as strings, so return ISO format string
            return datetime.now().isoformat()
        
        def sqlite_current_date():
            """SQLite-compatible current_date function that returns current date as YYYY-MM-DD."""
            # Return just the date part for Date fields
            return date.today().isoformat()
        
        # Register now() function for SQLite (PostgreSQL compatibility)
        # This allows text('now()') to work in SQLite
        dbapi_conn.create_function('now', 0, sqlite_now)
        # Register current_date for Date fields
        dbapi_conn.create_function('current_date', 0, sqlite_current_date)
    
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture
def mock_db_session():
    """Create a mock database session for integration tests."""
    session = MagicMock(spec=Session)
    session.query = MagicMock()
    session.add = MagicMock()
    session.commit = MagicMock()
    session.refresh = MagicMock()
    session.delete = MagicMock()
    session.rollback = MagicMock()
    session.close = MagicMock()
    session.flush = MagicMock()
    return session


@pytest.fixture
def sample_user_data():
    """Sample user data for testing."""
    return {
        "id": 1,
        "username": "testuser",
        "email": "test@example.com",
        "password_hash": hash_password("TestPassword123!"),
        "is_active": True,
        "is_admin": False,
        "language_preference": "en",
        "created_at": datetime.now(),
    }


@pytest.fixture
def sample_trip_data():
    """Sample trip data for testing."""
    return {
        "id": 1,
        "user_id": 1,
        "trip_name": "Test Trip",
        "trip_countries": ["DE", "FR"],
        "start_date": date(2025, 6, 1),
        "end_date": date(2025, 6, 10),
        "created_at": date.today(),
    }


@pytest.fixture
def sample_station_data():
    """Sample station data for testing."""
    return {
        "id": 1,
        "station_name": "Berlin",
        "station_name_de": "Berlin",
        "latitude": 52.52,
        "longitude": 13.405,
        "country": "Germany",
    }


@pytest.fixture
def test_user(test_db):
    """Create a test user in the database."""
    user = User(
        username="testuser",
        email="test@example.com",
        password_hash=hash_password("TestPassword123!"),
        is_active=True,
        is_admin=False,
        language_preference="en"
    )
    test_db.add(user)
    test_db.commit()
    test_db.refresh(user)
    return user


@pytest.fixture
def test_admin_user(test_db):
    """Create a test admin user in the database."""
    user = User(
        username="admin",
        email="admin@example.com",
        password_hash=hash_password("AdminPassword123!"),
        is_active=True,
        is_admin=True,
        language_preference="en"
    )
    test_db.add(user)
    test_db.commit()
    test_db.refresh(user)
    return user


@pytest.fixture
def test_trip(test_db, test_user):
    """Create a test trip in the database."""
    trip = Trip(
        user_id=test_user.id,
        trip_name="Test Trip",
        trip_countries=["Germany"],
        start_date=date(2025, 6, 1),
        end_date=date(2025, 6, 10)
    )
    test_db.add(trip)
    test_db.commit()
    test_db.refresh(trip)
    return trip


@pytest.fixture
def test_station(test_db):
    """Create a test station in the database."""
    station = Station(
        station_name="Berlin",
        station_name_de="Berlin",
        latitude=52.52,
        longitude=13.405,
        country="Germany"
    )
    test_db.add(station)
    test_db.commit()
    test_db.refresh(station)
    return station


@pytest.fixture
def mock_current_user():
    """Mock authenticated user."""
    from app.users.models import User
    user = Mock(spec=User)
    user.id = 1
    user.username = "testuser"
    user.email = "test@example.com"
    user.is_active = True
    user.is_admin = False
    user.language_preference = "en"
    return user


@pytest.fixture
def mock_admin_user():
    """Mock admin user."""
    from app.users.models import User
    user = Mock(spec=User)
    user.id = 1
    user.username = "admin"
    user.email = "admin@example.com"
    user.is_active = True
    user.is_admin = True
    user.language_preference = "en"
    return user

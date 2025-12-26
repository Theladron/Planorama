"""
Shared pytest fixtures for backend tests.
Uses mocks to avoid SQLite/PostgreSQL compatibility issues.
"""
import pytest
from unittest.mock import Mock, MagicMock, patch
from sqlalchemy.orm import Session
from datetime import datetime, date
from app.core.database import Base, SessionLocal
from app.core.security import hash_password


@pytest.fixture
def mock_db_session():
    """Create a mock database session."""
    session = MagicMock(spec=Session)
    session.query = MagicMock()
    session.add = MagicMock()
    session.commit = MagicMock()
    session.refresh = MagicMock()
    session.delete = MagicMock()
    session.rollback = MagicMock()
    session.close = MagicMock()
    return session


@pytest.fixture
def mock_db():
    """Mock database dependency injection."""
    with patch('app.core.database.get_db') as mock_get_db:
        mock_session = MagicMock(spec=Session)
        mock_get_db.return_value = iter([mock_session])
        yield mock_session


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
def mock_current_user():
    """Mock authenticated user."""
    from app.users.models import User
    user = Mock(spec=User)
    user.id = 1
    user.username = "testuser"
    user.email = "test@example.com"
    user.is_active = True
    user.is_admin = False
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
    return user


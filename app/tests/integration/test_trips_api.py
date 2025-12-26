"""
Integration tests for trips API endpoints.
Uses mocks to avoid database compatibility issues.
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from datetime import date
from app.main import app
from app.auth.services import get_current_active_user
from app.core.database import get_db


@pytest.mark.integration
class TestTripsAPI:
    """Test trips API endpoints."""

    @pytest.fixture
    def client(self):
        """Create a test client."""
        return TestClient(app)

    @pytest.fixture
    def mock_user(self):
        """Mock authenticated user."""
        user = MagicMock()
        user.id = 1
        user.username = "testuser"
        user.email = "test@example.com"
        user.is_active = True
        user.is_admin = False
        return user

    @pytest.fixture
    def mock_db(self, mock_db_session):
        """Mock database session."""
        return mock_db_session

    def test_get_trips(self, client, mock_db, mock_user):
        """Test getting user trips."""
        # Override dependencies - get_db is a generator
        def override_get_db():
            yield mock_db
        app.dependency_overrides[get_db] = override_get_db
        app.dependency_overrides[get_current_active_user] = lambda: mock_user

        # Mock the service function at the API level where it's used
        with patch('app.trips.api.get_user_trips') as mock_get_trips:
            # Create mock trip objects with all required fields
            mock_trip = type('Trip', (), {
                'id': 1,
                'trip_name': 'Test Trip',
                'start_date': date(2025, 6, 1),
                'end_date': date(2025, 6, 10),
                'user_id': 1,
                'created_at': date.today(),
            })()
            mock_get_trips.return_value = [mock_trip]

            try:
                # Make request (correct endpoint is /me for user trips)
                response = client.get("/api/trips/me")

                # Assertions
                assert response.status_code == 200
                data = response.json()
                assert isinstance(data, list)
                assert len(data) > 0
                assert data[0]["trip_name"] == "Test Trip"
            finally:
                # Clean up dependency overrides
                app.dependency_overrides.clear()

    def test_create_trip(self, client, mock_db, mock_user):
        """Test creating a new trip."""
        # Override dependencies - get_db is a generator
        def override_get_db():
            yield mock_db
        app.dependency_overrides[get_db] = override_get_db
        app.dependency_overrides[get_current_active_user] = lambda: mock_user

        # Mock the service function at the API level where it's used
        with patch('app.trips.api.create_trip') as mock_create_trip:
            # Create a mock trip object
            mock_trip = type('Trip', (), {
                'id': 1,
                'trip_name': 'New Trip',
                'start_date': date(2025, 6, 1),
                'end_date': date(2025, 6, 10),
                'user_id': 1,
                'created_at': date.today(),
            })()
            mock_create_trip.return_value = mock_trip

            try:
                # Make request
                response = client.post(
                    "/api/trips/",
                    json={
                        "trip_name": "New Trip",
                        "start_date": "2025-06-01",
                        "end_date": "2025-06-10",
                    }
                )

                # Assertions
                assert response.status_code == 200
                data = response.json()
                assert data["trip_name"] == "New Trip"
            finally:
                app.dependency_overrides.clear()

    def test_delete_trip(self, client, mock_db, mock_user):
        """Test deleting a trip."""
        # Override dependencies - get_db is a generator
        def override_get_db():
            yield mock_db
        app.dependency_overrides[get_db] = override_get_db
        app.dependency_overrides[get_current_active_user] = lambda: mock_user

        # Mock the service functions at the API level where they're used
        with patch('app.trips.api.get_trip') as mock_get_trip, \
             patch('app.trips.api.delete_trip') as mock_delete_trip:
            # Create a mock trip object
            mock_trip = type('Trip', (), {
                'id': 1,
                'user_id': 1,  # Same as mock_user.id
            })()
            mock_get_trip.return_value = mock_trip
            mock_delete_trip.return_value = True

            try:
                # Make request
                response = client.delete("/api/trips/1")

                # Assertions
                assert response.status_code == 200
            finally:
                app.dependency_overrides.clear()

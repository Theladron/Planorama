"""
Integration tests for authentication API endpoints.
Uses mocks to avoid database compatibility issues.
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from app.main import app
from app.core.database import get_db


@pytest.mark.integration
class TestAuthAPI:
    """Test authentication API endpoints."""

    @pytest.fixture
    def client(self):
        """Create a test client."""
        return TestClient(app)

    @pytest.fixture
    def mock_db(self, mock_db_session):
        """Mock database session."""
        return mock_db_session

    def test_register_user_success(self, client, mock_db):
        """Test successful user registration."""
        # Override database dependency - get_db is a generator
        def override_get_db():
            yield mock_db
        app.dependency_overrides[get_db] = override_get_db

        # Mock the service function at the API level where it's used
        with patch('app.users.api.create_user') as mock_create_user:
            from app.users.models import User
            # Create a simple object that can be serialized
            mock_user = type('User', (), {
                'id': 1,
                'username': 'testuser',
                'email': 'test@example.com',
                'is_active': True,
                'is_admin': False,
                'language_preference': 'en',
                'created_at': None,
                'updated_at': None,
            })()
            mock_create_user.return_value = mock_user

            try:
                # Make request
                response = client.post(
                    "/api/users/",
                    json={
                        "username": "testuser",
                        "email": "test@example.com",
                        "password": "TestPassword123!",
                    }
                )

                # Assertions
                assert response.status_code == 200
                data = response.json()
                assert "id" in data
                assert data["username"] == "testuser"
                assert data["email"] == "test@example.com"
                assert "password" not in data  # Password should not be in response
            finally:
                app.dependency_overrides.clear()

    def test_register_user_duplicate_email(self, client, mock_db):
        """Test registration with duplicate email."""
        # Override database dependency - get_db is a generator
        def override_get_db():
            yield mock_db
        app.dependency_overrides[get_db] = override_get_db

        # Mock the service function at the API level where it's used
        with patch('app.users.api.create_user') as mock_create_user:
            mock_create_user.side_effect = Exception("Email already exists")

            try:
                # Make request
                response = client.post(
                    "/api/users/",
                    json={
                        "username": "testuser",
                        "email": "existing@example.com",
                        "password": "TestPassword123!",
                    }
                )

                # Assertions
                assert response.status_code == 400
            finally:
                app.dependency_overrides.clear()

    def test_login_success(self, client, mock_db):
        """Test successful login."""
        # Override database dependency - get_db is a generator
        def override_get_db():
            yield mock_db
        app.dependency_overrides[get_db] = override_get_db

        # Mock the service function at the API level where it's used
        with patch('app.auth.api.authenticate_user') as mock_authenticate:
            from app.users.models import User
            mock_user = type('User', (), {
                'email': 'test@example.com',
                'is_admin': False,
            })()
            mock_authenticate.return_value = mock_user

            try:
                # Make request (using OAuth2PasswordRequestForm format)
                response = client.post(
                    "/api/auth/token",
                    data={
                        "username": "test@example.com",
                        "password": "TestPassword123!",
                    }
                )

                # Assertions
                assert response.status_code == 200
                data = response.json()
                assert "access_token" in data
                assert data["token_type"] == "bearer"
            finally:
                app.dependency_overrides.clear()

    def test_login_invalid_credentials(self, client, mock_db):
        """Test login with invalid credentials."""
        # Override database dependency - get_db is a generator
        def override_get_db():
            yield mock_db
        app.dependency_overrides[get_db] = override_get_db

        # Mock the service function at the API level where it's used
        with patch('app.auth.api.authenticate_user') as mock_authenticate:
            mock_authenticate.return_value = None

            try:
                # Make request
                response = client.post(
                    "/api/auth/token",
                    data={
                        "username": "test@example.com",
                        "password": "WrongPassword",
                    }
                )

                # Assertions
                assert response.status_code == 401
            finally:
                app.dependency_overrides.clear()

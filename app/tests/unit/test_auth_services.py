"""Unit tests for authentication service functions."""
import pytest
from datetime import timedelta, datetime, timezone
from fastapi import Request
from unittest.mock import Mock
import jwt
from app.auth.services import (
    authenticate_user, create_access_token,
    is_token_admin, get_token_from_request
)
from app.core.config_loader import settings
from app.core.security import verify_password


@pytest.mark.unit
class TestAuthServices:
    """Test authentication service functions."""

    def test_authenticate_user_success(self, test_db, test_user):
        """Test successful authentication with correct credentials."""
        user = authenticate_user(test_user.email, "TestPassword123!", test_db)
        assert user is not None
        assert user.id == test_user.id
        assert user.email == test_user.email

    def test_authenticate_user_wrong_password(self, test_db, test_user):
        """Test authentication with wrong password."""
        user = authenticate_user(test_user.email, "WrongPassword", test_db)
        assert user is None

    def test_authenticate_user_nonexistent_user(self, test_db):
        """Test authentication with non-existent user."""
        user = authenticate_user("nonexistent@example.com", "Password123!", test_db)
        assert user is None

    def test_authenticate_user_case_insensitive_email(self, test_db, test_user):
        """Test that email authentication is case-insensitive."""
        user = authenticate_user(test_user.email.upper(), "TestPassword123!", test_db)
        assert user is not None
        assert user.id == test_user.id

    def test_create_access_token_success(self):
        """Test creating an access token."""
        data = {"sub": "test@example.com", "is_admin": False}
        token = create_access_token(data)
        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0

    def test_create_access_token_with_expires_delta(self):
        """Test creating an access token with custom expiration."""
        data = {"sub": "test@example.com"}
        expires_delta = timedelta(minutes=30)
        token = create_access_token(data, expires_delta)
        
        decoded = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.ALGORITHM])
        assert decoded["sub"] == "test@example.com"
        assert "exp" in decoded
        
        exp_time = datetime.fromtimestamp(decoded["exp"], tz=timezone.utc)
        now = datetime.now(timezone.utc)
        assert (exp_time - now).total_seconds() < 31 * 60
        assert (exp_time - now).total_seconds() > 29 * 60

    def test_create_access_token_default_expiration(self):
        """Test that default expiration is used when not specified."""
        data = {"sub": "test@example.com"}
        token = create_access_token(data)
        decoded = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.ALGORITHM])
        assert "exp" in decoded

    def test_is_token_admin_true(self, test_admin_user):
        """Test checking if token belongs to admin user."""
        data = {"sub": test_admin_user.email, "is_admin": True}
        token = create_access_token(data)
        assert is_token_admin(token) is True

    def test_is_token_admin_false(self, test_user):
        """Test checking if token belongs to non-admin user."""
        data = {"sub": test_user.email, "is_admin": False}
        token = create_access_token(data)
        assert is_token_admin(token) is False

    def test_is_token_admin_invalid_token(self):
        """Test that invalid token returns False."""
        assert is_token_admin("invalid_token") is False

    def test_get_token_from_request_cookie(self):
        """Test extracting token from cookie."""
        mock_request = Mock(spec=Request)
        mock_request.cookies = {"swagger_authentication": "cookie_token_123"}
        mock_request.headers = {}
        token = get_token_from_request(mock_request)
        assert token == "cookie_token_123"

    def test_get_token_from_request_header_fallback(self):
        """Test that header is used as fallback when cookie is missing."""
        mock_request = Mock(spec=Request)
        mock_request.cookies = {}
        mock_request.headers = {"Authorization": "Bearer header_token_123"}
        token = get_token_from_request(mock_request)
        assert token == "header_token_123"

    def test_get_token_from_request_cookie_precedence(self):
        """Test that cookie takes precedence over header."""
        mock_request = Mock(spec=Request)
        mock_request.cookies = {"swagger_authentication": "cookie_token_123"}
        mock_request.headers = {"Authorization": "Bearer header_token_123"}
        token = get_token_from_request(mock_request)
        assert token == "cookie_token_123"

    def test_get_token_from_request_none(self):
        """Test that None is returned when neither cookie nor header present."""
        mock_request = Mock(spec=Request)
        mock_request.cookies = {}
        mock_request.headers = {}
        token = get_token_from_request(mock_request)
        assert token is None



"""Unit tests for user service functions."""
import pytest
from datetime import datetime
from sqlalchemy.exc import IntegrityError
from app.users.services import (
    get_users, get_user, get_user_by_email, create_user_from_auth0,
    delete_user, update_user, update_language_preference
)
from app.users.schemas import UserUpdate


@pytest.mark.unit
class TestUserServices:
    """Test user service functions with real database."""

    def test_get_users_empty(self, test_db):
        """Test getting all users when database is empty."""
        users = get_users(test_db)
        assert users == []

    def test_get_users_with_data(self, test_db, test_user):
        """Test getting all users."""
        users = get_users(test_db)
        assert len(users) == 1
        assert users[0].id == test_user.id
        assert users[0].email == test_user.email

    def test_get_user_exists(self, test_db, test_user):
        """Test getting a user by ID when user exists."""
        user = get_user(test_db, test_user.id)
        assert user is not None
        assert user.id == test_user.id
        assert user.email == test_user.email

    def test_get_user_not_exists(self, test_db):
        """Test getting a user by ID when user doesn't exist."""
        user = get_user(test_db, "auth0|nonexistent")
        assert user is None

    def test_get_user_by_email_exists(self, test_db, test_user):
        """Test getting a user by email when user exists."""
        user = get_user_by_email(test_db, test_user.email)
        assert user is not None
        assert user.email == test_user.email
        assert user.id == test_user.id

    def test_get_user_by_email_case_insensitive(self, test_db, test_user):
        """Test that email lookup is case-insensitive."""
        user = get_user_by_email(test_db, test_user.email.upper())
        assert user is not None
        assert user.email == test_user.email

    def test_get_user_by_email_not_exists(self, test_db):
        """Test getting a user by email when user doesn't exist."""
        user = get_user_by_email(test_db, "nonexistent@example.com")
        assert user is None

    def test_create_user_from_auth0_success(self, test_db):
        """Test creating a new user from Auth0."""
        auth0_id = "auth0|newuser123"
        user = create_user_from_auth0(
            db=test_db,
            auth0_id=auth0_id,
            email="newuser@example.com",
            username="newuser"
        )
        assert user is not None
        assert user.id == auth0_id
        assert user.username == "newuser"
        assert user.email == "newuser@example.com"
        assert user.is_active is True
        # Note: Admin status is determined by Auth0 roles, not stored in database

    def test_create_user_from_auth0_email_normalized(self, test_db):
        """Test that email is normalized (lowercased and stripped) on creation."""
        auth0_id = "auth0|testuser123"
        user = create_user_from_auth0(
            db=test_db,
            auth0_id=auth0_id,
            email="  TEST@EXAMPLE.COM  ",
            username="testuser"
        )
        assert user.email == "test@example.com"

    def test_create_user_from_auth0_duplicate_email(self, test_db, test_user):
        """Test that creating user with duplicate email updates existing user."""
        # The function should update the existing user with the new Auth0 ID
        updated_user = create_user_from_auth0(
            db=test_db,
            auth0_id="auth0|anotheruser123",
            email=test_user.email,
            username="anotheruser"
        )
        assert updated_user.id == "auth0|anotheruser123"
        assert updated_user.email == test_user.email
        assert updated_user.username == test_user.username  # Username should remain the same

    def test_delete_user_exists(self, test_db, test_user):
        """Test deleting an existing user."""
        user_id = test_user.id
        delete_user(test_db, user_id)
        deleted_user = get_user(test_db, user_id)
        assert deleted_user is None

    def test_delete_user_not_exists(self, test_db):
        """Test deleting a non-existent user (should not raise error)."""
        delete_user(test_db, "auth0|nonexistent", delete_from_auth0=False)
        assert True

    def test_update_user_username(self, test_db, test_user):
        """Test updating user username."""
        update_data = UserUpdate(username="updateduser")
        updated_user = update_user(test_db, test_user, update_data)
        assert updated_user.username == "updateduser"
        assert updated_user.email == test_user.email


    def test_update_user_no_data(self, test_db, test_user):
        """Test updating user with no data raises ValueError."""
        update_data = UserUpdate()
        with pytest.raises(ValueError, match="No data provided to update"):
            update_user(test_db, test_user, update_data)


    def test_update_language_preference_valid(self, test_db, test_user):
        """Test updating language preference with valid language."""
        updated_user = update_language_preference(test_db, test_user, "de")
        assert updated_user.language_preference == "de"

    def test_update_language_preference_english(self, test_db, test_user):
        """Test updating language preference to English."""
        test_user.language_preference = "de"
        test_db.commit()
        updated_user = update_language_preference(test_db, test_user, "en")
        assert updated_user.language_preference == "en"

    def test_update_language_preference_invalid(self, test_db, test_user):
        """Test updating language preference with invalid language raises ValueError."""
        with pytest.raises(ValueError, match="Unsupported language"):
            update_language_preference(test_db, test_user, "fr")



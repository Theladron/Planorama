"""User management service functions."""
from typing import Optional
from sqlalchemy.orm import Session
from app.users.models import User
from app.users.schemas import UserUpdate
from app.core.logging_config import logger

def get_users(db: Session):
    """Retrieve all users from the database.
    
    Args:
        db: Database session.
        
    Returns:
        List of all User objects.
    """
    return db.query(User).all()


def get_user(db: Session, user_id: str):
    """Retrieve a user by their Auth0 ID.
    
    Args:
        db: Database session.
        user_id: Auth0 user identifier (e.g., "auth0|...").
        
    Returns:
        User object if found, None otherwise.
    """
    return db.query(User).filter_by(id=user_id).first()


def get_user_by_email(db: Session, email: str):
    """Retrieve a user by their email address.
    
    Args:
        db: Database session.
        email: User email address (case-insensitive).
        
    Returns:
        User object if found, None otherwise.
    """
    normalized_email = (email or "").strip().lower()
    return db.query(User).filter_by(email=normalized_email).first()


def get_user_by_auth0_id(db: Session, auth0_id: str):
    """Retrieve a user by their Auth0 ID.
    
    Args:
        db: Database session.
        auth0_id: Auth0 user identifier (e.g., "auth0|...").
        
    Returns:
        User object if found, None otherwise.
    """
    return db.query(User).filter_by(id=auth0_id).first()




def create_user_from_auth0(
    db: Session,
    auth0_id: str,
    email: str,
    username: Optional[str] = None
) -> User:
    """Create a new user from Auth0 token data.
    
    Args:
        db: Database session.
        auth0_id: Auth0 user identifier (e.g., "auth0|...").
        email: User email address.
        username: Optional username (defaults to email prefix if not provided).
        
    Returns:
        Created or existing User object.
        
    Raises:
        Exception: If user creation fails.
    """
    # Check if user already exists
    existing_user = get_user_by_auth0_id(db, auth0_id)
    if existing_user:
        return existing_user
    
    # Check if email already exists (shouldn't happen with Auth0, but safety check)
    existing_email = get_user_by_email(db, email)
    if existing_email:
        # Update existing user with Auth0 ID
        existing_email.id = auth0_id
        db.commit()
        db.refresh(existing_email)
        return existing_email
    
    # Generate username from email if not provided
    if not username:
        username = email.split("@")[0]
    
    # Ensure username is unique
    base_username = username
    counter = 1
    while db.query(User).filter_by(username=username).first():
        username = f"{base_username}{counter}"
        counter += 1
    
    try:
        db_user = User(
            id=auth0_id,
            email=email.strip().lower(),
            username=username,
            is_active=True,
            language_preference="en"
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    except Exception as error:
        db.rollback()
        logger.error(f"Error creating user from Auth0: {error}")
        raise


def delete_user(db: Session, user_id: str, delete_from_auth0: bool = True):
    """Delete a user from the database and optionally from Auth0.
    
    Args:
        db: Database session.
        user_id: Auth0 user identifier.
        delete_from_auth0: If True, also delete the user from Auth0 (default: True).
                          Set to False if you only want to delete from local database.
    """
    db_user = get_user(db, user_id)
    if db_user:
        # Delete from Auth0 first (if requested)
        if delete_from_auth0:
            try:
                from app.core.auth0_management import delete_auth0_user, get_management_api_token
                token = get_management_api_token()
                deleted = delete_auth0_user(user_id, token)
                if not deleted:
                    logger.warning(f"Failed to delete user {user_id} from Auth0, but continuing with database deletion.")
            except Exception as auth0_error:
                logger.warning(f"Error deleting user from Auth0: {auth0_error}")
        
        # Delete from local database
        db.delete(db_user)
        db.commit()


def update_user(db: Session, user: User, update_data: UserUpdate):
    """Update user information.
    
    NOTE: Password updates are not supported with Auth0 (Auth0 handles passwords).
    
    Args:
        db: Database session.
        user: User object to update.
        update_data: UserUpdate schema with fields to update.
        
    Returns:
        Updated User object.
        
    Raises:
        ValueError: If no update data provided or attempting to change password with Auth0.
    """
    if not update_data.username:
        raise ValueError("No data provided to update")

    if update_data.username:
        user.username = update_data.username

    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def update_language_preference(db: Session, user: User, new_language: str):
    """Update a user's language preference.
    
    Args:
        db: Database session.
        user: User object to update.
        new_language: Language code ('en' or 'de').
        
    Returns:
        Updated User object.
        
    Raises:
        ValueError: If language is not supported.
    """
    if new_language not in ["en", "de"]:
        raise ValueError("Unsupported language. Allowed values are 'en' and 'de'.")

    user.language_preference = new_language
    db.add(user)
    db.commit()
    db.refresh(user)
    return user
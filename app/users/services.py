"""User management service functions."""
from sqlalchemy.orm import Session
from app.core.security import hash_password, verify_password
from app.users.models import User
from app.users.schemas import UserCreate, UserUpdate

def get_users(db: Session):
    """Retrieve all users from the database.
    
    Args:
        db: Database session.
        
    Returns:
        List of all User objects.
    """
    return db.query(User).all()


def get_user(db: Session, user_id: int):
    """Retrieve a user by their ID.
    
    Args:
        db: Database session.
        user_id: Unique user identifier.
        
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


def create_user(db: Session, user: UserCreate):
    """Create a new user in the database.
    
    Args:
        db: Database session.
        user: UserCreate schema with user information.
        
    Returns:
        Created User object.
        
    Raises:
        Exception: If user creation fails (e.g., duplicate email).
    """
    try:
        db_user = User(
            email=str(user.email).strip().lower(),
            username=user.username,
            password_hash=hash_password(user.password)
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    except Exception as error:
        print(f"Error creating user: {error}")
        raise


def delete_user(db: Session, user_id: int):
    """Delete a user from the database.
    
    Args:
        db: Database session.
        user_id: Unique user identifier.
    """
    db_user = get_user(db, user_id)
    if db_user:
        db.delete(db_user)
        db.commit()


def update_user(db: Session, user: User, update_data: UserUpdate):
    """Update user information.
    
    Args:
        db: Database session.
        user: User object to update.
        update_data: UserUpdate schema with fields to update.
        
    Returns:
        Updated User object.
        
    Raises:
        ValueError: If no update data provided or old password is incorrect.
    """
    if not any([update_data.username, update_data.old_password, update_data.new_password]):
        raise ValueError("No data provided to update")

    if update_data.username:
        user.username = update_data.username

    if update_data.old_password and update_data.new_password:
        if not verify_password(update_data.old_password, user.password_hash):
            raise ValueError("Old password is incorrect")
        user.password_hash = hash_password(update_data.new_password)

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
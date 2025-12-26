from sqlalchemy.orm import Session
from app.core.security import hash_password, verify_password
from app.users.models import User
from app.users.schemas import UserCreate, UserUpdate

def get_users(db: Session):
    return db.query(User).all()


def get_user(db: Session, user_id: int):
    return db.query(User).filter_by(id=user_id).first()


def get_user_by_email(db: Session, email: str):
    normalized_email = (email or "").strip().lower()
    return db.query(User).filter_by(email=normalized_email).first()


def create_user(db: Session, user: UserCreate):
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
    db_user = get_user(db, user_id)
    if db_user:
        db.delete(db_user)
        db.commit()
    return


def update_user(db: Session, user: User, update_data: UserUpdate):
    if not any([update_data.username, update_data.old_password, update_data.new_password]):
        raise ValueError("No data provided to update")

    if update_data.username:
        user.username = update_data.username

    if update_data.old_password and update_data.new_password:
        # Verify old password correctness
        if not verify_password(update_data.old_password, user.password_hash):
            raise ValueError("Old password is incorrect")
        user.password_hash = hash_password(update_data.new_password)

        db.add(user)
        db.commit()
        db.refresh(user)
        return user

def update_language_preference(db: Session, user: User, new_language: str):
    if new_language not in ["en", "de"]:
        raise ValueError("Unsupported language. Allowed values are 'en' and 'de'.")

    user.language_preference = new_language
    db.add(user)
    db.commit()
    db.refresh(user)
    return user
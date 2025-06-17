from sqlalchemy.orm import Session
from app.core.security import hash_password
from app.users.models import User
from app.users.schemas import UserCreate

def get_users(db: Session):
    return db.query(User).all()


def get_user(db: Session, user_id: int):
    return db.query(User).filter_by(id=user_id).first()


def get_user_by_email(db: Session, email: str):
    return db.query(User).filter_by(email=email).first()


def create_user(db: Session, user: UserCreate):
    db_user = User(
        email=str(user.email),
        username=user.username,
        password=hash_password(user.password)
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def delete_user(db: Session, user_id: int):
    db_user = get_user(db, user_id)
    if db_user:
        db.delete(db_user)
        db.commit()
    return
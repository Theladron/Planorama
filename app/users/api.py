from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.auth.services import get_current_active_user, get_current_admin_user
from app.core.database import get_db
from app.users.models import User
from app.users.schemas import UserSchema, UserCreate
from app.users.services import get_users, create_user, get_user, delete_user

user_router = APIRouter(
    prefix='/users',
    tags=['Users']
)
admin_user_router = APIRouter(
    prefix='/admin',
    tags=['Admin']
)

@user_router.get(
    '/',
    response_model=list[UserSchema],
    summary="List all users",
    description="Returns a list of all users in the system. This route should typically be restricted or extended with authentication if needed."
)
def user_list(db: Session = Depends(get_db)):
    db_users = get_users(db)
    return db_users


@user_router.get(
    '/me',
    response_model=UserSchema,
    summary="Get current user",
    description="Returns the currently authenticated user's information based on the token in use."
)
def get_current_user(current_user: User = Depends(get_current_active_user)):
    return current_user


@user_router.get(
    '/{user_id}',
    response_model=UserSchema,
    summary="Get user by ID",
    description="Fetches a user's details using their user ID. Returns 404 if the user does not exist."
)
def user_detail(user_id: int, db: Session = Depends(get_db)):
    db_user = get_user(db, user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


@user_router.delete(
    '/{user_id}',
    summary="Delete user by ID",
    description="Deletes a user from the database by their ID. Returns a confirmation message if successful."
)
def user_delete(user_id: int, db: Session = Depends(get_db)):
    db_user = get_user(db, user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    delete_user(db, db_user.id)
    return {"message": "User deleted"}


@user_router.post(
    "/",
    response_model=UserSchema,
    summary="Create a new user",
    description="Creates a new user account with the specified username, email, and password."
)
def user_post(user: UserCreate, db: Session = Depends(get_db)):
    return create_user(db, user)


@admin_user_router.delete(
    "/{user_id}",
    summary="Admin: Delete any user by ID",
    description="Allows an admin user to delete any user in the system by providing the user's ID."
)
def admin_delete_user_by_id(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    db_user = get_user(db, user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    delete_user(db, user_id)
    return {"message": "User deleted by admin"}

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.auth.services import get_current_active_user, get_current_admin_user
from app.core.database import get_db
from app.users.models import User
from app.users.schemas import UserSchema, UserCreate, UserUpdate, LanguagePreferenceUpdate
from app.users.services import (get_users,
                                create_user,
                                get_user,
                                delete_user,
                                update_user,
                                update_language_preference)

user_router = APIRouter(
    prefix="/users",
    tags=["Users"]
)

admin_user_router = APIRouter(
    prefix="/admin/users",
    tags=["Admin"]
)


@user_router.post(
    "/",
    response_model=UserSchema,
    summary="Register a new user",
    description="Creates a new user account with a username, email, and password."
)
def user_post(user: UserCreate, db: Session = Depends(get_db)):
    try:
        return create_user(db, user)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"User creation failed: {str(e)}")


@user_router.get(
    "/me",
    response_model=UserSchema,
    summary="Get current user",
    description="Returns information about the currently authenticated user."
)
def get_current_user(current_user: User = Depends(get_current_active_user)):
    return current_user


@user_router.patch(
    "/me",
    response_model=UserSchema,
    summary="Update current user's username and/or password",
    description="Allows user to update username and password (must provide old password to change password)."
)
def update_current_user(
    update_data: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    try:
        updated_user = update_user(db, current_user, update_data)
        return updated_user
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@user_router.patch(
    "/me/language",
    summary="Update current user's language preference",
    description="Change language preference to 'en' or 'de'."
)
def update_language(
    language_update: LanguagePreferenceUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    updated_user = update_language_preference(db, current_user, language_update.language_preference)
    return {"message": "Language preference updated successfully.",
            "language_preference": updated_user.language_preference}


@user_router.delete(
    "/me",
    summary="Delete your own user account",
    description="Deletes the authenticated user's account and returns a confirmation message. Client should clear auth token after this."
)
def delete_current_user(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    delete_user(db, current_user.id)
    return {"message": "Your account has been deleted. Please log out."}


@admin_user_router.get(
    "/",
    response_model=list[UserSchema],
    summary="Admin: List all users",
    description="Returns a list of all users. Admin access required."
)
def admin_user_list(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    users = get_users(db)
    return users


@admin_user_router.get(
    "/{user_id}",
    response_model=UserSchema,
    summary="Admin: Get user by ID",
    description="Returns user data for the specified ID. Admin access required."
)
def admin_get_user_by_id(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    user = get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@admin_user_router.delete(
    "/{user_id}",
    summary="Admin: Delete user by ID",
    description="Deletes a user by ID. Admin access required."
)
def admin_delete_user_by_id(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    user = get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    delete_user(db, user_id)
    return {"message": f"User with ID {user_id} deleted by admin."}

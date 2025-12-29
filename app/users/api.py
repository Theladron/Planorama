from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.auth.services import get_current_active_user, get_current_admin_user
from app.core.database import get_db
from app.users.models import User
from app.users.schemas import UserSchema, UserUpdate, LanguagePreferenceUpdate, PasswordUpdate
from app.users.services import (get_users,
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
    summary="Update current user's username",
    description="Allows user to update username."
)
def update_current_user(
    update_data: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    try:
        updated_user = update_user(db, current_user, update_data)
        return updated_user
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))


@user_router.patch(
    "/me/password",
    summary="Update current user's password",
    description="Updates the user's password in Auth0."
)
def update_password(
    password_data: PasswordUpdate,
    current_user: User = Depends(get_current_active_user)
):
    """Update user password via Auth0 Management API.
    
    Args:
        password_data: PasswordUpdate schema with new password.
        current_user: Current authenticated user.
        
    Returns:
        Success message.
        
    Raises:
        HTTPException: If password update fails.
    """
    new_password = password_data.password
    
    try:
        from app.core.auth0_management import get_management_api_token
        import requests
        from app.core.config_loader import settings
        
        token = get_management_api_token()
        url = f"https://{settings.AUTH0_DOMAIN}/api/v2/users/{current_user.id}"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        payload = {"password": new_password}
        
        response = requests.patch(url, json=payload, headers=headers, timeout=10)
        response.raise_for_status()
        
        return {"message": "Password updated successfully"}
    except requests.exceptions.HTTPError as e:
        error_detail = "Failed to update password"
        try:
            error_json = e.response.json()
            error_detail = error_json.get("message", str(error_json))
        except:
            error_detail = f"HTTP {e.response.status_code}: {e.response.text}"
        raise HTTPException(status_code=400, detail=error_detail)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update password: {str(e)}")


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
    summary="Admin: Get user by Auth0 ID",
    description="Returns user data for the specified Auth0 ID. Admin access required."
)
def admin_get_user_by_id(
    user_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    user = get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@admin_user_router.delete(
    "/{user_id}",
    summary="Admin: Delete user by Auth0 ID",
    description="Deletes a user by Auth0 ID. Admin access required."
)
def admin_delete_user_by_id(
    user_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    user = get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    delete_user(db, user_id)
    return {"message": f"User with Auth0 ID {user_id} deleted by admin."}

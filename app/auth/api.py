"""Auth router - Auth0 authentication only."""
from fastapi import APIRouter
from fastapi.responses import JSONResponse

auth_router = APIRouter(
    prefix="/auth",
    tags=["auth"],
)

# All authentication is now handled by Auth0
# Tokens are verified via get_current_user dependency in app/auth/services.py


@auth_router.get("/health")
async def auth_health():
    """Health check endpoint for auth service.
    
    Returns:
        JSON response indicating auth service is available.
    """
    return JSONResponse({
        "status": "ok",
        "message": "Auth service is running. Authentication is handled by Auth0.",
        "auth_method": "Auth0"
    })

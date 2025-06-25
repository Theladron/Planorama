from fastapi import APIRouter, Depends, HTTPException, status, Header
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
from app.auth.models import Token
from app.auth.services import authenticate_user, create_access_token
from app.core.database import get_db

auth_router = APIRouter(
    prefix="/auth",
    tags=["auth"],
)

@auth_router.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(
        data={
            "sub": user.email,
            "is_admin": user.is_admin,  # include admin info in token
        },
        expires_delta=access_token_expires,
    )
    return Token(access_token=access_token, token_type="bearer")


@auth_router.get("/check-token", status_code=200)
async def check_token_validity(authorization: str = Header(None)):
    """
    Validates the token sent in Authorization header.
    Returns 200 if valid, 401 if invalid.
    """
    if authorization is None or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid authorization header")

    token = authorization[7:]
    from app.auth.services import is_token_admin  # avoid circular import if any

    try:
        # Just try decoding it; if invalid, will raise
        from jwt import decode, InvalidTokenError
        from app.core.config_loader import settings
        SECRET_KEY = settings.JWT_SECRET_KEY
        ALGORITHM = "HS256"

        decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        # Token valid, return 200 OK
        return {"detail": "Token valid"}
    except InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

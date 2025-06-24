from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from fastapi.security import OAuth2PasswordRequestForm
from app.auth.models import Token
from app.auth.services import authenticate_user, create_access_token
from app.core.database import get_db
from typing import Annotated
from sqlalchemy.orm import Session
from datetime import timedelta

auth_router = APIRouter(
    prefix="/auth",
    tags=["auth"],
)

@auth_router.post("/token")
async def login_for_access_token(
    form_data = Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Session = Depends(get_db)
    ) -> Token:
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
            "is_admin": user.is_admin  # 👈 add this!
        },
        expires_delta=access_token_expires
    )

    return Token(access_token=access_token, token_type="bearer")
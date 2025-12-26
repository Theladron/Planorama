"""Authentication and authorization service functions."""
from fastapi import Depends, HTTPException, status, Request, Header
from sqlalchemy.orm import Session
from datetime import datetime, timedelta, timezone
from app.core.database import get_db
from app.users.services import get_user_by_email
from app.core.security import verify_password
from app.users.models import User
from typing import Optional
import jwt
from app.core.config_loader import settings
from jwt import decode, InvalidTokenError, ExpiredSignatureError

SECRET_KEY = settings.JWT_SECRET_KEY
ALGORITHM = settings.ALGORITHM


def authenticate_user(email: str, password: str, db: Session) -> Optional[User]:
    """Authenticate a user by email and password.
    
    Args:
        email: User email address.
        password: Plain text password.
        db: Database session.
        
    Returns:
        User object if authentication succeeds, None otherwise.
    """
    user = get_user_by_email(db, (email or "").strip().lower())
    if not user:
        return None
    if not verify_password(password, user.password_hash):
        return None
    return user


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token.
    
    Args:
        data: Dictionary containing token claims (typically includes 'sub' for email).
        expires_delta: Optional timedelta for token expiration (defaults to 60 minutes).
        
    Returns:
        Encoded JWT token string.
    """
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta if expires_delta
                                           else timedelta(minutes=60))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_token_from_auth_header(request: Request) -> str:
    """Extract JWT token from Authorization header.
    
    Args:
        request: FastAPI Request object.
        
    Returns:
        JWT token string (without 'Bearer ' prefix).
        
    Raises:
        HTTPException: If Authorization header is missing or invalid.
    """
    authorization = request.headers.get("Authorization")

    if authorization is None or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid authorization header")

    return authorization[7:]


async def get_current_user(token: str = Depends(get_token_from_auth_header),
                           db: Session = Depends(get_db)) -> User:
    """Get the current authenticated user from JWT token.
    
    Args:
        token: JWT token string.
        db: Database session.
        
    Returns:
        User object for the authenticated user.
        
    Raises:
        HTTPException: If token is invalid, expired, or user not found.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    expired_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token expired",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except ExpiredSignatureError:
        raise expired_exception
    except InvalidTokenError:
        raise credentials_exception

    user = get_user_by_email(db, email=email)
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """Get the current authenticated and active user.
    
    Args:
        current_user: User object from get_current_user dependency.
        
    Returns:
        User object if active.
        
    Raises:
        HTTPException: If user account is inactive.
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user",
        )
    return current_user


async def get_current_admin_user(current_user: User = Depends(get_current_user)) -> User:
    """Get the current authenticated admin user.
    
    Args:
        current_user: User object from get_current_user dependency.
        
    Returns:
        User object if admin.
        
    Raises:
        HTTPException: If user is not an admin.
    """
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )
    return current_user


def is_token_admin(token: str) -> bool:
    """Check if a JWT token belongs to an admin user.
    
    Args:
        token: JWT token string.
        
    Returns:
        True if token is valid and belongs to an admin, False otherwise.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload.get("is_admin", False)
    except jwt.InvalidTokenError:
        return False

def get_token_from_request(request: Request) -> Optional[str]:
    """Extract JWT token from request (checks cookie first, then header).
    
    Args:
        request: FastAPI Request object.
        
    Returns:
        JWT token string if found, None otherwise.
    """
    token = request.cookies.get("swagger_authentication")
    if token:
        return token
    auth = request.headers.get("Authorization")
    if auth and auth.startswith("Bearer "):
        return auth[7:]
    return None
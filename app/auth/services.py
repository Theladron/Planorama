"""Authentication and authorization service functions for Auth0."""
import requests
from jose import jwt, JWTError
from fastapi import Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from typing import Dict, Any
from app.core.database import get_db
from app.core.config_loader import settings
from app.users.models import User
from app.users.services import get_user_by_auth0_id, create_user_from_auth0, get_user_by_email


def get_auth0_jwks() -> Dict[str, Any]:
    """Fetch Auth0 JSON Web Key Set (JWKS) for token verification.
    
    Returns:
        Dictionary containing Auth0 public keys.
        
    Raises:
        HTTPException: If unable to fetch JWKS.
    """
    if not settings.AUTH0_DOMAIN:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="AUTH0_DOMAIN not configured"
        )
    
    jwks_url = f"https://{settings.AUTH0_DOMAIN}/.well-known/jwks.json"
    try:
        response = requests.get(jwks_url, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch Auth0 JWKS: {str(e)}"
        )


def get_rsa_key(token: str, jwks: Dict[str, Any]) -> Dict[str, Any]:
    """Get the RSA public key from JWKS that matches the token's key ID.
    
    Args:
        token: JWT token string.
        jwks: JWKS dictionary from Auth0.
        
    Returns:
        RSA key dictionary.
        
    Raises:
        HTTPException: If no matching key found.
    """
    try:
        unverified_header = jwt.get_unverified_header(token)
        kid = unverified_header.get("kid")
        
        if not kid:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token missing key ID (kid)"
            )
        
        for key in jwks.get("keys", []):
            if key.get("kid") == kid:
                return {
                    "kty": key["kty"],
                    "kid": key["kid"],
                    "use": key["use"],
                    "n": key["n"],
                    "e": key["e"]
                }
        
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unable to find appropriate key in JWKS"
        )
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token header: {str(e)}"
        )


def decode_auth0_token(token: str) -> Dict[str, Any]:
    """Decode and verify an Auth0 JWT token.
    
    Args:
        token: Auth0 JWT token string.
        
    Returns:
        Decoded token payload (claims).
        
    Raises:
        HTTPException: If token is invalid, expired, or verification fails.
    """
    if not settings.AUTH0_DOMAIN or not settings.AUTH0_AUDIENCE:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Auth0 not configured (AUTH0_DOMAIN or AUTH0_AUDIENCE missing)"
        )
    
    try:
        jwks = get_auth0_jwks()
        rsa_key = get_rsa_key(token, jwks)
        issuer = f"https://{settings.AUTH0_DOMAIN}/"
        
        payload = jwt.decode(
            token,
            rsa_key,
            algorithms=["RS256"],
            audience=settings.AUTH0_AUDIENCE,
            issuer=issuer
        )
        
        return payload
        
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Token verification error: {str(e)}"
        )


def has_admin_permission(token: str) -> bool:
    """Check if token has admin permission.
    
    Args:
        token: Auth0 JWT token string.
        
    Returns:
        True if token has Admin role or admin permission, False otherwise.
    """
    try:
        payload = decode_auth0_token(token)
        
        permissions = payload.get("permissions", [])
        if "admin" in permissions:
            return True
        
        for key in payload.keys():
            if "roles" in key.lower():
                roles = payload.get(key, [])
                if isinstance(roles, list) and "Admin" in roles:
                    return True
        
        return False
    except HTTPException:
        return False


def verify_auth0_token_and_get_user(token: str, db: Session) -> User:
    """Verify Auth0 JWT token and return or create user.
    
    Args:
        token: Auth0 JWT token string.
        db: Database session.
        
    Returns:
        User object.
        
    Raises:
        HTTPException: If token is invalid or user creation fails.
    """
    try:
        payload = decode_auth0_token(token)
        auth0_id = payload.get("sub")
        if not auth0_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token missing subject (sub) claim"
            )
        
        user = get_user_by_auth0_id(db, auth0_id)
        if user:
            db.refresh(user)
            return user
        
        email = payload.get("email")
        if not email:
            from app.core.auth0_management import get_management_api_token
            
            try:
                mgmt_token = get_management_api_token()
                url = f"https://{settings.AUTH0_DOMAIN}/api/v2/users/{auth0_id}"
                headers = {
                    "Authorization": f"Bearer {mgmt_token}",
                    "Content-Type": "application/json"
                }
                response = requests.get(url, headers=headers, timeout=10)
                response.raise_for_status()
                auth0_user_data = response.json()
                email = auth0_user_data.get("email")
            except Exception as e:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Unable to retrieve user email from Auth0"
                )
        
        if not email:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Unable to determine user email"
            )
        
        existing_user = get_user_by_email(db, email)
        if existing_user:
            existing_user.id = auth0_id
            db.commit()
            db.refresh(existing_user)
            return existing_user
        
        username = payload.get("preferred_username") or payload.get("nickname")
        if not username:
            username = email.split("@")[0]
        
        user = create_user_from_auth0(
            db=db,
            auth0_id=auth0_id,
            email=email,
            username=username
        )
        
        return user
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process Auth0 token: {str(e)}"
        )


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
    
    if authorization is None:
        raise HTTPException(status_code=401, detail="Missing authorization header")
    
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authorization header format")

    return authorization[7:]


async def get_current_user(token: str = Depends(get_token_from_auth_header),
                           db: Session = Depends(get_db)) -> User:
    """Get the current authenticated user from Auth0 JWT token.
    
    Args:
        token: Auth0 JWT token string.
        db: Database session.
        
    Returns:
        User object for the authenticated user (created if doesn't exist).
        
    Raises:
        HTTPException: If token is invalid, expired, or user creation fails.
    """
    try:
        return verify_auth0_token_and_get_user(token, db)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Could not validate credentials: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )


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


async def get_current_admin_user(
    token: str = Depends(get_token_from_auth_header),
    current_user: User = Depends(get_current_user)
) -> User:
    """Get the current authenticated admin user.
    
    Args:
        token: Auth0 JWT token string.
        current_user: User object from get_current_user dependency.
        
    Returns:
        User object if admin.
        
    Raises:
        HTTPException: If user is not an admin.
    """
    if not has_admin_permission(token):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )
    return current_user


def get_token_from_request(request: Request) -> str | None:
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
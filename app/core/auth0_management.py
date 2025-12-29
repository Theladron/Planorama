"""Auth0 Management API client for user management operations."""
import requests
from typing import Optional, Dict, Any
from app.core.config_loader import settings
from app.core.logging_config import logger


def get_management_api_token() -> str:
    """Get an access token for the Auth0 Management API.
    
    Returns:
        Management API access token.
        
    Raises:
        ValueError: If credentials are not configured.
        Exception: If token request fails.
    """
    if not settings.AUTH0_MANAGEMENT_CLIENT_ID:
        raise ValueError("AUTH0_MANAGEMENT_CLIENT_ID is not set")
    if not settings.AUTH0_MANAGEMENT_CLIENT_SECRET:
        raise ValueError("AUTH0_MANAGEMENT_CLIENT_SECRET is not set")
    if not settings.AUTH0_DOMAIN:
        raise ValueError("AUTH0_DOMAIN is not set")
    
    url = f"https://{settings.AUTH0_DOMAIN}/oauth/token"
    payload = {
        "client_id": settings.AUTH0_MANAGEMENT_CLIENT_ID,
        "client_secret": settings.AUTH0_MANAGEMENT_CLIENT_SECRET,
        "audience": f"https://{settings.AUTH0_DOMAIN}/api/v2/",
        "grant_type": "client_credentials"
    }
    headers = {"content-type": "application/json"}
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        if "access_token" not in data:
            raise ValueError(f"Auth0 response missing access_token: {data}")
        return data["access_token"]
    except requests.exceptions.HTTPError as e:
        error_detail = ""
        try:
            error_data = e.response.json()
            error_detail = f" - {error_data}"
        except:
            error_detail = f" - {e.response.text}"
        raise Exception(f"Failed to get Management API token: {e}{error_detail}")


def search_user_by_email(email: str, token: str) -> Optional[Dict[str, Any]]:
    """Search for a user in Auth0 by email address.
    
    Args:
        email: User email address.
        token: Management API access token.
        
    Returns:
        User object if found, None otherwise.
    """
    url = f"https://{settings.AUTH0_DOMAIN}/api/v2/users-by-email"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    params = {"email": email}
    
    try:
        response = requests.get(url, headers=headers, params=params, timeout=10)
        response.raise_for_status()
        users = response.json()
        return users[0] if users else None
    except requests.exceptions.RequestException:
        return None


def create_auth0_user(
    email: str,
    username: str,
    password: str,
    token: str,
    email_verified: bool = False
) -> Dict[str, Any]:
    """Create a new user in Auth0 via Management API.
    
    SECURITY: This function requires Management API access and should ONLY
    be called from trusted server-side code (e.g., seed scripts). Never expose
    as a public API endpoint.
    
    Args:
        email: User email address.
        username: Username.
        password: User password.
        token: Management API access token (obtained via get_management_api_token).
        email_verified: Whether the email should be marked as verified (default: False).
                        WARNING: Only set to True for trusted system/admin users.
                        Regular users must verify their email through Auth0's standard flow.
        
    Returns:
        Created user object from Auth0.
        
    Raises:
        Exception: If user creation fails.
    """
    url = f"https://{settings.AUTH0_DOMAIN}/api/v2/users"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    # Build payload - Auth0 database connections typically use email as username
    # Only include username field if the connection requires it (requires_username setting)
    # Most connections don't need it, so we omit it by default to avoid errors
    payload = {
        "email": email,
        "password": password,
        "email_verified": email_verified,
        "connection": settings.AUTH0_CONNECTION_NAME
    }
    
    response = requests.post(url, json=payload, headers=headers, timeout=10)
    
    # Provide detailed error information
    if not response.ok:
        error_detail = "Unknown error"
        try:
            error_json = response.json()
            error_detail = error_json.get("message", str(error_json))
            if "code" in error_json:
                error_detail = f"{error_json['code']}: {error_detail}"
        except (ValueError, KeyError):
            error_detail = response.text or f"HTTP {response.status_code}"
        
        raise requests.exceptions.HTTPError(
            f"Failed to create Auth0 user: {error_detail} (Status: {response.status_code})"
        )
    
    return response.json()


def ensure_email_verified(user_id: str, token: str) -> bool:
    """Ensure a user's email is verified in Auth0.
    
    Args:
        user_id: Auth0 user ID.
        token: Management API access token.
        
    Returns:
        True if email is verified (or was successfully updated), False otherwise.
    """
    url = f"https://{settings.AUTH0_DOMAIN}/api/v2/users/{user_id}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    try:
        # First, get current user to check status
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        user = response.json()
        
        # If already verified, no need to update
        if user.get("email_verified", False):
            return True
        
        # Update to verified
        payload = {"email_verified": True}
        response = requests.patch(url, json=payload, headers=headers, timeout=10)
        response.raise_for_status()
        return True
    except requests.exceptions.RequestException as e:
        logger.warning(f"Failed to verify email for user {user_id}: {e}")
        return False


def get_or_create_auth0_user(
    email: str,
    username: str,
    password: str,
    email_verified: bool = False
) -> Dict[str, Any]:
    """Get existing user from Auth0 or create a new one via Management API.
    
    Args:
        email: User email address.
        username: Username.
        password: User password (only used if user needs to be created).
        email_verified: Whether the email should be verified (default: False).
        
    Returns:
        User object from Auth0 with 'user_id' field.
        
    Raises:
        Exception: If user fetch/creation fails.
    """
    token = get_management_api_token()
    
    # Try to find existing user
    existing_user = search_user_by_email(email, token)
    if existing_user:
        user_id = existing_user.get('user_id')
        print(f"Found existing Auth0 user with email '{email}' (ID: {user_id})")
        # Only verify email if explicitly requested (for admin users)
        if email_verified:
            ensure_email_verified(user_id, token)
        return existing_user
    
    # Create new user
    print(f"Creating new Auth0 user with email '{email}'...")
    new_user = create_auth0_user(email, username, password, token, email_verified=email_verified)
    verified_status = "verified" if email_verified else "unverified"
    print(f"Created Auth0 user with ID: {new_user.get('user_id')} (email: {verified_status})")
    return new_user


def delete_auth0_user(user_id: str, token: str) -> bool:
    """Delete a user from Auth0.
    
    Args:
        user_id: Auth0 user ID (e.g., "auth0|...").
        token: Management API access token.
        
    Returns:
        True if successful, False otherwise.
    """
    url = f"https://{settings.AUTH0_DOMAIN}/api/v2/users/{user_id}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.delete(url, headers=headers, timeout=10)
        response.raise_for_status()
        return True
    except requests.exceptions.RequestException as e:
        logger.warning(f"Failed to delete user from Auth0: {e}")
        return False


def block_auth0_user(user_id: str, token: str, blocked: bool = True) -> bool:
    """Block or unblock a user in Auth0.
    
    Args:
        user_id: Auth0 user ID (e.g., "auth0|...").
        token: Management API access token.
        blocked: True to block user, False to unblock.
        
    Returns:
        True if successful, False otherwise.
    """
    url = f"https://{settings.AUTH0_DOMAIN}/api/v2/users/{user_id}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    payload = {"blocked": blocked}
    
    try:
        response = requests.patch(url, json=payload, headers=headers, timeout=10)
        response.raise_for_status()
        return True
    except requests.exceptions.RequestException as e:
        logger.warning(f"Failed to {'block' if blocked else 'unblock'} user in Auth0: {e}")
        return False


def assign_admin_role_to_user(user_id: str, token: str) -> bool:
    """Assign admin role to a user in Auth0.
    
    Args:
        user_id: Auth0 user ID.
        token: Management API access token.
        
    Returns:
        True if successful, False otherwise.
    """
    # First, we need to get the role ID for "Admin"
    # This is a simplified version - you may need to adjust based on your Auth0 setup
    roles_url = f"https://{settings.AUTH0_DOMAIN}/api/v2/roles"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    try:
        # Get all roles to find "Admin"
        response = requests.get(roles_url, headers=headers, timeout=10)
        
        if response.status_code == 403:
            logger.error("Management API token does not have permission to read roles. M2M application needs read:roles and assign:roles permissions.")
            return False
        
        response.raise_for_status()
        roles = response.json()
        
        admin_role = next((r for r in roles if r.get("name") == "Admin"), None)
        if not admin_role:
            logger.error("'Admin' role not found in Auth0. Please create an 'Admin' role in Auth0 Dashboard.")
            return False
        
        assign_url = f"https://{settings.AUTH0_DOMAIN}/api/v2/users/{user_id}/roles"
        payload = {"roles": [admin_role["id"]]}
        response = requests.post(assign_url, json=payload, headers=headers, timeout=10)
        
        if response.status_code == 403:
            logger.error("Management API token does not have permission to assign roles. M2M application needs assign:roles permission.")
            return False
        
        response.raise_for_status()
        logger.info(f"Assigned 'Admin' role to user {user_id}")
        return True
    except requests.exceptions.HTTPError as e:
        error_detail = "Unknown error"
        try:
            error_json = e.response.json()
            error_detail = error_json.get("message", str(error_json))
        except (ValueError, AttributeError):
            error_detail = str(e)
        logger.error(f"Failed to assign admin role: {error_detail}")
        return False
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to assign admin role: {e}")
        return False


"""Seed script for initial admin user creation from Auth0."""
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from app.core.database import SessionLocal, import_all_models
from app.core.config_loader import settings
from app.core.logging_config import logger
from app.core.auth0_management import (
    get_or_create_auth0_user,
    assign_admin_role_to_user,
    get_management_api_token,
    search_user_by_email,
    ensure_email_verified
)
from app.users.models import User
from app.users.services import get_user_by_auth0_id, create_user_from_auth0

import_all_models()


def seed_admin_user():
    """Create or fetch admin user from Auth0 and seed into database.
    
    Process:
    1. Get or create admin user in Auth0 using email/username/password
    2. Fetch the Auth0 user ID from the created/found user
    3. Check if user exists in our database by Auth0 ID
    4. If not, create user in database with admin privileges
    5. Optionally assign Admin role in Auth0
    
    Reads admin credentials from environment variables:
    - ADMIN_EMAIL: Admin email address
    - ADMIN_USERNAME: Admin username
    - ADMIN_PASSWORD: Admin password (for initial creation)
    """
    admin_email = settings.ADMIN_EMAIL
    admin_username = settings.ADMIN_USERNAME
    admin_password = settings.ADMIN_PASSWORD
    
    if not admin_email:
        logger.warning("ADMIN_EMAIL not set. Skipping admin user creation.")
        return
    
    if not admin_username:
        admin_username = admin_email.split("@")[0]
        logger.warning(f"ADMIN_USERNAME not set. Using '{admin_username}' from email.")
    
    if not admin_password:
        logger.warning("ADMIN_PASSWORD not set. Will try to find existing user in Auth0.")
        admin_password = None
    
    if not settings.AUTH0_MANAGEMENT_CLIENT_ID or not settings.AUTH0_MANAGEMENT_CLIENT_SECRET:
        logger.error("AUTH0_MANAGEMENT_CLIENT_ID and AUTH0_MANAGEMENT_CLIENT_SECRET must be set.")
        return
    
    db: Session = SessionLocal()
    try:
        logger.debug(f"Checking Auth0 for user with email '{admin_email}'...")
        try:
            if admin_password:
                auth0_user = get_or_create_auth0_user(
                    email=admin_email.lower().strip(),
                    username=admin_username,
                    password=admin_password,
                    email_verified=True
                )
            else:
                token = get_management_api_token()
                auth0_user = search_user_by_email(admin_email.lower().strip(), token)
                if not auth0_user:
                    logger.error("ADMIN_PASSWORD not set and user not found in Auth0. Cannot proceed.")
                    return
                ensure_email_verified(auth0_user.get("user_id"), token)
        except Exception as auth0_error:
            logger.error(f"Failed to get/create user in Auth0: {auth0_error}")
            raise
        
        auth0_user_id = auth0_user.get("user_id")
        if not auth0_user_id:
            logger.error(f"Failed to get Auth0 user ID from Auth0 response: {auth0_user}")
            return
        
        if not isinstance(auth0_user_id, str) or not auth0_user_id.strip():
            logger.error(f"Invalid Auth0 user ID: {auth0_user_id}")
            return
        
        logger.debug(f"Auth0 user ID: {auth0_user_id}")
        
        existing_db_user = get_user_by_auth0_id(db, auth0_user_id)
        if existing_db_user:
            logger.debug(f"User with Auth0 ID '{auth0_user_id}' already exists in database.")
        else:
            logger.debug(f"Creating user '{admin_username}' in database with Auth0 ID '{auth0_user_id}'...")
            try:
                admin_user = create_user_from_auth0(
                    db=db,
                    auth0_id=auth0_user_id,
                    email=admin_email.lower().strip(),
                    username=admin_username
                )
                logger.info(f"Admin user '{admin_username}' ({admin_email}) created successfully in database.")
            except Exception as create_error:
                logger.error(f"Failed to create user in database: {create_error}")
                raise
        
        logger.debug(f"Assigning 'Admin' role to user {auth0_user_id} in Auth0...")
        try:
            token = get_management_api_token()
            success = assign_admin_role_to_user(auth0_user_id, token)
            if success:
                logger.info(f"Successfully assigned 'Admin' role to user {auth0_user_id} in Auth0.")
            else:
                logger.error("CRITICAL: Failed to assign 'Admin' role in Auth0. The user will NOT have admin privileges.")
                raise Exception("Admin role assignment failed")
        except Exception as role_error:
            if "Admin role assignment failed" in str(role_error):
                raise
            logger.error(f"Could not assign Admin role in Auth0: {role_error}")
            raise
        
    except IntegrityError:
        logger.debug("User with Auth0 ID already exists (detected via IntegrityError). Skipping creation.")
        db.rollback()
    except Exception as error:
        logger.error(f"Failed to seed admin user: {error}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_admin_user()


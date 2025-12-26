"""
Seed script for initial admin user creation.
This script creates an admin user if one doesn't already exist.
"""
import os
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from app.core.database import SessionLocal, import_all_models
from app.core.security import hash_password
from app.users.models import User

import_all_models()


def seed_admin_user():
    """Create an admin user if it doesn't exist."""
    admin_email = os.getenv("ADMIN_EMAIL", "admin@planorama.com")
    admin_username = os.getenv("ADMIN_USERNAME", "admin")
    admin_password = os.getenv("ADMIN_PASSWORD")
    
    if not admin_password:
        print("WARNING: ADMIN_PASSWORD not set. Skipping admin user creation.")
        return
    
    db: Session = SessionLocal()
    try:
        existing_admin = db.query(User).filter_by(email=admin_email.lower().strip()).first()
        if existing_admin:
            print(f"Admin user with email '{admin_email}' already exists. Skipping creation.")
            if not existing_admin.is_admin:
                existing_admin.is_admin = True
                db.commit()
                print(f"Updated user '{admin_email}' to have admin privileges.")
            return
        admin_user = User(
            email=admin_email.lower().strip(),
            username=admin_username,
            password_hash=hash_password(admin_password),
            is_admin=True,
            is_active=True,
            language_preference="en"
        )
        
        db.add(admin_user)
        db.commit()
        db.refresh(admin_user)
        print(f"✓ Admin user '{admin_username}' ({admin_email}) created successfully.")
    except IntegrityError as error:
        print(f"Admin user with email '{admin_email}' already exists (detected via IntegrityError). Skipping creation.")
        db.rollback()
    except Exception as error:
        print(f"ERROR: Failed to create admin user: {error}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_admin_user()


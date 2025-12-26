"""Database configuration and session management."""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from app.core.config_loader import settings

engine = create_engine(str(settings.SQLALCHEMY_DATABASE_URI))
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models."""


def get_db():
    """Get a database session.
    
    Yields:
        Database session instance.
        
    Note:
        The session is automatically closed after use.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def import_all_models():
    """Import all SQLAlchemy models to ensure they are registered.
    
    This function must be called before creating database tables
    to ensure all models are properly registered with SQLAlchemy.
    """
    import app.users.models
    import app.trips.models
    import app.activities.models
    import app.quotes.models
    import app.stations.models
    import app.travel.models
    import app.trip_stations.models
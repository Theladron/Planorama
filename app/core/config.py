"""Configuration settings for the FastAPI application."""
from pydantic_core import MultiHostUrl
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Annotated, Any, Literal
from functools import cached_property
from pathlib import Path

from pydantic import (
    AnyUrl,
    BeforeValidator,
    computed_field,
    Field,
    PostgresDsn
)


def parse_cors(value: Any) -> list[str] | str:
    """Parse CORS origins from various input formats.
    
    Args:
        value: String with comma-separated origins, or a list of strings.
        
    Returns:
        List of origin strings or a single string, depending on input format.
        
    Raises:
        ValueError: If the input format is not recognized.
    """
    if isinstance(value, str) and not value.startswith("["):
        return [item.strip() for item in value.split(",")]
    elif isinstance(value, list | str):
        return value
    raise ValueError(value)

class Settings(BaseSettings):
    """Application settings loaded from environment variables.
    
    This class manages all configuration settings for the application,
    including API keys, database connections, security settings, and
    CORS configuration.
    """

    model_config = SettingsConfigDict(
        env_file=Path(".env") if Path(".env").exists() else None,
        env_file_encoding="utf-8",
        extra="ignore",
        env_ignore_empty=True,
    )
    APP_NAME: str = "Planorama"
    DEBUG: bool = False

    ORS_API_KEY: str
    AI_API_KEY: str

    # Auth0 Configuration
    AUTH0_DOMAIN: str = ""
    AUTH0_AUDIENCE: str = ""
    AUTH0_CLIENT_ID: str = ""  # SPA Client ID
    AUTH0_CLIENT_SECRET: str = ""  # SPA Client Secret
    
    # Auth0 Management API (for user creation/seeding)
    AUTH0_MANAGEMENT_CLIENT_ID: str = ""  # Management API M2M Client ID
    AUTH0_MANAGEMENT_CLIENT_SECRET: str = ""  # Management API M2M Client Secret
    AUTH0_CONNECTION_NAME: str = "Username-Password-Authentication"  # Auth0 database connection name
    
    # Auth0 Admin User (for seeding)
    ADMIN_EMAIL: str = ""  # Admin email (will be created/fetched in Auth0)
    ADMIN_USERNAME: str = ""  # Admin username
    ADMIN_PASSWORD: str = ""  # Admin password (for initial creation)

    DOMAIN: str
    ENVIRONMENT: Literal["local", "staging", "production"]

    @computed_field
    @property
    def server_host(self) -> str:
        """Compute the server host URL based on environment.
        
        Returns:
            HTTP URL for local environment, HTTPS URL for production/staging.
        """
        if self.ENVIRONMENT == "local":
            return f"http://{self.DOMAIN}"
        return f"https://{self.DOMAIN}"

    BACKEND_CORS_ORIGINS: Annotated[
        list[AnyUrl] | str, BeforeValidator(parse_cors)
    ] = Field(default_factory=list)

    POSTGRESQL_USERNAME: str
    POSTGRESQL_PASSWORD: str
    POSTGRESQL_SERVER: str
    POSTGRESQL_PORT: int
    POSTGRESQL_DATABASE: str

    @cached_property
    def SQLALCHEMY_DATABASE_URI(self):
        """Build the SQLAlchemy database URI from configuration.
        
        Returns:
            MultiHostUrl object representing the PostgreSQL connection string.
        """
        return MultiHostUrl.build(
            scheme="postgresql+psycopg2",
            username=self.POSTGRESQL_USERNAME,
            password=self.POSTGRESQL_PASSWORD,
            host=self.POSTGRESQL_SERVER,
            port=self.POSTGRESQL_PORT,
            path=self.POSTGRESQL_DATABASE,
        )
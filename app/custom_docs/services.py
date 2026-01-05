"""Custom OpenAPI documentation services."""

from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi


def setup_custom_openapi(app: FastAPI) -> None:
    """
    Configure and override FastAPI's OpenAPI schema generation.
    """

    def custom_openapi():
        # Use cached schema if already generated
        if app.openapi_schema:
            return app.openapi_schema

        schema = get_openapi(
            title="Planorama",
            version="0.8.0",
            description=(
                "Planorama is an all-in-one travel app that lets you plan your perfect trip. "
                "It gives you necessary data about travel routes, weather, and things to do "
                "while on vacation."
            ),
            routes=app.routes,
        )
        schema.setdefault("components", {}).setdefault("securitySchemes", {})[
            "BearerAuth"
        ] = {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
        }

        schema["security"] = [{"BearerAuth": []}]
        schema.get("paths", {}).pop("/api/auth/token", None)
        schema.get("paths", {}).pop("/api/auth/check-token", None)

        app.openapi_schema = schema
        return app.openapi_schema

    # Override FastAPI OpenAPI generator
    app.openapi = custom_openapi

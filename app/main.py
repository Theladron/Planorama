"""FastAPI application entry point."""
from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from starlette.middleware.cors import CORSMiddleware
from app.core.config_loader import settings
from app.core.database import import_all_models
from app.auth.api import auth_router
from app.users.api import user_router, admin_user_router
from app.trips.api import trip_router, admin_trip_router
from app.stations.api import station_router, admin_station_router
from app.travel.api import travel_router
from app.external_services.service_routes.api import frontend_router
from app.custom_docs.api import router as custom_docs_router

openapi_tags = [
    {"name": "Users", "description": "User operations"},
    {"name": "Trips", "description": "Trip operations"},
    {"name": "Admin", "description": "Admin-only operations"},
    {"name": "Health Checks", "description": "Application health checks"},
]

app = FastAPI(
    openapi_url=None,
    docs_url=None,
    redoc_url=None,
    openapi_tags=openapi_tags,
    debug=settings.DEBUG,
)

import_all_models()

if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin).strip("/") for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

app.include_router(auth_router, prefix="/api")
app.include_router(user_router, prefix="/api")
app.include_router(admin_user_router, prefix="/api")
app.include_router(trip_router, prefix="/api")
app.include_router(admin_trip_router, prefix="/api")
app.include_router(station_router, prefix="/api")
app.include_router(admin_station_router, prefix="/api")
app.include_router(travel_router, prefix="/api")
app.include_router(frontend_router, prefix="/api")
app.include_router(custom_docs_router)


@app.get("/")
async def root():
    """Redirect root path to API documentation.
    
    Returns:
        RedirectResponse to /api/docs endpoint.
    """
    return RedirectResponse(url="/api/docs")
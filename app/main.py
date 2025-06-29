from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from app.core.config_loader import settings
from app.core.database import import_all_models
from app.auth.api import auth_router
from app.users.api import user_router, admin_user_router
from app.trips.api import trip_router, admin_trip_router
from app.stations.api import station_router, admin_station_router
from app.travel.api import travel_router, admin_travel_router
from app.custom_docs.api import router as custom_docs_router  # import custom docs

openapi_tags = [
    {"name": "Users", "description": "User operations"},
    {"name": "Trips", "description": "Trip operations"},
    {"name": "Admin", "description": "Admin-only operations"},
    {"name": "Health Checks", "description": "Application health checks"},
]

app = FastAPI(
    openapi_url=None,  # Disable default openapi.json
    docs_url=None,     # Disable default /docs
    redoc_url=None,    # Disable default /redoc
    openapi_tags=openapi_tags,
    debug=settings.DEBUG,
)

# Import models
import_all_models()

# CORS
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin).strip("/") for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Include routers
app.include_router(auth_router, prefix="/api")
app.include_router(user_router, prefix="/api")
app.include_router(admin_user_router, prefix="/api")  # Admin routes
app.include_router(trip_router, prefix="/api")
app.include_router(admin_trip_router, prefix="/api")
app.include_router(station_router, prefix="/api")
app.include_router(admin_station_router, prefix="/api")
app.include_router(travel_router, prefix="/api")
app.include_router(admin_travel_router, prefix="/api")
app.include_router(custom_docs_router)

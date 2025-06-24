from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from app.core.config_loader import settings
from app.core.database import import_all_models
from app.auth.api import auth_router
from app.users.api import user_router

openapi_tags = [
    {
        "name": "Users",
        "description": "User operations",
    },
    {
        "name": "Health Checks",
        "description": "Application health checks",
    }
]
app = FastAPI(openapi_tags=openapi_tags,
              docs_url="/api/docs",
              debug=settings.DEBUG
              )

# importing all database models
import_all_models()

if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            str(origin).strip("/") for origin in settings.BACKEND_CORS_ORIGINS
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

app.include_router(auth_router, prefix='/api')
app.include_router(user_router, prefix='/api')


@app.get("/api/health", tags=['Health Checks'])
def read_root():
    return {"health": "true"}

# dynamic_fastapi_docs_demo.py
# This single file demonstrates dynamic FastAPI Swagger UI documentation
# based on user authentication and admin status.

# --- Core Imports ---
from fastapi import FastAPI, Request, Depends, HTTPException, status, APIRouter, Header
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from starlette.middleware.cors import CORSMiddleware

from pydantic import BaseModel, EmailStr
from datetime import datetime, timedelta, timezone
from typing import Optional, List, Dict, Any
import jwt
from jwt import InvalidTokenError
import hashlib  # For password hashing in this demo
import uvicorn  # For running the app directly


# --- Mock Configuration (Simulating app.core.config_loader.settings) ---
class Settings:
    JWT_SECRET_KEY: str = "your-super-secret-jwt-key-please-change-this-in-production"  # IMPORTANT: Change this!
    BACKEND_CORS_ORIGINS: List[str] = ["http://localhost:8000", "http://127.0.0.1:8000"]
    DEBUG: bool = True


settings = Settings()


# --- Mock Database and Models (Simulating app.core.database and app.users.models) ---
# In a real application, this would interact with SQLAlchemy, but for a single-file demo,
# we'll use a simple in-memory list of user objects.

# Pydantic Schema (from user schemas.py)
class UserBase(BaseModel):
    username: str
    email: EmailStr


class UserCreate(UserBase):
    password: str


class UserSchema(BaseModel):
    id: int
    username: str
    email: EmailStr
    is_admin: bool = False  # Added for clarity in schema

    class Config:
        from_attributes = True


# SQLAlchemy Model (from user models.py - simplified for in-memory)
class User:  # This mocks your SQLAlchemy User model
    def __init__(self, id: int, username: str, email: str, password_hash: str,
                 is_admin: bool = False, is_active: bool = True):
        self.id = id
        self.username = username
        self.email = email
        self.password_hash = password_hash
        self.is_active = is_active
        self.is_admin = is_admin
        self.created_at = datetime.now(timezone.utc)
        self.updated_at = datetime.now(timezone.utc)
        # trips relationship is omitted for this simplified demo


# In-memory "database"
# Mimics initial users. In a real app, these would come from your DB.
users_db: List[User] = []
user_id_counter = 0


# Helper to create initial mock users
def create_mock_user_in_db(username: str, email: str, password: str, is_admin: bool = False):
    global user_id_counter
    user_id_counter += 1
    hashed_password = hashlib.sha256(password.encode()).hexdigest()  # Simple hashing for demo
    user = User(id=user_id_counter, username=username, email=email, password_hash=hashed_password,
                is_admin=is_admin)
    users_db.append(user)
    return user


# Create some mock users for the demo
create_mock_user_in_db("user1", "user1@example.com", "password", is_admin=False)
create_mock_user_in_db("admin1", "admin1@example.com", "adminpass", is_admin=True)


# Mock DB Session (replaces app.core.database.get_db)
class MockDBSession:
    def query(self, model):
        # This is a very simplified query mimic for the demo
        class QueryMimic:
            def __init__(self, data):
                self.data = data

            def filter_by(self, **kwargs):
                filtered_data = [item for item in self.data if
                                 all(getattr(item, k) == v for k, v in kwargs.items())]
                return QueryMimic(filtered_data)

            def first(self):
                return self.data[0] if self.data else None

            def all(self):
                return self.data

        return QueryMimic(users_db)

    def add(self, obj):
        users_db.append(obj)

    def commit(self):
        pass  # No actual commit for in-memory

    def refresh(self, obj):
        pass  # No actual refresh for in-memory

    def delete(self, obj_to_delete):  # Renamed parameter to avoid conflict
        global users_db
        users_db = [u for u in users_db if u.id != obj_to_delete.id]


def get_db_mock():  # Renamed to avoid conflict if a real get_db exists
    # This acts as the dependency injector for the mock DB session
    yield MockDBSession()


# Mock import_all_models (replaces app.core.database.import_all_models)
def import_all_models_mock():
    pass  # No-op for this in-memory demo


# --- Security Helpers (Simulating app.core.security) ---
def hash_password_mock(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


def verify_password_mock(plain_password: str, hashed_password: str) -> bool:
    return hash_password_mock(plain_password) == hashed_password


# --- Auth Services (Simulating app.auth.services) ---
class Token(BaseModel):  # From app.auth.models
    access_token: str
    token_type: str


# Define OAuth2PasswordBearer.
# The tokenUrl must point to your actual token endpoint.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/token")


def authenticate_user_mock(email: str, password: str, db: MockDBSession) -> Optional[User]:
    """Authenticates a user by email and password using mock DB."""
    user = db.query(User).filter_by(email=email).first()
    if not user:
        return None
    if not verify_password_mock(password, user.password_hash):
        return None
    return user


def create_access_token_mock(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Creates a JWT access token."""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta if expires_delta else timedelta(minutes=15))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm="HS256")
    return encoded_jwt


async def get_current_user_mock(token: str = Depends(oauth2_scheme),
                                db: MockDBSession = Depends(get_db_mock)) -> User:
    """Retrieves the current user from a validated token."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=["HS256"])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except InvalidTokenError:
        raise credentials_exception
    # Now use the global get_user_by_email_mock defined below
    user = get_user_by_email_mock(db, email=email)
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user_mock(current_user: User = Depends(get_current_user_mock)) -> User:
    """Ensures the current user is active."""
    return current_user


async def get_current_admin_user_mock(current_user: User = Depends(get_current_user_mock)) -> User:
    """Ensures the current user has admin privileges."""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )
    return current_user


def get_token_from_request_mock(request: Request) -> Optional[str]:
    """
    Attempts to get the token from the Authorization header or a specific cookie.
    Used for non-dependency contexts like custom openapi.json generation.
    """
    auth = request.headers.get("Authorization")
    if auth and auth.startswith("Bearer "):
        return auth[7:]
    cookie_token = request.cookies.get("swagger_authentication")
    if cookie_token:
        return cookie_token
    return None


def is_token_admin_mock(token: str) -> bool:
    """Checks if a given token payload indicates admin status."""
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=["HS256"])
        return payload.get("is_admin", False)
    except InvalidTokenError:
        return False


async def get_admin_status_from_request_token_mock(request: Request) -> bool:
    """
    Dependency that attempts to determine if the user is an admin based on the token in the request.
    Does not raise exceptions for invalid tokens, returning False instead,
    suitable for dynamic OpenAPI schema generation.
    """
    token = get_token_from_request_mock(request)
    if token:
        return is_token_admin_mock(token)
    return False


# --- User Services (Simulating app.users.services) ---
# Explicitly defining these global functions to fix NameError
def get_users_mock(db: MockDBSession) -> List[User]:
    return db.query(User).all()


def get_user_mock(db: MockDBSession, user_id: int) -> Optional[User]:
    return db.query(User).filter_by(id=user_id).first()


def get_user_by_email_mock(db: MockDBSession, email: str) -> Optional[User]:
    return db.query(User).filter_by(email=email).first()


def create_user_mock(db: MockDBSession, user_create: UserCreate) -> User:
    global user_id_counter
    user_id_counter += 1
    db_user = User(
        id=user_id_counter,
        email=str(user_create.email),
        username=user_create.username,
        password_hash=hash_password_mock(user_create.password),  # Use mock hashing
        is_admin=False  # New users are not admin by default
    )
    db.add(db_user)
    db.commit()
    return db_user


def delete_user_mock(db: MockDBSession, user_id: int):
    db_user = get_user_mock(db, user_id)  # Use mock get_user
    if db_user:
        db.delete(db_user)
        db.commit()


# --- Auth API Router (Simulating app.auth.api) ---
auth_router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


@auth_router.post("/token", response_model=Token)
async def login_for_access_token_endpoint(
        form_data: OAuth2PasswordRequestForm = Depends(),
        db: MockDBSession = Depends(get_db_mock),
):
    user = authenticate_user_mock(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token_mock(
        data={
            "sub": user.email,
            "is_admin": user.is_admin,  # Include admin info in token payload
        },
        expires_delta=access_token_expires,
    )
    return Token(access_token=access_token, token_type="bearer")


# --- User API Routers (Simulating app.users.api) ---
user_router = APIRouter(
    prefix='/users',
    tags=['Users']
)
admin_user_router = APIRouter(
    prefix='/admin',
    tags=['Admin']
)


@user_router.get('/', response_model=list[UserSchema])
def user_list_endpoint(db: MockDBSession = Depends(get_db_mock)):
    db_users = get_users_mock(db)
    return db_users


@user_router.get('/me', response_model=UserSchema)
def get_current_user_info_endpoint(current_user: User = Depends(get_current_active_user_mock)):
    return current_user


@user_router.get('/{user_id}', response_model=UserSchema)
def user_detail_endpoint(user_id: int, db: MockDBSession = Depends(get_db_mock)):
    db_user = get_user_mock(db, user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


@user_router.delete('/{user_id}')
def user_delete_endpoint_func(user_id: int, db: MockDBSession = Depends(get_db_mock),
                              current_user: User = Depends(get_current_active_user_mock)):
    db_user = get_user_mock(db, user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")

    if not current_user.is_admin and current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this user")

    delete_user_mock(db, db_user)  # Pass the User object for mock delete
    return {"message": "User deleted"}


@user_router.post("/", response_model=UserSchema)
def user_post_endpoint_func(user: UserCreate, db: MockDBSession = Depends(get_db_mock)):
    existing_user = get_user_by_email_mock(db, user.email)
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return create_user_mock(db, user)


@admin_user_router.delete("/{user_id}")
def admin_delete_user_by_id_endpoint(user_id: int,
                                     db: MockDBSession = Depends(get_db_mock),
                                     current_user: User = Depends(
                                         get_current_admin_user_mock)):  # Ensures only admin can call this
    db_user = get_user_mock(db, user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    delete_user_mock(db, db_user)  # Pass the User object for mock delete
    return {"message": "User deleted by admin"}


# --- Mock Trips API Router (Simulating app.trips.api) ---
trip_router = APIRouter(
    prefix='/trips',
    tags=['Trips']
)


@trip_router.get('/')
def get_trips_endpoint(current_user: User = Depends(get_current_active_user_mock)):
    return [{"id": 1, "destination": "Paris", "user_id": current_user.id}]


# --- Custom Docs API Router (Simulating app.custom_docs.api) ---
custom_docs_router = APIRouter()


@custom_docs_router.get("/api/docs", include_in_schema=False)
async def custom_swagger_ui_html(request: Request) -> HTMLResponse:
    """
    Serves the custom Swagger UI HTML, injecting JavaScript to handle
    token persistence and dynamic OpenAPI schema loading.
    """
    swagger_ui_html = get_swagger_ui_html(
        openapi_url="/openapi.json",  # This will now hit the custom endpoint in this file
        title="API Docs",
        swagger_favicon_url="https://fastapi.tiangolo.com/img/favicon.png",
        swagger_ui_parameters={
            "persistAuthorization": True,
        }
    )

    html_content = swagger_ui_html.body
    if isinstance(html_content, bytes):
        html_content = html_content.decode("utf-8")

    # The most reliable way to inject scripts that interact with window.ui
    # is AFTER the main Swagger-UI-Bundle script has loaded.
    # We find that script tag and insert our custom JS immediately after it.
    swagger_bundle_script = '<script src="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui-bundle.js"></script>'
    swagger_standalone_script = '<script src="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui-standalone-preset.js"></script>'

    custom_js = """
    <script>
    // This variable will hold the Swagger UI instance
    let uiInstance;

    // This function will be called when the window has fully loaded, and it will then
    // wait for the Swagger UI components to be ready before injecting our logic.
    window.onload = function() {
        console.log("Custom JS: window.onload triggered. Starting Swagger UI readiness check...");

        // Ensure that SwaggerUIBundle (the constructor) and SwaggerUIStandalonePreset are available
        if (typeof SwaggerUIBundle !== 'undefined' && typeof SwaggerUIStandalonePreset !== 'undefined') {
            console.log("Custom JS: SwaggerUIBundle and SwaggerUIStandalonePreset found. Initializing UI...");

            // Explicitly create the Swagger UI instance. This is the key.
            uiInstance = SwaggerUIBundle({
                url: "/openapi.json", // Our custom OpenAPI endpoint
                dom_id: '#swagger-ui', // The default div ID where Swagger UI renders
                presets: [
                    SwaggerUIBundle.presets.apis,
                    SwaggerUIStandalonePreset
                ],
                layout: "BaseLayout",
                deepLinking: true,
                persistAuthorization: true,
                onComplete: function() { // IMPORTANT: This is the callback when Swagger UI is truly ready
                    console.log("Custom JS: Swagger UI onComplete callback triggered. UI is fully ready.");

                    // Make the instance globally accessible for easier debugging if needed.
                    window.ui = uiInstance;

                    // --- Inject Authorization Hooks ---
                    const originalAuthorize = uiInstance.authActions.authorize;
                    uiInstance.authActions.authorize = function(auth) {
                        console.log("Custom JS: Swagger UI Authorize called. Auth object:", auth);
                        const tokenName = Object.keys(auth)[0];
                        const tokenValue = auth[tokenName].value;

                        if (tokenValue) {
                            console.log("Custom JS: Saving token to cookie and localStorage:", tokenValue);
                            document.cookie = `swagger_authentication=${tokenValue}; path=/; SameSite=Lax; Max-Age=${30*60}`;
                            localStorage.setItem("swagger_authentication", tokenValue);
                        }
                        const result = originalAuthorize.call(this, auth);

                        console.log("Custom JS: Authorization complete. Forcing OpenAPI spec reload...");
                        uiInstance.specActions.updateUrl("/openapi.json");
                        uiInstance.specActions.download();
                        return result;
                    };

                    const originalLogout = uiInstance.authActions.logout;
                    uiInstance.authActions.logout = function() {
                        console.log("Custom JS: Swagger UI Logout called.");
                        document.cookie = 'swagger_authentication=; Max-Age=0; path=/; SameSite=Lax';
                        localStorage.removeItem("swagger_authentication");
                        const result = originalLogout.call(this);

                        console.log("Custom JS: Logout complete. Forcing OpenAPI spec reload...");
                        uiInstance.specActions.updateUrl("/openapi.json");
                        uiInstance.specActions.download();
                        return result;
                    };

                    // --- Initial Load Logic (Re-authorize if token found) ---
                    const savedToken = localStorage.getItem("swagger_authentication");
                    if (savedToken) {
                        console.log("Custom JS: Found saved token in localStorage. Re-authorizing Swagger UI...");
                        uiInstance.authActions.authorize({
                            "Bearer": {
                                "name": "Bearer",
                                "schema": {
                                    "type": "apiKey",
                                    "in": "header",
                                    "name": "Authorization"
                                },
                                "value": savedToken
                            }
                        });
                        // The authorize function itself will trigger the download(), so no need to call it here.
                    }

                    // --- Intercepting OpenAPI.json Request ---
                    uiInstance.get = uiInstance.get.wrap(function(orig) {
                        return function(url, request) {
                            if (url === "/openapi.json") {
                                console.log("Custom JS: Intercepting openapi.json request.");
                                const token = localStorage.getItem("swagger_authentication");
                                if (token) {
                                    if (!request.headers) {
                                        request.headers = {};
                                    }
                                    request.headers["Authorization"] = `Bearer ${token}`;
                                    console.log("Custom JS: Authorization header added to openapi.json request:", request.headers["Authorization"]);
                                } else {
                                    console.log("Custom JS: No token found in localStorage for openapi.json request.");
                                }
                            }
                            return orig.apply(this, arguments);
                        };
                    });

                    // Trigger an initial download of the OpenAPI spec after all hooks are in place.
                    console.log("Custom JS: Ensuring initial OpenAPI spec download with hooks active.");
                    uiInstance.specActions.download();
                }
            }); // End of onComplete function
        } else {
            // SwaggerUIBundle or SwaggerUIStandalonePreset not yet available, poll again
            console.log("Custom JS: SwaggerUIBundle or SwaggerUIStandalonePreset not yet available. Retrying...");
            setTimeout(checkAndInitializeSwaggerUI, 100);
        }
    };
    checkAndInitializeSwaggerUI(); // Start the primary check for Swagger UI readiness at window.onload
    </script>
    """

    # We ensure that both swagger-ui-bundle.js and swagger-ui-standalone-preset.js are present.
    # The get_swagger_ui_html function usually provides bundle.js, but standalone-preset might be missing.
    # We need both for SwaggerUIStandalonePreset.
    if swagger_bundle_script not in html_content:
        # Fallback if bundle script is not found (unlikely)
        html_content = html_content.replace("</head>",
                                            swagger_bundle_script + swagger_standalone_script + "</head>")
    elif swagger_standalone_script not in html_content:
        # Insert standalone-preset after bundle script if it's missing
        html_content = html_content.replace(swagger_bundle_script,
                                            swagger_bundle_script + swagger_standalone_script)

    # Now, inject our custom JS immediately after the standalone-preset script (or bundle if standalone wasn't added).
    if swagger_standalone_script in html_content:
        html_content = html_content.replace(swagger_standalone_script,
                                            swagger_standalone_script + custom_js)
    elif swagger_bundle_script in html_content:
        html_content = html_content.replace(swagger_bundle_script,
                                            swagger_bundle_script + custom_js)
    else:
        # Last resort fallback if no standard script tags are found
        html_content = html_content.replace("</body>", custom_js + "</body>")

    return HTMLResponse(content=html_content, status_code=200)


# --- Main FastAPI Application Setup ---
app = FastAPI(
    openapi_url=None,  # Disable default openapi.json
    docs_url=None,  # Disable default /docs
    redoc_url=None,  # Disable default /redoc
    openapi_tags=[
        {"name": "Users", "description": "User operations"},
        {"name": "Trips", "description": "Trip operations"},
        {"name": "Admin", "description": "Admin-only operations"},
        {"name": "Authentication", "description": "User authentication and token management"},
    ],
    debug=settings.DEBUG,
)

# Configure CORS middleware
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin).strip("/") for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Include all API routers
app.include_router(auth_router, prefix="/api")
app.include_router(user_router, prefix="/api")
app.include_router(admin_user_router, prefix="/api")
app.include_router(trip_router, prefix="/api")
app.include_router(custom_docs_router)


@app.get("/openapi.json", include_in_schema=False)
async def custom_openapi_json(request: Request) -> JSONResponse:
    """
    Custom endpoint to serve the OpenAPI schema dynamically.
    It filters routes based on the user's admin status.
    """
    full_openapi_schema = app.openapi()

    # Check if the token in the request indicates admin status
    is_admin_user = await get_admin_status_from_request_token_mock(request)

    if not is_admin_user:
        filtered_paths = {}
        for path, path_item in full_openapi_schema.get("paths", {}).items():
            # Filter out paths under the /api/admin prefix
            if not path.startswith("/api/admin"):
                filtered_paths[path] = path_item
        full_openapi_schema["paths"] = filtered_paths

        # Also remove the 'Admin' tag if no admin routes are shown
        filtered_tags = []
        for tag in full_openapi_schema.get("tags", []):
            if tag.get("name") != "Admin":
                filtered_tags.append(tag)
        full_openapi_schema["tags"] = filtered_tags

    return JSONResponse(full_openapi_schema)


# --- Uvicorn Run Block ---
if __name__ == "__main__":
    # To run this file: python dynamic_fastapi_docs_demo.py
    # Then navigate to http://127.0.0.1:8000/api/docs in your browser.
    uvicorn.run(app, host="0.0.0.0", port=8000)

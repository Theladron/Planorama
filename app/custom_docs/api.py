from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.openapi.docs import get_swagger_ui_html
from app.auth.services import get_token_from_request, verify_auth0_token_and_get_user
from app.core.database import get_db
from app.custom_docs.services import get_base_openapi_schema

router = APIRouter()


@router.get("/openapi.json", include_in_schema=False)
async def custom_openapi(request: Request):
    openapi_schema = get_base_openapi_schema(request.app)
    # Ensure OpenAPI version field is set (required by Swagger UI)
    if "openapi" not in openapi_schema:
        openapi_schema["openapi"] = "3.1.0"
    openapi_schema["info"]["title"] = "Planorama"
    openapi_schema["info"]["description"] = (
        "Planorama is an all-in-one travel app that lets you plan your perfect trip. "
        "It gives you necessary data "
        "about travel routes, weather, and things to do while on vacation."
    )
    openapi_schema["info"]["version"] = "0.8.0"
    # Auth0 Bearer token authentication
    openapi_schema.setdefault("components", {}).setdefault("securitySchemes", {})[
        "BearerAuth"
    ] = {
        "type": "http",
        "scheme": "bearer",
        "bearerFormat": "JWT"
    }
    openapi_schema.setdefault("security", [{"BearerAuth": []}])
    openapi_schema["paths"].pop("/api/auth/token", None)
    openapi_schema["paths"].pop("/api/auth/check-token", None)
    
    # Check if user is admin via Auth0 token (directly from token, not database)
    token = get_token_from_request(request)
    is_admin = False
    if token:
        try:
            from app.auth.services import has_admin_permission
            is_admin = has_admin_permission(token)
        except Exception:
            pass
    
    if not is_admin:
        filtered_paths = {
            path: path_item
            for path, path_item in openapi_schema["paths"].items()
            if not any("Admin" in method.get("tags", []) for method in path_item.values())
        }
        openapi_schema["paths"] = filtered_paths
        openapi_schema["tags"] = [
            tag for tag in openapi_schema.get("tags", [])
            if tag["name"] != "Admin"
        ]

    return JSONResponse(openapi_schema)


@router.get("/api/docs", include_in_schema=False)
async def custom_swagger_ui_html(request: Request):
    swagger_ui_html = get_swagger_ui_html(
        openapi_url="/openapi.json",
        title="API Docs",
        swagger_favicon_url="https://fastapi.tiangolo.com/img/favicon.png",
        swagger_ui_parameters={"persistAuthorization": True}
    )

    interceptor_script = """
<script>
(function interceptFetch() {
    const originalFetch = window.fetch;
    window.fetch = async function(input, init) {
        init = init || {};
        const url = typeof input === 'string' ? input : input.url;
        if (url.includes("/api/")) {
            if (!init.credentials) {
                init.credentials = 'include';
            }
        }
        const response = await originalFetch(input, init);
        return response;
    };
})();

(async function validateTokenOnLoad() {
    function getCookie(name) {
        const value = `; ${document.cookie}`;
        const parts = value.split(`; ${name}=`);
        if (parts.length === 2) return parts.pop().split(';').shift();
    }
    function deleteCookie(name) {
        document.cookie = name + '=; path=/; expires=Thu, 01 Jan 1970 00:00:01 GMT; SameSite=Lax';
    }
    const token = getCookie('swagger_authentication');
    if (!token) {
        return;
    }
    try {
        // Token validation is handled by Auth0 - just check if token exists
        if (!token) throw new Error("No token");
    } catch (e) {
        deleteCookie('swagger_authentication');
        location.reload();
    }
})();

(function interceptLogoutButton() {
    let lastAttachedButton = null;

    function getLogoutButton() {
        return Array.from(document.querySelectorAll('button'))
            .find(btn => btn.textContent.trim() === 'Logout');
    }

    function isSameButton(btn1, btn2) {
        return btn1 === btn2;
    }

    function attachLogoutHandler(button) {
        if (!button || isSameButton(button, lastAttachedButton)) return;

        button.addEventListener('click', () => {
            document.cookie = 'swagger_authentication=; path=/; expires=Thu, 01 Jan 1970 00:00:01 GMT; SameSite=Lax';
            location.reload();
        }, { once: true });

        lastAttachedButton = button;
    }

    function monitorLogoutButton() {
        setInterval(() => {
            const logoutButton = getLogoutButton();
            if (logoutButton) {
                attachLogoutHandler(logoutButton);
            }
        }, 500);
    }

    monitorLogoutButton();
})();

function hideAuthInputs() {
    const inputs = document.querySelectorAll('.auth-wrapper input');
    inputs.forEach(input => {
        input.style.display = 'none';
    });
}

setTimeout(hideAuthInputs, 1000);

// Also observe DOM changes to hide inputs if modal opens later
const observer = new MutationObserver(() => {
    hideAuthInputs();
});
observer.observe(document.body, { childList: true, subtree: true });

</script>
    """

    html = swagger_ui_html.body
    if isinstance(html, bytes):
        html = html.decode("utf-8")
    html = html.replace("</head>", interceptor_script + "</head>")

    return HTMLResponse(content=html, status_code=200)

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.openapi.docs import get_swagger_ui_html
from app.auth.services import get_token_from_request, is_token_admin
from app.custom_docs.services import get_base_openapi_schema

router = APIRouter()


@router.get("/openapi.json", include_in_schema=False)
async def custom_openapi(request: Request):
    openapi_schema = get_base_openapi_schema(request.app)
    openapi_schema["info"]["title"] = "Planorama"
    openapi_schema["info"]["description"] = (
        "Planorama is an all-in-one travel app that lets you plan your perfect trip. "
        "It gives you necessary data "
        "about travel routes, weather, and things to do while on vacation."
    )
    openapi_schema["info"]["version"] = "0.8.0"
    openapi_schema.setdefault("components", {}).setdefault("securitySchemes", {})[
        "OAuth2Password"
    ] = {
        "type": "oauth2",
        "flows": {
            "password": {
                "tokenUrl": "/api/auth/token",
                "scopes": {}
            }
        }
    }
    openapi_schema.setdefault("security", [{"OAuth2Password": []}])

    token = get_token_from_request(request)
    if token is None or not is_token_admin(token):
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
        if (url.includes("/api/auth/token") && response.ok) {
            try {
                const clone = response.clone();
                const data = await clone.json();
                if (data.access_token) {
                    const safeToken = encodeURIComponent(data.access_token);
                    document.cookie = `swagger_authentication=${safeToken}; path=/; SameSite=Lax`;
                    location.reload();  // <<< reload after login
                }
            } catch (e) {}
        }
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
        const res = await fetch('/api/auth/check-token', {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${decodeURIComponent(token)}`,
            },
            credentials: 'include'
        });
        if (!res.ok) throw new Error("Invalid token");
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
</script>
    """

    html = swagger_ui_html.body
    if isinstance(html, bytes):
        html = html.decode("utf-8")
    html = html.replace("</head>", interceptor_script + "</head>")

    return HTMLResponse(content=html, status_code=200)

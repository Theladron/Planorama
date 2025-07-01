from copy import deepcopy
from fastapi import FastAPI


def get_base_openapi_schema(app: FastAPI):
    if not hasattr(app, "base_openapi_schema"):
        app.base_openapi_schema = app.openapi()  # Generate once and cache base schema
    return deepcopy(app.base_openapi_schema)  # Return a copy for safe modification
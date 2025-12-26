from copy import deepcopy
from fastapi import FastAPI


def get_base_openapi_schema(app: FastAPI):
    if not hasattr(app, "base_openapi_schema"):
        app.base_openapi_schema = app.openapi()
    return deepcopy(app.base_openapi_schema)
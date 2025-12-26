"""Custom OpenAPI documentation services."""
from copy import deepcopy
from fastapi import FastAPI


def get_base_openapi_schema(app: FastAPI):
    """Get a deep copy of the base OpenAPI schema.
    
    Args:
        app: FastAPI application instance.
        
    Returns:
        Deep copy of the OpenAPI schema dictionary.
    """
    if not hasattr(app, "base_openapi_schema"):
        app.base_openapi_schema = app.openapi()
    return deepcopy(app.base_openapi_schema)
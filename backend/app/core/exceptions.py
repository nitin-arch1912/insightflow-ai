"""
Standardized error responses and global exception handlers.

All API errors return a consistent RFC 7807-inspired JSON shape:
{
  "error": {
    "code": "NOT_FOUND",
    "message": "Resource not found",
    "details": null,
    "request_id": "a1b2c3d4-..."
  }
}

This ensures the frontend and API consumers always handle a single,
predictable error schema regardless of whether the error came from:
  - Route not found (404)
  - Method not allowed (405)
  - Pydantic schema validation failure (422)
  - Business logic exception (HTTPException)
  - Unhandled server crash (500)
"""

from typing import Any

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)

REQUEST_ID_HEADER = "X-Request-ID"


# ------------------------------------------------------------------ #
# Schemas                                                              #
# ------------------------------------------------------------------ #

class ErrorDetail(BaseModel):
    code: str
    message: str
    details: Any = None
    request_id: str | None = None


class ErrorResponse(BaseModel):
    error: ErrorDetail


# ------------------------------------------------------------------ #
# Helper to get request_id safely                                      #
# ------------------------------------------------------------------ #

def _get_request_id(request: Request) -> str | None:
    return getattr(request.state, "request_id", None) or request.headers.get(REQUEST_ID_HEADER)


def _build_headers(request_id: str | None) -> dict[str, str] | None:
    return {REQUEST_ID_HEADER: request_id} if request_id else None


# ------------------------------------------------------------------ #
# Status code to error code mapper                                     #
# ------------------------------------------------------------------ #

STATUS_CODE_MAP = {
    400: "BAD_REQUEST",
    401: "UNAUTHORIZED",
    403: "FORBIDDEN",
    404: "NOT_FOUND",
    405: "METHOD_NOT_ALLOWED",
    409: "CONFLICT",
    422: "VALIDATION_ERROR",
    500: "INTERNAL_SERVER_ERROR",
    502: "BAD_GATEWAY",
    503: "SERVICE_UNAVAILABLE",
}


# ------------------------------------------------------------------ #
# Exception Handlers                                                   #
# ------------------------------------------------------------------ #

async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    """Handle FastAPI and Starlette HTTPExceptions (e.g., 404, 405, explicit HTTPException)."""
    request_id = _get_request_id(request)
    code = STATUS_CODE_MAP.get(exc.status_code, "HTTP_ERROR")

    # exc.detail can be a string or a structured object
    message = exc.detail if isinstance(exc.detail, str) else "An HTTP error occurred"
    details = exc.detail if not isinstance(exc.detail, str) else None

    payload = {
        "error": {
            "code": code,
            "message": message,
            "details": details,
            "request_id": request_id,
        }
    }
    return JSONResponse(
        status_code=exc.status_code,
        content=payload,
        headers=_build_headers(request_id),
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """Handle Pydantic validation errors (422 Unprocessable Content)."""
    request_id = _get_request_id(request)

    # Format Pydantic errors into readable field-level error details
    formatted_errors = []
    for err in exc.errors():
        loc = " -> ".join(str(item) for item in err.get("loc", []))
        formatted_errors.append({
            "field": loc,
            "message": err.get("msg", "Invalid value"),
            "type": err.get("type", "value_error"),
        })

    payload = {
        "error": {
            "code": "VALIDATION_ERROR",
            "message": "Request validation failed",
            "details": formatted_errors,
            "request_id": request_id,
        }
    }
    return JSONResponse(
        status_code=422,
        content=payload,
        headers=_build_headers(request_id),
    )


async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle any uncaught exception (500 Internal Server Error)."""
    request_id = _get_request_id(request)

    logger.error(
        "Unhandled exception processing %s %s [%s]: %s",
        request.method,
        request.url.path,
        request_id,
        str(exc),
        exc_info=True,
    )

    # Never leak internal stack traces or database errors in production
    message = "An unexpected internal server error occurred"
    details = str(exc) if settings.debug and settings.app_env == "development" else None

    payload = {
        "error": {
            "code": "INTERNAL_SERVER_ERROR",
            "message": message,
            "details": details,
            "request_id": request_id,
        }
    }
    return JSONResponse(
        status_code=500,
        content=payload,
        headers=_build_headers(request_id),
    )


# ------------------------------------------------------------------ #
# Registration function                                                #
# ------------------------------------------------------------------ #

def register_exception_handlers(app: FastAPI) -> None:
    """Register all global exception handlers on the FastAPI application."""
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(Exception, unhandled_exception_handler)

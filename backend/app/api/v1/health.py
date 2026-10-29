"""
Health check endpoint — /api/v1/health

This is the first real endpoint in InsightFlow AI.

Responsibilities:
  - Confirm the API process is alive.
  - Report the application version and environment.
  - (Future) Report database and dependency health.

We use a Pydantic response model so the shape is:
  - Validated on the way out (we can never accidentally return a dict with
    the wrong keys).
  - Documented automatically in the OpenAPI schema (/docs).
"""

from fastapi import APIRouter
from pydantic import BaseModel

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(tags=["Health"])


# ------------------------------------------------------------------ #
# Response model                                                       #
# ------------------------------------------------------------------ #

class HealthResponse(BaseModel):
    """Shape of the health endpoint response."""

    status: str
    version: str
    environment: str

    model_config = {"json_schema_extra": {"example": {"status": "ok", "version": "0.1.0", "environment": "development"}}}


# ------------------------------------------------------------------ #
# Route                                                                #
# ------------------------------------------------------------------ #

@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Health check",
    description=(
        "Returns the current status of the API. "
        "Use this endpoint for load-balancer and monitoring probes."
    ),
)
async def health_check() -> HealthResponse:
    """
    Return application health status.

    This endpoint is intentionally simple — it only checks that the
    Python process is running and configuration loaded correctly.
    Phase 3 will extend this to include a database ping.
    """
    logger.info("Health check requested")
    return HealthResponse(
        status="ok",
        version=settings.app_version,
        environment=settings.app_env,
    )

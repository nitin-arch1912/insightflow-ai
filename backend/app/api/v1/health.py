"""
Health check endpoint — /api/v1/health

Responsibilities:
  - Confirm the API process is alive.
  - Report the application version and environment.
  - Check database connectivity (ping).
"""

from fastapi import APIRouter
from pydantic import BaseModel

from app.core.config import settings
from app.core.logging import get_logger
from app.db.session import check_database_health

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
    database: str

    model_config = {
        "json_schema_extra": {
            "example": {
                "status": "ok",
                "version": "0.1.0",
                "environment": "development",
                "database": "connected",
            }
        }
    }


# ------------------------------------------------------------------ #
# Route                                                                #
# ------------------------------------------------------------------ #

@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Health check",
    description=(
        "Returns the current operational status of the API and its dependencies "
        "(including database connectivity)."
    ),
)
async def health_check() -> HealthResponse:
    """
    Return application and database health status.
    """
    db_connected = await check_database_health()
    status_str = "ok" if db_connected else "degraded"
    db_status = "connected" if db_connected else "disconnected"

    return HealthResponse(
        status=status_str,
        version=settings.app_version,
        environment=settings.app_env,
        database=db_status,
    )

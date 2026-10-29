"""
System info endpoint — /api/v1/info

Responsibilities:
  - Return application metadata: name, version, environment.
  - Return operational metrics: server time (UTC), process uptime in seconds.
  - Useful for client health dashboards, release tracking, and debugging.
"""

from datetime import datetime, timezone

from fastapi import APIRouter
from pydantic import BaseModel

from app.core.config import settings

router = APIRouter(tags=["System"])

# Record the module load / process start timestamp in UTC
SERVER_START_TIME = datetime.now(timezone.utc)


class SystemInfoResponse(BaseModel):
    name: str
    version: str
    environment: str
    status: str
    server_time: str
    uptime_seconds: float

    model_config = {
        "json_schema_extra": {
            "example": {
                "name": "InsightFlow AI",
                "version": "0.1.0",
                "environment": "development",
                "status": "operational",
                "server_time": "2026-10-29T14:50:00Z",
                "uptime_seconds": 124.5,
            }
        }
    }


@router.get(
    "/info",
    response_model=SystemInfoResponse,
    summary="System information",
    description="Returns application release version, environment, server timestamp, and uptime.",
)
async def get_system_info() -> SystemInfoResponse:
    now = datetime.now(timezone.utc)
    uptime = (now - SERVER_START_TIME).total_seconds()

    return SystemInfoResponse(
        name=settings.app_name,
        version=settings.app_version,
        environment=settings.app_env,
        status="operational",
        server_time=now.isoformat(),
        uptime_seconds=round(uptime, 2),
    )

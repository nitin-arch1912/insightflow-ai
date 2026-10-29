"""
InsightFlow AI — FastAPI application entry point.

This module:
  1. Creates the FastAPI app instance.
  2. Registers all API routers.
  3. Configures global middleware (CORS, etc.) as needed.
  4. Exposes a root redirect and a top-level health shortcut.

Run locally:
    uvicorn app.main:app --reload --port 8000

The app is importable without starting a server, which lets pytest
create a TestClient without side effects.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse

from app.api.v1 import health as health_router
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)

# ------------------------------------------------------------------ #
# App factory                                                          #
# ------------------------------------------------------------------ #

def create_app() -> FastAPI:
    """
    Construct and configure the FastAPI application.

    Separating construction into a factory function makes it easy to
    create fresh app instances in tests without global state leaking
    between test runs.
    """
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description=(
            "InsightFlow AI — Business intelligence platform. "
            "Interactive API docs are available at /docs."
        ),
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
    )

    # ---------------------------------------------------------------- #
    # CORS                                                               #
    # Broad during development; tighten before production.              #
    # ---------------------------------------------------------------- #
    origins = ["http://localhost:5173", "http://localhost:3000"]  # Vite + CRA
    if settings.app_env != "production":
        origins.append("*")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ---------------------------------------------------------------- #
    # Routers                                                            #
    # ---------------------------------------------------------------- #
    API_PREFIX = "/api/v1"

    app.include_router(health_router.router, prefix=API_PREFIX)

    # ---------------------------------------------------------------- #
    # Root redirect                                                      #
    # ---------------------------------------------------------------- #
    @app.get("/", include_in_schema=False)
    async def root() -> RedirectResponse:
        """Redirect root to the interactive API docs."""
        return RedirectResponse(url="/docs")

    # ---------------------------------------------------------------- #
    # Top-level /health shortcut (for simple monitoring probes)         #
    # ---------------------------------------------------------------- #
    @app.get("/health", include_in_schema=False)
    async def root_health() -> dict:
        """
        Bare /health for load-balancer probes.
        Returns the same shape as /api/v1/health.
        """
        return {
            "status": "ok",
            "version": settings.app_version,
            "environment": settings.app_env,
        }

    logger.info(
        "InsightFlow AI started",
        extra={"version": settings.app_version, "env": settings.app_env},
    )

    return app


# Module-level app instance — uvicorn imports this
app: FastAPI = create_app()

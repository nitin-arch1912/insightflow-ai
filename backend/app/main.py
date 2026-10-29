"""
InsightFlow AI — FastAPI application entry point.

This module:
  1. Creates the FastAPI app instance.
  2. Registers global middlewares (CORS, RequestID).
  3. Configures global exception handlers (RFC 7807 problem details).
  4. Registers all API routers.
  5. Exposes a root redirect and a top-level health shortcut.

Run locally:
    uvicorn app.main:app --reload --port 8000

The app is importable without starting a server, which lets pytest
create a TestClient without side effects.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse

from app.api.v1 import analytics as analytics_router
from app.api.v1 import health as health_router
from app.api.v1 import info as info_router
from app.core.config import settings
from app.core.exceptions import register_exception_handlers
from app.core.logging import get_logger
from app.core.middleware import RequestIDMiddleware

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
    # Middlewares                                                        #
    # Middlewares execute in reverse order of addition:                #
    # 1. RequestIDMiddleware attaches request_id to state & headers     #
    # 2. CORSMiddleware handles CORS preflights and headers            #
    # ---------------------------------------------------------------- #
    origins = ["http://localhost:5173", "http://localhost:3000"]
    if settings.app_env != "production":
        origins.append("*")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_middleware(RequestIDMiddleware)

    # ---------------------------------------------------------------- #
    # Exception Handlers (RFC 7807 uniform errors)                     #
    # ---------------------------------------------------------------- #
    register_exception_handlers(app)

    # ---------------------------------------------------------------- #
    # Routers                                                            #
    # ---------------------------------------------------------------- #
    API_PREFIX = "/api/v1"

    app.include_router(health_router.router, prefix=API_PREFIX)
    app.include_router(info_router.router, prefix=API_PREFIX)
    app.include_router(analytics_router.router, prefix=API_PREFIX)

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
        from app.db.session import check_database_health
        db_connected = await check_database_health()
        return {
            "status": "ok" if db_connected else "degraded",
            "version": settings.app_version,
            "environment": settings.app_env,
            "database": "connected" if db_connected else "disconnected",
        }

    logger.info(
        "InsightFlow AI initialized",
        extra={"version": settings.app_version, "env": settings.app_env},
    )

    return app


# Module-level app instance — uvicorn imports this
app: FastAPI = create_app()

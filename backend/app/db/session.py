"""
Database engine, session factory, and FastAPI dependency injection.

Uses SQLAlchemy 2.0 async engine and sessionmaker:
  - Supports PostgreSQL via asyncpg (`postgresql+asyncpg://...`)
  - Supports SQLite via aiosqlite (`sqlite+aiosqlite:///...`) for zero-dependency local dev
  - Provides `get_db` FastAPI dependency for request-scoped database sessions
  - Provides `check_database_health` for system probe verification
"""

from collections.abc import AsyncGenerator
from sqlalchemy import text
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)

# Configure engine arguments based on database dialect
engine_kwargs: dict = {
    "echo": False,
    "future": True,
}

# For SQLite, disable same-thread checking and handle connection pool correctly
if settings.database_url.startswith("sqlite"):
    engine_kwargs["connect_args"] = {"check_same_thread": False}
else:
    # PostgreSQL connection pool settings
    engine_kwargs["pool_pre_ping"] = True
    engine_kwargs["pool_size"] = 10
    engine_kwargs["max_overflow"] = 20

engine: AsyncEngine = create_async_engine(settings.database_url, **engine_kwargs)

# Request-scoped async session factory
async_session_factory = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI dependency yielding a clean, transaction-safe async database session.

    Usage:
        @router.get("/items")
        async def list_items(db: AsyncSession = Depends(get_db)):
            ...
    """
    async with async_session_factory() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def check_database_health() -> bool:
    """
    Perform a lightweight database connectivity check (SELECT 1).

    Returns True if the database is reachable and responsive, False otherwise.
    """
    try:
        async with engine.connect() as conn:
            result = await conn.execute(text("SELECT 1"))
            return result.scalar() == 1
    except Exception as exc:
        logger.warning("Database health check failed: %s", str(exc))
        return False

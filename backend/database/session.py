"""
database/session.py

Async SQLAlchemy engine and session factory.

Design decisions
----------------
- AsyncEngine is created once and shared for the process lifetime.
- AsyncSessionLocal is a session factory (not a session itself).
- ``get_db_session`` is a FastAPI dependency that yields one session per
  request and ensures it is always closed, even on exception.
- The engine is disposed in the lifespan shutdown hook (core/lifespan.py).
"""

from __future__ import annotations

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from core.config import settings

# ─────────────────────────────────────────────────────────────────────────────
# Engine
# ─────────────────────────────────────────────────────────────────────────────

engine: AsyncEngine = create_async_engine(
    settings.database_url,
    pool_size=settings.database_pool_size,
    max_overflow=settings.database_max_overflow,
    echo=settings.debug,  # log SQL statements in debug mode
    pool_pre_ping=True,  # drop stale connections transparently
    future=True,
)

# ─────────────────────────────────────────────────────────────────────────────
# Session factory
# ─────────────────────────────────────────────────────────────────────────────

AsyncSessionLocal: async_sessionmaker[AsyncSession] = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,  # prevents lazy-loading after commit
)


# ─────────────────────────────────────────────────────────────────────────────
# FastAPI dependency
# ─────────────────────────────────────────────────────────────────────────────


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Yield a scoped AsyncSession for one HTTP request.

    The session is always closed in the ``finally`` block — even if the
    handler raises an exception or the client disconnects mid-stream.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

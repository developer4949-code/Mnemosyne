"""
database/session.py

Async SQLAlchemy engine and session factory.

This module manages the connection pool to PostgreSQL.
It exposes `get_db_session()` which can be used as a FastAPI dependency,
ensuring that database sessions are properly closed after each request.
"""

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from core.config import settings

# Create the async engine
# The pool size and overflow limit concurrent connections.
engine: AsyncEngine = create_async_engine(
    settings.database_url,
    pool_size=settings.database_pool_size,
    max_overflow=settings.database_max_overflow,
    pool_pre_ping=True,  # Verify connections before using them
    echo=settings.debug, # Log SQL queries in debug mode
)

# Create the session factory
# expire_on_commit=False is required for async SQLAlchemy
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI dependency that provides a database session.
    Yields the session to the route handler, and closes it when done.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

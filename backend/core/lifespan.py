"""
core/lifespan.py

Application lifecycle management.

This module replaces the deprecated @app.on_event("startup") and 
@app.on_event("shutdown") hooks. All setup (database connection pools,
Redis connections, logging configuration) and teardown logic lives here.
"""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from loguru import logger

from core.config import settings
from core.logger import setup_logging
# from database.session import engine (will be imported later when used)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Manage the full application lifecycle.

    Code before `yield` runs at startup.
    Code after `yield` runs at shutdown.
    """
    # ── STARTUP ──────────────────────────────────────────────────────────────
    setup_logging()
    
    logger.info(
        "Starting {app} v{version}  env={env}  debug={debug}",
        app=settings.app_name,
        version=settings.app_version,
        env=settings.environment.value,
        debug=settings.debug,
    )

    # Future startup tasks (Milestone 2+):
    # logger.info("Initializing database connection pool...")
    # (The async engine connects automatically, but we might verify it here)

    logger.info("Startup complete — ready to accept requests")

    yield  # ◄── application is live here ─────────────────────────────────────

    # ── SHUTDOWN ─────────────────────────────────────────────────────────────
    logger.info("Shutting down {app} …", app=settings.app_name)

    # Future teardown tasks (Milestone 2+):
    # logger.info("Disposing database connection pool...")
    # from database.session import engine
    # await engine.dispose()

    logger.info("Shutdown complete.")

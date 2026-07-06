"""
core/logger.py

Structured, production-grade logging via Loguru.

Design goals
────────────
* Single call to `setup_logging()` at startup configures everything.
* Development  →  colourised human-readable text to stdout.
* Production   →  JSON lines to stdout (compatible with Datadog, Loki,
                  Google Cloud Logging, etc.) + rotating file sink.
* Loguru's `enqueue=True` keeps log writes non-blocking so they never
  slow down async request handlers.
* stdlib `logging` is intercepted, so third-party libraries (SQLAlchemy,
  httpx, uvicorn, etc.) also route through Loguru automatically.
"""

import logging
import sys
from typing import Any

from loguru import logger

from core.config import settings


# ─────────────────────────────────────────────────────────────────────────────
# stdlib → Loguru bridge
# ─────────────────────────────────────────────────────────────────────────────


class _InterceptHandler(logging.Handler):
    """
    Redirect every stdlib `logging` record into Loguru.

    Without this, libraries that call `logging.getLogger(__name__).info(…)`
    would print to stderr in a completely different format.
    """

    def emit(self, record: logging.LogRecord) -> None:
        try:
            level: str | int = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # Walk up the call stack to find the real originator of the log call.
        frame, depth = logging.currentframe(), 0
        while frame and (depth == 0 or frame.f_code.co_filename == logging.__file__):
            frame = frame.f_back  # type: ignore[assignment]
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(
            level, record.getMessage()
        )


# ─────────────────────────────────────────────────────────────────────────────
# JSON sink  (staging / production)
# ─────────────────────────────────────────────────────────────────────────────


def _json_sink(message: Any) -> None:
    """
    Write one JSON line per log record to stdout.

    Each line is self-contained and parseable by any log aggregator.
    Fields: timestamp, level, logger name, function, line, message,
    environment, version, and any extra context from `logger.bind(…)`.
    """
    import json
    import traceback

    record = message.record
    payload: dict[str, Any] = {
        "timestamp": record["time"].isoformat(),
        "level": record["level"].name,
        "logger": record["name"],
        "function": record["function"],
        "line": record["line"],
        "message": record["message"],
        "environment": settings.environment.value,
        "version": settings.app_version,
        **record["extra"],  # fields added via logger.bind(request_id=…)
    }

    if record["exception"]:
        payload["exception"] = "".join(
            traceback.format_exception(*record["exception"])
        )

    print(json.dumps(payload), flush=True)  # noqa: T201


# ─────────────────────────────────────────────────────────────────────────────
# Public API
# ─────────────────────────────────────────────────────────────────────────────


def setup_logging() -> None:
    """
    Configure all log sinks.

    Must be called exactly once, inside the FastAPI lifespan context manager,
    before any other application code runs.
    """
    # Remove Loguru's default sink so we control everything.
    logger.remove()

    use_json: bool = settings.log_format.lower() == "json"

    if use_json:
        # ── Production / staging: structured JSON to stdout ──────────────────
        logger.add(
            _json_sink,
            level=settings.log_level,
            enqueue=True,
            backtrace=False,    # don't leak tracebacks in prod logs
            diagnose=False,
        )
    else:
        # ── Development: pretty colourised text to stdout ─────────────────────
        logger.add(
            sys.stdout,
            level=settings.log_level,
            colorize=True,
            format=(
                "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
                "<level>{level: <8}</level> | "
                "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan>"
                " — <level>{message}</level>"
            ),
            enqueue=True,
            backtrace=settings.debug,
            diagnose=settings.debug,
        )

    # ── Rotating file sink (all environments) ────────────────────────────────
    logger.add(
        settings.log_file_path,
        level=settings.log_level,
        rotation="50 MB",       # new file at 50 MB
        retention="30 days",    # purge files older than 30 days
        compression="gz",       # gzip rotated files to save disk space
        enqueue=True,
        backtrace=False,
        diagnose=False,
        serialize=True,         # always JSON in files for grep-ability
    )

    # ── Intercept stdlib logging ──────────────────────────────────────────────
    logging.basicConfig(handlers=[_InterceptHandler()], level=0, force=True)

    # Silence overly verbose libraries in production.
    if not settings.debug:
        for noisy in ("uvicorn.access", "httpx", "httpcore"):
            logging.getLogger(noisy).setLevel(logging.WARNING)

    logger.info(
        "Logging configured  env={env}  level={level}  format={fmt}",
        env=settings.environment.value,
        level=settings.log_level,
        fmt=settings.log_format,
    )

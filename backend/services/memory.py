"""
services/memory.py

Business service for memory ingestion use cases.
"""

from __future__ import annotations

from memory_engine.pipeline.ingestion import MemoryIngestionPipeline
from schemas.memory import MemoryIngestRequest, MemoryIngestResult


class MemoryService:
    """Application-facing facade over the memory engine."""

    def __init__(self, pipeline: MemoryIngestionPipeline | None = None) -> None:
        self._pipeline = pipeline or MemoryIngestionPipeline()

    async def ingest_conversation(
        self,
        request: MemoryIngestRequest,
    ) -> MemoryIngestResult:
        return self._pipeline.process(request)


def get_memory_service() -> MemoryService:
    """Factory used by FastAPI dependencies."""
    return MemoryService()

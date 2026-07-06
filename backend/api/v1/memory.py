"""
api/v1/memory.py

Memory ingestion and retrieval endpoints.
"""

from typing import Annotated

from fastapi import APIRouter, Depends, status

from core.config import settings
from schemas.memory import MemoryIngestRequest, MemoryIngestResult
from schemas.response import SuccessResponse, success
from services.memory import MemoryService, get_memory_service

router = APIRouter()
MemoryServiceDep = Annotated[MemoryService, Depends(get_memory_service)]


@router.post(
    "/ingest",
    summary="Process a conversation into structured memory",
    response_model=SuccessResponse[MemoryIngestResult],
    status_code=status.HTTP_202_ACCEPTED,
)
async def ingest_conversation(
    request: MemoryIngestRequest,
    memory_service: MemoryServiceDep,
) -> SuccessResponse[MemoryIngestResult]:
    """Transform conversation messages into chunks, memories, graph edges, and DNA."""
    result = await memory_service.ingest_conversation(request)
    return success(
        message="Conversation processed into structured memory",
        data=result,
        version=settings.app_version,
    )

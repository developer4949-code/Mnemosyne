import pytest

from schemas.memory import ConversationMessage, MemoryIngestRequest, MemoryKind
from services.memory import MemoryService


@pytest.mark.asyncio
async def test_memory_ingestion_extracts_ranked_project_knowledge() -> None:
    request = MemoryIngestRequest(
        project_id="mnemosyne",
        conversation_id="chat-1",
        messages=[
            ConversationMessage(
                role="user",
                external_id="m1",
                content=(
                    "The system must support persistent project memory. "
                    "We decided to use FastAPI with SQLAlchemy in backend/app/main.py."
                ),
            ),
            ConversationMessage(
                role="assistant",
                external_id="m2",
                content=(
                    "TODO: implement a memory ingestion pipeline. "
                    "The memory engine uses Qdrant for vector search."
                ),
            ),
        ],
    )

    result = await MemoryService().ingest_conversation(request)

    assert result.chunk_count == 1
    assert result.memory_count >= 4
    assert result.memories[0].importance >= result.memories[-1].importance
    assert {memory.kind for memory in result.memories} >= {
        MemoryKind.REQUIREMENT,
        MemoryKind.DECISION,
        MemoryKind.TODO,
        MemoryKind.FILE_REFERENCE,
        MemoryKind.DEPENDENCY,
    }
    assert "backend/app/main.py" in result.project_dna_patch.file_references
    assert "fastapi" in result.project_dna_patch.dependencies
    assert len(result.memories[0].embedding) == 64


@pytest.mark.asyncio
async def test_memory_ingestion_is_deterministic_for_same_payload() -> None:
    request = MemoryIngestRequest(
        project_id="mnemosyne",
        conversation_id="chat-2",
        messages=[
            ConversationMessage(
                role="user",
                external_id="m1",
                content="Decision: the provider layer should use adapters.",
            ),
        ],
    )

    service = MemoryService()
    first = await service.ingest_conversation(request)
    second = await service.ingest_conversation(request)

    assert [memory.id for memory in first.memories] == [
        memory.id for memory in second.memories
    ]
    assert first.memories[0].embedding == second.memories[0].embedding

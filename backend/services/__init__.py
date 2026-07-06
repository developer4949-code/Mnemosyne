"""
services/__init__.py

Business logic layer.

Services sit between the API layer and the data/AI layers.
They orchestrate repositories and memory engine components
to fulfill business use cases.

Rules:
  * Services never import from `api/` — no FastAPI-specific types here.
  * Services call repositories for data and memory_engine for AI work.
  * Each service has a single responsibility (document ingestion,
    conversation management, memory retrieval, etc.).

Future services (added in Milestone 3+):
  document_service.py
  ingestion_service.py
  conversation_service.py
  memory_service.py
  search_service.py
  project_service.py
"""

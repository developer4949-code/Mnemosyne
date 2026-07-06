"""
repositories/__init__.py

The data access layer.

Repositories are the only place that issues database queries.
They abstract all SQLAlchemy operations so that:
  * Services never touch the ORM directly
  * Database logic is centralised and testable in isolation
  * Swapping the underlying storage is a repository-level change only

Pattern used: Repository Pattern (not Active Record).

Future repositories (added in Milestone 2+):
  user_repository.py
  project_repository.py
  document_repository.py
  chunk_repository.py
  conversation_repository.py
  memory_repository.py
"""

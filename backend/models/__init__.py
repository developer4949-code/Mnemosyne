"""
models/__init__.py

SQLAlchemy ORM model definitions.

Each file in this package maps to one or more database tables.
Models define the shape of persisted data — they are never used
directly in API responses (that's the schemas package's job).

Future models (added in Milestone 2+):
  user.py          — User accounts and authentication
  project.py       — Project / workspace grouping
  document.py      — Uploaded or linked source documents
  chunk.py         — Processed document chunks with embeddings
  conversation.py  — Chat conversation sessions
  message.py       — Individual messages within conversations
  memory.py        — Extracted memory fragments
"""

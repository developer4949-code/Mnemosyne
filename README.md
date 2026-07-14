# 🧠 Mnemosyne — AI Memory Platform

> **Persistent memory layer for Large Language Models.**
>
> Mnemosyne remembers your projects so you never have to rebuild context again.

[![CI](https://github.com/your-org/mnemosyne/actions/workflows/ci.yml/badge.svg)](https://github.com/your-org/mnemosyne/actions)
[![Python 3.12](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.116-green.svg)](https://fastapi.tiangolo.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 📖 Overview

Current AI assistants lose all project context the moment you start a new conversation.  
**Mnemosyne solves this** by continuously transforming conversations into structured knowledge.

The system:
- Captures conversations from popular AI platforms (ChatGPT, Gemini, Claude, Perplexity).
- Extracts facts, decisions, bugs, TODOs, dependencies, and relationships.
- Stores them as dense vector embeddings in Qdrant.
- On new conversations, retrieves and injects the most relevant context automatically.

---

## 🏗️ Architecture

```
Browser Extension (Chrome)
        │  captures messages
        ▼
FastAPI Backend (REST API)
        │
        ├── Memory Engine
        │       ├── Chunking
        │       ├── Knowledge Extraction (rule-based → LLM-enhanced)
        │       ├── Importance Scoring
        │       ├── Embedding Generation
        │       ├── Vector Storage (Qdrant)
        │       ├── Knowledge Graph
        │       ├── Project DNA
        │       ├── Context Builder
        │       └── Prompt Optimizer
        │
        ├── Provider Router (Groq / Gemini / OpenRouter / Ollama / HuggingFace)
        │
        ├── PostgreSQL (structured data)
        ├── Redis (caching)
        └── Qdrant (vector database)
```

---

## 🚀 Quick Start

### Prerequisites

- Docker & Docker Compose
- Python 3.12+ (for local dev)

### 1. Clone the repository

```bash
git clone https://github.com/your-org/mnemosyne.git
cd mnemosyne
```

### 2. Configure environment

```bash
cd backend
cp .env.example .env
# Edit .env and set at minimum:
#   SECRET_KEY=<a long random string>
#   GROQ_API_KEY=<your Groq key>   (or GEMINI_API_KEY / leave blank for local)
```

### 3. Start all services

```bash
docker compose up -d
```

This starts:
| Service | URL |
|---------|-----|
| Mnemosyne API | http://localhost:8000 |
| Swagger Docs | http://localhost:8000/docs |
| PostgreSQL | localhost:5432 |
| Redis | localhost:6379 |
| Qdrant UI | http://localhost:6333/dashboard |

### 4. Run database migrations

```bash
docker compose exec api alembic -c alembic.ini upgrade head
```

### 5. Load the Chrome extension

1. Open Chrome → `chrome://extensions`
2. Enable **Developer mode** (top-right toggle)
3. Click **Load unpacked** → select `mnemosyne/extension/`
4. Click the 🧠 icon in your toolbar
5. Enter your API URL (`http://localhost:8000/api/v1`) and sign in

---

## 📡 API Reference

Full interactive docs available at **`/docs`** (development mode).

### Key endpoints

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/api/v1/auth/register` | Create an account |
| `POST` | `/api/v1/auth/login` | Obtain a JWT token |
| `GET`  | `/api/v1/auth/me` | Current user profile |
| `POST` | `/api/v1/projects` | Create a project |
| `GET`  | `/api/v1/projects` | List your projects |
| `POST` | `/api/v1/memory/ingest` | Process a conversation |
| `POST` | `/api/v1/retrieval` | Semantic context retrieval |
| `GET`  | `/api/v1/health/live` | Liveness check |
| `GET`  | `/api/v1/health/ready` | Readiness check |

---

## 🔧 Development

### Install dependencies

```bash
cd backend
python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Run locally (without Docker)

Ensure PostgreSQL, Redis, and Qdrant are running (or use `docker compose up postgres redis qdrant -d`), then:

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### Run tests

```bash
pytest                                 # all unit tests
pytest -m "not integration"            # skip integration tests
pytest --cov=. --cov-report=term       # with coverage
```

### Lint & format

```bash
ruff check .
ruff format .
```

---

## 🧪 Provider Configuration

Set API keys in `.env`:

```env
GROQ_API_KEY=gsk_...          # https://console.groq.com
GEMINI_API_KEY=AIza...        # https://ai.google.dev
# OpenRouter, Ollama, HuggingFace also supported
```

Configure providers via the API (`/api/v1/providers`) or use the `local` provider (no API key required — uses deterministic hashing embeddings for development).

---

## 📁 Project Structure

```
mnemosyne/
├── backend/
│   ├── api/              # FastAPI routers (v1/)
│   ├── core/             # Config, security, auth, logger, lifespan
│   ├── database/         # SQLAlchemy base, session, migrations
│   ├── memory_engine/    # Chunking, extraction, embeddings, retrieval, graph, DNA
│   ├── models/           # SQLAlchemy ORM models
│   ├── providers/        # AI provider adapters (Groq, Gemini, Ollama, etc.)
│   ├── repositories/     # Data access layer
│   ├── schemas/          # Pydantic request/response models
│   ├── services/         # Business logic layer
│   ├── tests/            # Unit and integration tests
│   ├── workers/          # Background task functions
│   ├── main.py           # FastAPI app entry point
│   ├── Dockerfile        # Multi-stage production image
│   ├── docker-compose.yml
│   └── requirements.txt
│
├── extension/            # Chrome Extension (Manifest V3)
│   ├── manifest.json
│   ├── background.js     # Service worker
│   ├── content.js        # Page observer & injector
│   ├── popup.html
│   ├── popup.js
│   └── styles.css
│
├── .github/
│   └── workflows/ci.yml  # GitHub Actions CI/CD
│
└── README.md
```

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/my-feature`)
3. Commit with clear messages
4. Ensure tests pass (`pytest`)
5. Open a Pull Request

---

## 📄 License

MIT — see [LICENSE](LICENSE).

---

*Mnemosyne is named after the Greek goddess of memory and the mother of the Muses.*

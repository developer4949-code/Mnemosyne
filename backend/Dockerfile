# ═══════════════════════════════════════════════════════════════════
#  Mnemosyne Backend — Dockerfile
#  Multi-stage build: keeps the production image lean by separating
#  the dependency installation step from the runtime image.
# ═══════════════════════════════════════════════════════════════════

# ────────────────────────────────────────────
# Stage 1 — dependency builder
# ────────────────────────────────────────────
FROM python:3.12-slim AS builder

WORKDIR /build

# Install build tools needed to compile some Python wheels.
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy only requirements first — Docker caches this layer until
# requirements.txt changes, keeping rebuilds fast.
COPY requirements.txt .

RUN pip install --upgrade pip \
    && pip install --no-cache-dir --prefix=/install -r requirements.txt


# ────────────────────────────────────────────
# Stage 2 — production runtime
# ────────────────────────────────────────────
FROM python:3.12-slim AS runtime

# Security: run as non-root user.
RUN useradd --create-home --shell /bin/bash mnemosyne

WORKDIR /backend

# Copy installed packages from builder.
COPY --from=builder /install /usr/local

# Copy application source.
COPY . .

# Create the log directory and make it writable by the app user.
RUN mkdir -p logs && chown -R mnemosyne:mnemosyne /backend

USER mnemosyne

# Expose the default port (can be overridden via env PORT).
EXPOSE 8000

# Health check — Docker / Compose will use this.
HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/api/v1/health/live')"

# Uvicorn is the ASGI server. --workers is set to 1 here because
# production scaling is handled at the container orchestration level
# (multiple replicas), not inside a single container.
CMD ["uvicorn", "app.main:app", \
     "--host", "0.0.0.0", \
     "--port", "8000", \
     "--workers", "1", \
     "--log-config", "/dev/null"]

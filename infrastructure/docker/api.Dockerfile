# syntax=docker/dockerfile:1.4
# ============================================================
# Stage 1: Builder — install deps with build tools
# ============================================================
FROM python:3.12-slim AS builder

WORKDIR /build

# Install OS-level build deps (only needed to compile wheels)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    libmagic1 \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies into a prefix dir so we can copy them clean
COPY requirements.txt .
RUN pip install --upgrade pip \
    && pip install --no-cache-dir --prefix=/install -r requirements.txt

# ============================================================
# Stage 2: Runtime — lean production image
# ============================================================
FROM python:3.12-slim AS runtime

# Install only runtime OS libraries
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    libmagic1 \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN groupadd --gid 1001 appgroup \
    && useradd --uid 1001 --gid appgroup --shell /bin/bash --create-home appuser

WORKDIR /app

# Copy installed packages from builder
COPY --from=builder /install /usr/local

# Copy application source
COPY --chown=appuser:appgroup . .

# Switch to non-root
USER appuser

EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')"

# Production: gunicorn managing uvicorn workers
# WEB_CONCURRENCY can be overridden at runtime
CMD ["sh", "-c", "gunicorn main:app -k uvicorn.workers.UvicornWorker --workers ${WEB_CONCURRENCY:-4} --bind 0.0.0.0:8000 --access-logfile - --error-logfile - --log-level info --timeout 120"]

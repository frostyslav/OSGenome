# syntax = docker/dockerfile:latest

# Build stage - Install dependencies and build application
FROM docker.io/python:3.13-slim AS builder

# Install uv for dependency management
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# Create non-root user for building
RUN useradd -m -u 1000 appuser

# Set working directory and change ownership
WORKDIR /app
RUN chown appuser:appuser /app

# Switch to non-root user for dependency installation
USER appuser

# Copy dependency files first for better layer caching
COPY --chown=appuser:appuser pyproject.toml uv.lock README.md ./

# Install dependencies in a virtual environment (production only)
RUN uv sync --frozen --no-cache --no-dev

# Copy application source code
COPY --chown=appuser:appuser SNPedia ./SNPedia

# Production stage - Minimal runtime image
FROM docker.io/python:3.13-slim AS production

LABEL org.opencontainers.image.title="OSGenome"
LABEL org.opencontainers.image.description="An Open Source Web Application for Genetic Data (SNPs) using Ancestry and Data Crawling Technologies."
LABEL org.opencontainers.image.url="https://github.com/frostyslav/OSGenome"
LABEL org.opencontainers.image.documentation="https://github.com/frostyslav/OSGenome/README.md"
LABEL org.opencontainers.image.source="https://github.com/frostyslav/OSGenome"
LABEL org.opencontainers.image.licenses="GNU General Public License v3.0"

# Install only runtime dependencies and curl for health checks
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        curl \
        ca-certificates && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# Install uv for runtime
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# Create non-root user
RUN useradd -m -u 1000 appuser

# Set working directory
WORKDIR /app

# Copy virtual environment and application from builder stage
COPY --from=builder --chown=appuser:appuser /app/.venv /app/.venv
COPY --from=builder --chown=appuser:appuser /app/SNPedia /app/SNPedia
COPY --from=builder --chown=appuser:appuser /app/pyproject.toml /app/pyproject.toml
COPY --from=builder --chown=appuser:appuser /app/README.md /app/README.md

# Create data directory for genetic data files
RUN mkdir -p /app/data && \
    chown -R appuser:appuser /app/data

# Switch to non-root user
USER appuser

# Set environment variables
ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONPATH="/app" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

EXPOSE 8080

# Enhanced health check with multiple endpoints and better error handling
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8080/api/health || \
        /app/.venv/bin/python -c "import urllib.request, sys; \
        try: \
            response = urllib.request.urlopen('http://localhost:8080/api/health', timeout=5); \
            data = response.read().decode('utf-8'); \
            import json; \
            health = json.loads(data); \
            sys.exit(0 if health.get('status') in ['healthy', 'degraded'] else 1) \
        except Exception as e: \
            print(f'Health check failed: {e}'); \
            sys.exit(1)"

# Use exec form for better signal handling - use virtual environment directly
ENTRYPOINT ["/app/.venv/bin/gunicorn", "--config", "SNPedia/gunicorn_config.py", "SNPedia.app:app"]

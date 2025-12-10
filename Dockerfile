# syntax = docker/dockerfile:latest
FROM docker.io/python:3.13-slim AS python
LABEL org.opencontainers.image.title="OSGenome"
LABEL org.opencontainers.image.description="An Open Source Web Application for Genetic Data (SNPs) using Ancestry and Data Crawling Technologies."
LABEL org.opencontainers.image.url="https://github.com/frostyslav/OSGenome"
LABEL org.opencontainers.image.documentation="https://github.com/frostyslav/OSGenome/README.md"
LABEL org.opencontainers.image.source="https://github.com/frostyslav/OSGenome"
LABEL org.opencontainers.image.licenses="GNU General Public License v3.0"

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

WORKDIR /app

# Copy pyproject.toml, uv.lock, README.md, and SNPedia
COPY --link pyproject.toml ./
COPY --link uv.lock ./
COPY --link README.md ./
COPY --link SNPedia ./SNPedia

# Install dependencies with uv
RUN uv sync --frozen --no-cache

# Create non-root user and set ownership
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

EXPOSE 8080

# Healthcheck to monitor container health
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD uv run python -c "import urllib.request; urllib.request.urlopen('http://localhost:8080/api/health').read()" || exit 1

ENTRYPOINT ["uv", "run", "gunicorn", "--config", "SNPedia/gunicorn_config.py", "SNPedia.app:app"]

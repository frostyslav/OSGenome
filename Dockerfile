# syntax = docker/dockerfile:latest
FROM docker.io/python:3-slim AS python
LABEL org.opencontainers.image.title="OSGenome"
LABEL org.opencontainers.image.description="An Open Source Web Application for Genetic Data (SNPs) using Ancestry and Data Crawling Technologies."
LABEL org.opencontainers.image.url="https://github.com/frostyslav/OSGenome"
LABEL org.opencontainers.image.documentation="https://github.com/frostyslav/OSGenome/README.md"
LABEL org.opencontainers.image.source="https://github.com/frostyslav/OSGenome"
LABEL org.opencontainers.image.licenses="GNU General Public License v3.0"

WORKDIR /app

COPY --link requirements.txt ./
RUN pip install -r requirements.txt

COPY --link SNPedia ./SNPedia

EXPOSE 8080

ENTRYPOINT ["gunicorn", "--config", "SNPedia/gunicorn_config.py", "SNPedia.app:app"]

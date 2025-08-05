# syntax = docker/dockerfile:latest

# Install dependencies only when needed
FROM docker.io/python:3-slim AS python
LABEL org.opencontainers.image.title="OSGenome"
LABEL org.opencontainers.image.description="An Open Source Web Application for Genetic Data (SNPs) using 23AndMe and Data Crawling Technologies."
LABEL org.opencontainers.image.url="https://github.com/mentatpsi/OSGenome"
LABEL org.opencontainers.image.documentation="https://github.com/mentatpsi/OSGenome/README.md"
LABEL org.opencontainers.image.source="https://github.com/mentatpsi/OSGenome"
LABEL org.opencontainers.image.licenses="GNU General Public License v3.0"

WORKDIR /app

COPY --link SNPedia requirements.txt ./

# RUN apt-get update \
#     && apt-get install -y \
#       tk \
#     && rm -rf /var/lib/apt/lists/*

RUN pip install -r requirements.txt

# ENV PORT 3000
# EXPOSE $PORT

# ENTRYPOINT ["docker-entrypoint.sh"]
# CMD ["node", "server.js"]

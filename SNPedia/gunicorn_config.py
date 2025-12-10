"""Gunicorn configuration for OSGenome application.

This module contains the configuration settings for running the OSGenome
Flask application with Gunicorn WSGI server in production environments.

Configuration includes worker processes, threading, binding, and security
headers for proper reverse proxy operation.

Environment Variables:
    GUNICORN_PROCESSES: Number of worker processes (default: 1)
    GUNICORN_THREADS: Number of threads per worker (default: 4)
    GUNICORN_BIND: Address and port to bind to (default: 0.0.0.0:8080)
"""

import os

workers = int(os.environ.get("GUNICORN_PROCESSES", "1"))
threads = int(os.environ.get("GUNICORN_THREADS", "4"))
# timeout = int(os.environ.get('GUNICORN_TIMEOUT', '120'))
bind = os.environ.get("GUNICORN_BIND", "0.0.0.0:8080")

forwarded_allow_ips = "*"
secure_scheme_headers = {"X-Forwarded-Proto": "https"}

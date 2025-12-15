"""Prometheus metrics configuration and collection.

This module provides Prometheus metrics collection for the SNPedia application,
including request metrics, response times, and application-specific counters.

Example:
    Basic usage:
        >>> from SNPedia.core.metrics import init_metrics, REQUEST_COUNT
        >>> init_metrics(app)
        >>> REQUEST_COUNT.labels(method='GET', endpoint='/').inc()

Attributes:
    REQUEST_COUNT (Counter): Total number of HTTP requests.
    REQUEST_DURATION (Histogram): HTTP request duration in seconds.
    REQUEST_SIZE (Histogram): HTTP request size in bytes.
    RESPONSE_SIZE (Histogram): HTTP response size in bytes.
    SNP_QUERIES (Counter): Total number of SNP queries processed.
    CACHE_HITS (Counter): Total number of cache hits.
    CACHE_MISSES (Counter): Total number of cache misses.
"""

import time
from typing import Optional

from flask import Flask, Request, Response, g, request
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST

from SNPedia.core.logger import logger

# HTTP Metrics
REQUEST_COUNT = Counter(
    'http_requests_total',
    'Total number of HTTP requests',
    ['method', 'endpoint', 'status']
)

REQUEST_DURATION = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration in seconds',
    ['method', 'endpoint']
)

REQUEST_SIZE = Histogram(
    'http_request_size_bytes',
    'HTTP request size in bytes',
    ['method', 'endpoint']
)

RESPONSE_SIZE = Histogram(
    'http_response_size_bytes',
    'HTTP response size in bytes',
    ['method', 'endpoint', 'status']
)

# Application-specific metrics
SNP_QUERIES = Counter(
    'snp_queries_total',
    'Total number of SNP queries processed',
    ['query_type']
)

CACHE_HITS = Counter(
    'cache_hits_total',
    'Total number of cache hits',
    ['cache_type']
)

CACHE_MISSES = Counter(
    'cache_misses_total',
    'Total number of cache misses',
    ['cache_type']
)

ERROR_COUNT = Counter(
    'application_errors_total',
    'Total number of application errors',
    ['error_type', 'endpoint']
)

# RSID count metrics
RSID_COUNTS = Gauge(
    'rsid_counts',
    'Number of RSIDs by category',
    ['category']
)


def get_endpoint_name(request: Request) -> str:
    """Get a normalized endpoint name for metrics.
    
    Args:
        request (Request): The Flask request object.
        
    Returns:
        str: Normalized endpoint name.
    """
    if request.endpoint:
        return request.endpoint
    return request.path


def before_request() -> None:
    """Record request start time for duration calculation."""
    g.start_time = time.time()


def after_request(response: Response) -> Response:
    """Record metrics after each request.
    
    Args:
        response (Response): The Flask response object.
        
    Returns:
        Response: The unmodified response object.
    """
    # Skip metrics endpoint to avoid self-monitoring
    if request.path == '/metrics':
        return response
        
    endpoint = get_endpoint_name(request)
    method = request.method
    status = str(response.status_code)
    
    # Record request count
    REQUEST_COUNT.labels(method=method, endpoint=endpoint, status=status).inc()
    
    # Record request duration
    if hasattr(g, 'start_time'):
        duration = time.time() - g.start_time
        REQUEST_DURATION.labels(method=method, endpoint=endpoint).observe(duration)
    
    # Record request size
    if request.content_length:
        REQUEST_SIZE.labels(method=method, endpoint=endpoint).observe(request.content_length)
    
    # Record response size
    if response.content_length:
        RESPONSE_SIZE.labels(method=method, endpoint=endpoint, status=status).observe(response.content_length)
    
    return response


def record_snp_query(query_type: str) -> None:
    """Record a SNP query metric.
    
    Args:
        query_type (str): Type of SNP query (e.g., 'search', 'lookup', 'batch').
    """
    SNP_QUERIES.labels(query_type=query_type).inc()
    logger.debug(f"Recorded SNP query: {query_type}")


def record_cache_hit(cache_type: str) -> None:
    """Record a cache hit metric.
    
    Args:
        cache_type (str): Type of cache (e.g., 'snp_data', 'api_response').
    """
    CACHE_HITS.labels(cache_type=cache_type).inc()
    logger.debug(f"Recorded cache hit: {cache_type}")


def record_cache_miss(cache_type: str) -> None:
    """Record a cache miss metric.
    
    Args:
        cache_type (str): Type of cache (e.g., 'snp_data', 'api_response').
    """
    CACHE_MISSES.labels(cache_type=cache_type).inc()
    logger.debug(f"Recorded cache miss: {cache_type}")


def record_error(error_type: str, endpoint: Optional[str] = None) -> None:
    """Record an application error metric.
    
    Args:
        error_type (str): Type of error (e.g., 'validation', 'api', 'database').
        endpoint (Optional[str]): Endpoint where error occurred.
    """
    if endpoint is None:
        endpoint = get_endpoint_name(request) if request else 'unknown'
    
    ERROR_COUNT.labels(error_type=error_type, endpoint=endpoint).inc()
    logger.debug(f"Recorded error: {error_type} at {endpoint}")


def update_rsid_counts(total: int, interesting: int, uncommon: int) -> None:
    """Update RSID count metrics.
    
    Args:
        total (int): Total number of RSIDs.
        interesting (int): Number of interesting RSIDs.
        uncommon (int): Number of uncommon RSIDs.
    """
    RSID_COUNTS.labels(category='total').set(total)
    RSID_COUNTS.labels(category='interesting').set(interesting)
    RSID_COUNTS.labels(category='uncommon').set(uncommon)
    logger.debug(f"Updated RSID counts: total={total}, interesting={interesting}, uncommon={uncommon}")


def metrics_endpoint() -> Response:
    """Prometheus metrics endpoint.
    
    Returns:
        Response: Prometheus metrics in text format.
    """
    return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)


def init_metrics(app: Flask) -> None:
    """Initialize Prometheus metrics for the Flask application.
    
    Args:
        app (Flask): The Flask application instance.
    """
    # Register request hooks
    app.before_request(before_request)
    app.after_request(after_request)
    
    # Register metrics endpoint
    app.add_url_rule('/metrics', 'metrics', metrics_endpoint, methods=['GET'])
    
    logger.info("Prometheus metrics initialized")
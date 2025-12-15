"""API routes for SNPedia application."""

from typing import Tuple

from flask import Blueprint, Response, abort, jsonify, request
from werkzeug.utils import secure_filename

from SNPedia.core.logger import logger
from SNPedia.core.metrics import record_snp_query, record_error
from SNPedia.services.cache_service import CacheService
from SNPedia.services.snp_service import SNPService
from SNPedia.services.statistics_service import StatisticsService


def _create_rsids_routes(api: Blueprint, snp_service: SNPService) -> None:
    """Create RSID-related routes."""

    @api.route("/rsids", methods=["GET"])
    def get_rsids() -> Tuple[Response, int]:
        """Get RSIDs data with pagination support."""
        try:
            # Record SNP query metric
            query_type = "paginated" if ("page" in request.args or "page_size" in request.args) else "all"
            record_snp_query(query_type)
            
            # Get pagination parameters
            page = request.args.get("page", 1, type=int)
            page_size = request.args.get("page_size", 100, type=int)

            # Limit page size
            max_page_size = 1000
            if page_size > max_page_size:
                page_size = max_page_size

            # Check if pagination is requested
            use_pagination = "page" in request.args or "page_size" in request.args

            if use_pagination:
                # Get paginated results
                paginated_response = snp_service.get_results_paginated(
                    page=page, page_size=page_size
                )
                return jsonify(paginated_response.to_dict()), 200
            else:
                # Get all results
                results = snp_service.get_all_results()
                if not results:
                    return (
                        jsonify({"results": [], "message": "No data available"}),
                        200,
                    )
                return jsonify({"results": results}), 200

        except Exception as e:
            logger.error(f"Error fetching RSIDs: {str(e)}")
            record_error("api_error", "get_rsids")
            abort(500, description="Error fetching data")


def _create_statistics_routes(api: Blueprint, stats_service: StatisticsService) -> None:
    """Create statistics-related routes."""

    @api.route("/statistics", methods=["GET"])
    def get_statistics() -> Tuple[Response, int]:
        """Get statistics about the genetic data."""
        try:
            record_snp_query("statistics")
            stats = stats_service.get_genetic_statistics()
            return jsonify(stats.to_dict()), 200
        except Exception as e:
            logger.error(f"Error calculating statistics: {str(e)}")
            record_error("statistics_error", "get_statistics")
            abort(500, description="Error calculating statistics")

    @api.route("/config", methods=["GET"])
    def get_config() -> Tuple[Response, int]:
        """Get non-sensitive configuration information."""
        try:
            config_info = stats_service.get_config_info()
            return jsonify(config_info.to_dict()), 200
        except Exception as e:
            logger.error(f"Error fetching config: {str(e)}")
            abort(500, description="Error fetching configuration")

    @api.route("/health", methods=["GET"])
    def health_check() -> Tuple[Response, int]:
        """Health check endpoint for monitoring."""
        try:
            health_status = stats_service.get_health_status()
            status_code = 200 if health_status.status != "unhealthy" else 500
            return jsonify(health_status.to_dict()), status_code
        except Exception as e:
            logger.error(f"Health check failed: {str(e)}")
            return jsonify({"status": "unhealthy", "error": str(e)}), 500


def _create_cache_routes(api: Blueprint, cache_service: CacheService) -> None:
    """Create cache-related routes."""

    @api.route("/cache/stats", methods=["GET"])
    def get_cache_stats() -> Tuple[Response, int]:
        """Get cache statistics."""
        try:
            record_snp_query("cache_stats")
            stats = cache_service.get_stats()
            return jsonify(stats), 200
        except Exception as e:
            logger.error(f"Error fetching cache stats: {str(e)}")
            record_error("cache_error", "get_cache_stats")
            abort(500, description="Error fetching cache statistics")

    @api.route("/cache/clear", methods=["POST"])
    def clear_cache() -> Tuple[Response, int]:
        """Clear all cache entries."""
        try:
            record_snp_query("cache_clear")
            success = cache_service.clear_all()
            if success:
                return jsonify({"message": "Cache cleared successfully"}), 200
            else:
                record_error("cache_error", "clear_cache")
                abort(500, description="Error clearing cache")
        except Exception as e:
            logger.error(f"Error clearing cache: {str(e)}")
            record_error("cache_error", "clear_cache")
            abort(500, description="Error clearing cache")

    @api.route("/cache/invalidate/<filename>", methods=["POST"])
    def invalidate_cache(filename: str) -> Tuple[Response, int]:
        """Invalidate cache for a specific file."""
        try:
            # Sanitize filename
            safe_filename = secure_filename(filename)
            if not safe_filename:
                abort(400, description="Invalid filename")

            success = cache_service.invalidate_file(safe_filename)
            if success:
                return (
                    jsonify({"message": f"Cache invalidated for {safe_filename}"}),
                    200,
                )
            else:
                abort(500, description="Error invalidating cache")
        except Exception as e:
            logger.error(f"Error invalidating cache: {str(e)}")
            abort(500, description="Error invalidating cache")


def create_api_blueprint() -> Blueprint:
    """Create and configure the API blueprint.

    This function creates a Flask blueprint with all API routes organized
    into logical groups for better maintainability and reduced complexity.

    Returns:
        Blueprint: Configured Flask blueprint with all API routes.

    Example:
        >>> from SNPedia.api.routes import create_api_blueprint
        >>> api_bp = create_api_blueprint()
        >>> app.register_blueprint(api_bp)
    """
    api = Blueprint("api", __name__, url_prefix="/api")

    # Initialize services
    snp_service = SNPService()
    cache_service = CacheService()
    stats_service = StatisticsService()

    # Register route groups
    _create_rsids_routes(api, snp_service)
    _create_statistics_routes(api, stats_service)
    _create_cache_routes(api, cache_service)

    return api

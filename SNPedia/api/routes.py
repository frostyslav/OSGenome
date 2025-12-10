"""API routes for SNPedia application."""

from flask import Blueprint, jsonify, request, abort
from werkzeug.utils import secure_filename

from SNPedia.services.snp_service import SNPService
from SNPedia.services.file_service import FileService
from SNPedia.services.cache_service import CacheService
from SNPedia.services.statistics_service import StatisticsService
from SNPedia.core.logger import logger


def create_api_blueprint() -> Blueprint:
    """Create and configure the API blueprint."""
    api = Blueprint('api', __name__, url_prefix='/api')
    
    # Initialize services
    snp_service = SNPService()
    cache_service = CacheService()
    stats_service = StatisticsService()
    
    @api.route("/rsids", methods=["GET"])
    def get_rsids():
        """Get RSIDs data with pagination support."""
        try:
            # Get pagination parameters
            page = request.args.get('page', 1, type=int)
            page_size = request.args.get('page_size', 100, type=int)
            
            # Limit page size
            max_page_size = 1000
            if page_size > max_page_size:
                page_size = max_page_size
            
            # Check if pagination is requested
            use_pagination = 'page' in request.args or 'page_size' in request.args
            
            if use_pagination:
                # Get paginated results
                paginated_response = snp_service.get_results_paginated(page=page, page_size=page_size)
                return jsonify(paginated_response.to_dict())
            else:
                # Get all results
                results = snp_service.get_all_results()
                if not results:
                    return jsonify({"results": [], "message": "No data available"}), 200
                return jsonify({"results": results})
                
        except Exception as e:
            logger.error(f"Error fetching RSIDs: {str(e)}")
            abort(500, description="Error fetching data")
    
    @api.route("/statistics", methods=["GET"])
    def get_statistics():
        """Get statistics about the genetic data."""
        try:
            stats = stats_service.get_genetic_statistics()
            return jsonify(stats.to_dict())
        except Exception as e:
            logger.error(f"Error calculating statistics: {str(e)}")
            abort(500, description="Error calculating statistics")
    
    @api.route("/config", methods=["GET"])
    def get_config():
        """Get non-sensitive configuration information."""
        try:
            config_info = stats_service.get_config_info()
            return jsonify(config_info.to_dict())
        except Exception as e:
            logger.error(f"Error fetching config: {str(e)}")
            abort(500, description="Error fetching configuration")
    
    @api.route("/health", methods=["GET"])
    def health_check():
        """Health check endpoint for monitoring."""
        try:
            health_status = stats_service.get_health_status()
            status_code = 200 if health_status.status != "unhealthy" else 500
            return jsonify(health_status.to_dict()), status_code
        except Exception as e:
            logger.error(f"Health check failed: {str(e)}")
            return jsonify({
                "status": "unhealthy",
                "error": str(e)
            }), 500
    
    @api.route("/cache/stats", methods=["GET"])
    def get_cache_stats():
        """Get cache statistics."""
        try:
            stats = cache_service.get_stats()
            return jsonify(stats)
        except Exception as e:
            logger.error(f"Error fetching cache stats: {str(e)}")
            abort(500, description="Error fetching cache statistics")
    
    @api.route("/cache/clear", methods=["POST"])
    def clear_cache():
        """Clear all cache entries."""
        try:
            success = cache_service.clear_all()
            if success:
                return jsonify({"message": "Cache cleared successfully"})
            else:
                abort(500, description="Error clearing cache")
        except Exception as e:
            logger.error(f"Error clearing cache: {str(e)}")
            abort(500, description="Error clearing cache")
    
    @api.route("/cache/invalidate/<filename>", methods=["POST"])
    def invalidate_cache(filename):
        """Invalidate cache for a specific file."""
        try:
            # Sanitize filename
            safe_filename = secure_filename(filename)
            if not safe_filename:
                abort(400, description="Invalid filename")
            
            success = cache_service.invalidate_file(safe_filename)
            if success:
                return jsonify({"message": f"Cache invalidated for {safe_filename}"})
            else:
                abort(500, description="Error invalidating cache")
        except Exception as e:
            logger.error(f"Error invalidating cache: {str(e)}")
            abort(500, description="Error invalidating cache")
    
    return api
"""Swagger-enabled API routes for SNPedia application.

This module provides OpenAPI/Swagger documentation for the SNPedia API endpoints
using Flask-RESTX. It wraps the existing API functionality with proper documentation
and validation.
"""

from flask import Blueprint, request
from flask_restx import Api, Resource, fields
from werkzeug.utils import secure_filename

from SNPedia.core.logger import logger
from SNPedia.core.metrics import record_error, record_snp_query
from SNPedia.services.cache_service import CacheService
from SNPedia.services.snp_service import SNPService
from SNPedia.services.statistics_service import StatisticsService


def create_swagger_blueprint() -> Blueprint:
    """Create and configure the Swagger-enabled API blueprint.

    Returns:
        Blueprint: Configured Flask blueprint with Swagger documentation.
    """
    blueprint = Blueprint('swagger_api', __name__, url_prefix='/api/v1')
    
    api = Api(
        blueprint,
        version='1.0',
        title='SNPedia API',
        description='API for accessing SNP (Single Nucleotide Polymorphism) genetic data',
        doc='/docs/'
    )

    # Initialize services
    snp_service = SNPService()
    cache_service = CacheService()
    stats_service = StatisticsService()

    # Define response models
    rsid_model = api.model('RSID', {
        'Name': fields.String(required=True, description='RS identifier (RSID)'),
        'Description': fields.String(description='SNPedia description of the SNP'),
        'Genotype': fields.String(description='Personal genotype for this SNP'),
        'Variations': fields.String(description='HTML-formatted variation information'),
        'StabilizedOrientation': fields.String(description='Stabilized orientation from SNPedia'),
        'IsInteresting': fields.String(description='Whether SNP is interesting (Yes/No)'),
        'IsUncommon': fields.String(description='Whether genotype is uncommon (Yes/No)')
    })

    pagination_model = api.model('Pagination', {
        'page': fields.Integer(required=True, description='Current page number'),
        'page_size': fields.Integer(required=True, description='Items per page'),
        'total': fields.Integer(required=True, description='Total number of items'),
        'total_pages': fields.Integer(required=True, description='Total number of pages'),
        'has_next': fields.Boolean(required=True, description='Whether there is a next page'),
        'has_prev': fields.Boolean(required=True, description='Whether there is a previous page')
    })

    paginated_rsids_model = api.model('PaginatedRSIDs', {
        'results': fields.List(fields.Nested(rsid_model), required=True, description='List of RSIDs'),
        'pagination': fields.Nested(pagination_model, required=True, description='Pagination information')
    })

    statistics_model = api.model('Statistics', {
        'total': fields.Integer(description='Total number of SNPs'),
        'interesting': fields.Integer(description='Number of interesting SNPs'),
        'uncommon': fields.Integer(description='Number of uncommon SNPs')
    })

    health_model = api.model('Health', {
        'status': fields.String(required=True, description='Health status', enum=['healthy', 'degraded', 'unhealthy']),
        'data_loaded': fields.Boolean(required=True, description='Whether data is loaded'),
        'data_count': fields.Integer(required=True, description='Number of data items loaded'),
        'config_valid': fields.Boolean(required=True, description='Whether configuration is valid'),
        'config_warnings': fields.List(fields.String, description='Configuration warnings'),
        'version': fields.String(required=True, description='Application version'),
        'cache': fields.Raw(description='Cache statistics')
    })

    config_model = api.model('Config', {
        'config': fields.Raw(description='Configuration settings'),
        'environment': fields.String(description='Environment name')
    })

    cache_stats_model = api.model('CacheStats', {
        'size': fields.Integer(description='Current cache size'),
        'max_size': fields.Integer(description='Maximum cache size'),
        'hits': fields.Integer(description='Cache hits'),
        'misses': fields.Integer(description='Cache misses'),
        'hit_rate': fields.String(description='Cache hit rate percentage'),
        'total_requests': fields.Integer(description='Total cache requests')
    })

    # RSIDs namespace
    rsids_ns = api.namespace('rsids', description='RSID operations')

    @rsids_ns.route('')
    class RSIDList(Resource):
        @rsids_ns.doc('get_rsids')
        @rsids_ns.param('page', 'Page number (optional)', type='integer')
        @rsids_ns.param('page_size', 'Items per page (optional, max 1000)', type='integer')
        @rsids_ns.marshal_with(paginated_rsids_model)
        def get(self):
            """Get RSIDs data with optional pagination support."""
            try:
                # Parse query parameters
                page = request.args.get('page', 1, type=int)
                page_size = request.args.get('page_size', 100, type=int)

                # Record SNP query metric
                query_type = (
                    "paginated"
                    if ("page" in request.args or "page_size" in request.args)
                    else "all"
                )
                record_snp_query(query_type)

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
                    return paginated_response.to_dict()
                else:
                    # Get all results
                    results = snp_service.get_all_results()
                    if not results:
                        return {"results": [], "message": "No data available"}
                    return {"results": results}

            except Exception as e:
                logger.error(f"Error fetching RSIDs: {str(e)}")
                record_error("api_error", "get_rsids")
                api.abort(500, "Error fetching data")

    # Statistics namespace
    stats_ns = api.namespace('statistics', description='Statistics operations')

    @stats_ns.route('')
    class Statistics(Resource):
        @stats_ns.doc('get_statistics')
        @stats_ns.marshal_with(statistics_model, skip_none=True)
        def get(self):
            """Get statistics about the genetic data."""
            try:
                record_snp_query("statistics")
                stats = stats_service.get_genetic_statistics()
                return stats.to_dict()
            except Exception as e:
                logger.error(f"Error calculating statistics: {str(e)}")
                record_error("statistics_error", "get_statistics")
                api.abort(500, "Error calculating statistics")

    @stats_ns.route('/config')
    class Config(Resource):
        @stats_ns.doc('get_config')
        @stats_ns.marshal_with(config_model)
        def get(self):
            """Get non-sensitive configuration information."""
            try:
                config_info = stats_service.get_config_info()
                return config_info.to_dict()
            except Exception as e:
                logger.error(f"Error fetching config: {str(e)}")
                api.abort(500, "Error fetching configuration")

    @stats_ns.route('/health')
    class Health(Resource):
        @stats_ns.doc('health_check')
        @stats_ns.marshal_with(health_model)
        def get(self):
            """Health check endpoint for monitoring."""
            try:
                health_status = stats_service.get_health_status()
                return health_status.to_dict()
            except Exception as e:
                logger.error(f"Health check failed: {str(e)}")
                api.abort(500, f"Health check failed: {str(e)}")

    # Cache namespace
    cache_ns = api.namespace('cache', description='Cache operations')

    @cache_ns.route('/stats')
    class CacheStats(Resource):
        @cache_ns.doc('get_cache_stats')
        @cache_ns.marshal_with(cache_stats_model)
        def get(self):
            """Get cache statistics."""
            try:
                record_snp_query("cache_stats")
                stats = cache_service.get_stats()
                return stats
            except Exception as e:
                logger.error(f"Error fetching cache stats: {str(e)}")
                record_error("cache_error", "get_cache_stats")
                api.abort(500, "Error fetching cache statistics")

    @cache_ns.route('/clear')
    class CacheClear(Resource):
        @cache_ns.doc('clear_cache')
        def post(self):
            """Clear all cache entries."""
            try:
                record_snp_query("cache_clear")
                success = cache_service.clear_all()
                if success:
                    return {"message": "Cache cleared successfully"}
                else:
                    record_error("cache_error", "clear_cache")
                    api.abort(500, "Error clearing cache")
            except Exception as e:
                logger.error(f"Error clearing cache: {str(e)}")
                record_error("cache_error", "clear_cache")
                api.abort(500, "Error clearing cache")

    @cache_ns.route('/invalidate/<string:filename>')
    class CacheInvalidate(Resource):
        @cache_ns.doc('invalidate_cache')
        @cache_ns.param('filename', 'Filename to invalidate from cache')
        def post(self, filename):
            """Invalidate cache for a specific file."""
            try:
                # Sanitize filename
                safe_filename = secure_filename(filename)
                if not safe_filename:
                    api.abort(400, "Invalid filename")

                success = cache_service.invalidate_file(safe_filename)
                if success:
                    return {"message": f"Cache invalidated for {safe_filename}"}
                else:
                    api.abort(500, "Error invalidating cache")
            except Exception as e:
                logger.error(f"Error invalidating cache: {str(e)}")
                api.abort(500, "Error invalidating cache")

    return blueprint
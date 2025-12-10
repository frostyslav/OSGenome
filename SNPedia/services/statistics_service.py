"""Service for statistics and health check operations."""

import os

from SNPedia.core.config import get_config
from SNPedia.core.logger import logger
from SNPedia.models.response_models import (
    ConfigResponse,
    HealthCheckResponse,
    StatisticsResponse,
)
from SNPedia.services.cache_service import CacheService
from SNPedia.services.snp_service import SNPService


class StatisticsService:
    """Service for statistics and system health operations."""

    def __init__(self):
        self.snp_service = SNPService()
        self.cache_service = CacheService()

    def get_health_status(self) -> HealthCheckResponse:
        """Get comprehensive health check status."""
        try:
            # Check data availability
            stats = self.snp_service.get_statistics()
            data_loaded = stats.total > 0
            data_count = stats.total

            # Check configuration
            config = get_config()
            validation = config.validate()

            # Get cache stats
            cache_stats = self.cache_service.get_stats()

            # Determine overall status
            status = "healthy"
            if not validation["valid"]:
                status = "degraded"
            elif not data_loaded:
                status = "degraded"

            return HealthCheckResponse(
                status=status,
                data_loaded=data_loaded,
                data_count=data_count,
                config_valid=validation["valid"],
                config_warnings=validation["warnings"],
                version=config.APP_VERSION,
                cache_stats=cache_stats,
            )

        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return HealthCheckResponse(
                status="unhealthy",
                data_loaded=False,
                data_count=0,
                config_valid=False,
                config_warnings=[f"Health check error: {str(e)}"],
                version="unknown",
                cache_stats={},
            )

    def get_config_info(self) -> ConfigResponse:
        """Get non-sensitive configuration information."""
        try:
            config = get_config()
            config_dict = config.to_dict()
            environment = os.environ.get("FLASK_ENV", "development")

            return ConfigResponse(config=config_dict, environment=environment)

        except Exception as e:
            logger.error(f"Error getting config info: {e}")
            return ConfigResponse(config={"error": str(e)}, environment="unknown")

    def get_genetic_statistics(self) -> StatisticsResponse:
        """Get statistics about genetic data."""
        return self.snp_service.get_statistics()

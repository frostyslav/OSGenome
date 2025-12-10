"""Service for cache management operations."""

from typing import Dict, Any
from SNPedia.utils.cache_manager import get_cache_stats, clear_all_cache, invalidate_cache
from SNPedia.core.logger import logger


class CacheService:
    """Service for managing cache operations."""
    
    @staticmethod
    def get_stats() -> Dict[str, Any]:
        """Get cache statistics."""
        try:
            return get_cache_stats()
        except Exception as e:
            logger.error(f"Error getting cache stats: {e}")
            return {
                "total_entries": 0,
                "total_size_mb": 0,
                "hit_rate": 0.0,
                "error": str(e)
            }
    
    @staticmethod
    def clear_all() -> bool:
        """Clear all cache entries."""
        try:
            clear_all_cache()
            logger.info("All cache cleared successfully")
            return True
        except Exception as e:
            logger.error(f"Error clearing cache: {e}")
            return False
    
    @staticmethod
    def invalidate_file(filename: str) -> bool:
        """Invalidate cache for a specific file."""
        try:
            invalidate_cache(filename)
            logger.info(f"Cache invalidated for {filename}")
            return True
        except Exception as e:
            logger.error(f"Error invalidating cache for {filename}: {e}")
            return False
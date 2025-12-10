"""Cache manager for efficient data loading and caching."""

import json
import os
import time
from functools import lru_cache
from threading import Lock
from typing import Any, Dict, Optional

from SNPedia.core.config import get_config
from SNPedia.core.logger import get_logger

logger = get_logger(__name__)
config = get_config()


class CacheEntry:
    """Represents a cached data entry with metadata."""

    def __init__(self, data: Any, ttl: int = 3600) -> None:
        """Initialize cache entry.

        Args:
            data (Any): The data to cache.
            ttl (int): Time-to-live in seconds. Defaults to 3600 (1 hour).
        """
        self.data = data
        self.timestamp = time.time()
        self.ttl = ttl
        self.access_count = 0

    def is_expired(self) -> bool:
        """Check if cache entry has expired."""
        return time.time() - self.timestamp > self.ttl

    def access(self) -> Any:
        """Access the cached data and update metadata."""
        self.access_count += 1
        return self.data


class DataCache:
    """Thread-safe cache manager with LRU eviction and TTL support."""

    def __init__(self, max_size: int = 100, default_ttl: int = 3600) -> None:
        """Initialize cache manager.

        Args:
            max_size: Maximum number of entries to cache
            default_ttl: Default time-to-live in seconds
        """
        self._cache: Dict[str, CacheEntry] = {}
        self._lock = Lock()
        self._max_size = max_size
        self._default_ttl = default_ttl
        self._hits = 0
        self._misses = 0

    def get(self, key: str) -> Optional[Any]:
        """Get data from cache.

        Args:
            key: Cache key

        Returns:
            Cached data or None if not found/expired
        """
        with self._lock:
            if key not in self._cache:
                self._misses += 1
                return None

            entry = self._cache[key]

            # Check if expired
            if entry.is_expired():
                del self._cache[key]
                self._misses += 1
                logger.debug(f"Cache expired for key: {key}")
                return None

            self._hits += 1
            return entry.access()

    def set(self, key: str, data: Any, ttl: Optional[int] = None) -> None:
        """Set data in cache.

        Args:
            key: Cache key
            data: Data to cache
            ttl: Time-to-live in seconds (uses default if None)
        """
        with self._lock:
            # Evict if cache is full
            if len(self._cache) >= self._max_size and key not in self._cache:
                self._evict_lru()

            ttl = ttl if ttl is not None else self._default_ttl
            self._cache[key] = CacheEntry(data, ttl)
            logger.debug(f"Cached data for key: {key}")

    def invalidate(self, key: str) -> None:
        """Invalidate a cache entry.

        Args:
            key: Cache key to invalidate
        """
        with self._lock:
            if key in self._cache:
                del self._cache[key]
                logger.debug(f"Invalidated cache for key: {key}")

    def clear(self) -> None:
        """Clear all cache entries."""
        with self._lock:
            self._cache.clear()
            self._hits = 0
            self._misses = 0
            logger.info("Cache cleared")

    def _evict_lru(self) -> None:
        """Evict least recently used entry."""
        if not self._cache:
            return

        # Find entry with oldest timestamp and lowest access count
        lru_key = min(
            self._cache.keys(),
            key=lambda k: (self._cache[k].access_count, self._cache[k].timestamp),
        )

        del self._cache[lru_key]
        logger.debug(f"Evicted LRU entry: {lru_key}")

    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics.

        Returns:
            Dictionary with cache statistics
        """
        with self._lock:
            total_requests = self._hits + self._misses
            hit_rate = (self._hits / total_requests * 100) if total_requests > 0 else 0

            return {
                "size": len(self._cache),
                "max_size": self._max_size,
                "hits": self._hits,
                "misses": self._misses,
                "hit_rate": f"{hit_rate:.2f}%",
                "total_requests": total_requests,
            }


# Global cache instance
_data_cache = DataCache(
    max_size=getattr(config, "CACHE_MAX_SIZE", 100),
    default_ttl=getattr(config, "CACHE_TTL", 3600),
)


def get_cache() -> DataCache:
    """Get the global cache instance."""
    return _data_cache


@lru_cache(maxsize=10)
def _get_file_path(filename: str) -> str:
    """Get full file path with caching.

    Handles both local development and Docker environments:
    - Docker: /app/data/
    - Local: ./data/
    """
    # Check for Docker environment (data mounted at /app/data)
    docker_path = os.path.join("/app", "data", filename)
    if os.path.exists(docker_path):
        return docker_path

    # Use root data directory for local development
    return os.path.join(os.path.curdir, "data", filename)


def load_json_lazy(filename: str, use_cache: bool = True) -> Optional[Any]:
    """Load JSON file with caching support.

    Args:
        filename: Name of the JSON file to load
        use_cache: Whether to use cache

    Returns:
        Loaded data or None if error
    """
    cache_key = f"json:{filename}"

    # Try cache first
    if use_cache:
        cached_data = _data_cache.get(cache_key)
        if cached_data is not None:
            logger.debug(f"Cache hit for {filename}")
            return cached_data

    # Load from file
    try:
        filepath = _get_file_path(filename)

        if not os.path.isfile(filepath):
            logger.warning(f"File not found: {filepath}")
            return None

        # Check file size
        file_size = os.path.getsize(filepath)
        max_size = getattr(config, "MAX_FILE_SIZE_LOAD", 500 * 1024 * 1024)

        if file_size > max_size:
            logger.error(f"File too large: {filepath} ({file_size} bytes)")
            return None

        with open(filepath, encoding="utf-8") as f:
            data = json.load(f)

        # Cache the data
        if use_cache:
            _data_cache.set(cache_key, data)

        logger.debug(f"Loaded {filename} from disk ({file_size} bytes)")
        return data

    except Exception as e:
        logger.error(f"Error loading {filename}: {e}")
        return None


def load_json_paginated(
    filename: str, page: int = 1, page_size: int = 100, use_cache: bool = True
) -> Dict[str, Any]:
    """Load JSON file with pagination support.

    Args:
        filename: Name of the JSON file to load
        page: Page number (1-indexed)
        page_size: Number of items per page
        use_cache: Whether to use cache

    Returns:
        Dictionary with paginated data and metadata
    """
    # Load full data (will be cached)
    data = load_json_lazy(filename, use_cache=use_cache)

    if data is None:
        return {
            "data": [],
            "page": page,
            "page_size": page_size,
            "total": 0,
            "total_pages": 0,
        }

    # Handle both list and dict data
    if isinstance(data, dict):
        items = list(data.values())
    elif isinstance(data, list):
        items = data
    else:
        logger.error(f"Unexpected data type in {filename}: {type(data)}")
        return {
            "data": [],
            "page": page,
            "page_size": page_size,
            "total": 0,
            "total_pages": 0,
        }

    total = len(items)
    total_pages = (total + page_size - 1) // page_size  # Ceiling division

    # Validate page number
    if page < 1:
        page = 1
    elif page > total_pages and total_pages > 0:
        page = total_pages

    # Calculate slice indices
    start_idx = (page - 1) * page_size
    end_idx = start_idx + page_size

    # Get page data
    page_data = items[start_idx:end_idx]

    return {
        "data": page_data,
        "page": page,
        "page_size": page_size,
        "total": total,
        "total_pages": total_pages,
        "has_next": page < total_pages,
        "has_prev": page > 1,
    }


def invalidate_cache(filename: str) -> None:
    """Invalidate cache for a specific file.

    Args:
        filename: Name of the file to invalidate
    """
    cache_key = f"json:{filename}"
    _data_cache.invalidate(cache_key)
    logger.info(f"Invalidated cache for {filename}")


def clear_all_cache() -> None:
    """Clear all cached data."""
    _data_cache.clear()
    logger.info("Cleared all cache")


def get_cache_stats() -> Dict[str, Any]:
    """Get cache statistics.

    Returns:
        Dictionary with cache statistics
    """
    return _data_cache.get_stats()

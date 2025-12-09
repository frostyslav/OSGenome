# Caching and Data Loading Optimization

## Overview

OSGenome implements an intelligent caching system to optimize data loading and reduce memory usage. Instead of loading entire JSON files into memory at startup, data is now loaded on-demand and cached for subsequent requests.

## Features

### 1. Lazy Loading
- Data files are only loaded when first requested
- Reduces startup time and initial memory footprint
- Automatically handles missing files gracefully

### 2. LRU Cache
- Implements Least Recently Used (LRU) eviction policy
- Configurable cache size limits
- Thread-safe for concurrent requests
- Automatic eviction of least-used entries when cache is full

### 3. Time-To-Live (TTL)
- Cached entries automatically expire after a configurable period
- Prevents serving stale data
- Default TTL: 1 hour (configurable)

### 4. Pagination Support
- API endpoints support pagination for large datasets
- Reduces response size and improves performance
- Configurable page sizes with maximum limits

### 5. Cache Management
- Real-time cache statistics
- Manual cache invalidation
- Clear all cache entries
- Per-file cache invalidation

## Configuration

Add these settings to your `.env` file:

```bash
# Caching Configuration
CACHE_ENABLED=true                   # Enable/disable caching
CACHE_MAX_SIZE=100                   # Maximum number of cached entries
CACHE_TTL=3600                       # Cache time-to-live in seconds (1 hour)

# Pagination Configuration
DEFAULT_PAGE_SIZE=100                # Default number of items per page
MAX_PAGE_SIZE=1000                   # Maximum allowed page size
```

## API Endpoints

### Get RSIDs with Pagination

**Without pagination (returns all data, cached):**
```bash
GET /api/rsids
```

**With pagination:**
```bash
GET /api/rsids?page=1&page_size=100
```

Response:
```json
{
  "results": [...],
  "pagination": {
    "page": 1,
    "page_size": 100,
    "total": 500,
    "total_pages": 5,
    "has_next": true,
    "has_prev": false
  }
}
```

### Cache Statistics

Get current cache performance metrics:
```bash
GET /api/cache/stats
```

Response:
```json
{
  "size": 5,
  "max_size": 100,
  "hits": 150,
  "misses": 10,
  "hit_rate": "93.75%",
  "total_requests": 160
}
```

### Clear Cache

Clear all cached entries:
```bash
POST /api/cache/clear
```

### Invalidate Specific File Cache

Invalidate cache for a specific file:
```bash
POST /api/cache/invalidate/result_table.json
```

## Usage in Code

### Load Data with Caching

```python
from SNPedia.utils.cache_manager import load_json_lazy

# Load data (will be cached automatically)
data = load_json_lazy("result_table.json")
```

### Load Data with Pagination

```python
from SNPedia.utils.cache_manager import load_json_paginated

# Load paginated data
result = load_json_paginated("result_table.json", page=1, page_size=100)

print(f"Total items: {result['total']}")
print(f"Total pages: {result['total_pages']}")
print(f"Current page data: {result['data']}")
```

### Get Cache Statistics

```python
from SNPedia.utils.cache_manager import get_cache_stats

stats = get_cache_stats()
print(f"Cache hit rate: {stats['hit_rate']}")
```

### Invalidate Cache

```python
from SNPedia.utils.cache_manager import invalidate_cache, clear_all_cache

# Invalidate specific file
invalidate_cache("result_table.json")

# Clear all cache
clear_all_cache()
```

## Performance Benefits

### Before (No Caching)
- ❌ Entire JSON file loaded into memory at startup
- ❌ High memory usage for large datasets
- ❌ Slow startup time
- ❌ No pagination support
- ❌ All data loaded even if not needed

### After (With Caching)
- ✅ Data loaded on-demand (lazy loading)
- ✅ Reduced memory footprint
- ✅ Fast startup time
- ✅ Pagination support for large datasets
- ✅ Automatic cache management with LRU eviction
- ✅ Configurable TTL prevents stale data
- ✅ Thread-safe for concurrent requests

## Memory Usage Example

For a 100MB JSON file with 10,000 entries:

**Without caching:**
- Memory at startup: ~100MB
- Memory per request: ~100MB (entire dataset in memory)

**With caching (page_size=100):**
- Memory at startup: ~1MB
- Memory per request: ~1MB (only requested page)
- Cache memory: ~10MB (for 100 cached entries)
- **Total savings: ~89MB (89% reduction)**

## Best Practices

1. **Use Pagination for Large Datasets**
   - Request only the data you need
   - Reduces network transfer and client-side processing

2. **Monitor Cache Performance**
   - Check `/api/cache/stats` regularly
   - Adjust `CACHE_MAX_SIZE` based on hit rate

3. **Invalidate Cache After Updates**
   - Call `/api/cache/invalidate/<filename>` after data updates
   - Ensures clients receive fresh data

4. **Configure TTL Appropriately**
   - Shorter TTL for frequently updated data
   - Longer TTL for static reference data

5. **Adjust Cache Size**
   - Increase `CACHE_MAX_SIZE` if you have available memory
   - Decrease if memory is constrained

## Monitoring

### Health Check Endpoint

The `/api/health` endpoint now includes cache statistics:

```bash
GET /api/health
```

Response:
```json
{
  "status": "healthy",
  "data_loaded": true,
  "data_count": 500,
  "cache": {
    "size": 5,
    "max_size": 100,
    "hits": 150,
    "misses": 10,
    "hit_rate": "93.75%"
  }
}
```

## Troubleshooting

### High Cache Miss Rate

If you see a low hit rate (<70%):
- Increase `CACHE_MAX_SIZE`
- Increase `CACHE_TTL`
- Check if data is being invalidated too frequently

### High Memory Usage

If memory usage is too high:
- Decrease `CACHE_MAX_SIZE`
- Decrease `CACHE_TTL`
- Use pagination more aggressively

### Stale Data

If you're seeing outdated data:
- Decrease `CACHE_TTL`
- Manually invalidate cache after updates
- Consider disabling cache for frequently updated data

## Migration Guide

### Updating Existing Code

**Old code (direct loading):**
```python
from SNPedia.utils.file_utils import load_from_file

results = load_from_file("result_table.json")
```

**New code (with caching):**
```python
from SNPedia.utils.cache_manager import load_json_lazy

results = load_json_lazy("result_table.json")
```

**Or use file_utils with caching enabled:**
```python
from SNPedia.utils.file_utils import load_from_file

results = load_from_file("result_table.json", use_cache=True)
```

### Backward Compatibility

The `load_from_file` function maintains backward compatibility:
- Default behavior unchanged (no caching)
- Pass `use_cache=True` to enable caching
- Existing code continues to work without modifications

## Testing

Run cache tests:
```bash
python test_cache.py
```

All tests should pass, verifying:
- Cache set/get operations
- LRU eviction
- TTL expiration
- Pagination
- Cache invalidation
- Statistics tracking

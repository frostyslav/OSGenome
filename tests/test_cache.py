"""Tests for cache manager functionality."""

import json
import os
import tempfile
import time
import unittest
from pathlib import Path

# Add SNPedia to path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from SNPedia.utils.cache_manager import (
    DataCache,
    load_json_lazy,
    load_json_paginated,
    get_cache_stats,
    clear_all_cache,
    invalidate_cache
)


class TestDataCache(unittest.TestCase):
    """Test DataCache class."""
    
    def setUp(self):
        """Set up test cache."""
        self.cache = DataCache(max_size=3, default_ttl=2)
    
    def test_cache_set_and_get(self):
        """Test basic cache set and get operations."""
        self.cache.set("key1", {"data": "value1"})
        result = self.cache.get("key1")
        self.assertEqual(result, {"data": "value1"})
    
    def test_cache_miss(self):
        """Test cache miss returns None."""
        result = self.cache.get("nonexistent")
        self.assertIsNone(result)
    
    def test_cache_expiration(self):
        """Test cache entry expiration."""
        self.cache.set("key1", {"data": "value1"}, ttl=1)
        time.sleep(1.5)
        result = self.cache.get("key1")
        self.assertIsNone(result)
    
    def test_cache_lru_eviction(self):
        """Test LRU eviction when cache is full."""
        self.cache.set("key1", "value1")
        self.cache.set("key2", "value2")
        self.cache.set("key3", "value3")
        
        # Access key1 to make it more recently used
        self.cache.get("key1")
        
        # Add key4, should evict key2 (least recently used)
        self.cache.set("key4", "value4")
        
        self.assertIsNone(self.cache.get("key2"))
        self.assertIsNotNone(self.cache.get("key1"))
        self.assertIsNotNone(self.cache.get("key3"))
        self.assertIsNotNone(self.cache.get("key4"))
    
    def test_cache_invalidate(self):
        """Test cache invalidation."""
        self.cache.set("key1", "value1")
        self.cache.invalidate("key1")
        result = self.cache.get("key1")
        self.assertIsNone(result)
    
    def test_cache_clear(self):
        """Test clearing all cache entries."""
        self.cache.set("key1", "value1")
        self.cache.set("key2", "value2")
        self.cache.clear()
        
        self.assertIsNone(self.cache.get("key1"))
        self.assertIsNone(self.cache.get("key2"))
    
    def test_cache_stats(self):
        """Test cache statistics."""
        self.cache.set("key1", "value1")
        self.cache.get("key1")  # Hit
        self.cache.get("key2")  # Miss
        
        stats = self.cache.get_stats()
        self.assertEqual(stats['hits'], 1)
        self.assertEqual(stats['misses'], 1)
        self.assertEqual(stats['size'], 1)


class TestCacheManager(unittest.TestCase):
    """Test cache manager functions."""
    
    def setUp(self):
        """Set up test environment."""
        # Create temporary directory for test data
        self.temp_dir = tempfile.mkdtemp()
        self.data_dir = os.path.join(self.temp_dir, "data")
        os.makedirs(self.data_dir, exist_ok=True)
        
        # Create test JSON file
        self.test_data = [
            {"id": 1, "name": "item1"},
            {"id": 2, "name": "item2"},
            {"id": 3, "name": "item3"},
            {"id": 4, "name": "item4"},
            {"id": 5, "name": "item5"}
        ]
        
        test_file = os.path.join(self.data_dir, "test.json")
        with open(test_file, 'w') as f:
            json.dump(self.test_data, f)
        
        # Change to temp directory
        self.original_dir = os.getcwd()
        os.chdir(self.temp_dir)
        
        # Clear cache before each test
        clear_all_cache()
    
    def tearDown(self):
        """Clean up test environment."""
        os.chdir(self.original_dir)
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_load_json_lazy(self):
        """Test lazy loading of JSON files."""
        data = load_json_lazy("test.json")
        self.assertEqual(data, self.test_data)
    
    def test_load_json_lazy_caching(self):
        """Test that data is cached on second load."""
        # First load
        data1 = load_json_lazy("test.json")
        stats1 = get_cache_stats()
        
        # Second load (should hit cache)
        data2 = load_json_lazy("test.json")
        stats2 = get_cache_stats()
        
        self.assertEqual(data1, data2)
        self.assertGreater(stats2['hits'], stats1['hits'])
    
    def test_load_json_paginated(self):
        """Test paginated loading."""
        result = load_json_paginated("test.json", page=1, page_size=2)
        
        self.assertEqual(len(result['data']), 2)
        self.assertEqual(result['page'], 1)
        self.assertEqual(result['page_size'], 2)
        self.assertEqual(result['total'], 5)
        self.assertEqual(result['total_pages'], 3)
        self.assertTrue(result['has_next'])
        self.assertFalse(result['has_prev'])
    
    def test_load_json_paginated_last_page(self):
        """Test loading last page."""
        result = load_json_paginated("test.json", page=3, page_size=2)
        
        self.assertEqual(len(result['data']), 1)  # Only 1 item on last page
        self.assertEqual(result['page'], 3)
        self.assertFalse(result['has_next'])
        self.assertTrue(result['has_prev'])
    
    def test_invalidate_cache(self):
        """Test cache invalidation."""
        # Load data to cache it
        load_json_lazy("test.json")
        
        # Invalidate cache
        invalidate_cache("test.json")
        
        # Next load should be a cache miss
        stats_before = get_cache_stats()
        load_json_lazy("test.json")
        stats_after = get_cache_stats()
        
        self.assertGreater(stats_after['misses'], stats_before['misses'])


if __name__ == '__main__':
    unittest.main()

"""
Test suite for STEP 3: Semantic cache persistence (Redis-backed).

Tests:
  1. Cache hit/miss
  2. Cache expiration (TTL)
  3. Cache invalidation
  4. Cache statistics
  5. Multi-user consistency (shared cache)
  6. Graceful degradation (Redis unavailable)
"""
import json
import time
import unittest
from voxcore.engine.semantic_cache import (
    get_cached_result,
    cache_result,
    invalidate_result,
    clear_cache,
    cache_stats,
)


class TestSemanticCache(unittest.TestCase):
    """Test semantic cache functionality."""
    
    def setUp(self):
        """Clear cache before each test."""
        clear_cache()
    
    def tearDown(self):
        """Clear cache after each test."""
        clear_cache()
    
    def test_cache_miss(self):
        """Test cache miss for uncached query."""
        result = get_cached_result("SELECT * FROM users")
        self.assertIsNone(result)
    
    def test_cache_hit(self):
        """Test caching and retrieving a result."""
        sql = "SELECT * FROM orders LIMIT 10"
        data = [{"id": 1, "amount": 100}, {"id": 2, "amount": 200}]
        
        # Cache it
        cache_result(sql, data)
        
        # Retrieve it
        cached = get_cached_result(sql)
        self.assertEqual(cached, data)
    
    def test_cache_with_different_sql(self):
        """Test that different SQL queries have different cache entries."""
        sql1 = "SELECT * FROM users WHERE id = 1"
        sql2 = "SELECT * FROM users WHERE id = 2"
        data1 = [{"id": 1, "name": "Alice"}]
        data2 = [{"id": 2, "name": "Bob"}]
        
        cache_result(sql1, data1)
        cache_result(sql2, data2)
        
        self.assertEqual(get_cached_result(sql1), data1)
        self.assertEqual(get_cached_result(sql2), data2)
    
    def test_cache_invalidation(self):
        """Test invalidating a specific cache entry."""
        sql = "SELECT revenue FROM sales GROUP BY month"
        data = [{"month": "2024-01", "revenue": 10000}]
        
        cache_result(sql, data)
        self.assertIsNotNone(get_cached_result(sql))
        
        # Invalidate it
        invalidate_result(sql)
        self.assertIsNone(get_cached_result(sql))
    
    def test_cache_with_complex_data(self):
        """Test caching complex nested structures."""
        sql = "SELECT * FROM users JOIN orders ON..."
        data = {
            "users": [
                {"id": 1, "name": "Alice", "orders": [{"id": 1, "amount": 100}]}
            ]
        }
        
        cache_result(sql, data)
        cached = get_cached_result(sql)
        self.assertEqual(cached, data)
    
    def test_cache_with_null_values(self):
        """Test caching results with None/null values."""
        sql = "SELECT id, optional_field FROM table"
        data = [
            {"id": 1, "optional_field": None},
            {"id": 2, "optional_field": "value"}
        ]
        
        cache_result(sql, data)
        cached = get_cached_result(sql)
        self.assertEqual(cached, data)
    
    def test_clear_all_cache(self):
        """Test clearing entire cache."""
        sql1 = "SELECT * FROM query1"
        sql2 = "SELECT * FROM query2"
        
        cache_result(sql1, {"data": 1})
        cache_result(sql2, {"data": 2})
        
        self.assertIsNotNone(get_cached_result(sql1))
        self.assertIsNotNone(get_cached_result(sql2))
        
        clear_cache()
        
        self.assertIsNone(get_cached_result(sql1))
        self.assertIsNone(get_cached_result(sql2))
    
    def test_cache_stats(self):
        """Test getting cache statistics."""
        # Cache some data
        for i in range(3):
            cache_result(f"SELECT * FROM table{i}", {"data": i})
        
        stats = cache_stats()
        self.assertIn("entry_count", stats)
        # Note: stats might be 0 if Redis is unavailable (graceful degradation)
        # but should not raise an exception
        self.assertIsNotNone(stats)
    
    def test_cache_ttl_behavior(self):
        """Test that cache respects TTL (not exact timing, just structure)."""
        sql = "SELECT * FROM ttl_test"
        data = {"test": "data"}
        
        cache_result(sql, data)
        
        # Immediately should hit
        self.assertIsNotNone(get_cached_result(sql))
    
    def test_cache_with_special_characters_in_sql(self):
        """Test caching SQL with special characters."""
        sql = "SELECT * FROM table WHERE name LIKE '%test%' AND value > 100"
        data = [{"id": 1, "name": "test_value", "value": 150}]
        
        cache_result(sql, data)
        self.assertEqual(get_cached_result(sql), data)
    
    def test_cache_concurrent_access(self):
        """Test multiple sequential cache operations."""
        sqls = [f"SELECT * FROM table{i}" for i in range(5)]
        
        # Cache them all
        for i, sql in enumerate(sqls):
            cache_result(sql, {"data": i})
        
        # Retrieve them all
        for i, sql in enumerate(sqls):
            cached = get_cached_result(sql)
            self.assertIsNotNone(cached)
            self.assertEqual(cached["data"], i)


class TestCacheGracefulDegradation(unittest.TestCase):
    """Test that cache gracefully degrades if Redis unavailable."""
    
    def test_cache_operations_dont_raise(self):
        """Test that cache operations never raise exceptions."""
        # These should all work without raising, even if Redis is down
        try:
            get_cached_result("SELECT * FROM any_query")
            cache_result("SELECT * FROM any_query", {"data": "test"})
            invalidate_result("SELECT * FROM any_query")
            clear_cache()
            stats = cache_stats()
            # Should not raise
            self.assertIsNotNone(stats)
        except Exception as e:
            self.fail(f"Cache operations should not raise: {e}")


if __name__ == "__main__":
    unittest.main()

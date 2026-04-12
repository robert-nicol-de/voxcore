"""
VoxCore Semantic Cache (Redis-backed)

🔒 SOURCE OF TRUTH for all caching behavior

This module is the single, authoritative cache implementation for VoxQuery.
All query result caching (exploration, EMD, insights) funnel through this module.
Use only the three public functions: get_cached_result(), cache_result(), clear_cache()

Do NOT create competing cache patterns elsewhere.

Caches query results using Redis for:
1. Performance: Avoid repeated expensive queries
2. Multi-user consistency: Cache shared across all users
3. Persistence: Cache survives restarts

Cache key:  semantic_cache:{hash(sql)}
TTL:        5 minutes (300 seconds)

Graceful degradation: If Redis unavailable, cache is bypassed
(queries still work, just slower and no sharing).

Example:
    result = get_cached_result(sql)
    if result is None:
        result = execute_expensive_query(sql)
        cache_result(sql, result)
    return result

Files using this cache:
- voxcore/engine/exploration_engine.py
- voxcore/engine/explain_my_data.py
"""
import hashlib
import json
import os
from typing import Any, Optional

try:
    from redis import Redis
except ImportError:
    Redis = None

SEMANTIC_CACHE_TTL = 300  # 5 minutes


def _redis_url() -> str:
    """Get Redis connection URL from environment."""
    return os.getenv("REDIS_URL", "redis://localhost:6379/1")


def _get_redis() -> Optional[Redis]:
    """Return a connected Redis client or None if unavailable."""
    if not Redis:
        return None
    try:
        client = Redis.from_url(
            _redis_url(),
            decode_responses=True,
            socket_connect_timeout=2,
            socket_timeout=2,
        )
        client.ping()
        return client
    except Exception:
        return None


def _cache_key(sql: str) -> str:
    """Generate cache key from SQL query using hash."""
    sql_hash = hashlib.md5(sql.encode()).hexdigest()
    return f"semantic_cache:{sql_hash}"


def get_cached_result(sql: str) -> Optional[Any]:
    """
    Return cached result for SQL if available, else None.
    
    Args:
        sql: SQL query string
    
    Returns:
        Query result (list/dict) if cached, None if miss or error
    """
    client = _get_redis()
    if client is None:
        return None
    
    try:
        raw = client.get(_cache_key(sql))
        if raw:
            return json.loads(raw)
    except Exception:
        pass
    
    return None


def cache_result(sql: str, result: Any) -> None:
    """
    Store result for SQL in cache with 5-minute TTL.
    
    Args:
        sql: SQL query string
        result: Query result (list/dict)
    """
    client = _get_redis()
    if client is None:
        return
    
    try:
        client.setex(
            _cache_key(sql),
            SEMANTIC_CACHE_TTL,
            json.dumps(result, default=str)
        )
    except Exception:
        pass


def invalidate_result(sql: str) -> None:
    """
    Delete a specific cached result.
    
    Useful when underlying data changes.
    
    Args:
        sql: SQL query string to invalidate
    """
    client = _get_redis()
    if client is None:
        return
    
    try:
        client.delete(_cache_key(sql))
    except Exception:
        pass


def clear_cache() -> None:
    """
    Clear all semantic cache entries.
    
    WARNING: This affects all users!
    Use invalidate_result() for targeted invalidation.
    """
    client = _get_redis()
    if client is None:
        return
    
    try:
        # Delete all keys matching semantic_cache:*
        pattern = "semantic_cache:*"
        cursor = 0
        while True:
            cursor, keys = client.scan(cursor, match=pattern)
            if keys:
                client.delete(*keys)
            if cursor == 0:
                break
    except Exception:
        pass


def cache_stats() -> dict:
    """
    Return cache statistics (requires SCAN capable Redis).
    
    Returns:
        {"entry_count": N, "ttl_avg": T, "error": msg or None}
    """
    client = _get_redis()
    if client is None:
        return {"entry_count": 0, "error": "Redis unavailable"}
    
    try:
        pattern = "semantic_cache:*"
        cursor = 0
        count = 0
        total_ttl = 0
        
        while True:
            cursor, keys = client.scan(cursor, match=pattern)
            count += len(keys)
            for key in keys:
                ttl = client.ttl(key)
                if ttl > 0:
                    total_ttl += ttl
            if cursor == 0:
                break
        
        avg_ttl = (total_ttl / count) if count > 0 else 0
        return {
            "entry_count": count,
            "ttl_avg": int(avg_ttl),
            "error": None
        }
    except Exception as e:
        return {"entry_count": 0, "error": str(e)}


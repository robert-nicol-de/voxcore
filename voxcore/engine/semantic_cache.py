"""
VoxCore Semantic Cache
Simple in-memory cache for query results. Used by Explain My Data and other engines to avoid repeated heavy queries.
"""

_cache = {}

def get_cached_result(sql):
    """Return cached result for SQL if available, else None."""
    return _cache.get(sql)

def cache_result(sql, result):
    """Store result for SQL in cache."""
    _cache[sql] = result

def clear_cache():
    """Clear the entire semantic cache."""
    _cache.clear()

# Semantic Cache - Single Source of Truth for Caching

## Overview

`semantic_cache.py` is the **single, authoritative cache implementation** for VoxQuery. All caching operations (query results, exploration plans, EMD data) funnel through this module.

**Location:** `voxcore/engine/semantic_cache.py`

**Status:** ✅ **Source of Truth** - All other modules use this API consistently

---

## Purpose

The semantic cache provides:
1. **Performance** - Cache query results to avoid re-executing expensive queries
2. **Multi-user consistency** - Cached results shared across all users
3. **Persistence** - Cache survives service restarts (Redis-backed)
4. **Graceful degradation** - If Redis unavailable, queries still work (just slower, no sharing)

---

## Public API (The Only Cache Interface)

### 1. `get_cached_result(sql: str) -> Optional[Any]`

Retrieve a cached query result.

**Parameters:**
- `sql` (str): SQL query string (used as cache key via MD5 hash)

**Returns:**
- Query result (list/dict) if found in cache
- `None` if cache miss or error

**Example:**
```python
from voxcore.engine.semantic_cache import get_cached_result

cached = get_cached_result("SELECT region, SUM(revenue) FROM sales GROUP BY region")
if cached is not None:
    return cached  # Use cached result
```

### 2. `cache_result(sql: str, result: Any) -> None`

Store a query result in cache with 5-minute TTL.

**Parameters:**
- `sql` (str): SQL query string (cache key)
- `result` (Any): Query result to cache (list/dict, serialized to JSON)

**Returns:**
- None (fire-and-forget operation)

**Example:**
```python
from voxcore.engine.semantic_cache import cache_result

# After executing an expensive query
result = execute_sql(sql, db)
cache_result(sql, result)  # Cache for next use
return result
```

### 3. `clear_cache() -> None`

Clear all cache entries.

**Parameters:**
- None

**Returns:**
- None

**WARNING:** Affects all users, all sessions. Use `invalidate_result()` for targeted invalidation instead.

**Example:**
```python
from voxcore.engine.semantic_cache import clear_cache

# When redeploying data or clearing stale data
clear_cache()
```

### 4. `invalidate_result(sql: str) -> None` (Bonus - Targeted Invalidation)

Delete a specific cached result when underlying data changes.

**Parameters:**
- `sql` (str): SQL query to invalidate

**Returns:**
- None

**Example:**
```python
from voxcore.engine.semantic_cache import invalidate_result

# When a specific table is updated
invalidate_result("SELECT * FROM users WHERE region = 'US'")
```

---

## Cache Behavior

### Key Characteristics

| Property | Value | Details |
|----------|-------|---------|
| **Backend** | Redis | Requires Redis running on REDIS_URL |
| **Key Format** | `semantic_cache:{MD5(sql)}` | Deterministic, collision-resistant |
| **TTL** | 300 seconds (5 minutes) | Auto-expiry, configurable via SEMANTIC_CACHE_TTL |
| **Serialization** | JSON | All results converted to JSON for storage |
| **Fallback** | Graceful degradation | If Redis unavailable, cache returns None, queries still execute |

### Cache Miss Handling

```python
# Standard pattern: check cache first, then execute
from voxcore.engine.semantic_cache import get_cached_result, cache_result

sql = "SELECT region, SUM(revenue) FROM sales GROUP BY region"

# Check cache
cached = get_cached_result(sql)
if cached is not None:
    return cached

# Cache miss: execute and cache
result = execute_expensive_query(sql)
cache_result(sql, result)
return result
```

### Environment

**Configuration via environment variables:**

```bash
# Redis connection URL (default: redis://localhost:6379/1)
export REDIS_URL="redis://localhost:6379/1"

# Cache TTL in seconds (default: 300)
export SEMANTIC_CACHE_TTL="300"
```

---

## Current Usage

### Files Using Semantic Cache (✅ Aligned)

All files use the consistent, function-based API:

| File | Usage | Functions |
|------|-------|-----------|
| `voxcore/engine/exploration_engine.py` | Background exploration queries cached | `get_cached_result()`, `cache_result()`, `clear_cache()` |
| `voxcore/engine/explain_my_data.py` | EMD queries cached for instant display | `get_cached_result()`, `cache_result()` |

### Usage Verification

**exploration_engine.py:**
```python
from voxcore.engine.semantic_cache import get_cached_result, cache_result, clear_cache

# In _execute_exploration_plan():
cached = get_cached_result(sql)
if cached is not None:
    return cached

# After successful execution:
cache_result(sql, result.data)
```

**explain_my_data.py:**
```python
from voxcore.engine.semantic_cache import get_cached_result, cache_result

# In run_query_with_cache():
cached = get_cached_result(sql)
if cached is not None:
    return cached

# After successful execution:
cache_result(sql, result.data)
```

---

## No Competing Cache Patterns

✅ **Verified:** No other cache implementations in voxcore/engine/

The following files have their own cache for module-specific purposes (not competing with semantic_cache):
- `backend/performance/performance_orchestrator.py` - Local performance metrics cache
- `backend/services/policy_store.py` - Policy document cache

These are intentional, separate caches for different purposes and do NOT interfere with semantic_cache.

---

## Optional Metadata Enhancement

The cache can optionally be enhanced with metadata for analytics:

```python
@dataclass
class CacheEntry:
    """Optional metadata wrapper (for future use)"""
    result: Any                  # Query result
    created_time: datetime       # When cached
    hit_count: int              # Times accessed
```

**Decision:** Only implement if Playground needs to:
- Alert users when cache is stale ("Results from X minutes ago")
- Track cache effectiveness (hit rate per query)
- Recommend cache invalidation (when hit_count is high but data may have changed)

Currently: **Not implemented** (not needed for current Playground requirements)

---

## Checklist: Source of Truth

- ✅ Semantic_cache.py is the single, authoritative cache implementation
- ✅ No competing cache patterns for query results
- ✅ exploration_engine.py uses standardized API consistently
- ✅ explain_my_data.py uses standardized API consistently
- ✅ All functions documented with examples
- ✅ Optional metadata enhancement noted for future use
- ✅ Environment configuration documented
- ✅ Graceful degradation (Redis optional) implemented

---

## Best Practices

### DO ✅

- Always check cache before executing expensive queries
- Use the standardized API (get_cached_result, cache_result, clear_cache)
- Cache results from VoxCoreEngine-governed queries
- Use SQL string as cache key (deterministic)
- Handle None returns from get_cached_result() gracefully

### DON'T ❌

- Create competing cache implementations for query results
- Use manual Redis clients (always use semantic_cache functions)
- Cache sensitive data without considering retention
- Clear cache without understanding impact (affects all users)
- Assume Redis is always available (handle graceful degradation)

---

## Example: Complete Caching Workflow

```python
from voxcore.engine.semantic_cache import get_cached_result, cache_result

def run_analysis_query(sql: str, db: Any) -> List[Dict]:
    """Execute query with caching"""
    
    # Step 1: Check cache
    cached = get_cached_result(sql)
    if cached is not None:
        print("✓ Cache hit!")
        return cached
    
    # Step 2: Cache miss, execute query
    print("○ Cache miss, executing...")
    result = execute_sql(sql, db)
    
    # Step 3: Store in cache (fire-and-forget)
    cache_result(sql, result)
    
    # Step 4: Return result
    return result
```

---

## Future Enhancements

1. **Metadata wrapper** - Track cache hit count, created time for analytics
2. **Selective invalidation** - Pre-define which queries to cache vs. skip
3. **Cache warming** - Pre-populate cache with common queries on startup
4. **Cache statistics** - Expose hit rate, memory usage, TTL distribution
5. **Cache priority** - Mark some queries as higher priority (shorter TTL if memory constraint)
6. **Multi-tier caching** - L1: In-memory (fast), L2: Redis (shared)

---

## References

- **Source:** `voxcore/engine/semantic_cache.py` (140 lines)
- **Tests:** See exploration_engine and explain_my_data integration
- **Configuration:** Via REDIS_URL and SEMANTIC_CACHE_TTL environment variables
- **TTL:** 5 minutes (300 seconds) by default


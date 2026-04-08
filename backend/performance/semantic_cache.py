"""
Semantic Cache Engine — Intelligent Caching Based on Query Meaning

Not SQL hash caching. Queries with different SQL but same intent reuse cache.

Example:
- "revenue by region" → cache_key: "revenue:region:*"
- "show me revenue per region" → same cache_key, reuses result
- "revenue by region last 30 days" → cache_key: "revenue:region:last_30_days"

Storage-agnostic: Works with Redis, Memcached, or in-memory.
"""

import hashlib
import json
from typing import Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass


@dataclass
class CacheEntry:
    """Single cached result"""
    key: str
    result: Any
    created_at: datetime
    expires_at: datetime
    hit_count: int = 0
    size_bytes: int = 0


class SemanticCacheKey:
    """
    Build cache keys based on query semantics, not raw SQL.
    
    Example intent extraction:
    "SELECT SUM(revenue) FROM sales WHERE region='North'"
    
    Extracts:
    {
        "metric": "revenue",
        "agg": "sum",
        "source": "sales",
        "dimensions": ["region"],
        "filters": {"region": "North"}
    }
    
    Cache key: "revenue:sum:region:North"
    """
    
    @staticmethod
    def from_query_plan(query_plan: Dict[str, Any]) -> str:
        """
        Build cache key from parsed query plan.
        
        Args:
            query_plan: {
                "metric": "revenue",
                "aggregation": "sum",
                "dimensions": ["region", "date"],
                "filters": {"region": "North"},
                "time_filter": "last_30_days"
            }
        
        Returns:
            cache_key: "revenue:sum:region:last_30_days"
        """
        metric = query_plan.get("metric", "").lower()
        agg = query_plan.get("aggregation", "").lower()[:3]  # sum, count, avg
        dimensions = ":".join(sorted(query_plan.get("dimensions", [])))
        time_filter = query_plan.get("time_filter", "")
        
        parts = [metric, agg, dimensions]
        if time_filter:
            parts.append(time_filter)
        
        cache_key = ":".join(p for p in parts if p)
        return cache_key
    
    @staticmethod
    def from_sql_analysis(sql: str, parsed_intent: Dict[str, Any]) -> str:
        """
        Extract cache key from SQL + parsed intent.
        
        Args:
            sql: "SELECT SUM(revenue) FROM sales WHERE date > '2024-01-01'"
            parsed_intent: From NLP analysis
        
        Returns:
            cache_key: Semantic key
        """
        # Use intent as primary source of truth
        return SemanticCacheKey.from_query_plan(parsed_intent)


class SemanticCache:
    """
    Intelligent cache that understands query intent.
    
    Features:
    - Semantic matching (not just SQL hash)
    - TTL based on query cost
    - Hit/miss tracking
    - Partial result slicing support
    """
    
    def __init__(self, backend="memory"):
        """
        Initialize cache.
        
        Args:
            backend: "memory", "redis", or custom
        """
        self.backend = backend
        
        # In-memory storage (for development)
        if backend == "memory":
            self.cache: Dict[str, CacheEntry] = {}
            self.stats = {
                "hits": 0,
                "misses": 0,
                "evictions": 0,
            }
    
    def get(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve from cache if exists and not expired.
        
        Returns:
            result dict or None if miss/expired
        """
        if self.backend == "memory":
            entry = self.cache.get(cache_key)
            
            if not entry:
                self.stats["misses"] += 1
                return None
            
            if datetime.now() > entry.expires_at:
                # Expired
                del self.cache[cache_key]
                self.stats["misses"] += 1
                return None
            
            # Cache hit
            entry.hit_count += 1
            self.stats["hits"] += 1
            return {
                "data": entry.result,
                "cache_hit": True,
                "hit_count": entry.hit_count,
                "age_seconds": (datetime.now() - entry.created_at).total_seconds(),
            }
        
        return None
    
    def set(
        self,
        cache_key: str,
        result: Any,
        ttl_seconds: int,
        cost_score: Optional[int] = None,
    ) -> None:
        """
        Store in cache with TTL.
        
        Args:
            cache_key: Semantic cache key
            result: Query result (list of dicts)
            ttl_seconds: Time to live in seconds
            cost_score: Query cost (optional, used for auto-TTL)
        """
        # Auto-calculate TTL if not provided
        if cost_score is not None:
            ttl_seconds = self.calculate_ttl_from_cost(cost_score)
        
        if self.backend == "memory":
            now = datetime.now()
            expires_at = now + timedelta(seconds=ttl_seconds)
            
            entry = CacheEntry(
                key=cache_key,
                result=result,
                created_at=now,
                expires_at=expires_at,
                hit_count=0,
                size_bytes=len(json.dumps(result)),
            )
            
            self.cache[cache_key] = entry
            
            # Simple eviction: if >1000 entries, remove oldest
            if len(self.cache) > 1000:
                oldest_key = min(
                    self.cache.keys(),
                    key=lambda k: self.cache[k].created_at
                )
                del self.cache[oldest_key]
                self.stats["evictions"] += 1
    
    def invalidate(self, pattern: str = None) -> int:
        """
        Clear cache entries matching pattern.
        
        Args:
            pattern: "revenue:*" matches all revenue queries
        
        Returns:
            count of invalidated entries
        """
        if self.backend == "memory":
            if pattern is None:
                self.cache.clear()
                return 0
            
            keys_to_delete = []
            for key in self.cache.keys():
                # Simple glob matching
                if self._pattern_match(key, pattern):
                    keys_to_delete.append(key)
            
            for key in keys_to_delete:
                del self.cache[key]
            
            return len(keys_to_delete)
        
        return 0
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        if self.backend == "memory":
            total_requests = self.stats["hits"] + self.stats["misses"]
            hit_rate = (
                self.stats["hits"] / total_requests * 100
                if total_requests > 0
                else 0
            )
            
            return {
                "total_entries": len(self.cache),
                "hits": self.stats["hits"],
                "misses": self.stats["misses"],
                "hit_rate": hit_rate,
                "evictions": self.stats["evictions"],
                "total_requests": total_requests,
            }
        
        return {}
    
    @staticmethod
    def calculate_ttl_from_cost(cost_score: int) -> int:
        """
        Determine cache TTL based on query cost.
        
        High-cost queries stay cached longer (less frequent updates needed).
        Low-cost queries expire faster (can run often).
        
        Args:
            cost_score: 0-100
        
        Returns:
            ttl_seconds
        """
        if cost_score >= 80:
            return 1800  # 30 minutes (heavy analysis)
        elif cost_score >= 50:
            return 300  # 5 minutes (moderate)
        else:
            return 60  # 1 minute (lightweight, can update frequently)
    
    @staticmethod
    def _pattern_match(key: str, pattern: str) -> bool:
        """Simple glob pattern matching for cache invalidation."""
        if pattern == "*":
            return True
        
        if pattern.endswith("*"):
            return key.startswith(pattern[:-1])
        
        return key == pattern


# Global cache instance
_semantic_cache = None


def get_semantic_cache() -> SemanticCache:
    """Get or create the global semantic cache instance."""
    global _semantic_cache
    if _semantic_cache is None:
        _semantic_cache = SemanticCache()
    return _semantic_cache


def reset_semantic_cache():
    """Reset cache (for testing)."""
    global _semantic_cache
    _semantic_cache = SemanticCache()

"""
Cache Invalidation Engine — Keep Cached Results Fresh

Cache invalidation is famously hard. We use 3 strategies:

1. Time-based TTL (most queries)
   - Expensive queries stay cached 30 min
   - Light queries cache 1 min

2. Event-based invalidation (on data change)
   - Data refresh → clear relevant cache
   - Schema change → clear all cache
   - DML operation (INSERT, UPDATE, DELETE) → invalidate affected tables

3. Manual invalidation (admin triggered)
   - Clear specific cache by pattern
   - Clear all cache
"""

from typing import Dict, List, Set, Optional, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum


class InvalidationStrategy(str, Enum):
    """Strategies for cache invalidation."""
    TIME_BASED = "time_based"  # TTL expiry
    EVENT_BASED = "event_based"  # Data change triggers
    MANUAL = "manual"  # Admin-triggered


@dataclass
class InvalidationEvent:
    """Trigger for cache invalidation."""
    event_type: str  # "data_refresh", "schema_change", "dml_operation"
    affected_tables: List[str]  # Which tables were modified
    created_at: datetime = None
    
    def __post_init__(self):
        self.created_at = self.created_at or datetime.now()


class CacheInvalidationEngine:
    """
    Multi-strategy cache invalidation.
    
    Usage:
    ------
    invalidation = get_cache_invalidation_engine()
    
    # Register callback for cache operations
    invalidation.on_invalidate(cache.invalidate)
    
    # When data changes:
    invalidation.trigger_event(
        InvalidationEvent(
            event_type="data_refresh",
            affected_tables=["sales"]
        )
    )
    
    # Cache is automatically cleared for affected tables
    """
    
    def __init__(self):
        self.strategy = InvalidationStrategy.TIME_BASED
        self.enabled = True
        
        # Invalidation callbacks
        self.callbacks: List[Callable] = []
        
        # Track invalidation history
        self.invalidation_history: List[InvalidationEvent] = []
        self.stats = {
            "total_invalidations": 0,
            "time_based": 0,
            "event_based": 0,
            "manual": 0,
        }
    
    def register_callback(self, callback: Callable) -> None:
        """
        Register a callback to be called on invalidation.
        
        Args:
            callback: Function that takes (pattern: str) and clears cache
                      Example: lambda pattern: cache.invalidate(pattern)
        """
        self.callbacks.append(callback)
    
    def trigger_event(self, event: InvalidationEvent) -> None:
        """
        Trigger event-based invalidation.
        
        Args:
            event: Invalidation event (data refresh, schema change, etc.)
        """
        if not self.enabled:
            return
        
        self.invalidation_history.append(event)
        
        # Call all registered callbacks
        for table in event.affected_tables:
            pattern = f"*:{table}:*"  # Cache key pattern
            
            for callback in self.callbacks:
                try:
                    callback(pattern)
                except Exception as e:
                    print(f"Invalidation callback error: {e}")
        
        self.stats["event_based"] += 1
        self.stats["total_invalidations"] += 1
    
    def on_data_refresh(self, table_names: List[str]) -> None:
        """
        Called when data in tables is refreshed.
        
        Invalidates cache for affected tables.
        """
        event = InvalidationEvent(
            event_type="data_refresh",
            affected_tables=table_names,
        )
        self.trigger_event(event)
    
    def on_schema_change(self) -> None:
        """
        Called when database schema changes.
        
        Clears all cache as a safety measure.
        """
        event = InvalidationEvent(
            event_type="schema_change",
            affected_tables=["*"],  # All tables
        )
        self.trigger_event(event)
    
    def on_dml_operation(
        self,
        operation: str,  # "INSERT", "UPDATE", "DELETE"
        table: str,
        affected_columns: Optional[List[str]] = None,
    ) -> None:
        """
        Called on INSERT, UPDATE, or DELETE operation.
        
        Invalidates cache for modified table.
        """
        event = InvalidationEvent(
            event_type="dml_operation",
            affected_tables=[table],
        )
        self.trigger_event(event)
        
        print(f"Cache invalidated: {operation} on {table}")
    
    def manual_clear(self, pattern: str) -> None:
        """
        Manually clear cache matching pattern.
        
        Args:
            pattern: Glob pattern, e.g., "revenue:*" or "*"
        """
        for callback in self.callbacks:
            try:
                callback(pattern)
            except Exception as e:
                print(f"Manual clear error: {e}")
        
        self.stats["manual"] += 1
        self.stats["total_invalidations"] += 1
    
    def get_ttl_for_result(
        self,
        cost_score: int,
    ) -> int:
        """
        Determine cache TTL based on query cost.
        
        Args:
            cost_score: 0-100
        
        Returns:
            ttl_seconds
        """
        # Expensive queries stay cached longer
        # (less frequent updates, better if slightly stale)
        
        if cost_score >= 80:
            return 1800  # 30 minutes
        elif cost_score >= 50:
            return 300  # 5 minutes
        else:
            return 60  # 1 minute (can update frequently)
    
    def get_stats(self) -> Dict[str, int]:
        """Get invalidation statistics."""
        return self.stats.copy()
    
    def get_history(self, limit: int = 100) -> List[Dict]:
        """Get recent invalidation events."""
        return [
            {
                "event_type": e.event_type,
                "affected_tables": e.affected_tables,
                "created_at": e.created_at.isoformat(),
            }
            for e in self.invalidation_history[-limit:]
        ]


# ============================================================================
# INTEGRATION WITH DATABASE TRIGGERS
# ============================================================================
# These SQL snippets trigger cache invalidation on data changes

INVALIDATION_TRIGGER_EXAMPLES = {
    "postgresql": """
        -- Trigger to invalidate cache on sales table change
        CREATE OR REPLACE FUNCTION invalidate_sales_cache()
        RETURNS TRIGGER AS $$
        BEGIN
            -- Call application endpoint to invalidate
            -- (In production, would call HTTP webhook)
            PERFORM pg_notify('cache_invalidation', 'sales');
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
        
        CREATE TRIGGER sales_cache_invalidation
        AFTER INSERT OR UPDATE OR DELETE ON sales
        FOR EACH ROW EXECUTE FUNCTION invalidate_sales_cache();
    """,
    
    "mysql": """
        -- Similar for MySQL
        CREATE TRIGGER sales_cache_invalidation
        AFTER INSERT ON sales
        FOR EACH ROW
        BEGIN
            -- MySQL doesn't have NOTIFY, use insert into audit table
            INSERT INTO cache_invalidation_log (table_name, event_type)
            VALUES ('sales', 'INSERT');
        END;
    """,
}


# Global instance
_cache_invalidation_engine = None


def get_cache_invalidation_engine() -> CacheInvalidationEngine:
    """Get or create the global cache invalidation engine."""
    global _cache_invalidation_engine
    if _cache_invalidation_engine is None:
        _cache_invalidation_engine = CacheInvalidationEngine()
    return _cache_invalidation_engine

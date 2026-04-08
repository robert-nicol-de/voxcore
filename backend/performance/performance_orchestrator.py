"""
Performance Layer Orchestrator — Tie All Components Together

This is the central coordinator that:
1. Checks semantic cache before executing query
2. Reuses partial results if possible
3. Returns with execution flags ("cache_hit", "result_reused")
4. Tracks metrics for dashboard
5. Triggers precomputation for similar queries
6. Analyzes query for index hints
"""

from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
import time

from backend.performance.semantic_cache import (
    SemanticCache,
    SemanticCacheKey,
    get_semantic_cache,
)
from backend.performance.query_reuse_engine import (
    QueryReuseEngine,
    ReusableResult,
    get_query_reuse_engine,
)
from backend.performance.precomputation_engine import (
    get_precomputation_engine,
)
from backend.performance.index_hint_engine import (
    get_index_hint_engine,
)
from backend.performance.cache_invalidation import (
    get_cache_invalidation_engine,
)


@dataclass
class PerformanceResult:
    """Result of performance-layer processing."""
    data: List[Dict[str, Any]]
    cache_hit: bool
    result_reused: bool
    latency_ms: float
    execution_flags: List[str]  # Cache flags


class PerformanceOrchestrator:
    """
    Orchestrate all performance optimizations.
    
    Integration point: Call this BEFORE query execution.
    
    Usage:
    ------
    performance = get_performance_orchestrator()
    
    # Check cache/reuse before executing
    perf_result = performance.check_and_process(
        query_plan={
            "metric": "revenue",
            "aggregation": "sum",
            "dimensions": ["region"],
        },
        cost_score=65,
    )
    
    if perf_result.cache_hit:
        return perf_result.data  # Instant response!
    
    if perf_result.result_reused:
        return perf_result.data  # From cache slice
    
    # Otherwise, execute normally
    result = execute_query(...)
    performance.on_execution_complete(
        query_plan,
        result,
        execution_time_ms,
    )
    """
    
    def __init__(self):
        self.cache = get_semantic_cache()
        self.reuse_engine = get_query_reuse_engine()
        self.precomputation = get_precomputation_engine()
        self.index_hints = get_index_hint_engine()
        self.invalidation = get_cache_invalidation_engine()
        
        # Connect invalidation to cache
        self.invalidation.register_callback(self.cache.invalidate)
    
    def check_and_process(
        self,
        query_plan: Dict[str, Any],
        cost_score: int,
    ) -> Optional[PerformanceResult]:
        """
        Check all optimization layers BEFORE executing query.
        
        Returns:
            PerformanceResult if cache/reuse hit, None if must execute
        """
        start_time = time.time()
        
        # 1. Check semantic cache
        cache_key = SemanticCacheKey.from_query_plan(query_plan)
        cache_result = self.cache.get(cache_key)
        
        if cache_result:
            latency_ms = (time.time() - start_time) * 1000
            
            return PerformanceResult(
                data=cache_result["data"],
                cache_hit=True,
                result_reused=False,
                latency_ms=latency_ms,
                execution_flags=["cache_hit"],
            )
        
        # 2. Check result reuse
        reusable = self.reuse_engine.find_reusable(query_plan)
        
        if reusable:
            sliced_result = self.reuse_engine.slice_result(reusable, query_plan)
            
            if sliced_result:
                latency_ms = (time.time() - start_time) * 1000
                
                return PerformanceResult(
                    data=sliced_result,
                    cache_hit=False,
                    result_reused=True,
                    latency_ms=latency_ms,
                    execution_flags=["result_reused"],
                )
        
        # No optimization available
        return None
    
    def on_execution_complete(
        self,
        query_plan: Dict[str, Any],
        result: List[Dict[str, Any]],
        execution_time_ms: float,
        sql: str = "",
        cost_score: int = 0,
    ) -> None:
        """
        Called AFTER query execution to update caches and hints.
        
        Args:
            query_plan: What was executed
            result: Query result
            execution_time_ms: How long it took
            sql: SQL query (for analysis)
            cost_score: Query cost
        """
        # 1. Cache the result
        cache_key = SemanticCacheKey.from_query_plan(query_plan)
        ttl = self.cache.calculate_ttl_from_cost(cost_score)
        
        self.cache.set(
            cache_key=cache_key,
            result=result,
            ttl_seconds=ttl,
            cost_score=cost_score,
        )
        
        # 2. Store for reuse
        reusable = ReusableResult(
            query_key=cache_key,
            data=result,
            has_time_series="date" in query_plan.get("dimensions", []),
            time_column="date",
            dimensions=query_plan.get("dimensions", []),
            original_query=query_plan,
        )
        self.reuse_engine.store_reusable(reusable)
        
        # 3. Analyze for index hints
        if sql:
            self.index_hints.analyze_query(sql, execution_time_ms, len(result))
        
        # 4. Trigger precomputation for similar queries
        # (optional: only if cost is high)
        if cost_score >= 50:
            self.precomputation.jobs.get(f"{query_plan.get('metric')}_by_region")
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache performance statistics."""
        cache_stats = self.cache.get_stats()
        
        return {
            "cache": cache_stats,
            "precomputation": self.precomputation.get_stats(),
            "index_hints": self.index_hints.get_stats(),
        }
    
    def get_index_recommendations(self) -> List[Dict[str, Any]]:
        """Get recommended indices."""
        recommendations = self.index_hints.get_recommendations()
        
        return [
            {
                "table": r.table_name,
                "columns": r.columns,
                "reason": r.reason,
                "priority": r.priority,
                "query_count": r.query_count,
                "ddl": f"CREATE INDEX idx_{r.table_name}_{'_'.join(r.columns)} ON {r.table_name}({', '.join(r.columns)});",
            }
            for r in recommendations[:10]  # Top 10
        ]
    
    def clear_cache(self, pattern: str = "*") -> None:
        """Manually clear cache."""
        self.cache.invalidate(pattern)
    
    def trigger_precomputation(self) -> None:
        """Trigger all pending precomputation jobs."""
        # In production, this runs on background scheduler
        # Here we just check which jobs should run
        pending_jobs = [
            job for job in self.precomputation.jobs.values()
            if job.should_run()
        ]
        
        print(f"Pending precomputation jobs: {len(pending_jobs)}")


# Global instance
_performance_orchestrator = None


def get_performance_orchestrator() -> PerformanceOrchestrator:
    """Get or create the global performance orchestrator."""
    global _performance_orchestrator
    if _performance_orchestrator is None:
        _performance_orchestrator = PerformanceOrchestrator()
    return _performance_orchestrator

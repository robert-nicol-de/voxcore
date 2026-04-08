"""
Performance Layer — Sub-second Query Responses

Components:
1. SemanticCache — Intelligent caching based on query intent
2. QueryReuseEngine — Reuse partial results through slicing
3. PrecomputationEngine — Run expensive queries in background
4. IndexHintEngine — Suggest database indices automatically
5. CacheInvalidationEngine — Keep data fresh
6. PerformanceOrchestrator — Tie it all together

Integration:
    from backend.performance import get_performance_orchestrator
    
    perf = get_performance_orchestrator()
    
    # Before execution
    cached = perf.check_and_process(query_plan, cost_score)
    if cached:
        return cached.data
    
    # After execution
    perf.on_execution_complete(query_plan, result, time_ms)
"""

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
    PrecomputationEngine,
    PrecomputeJob,
    get_precomputation_engine,
    COMMON_PRECOMPUTE_JOBS,
)
from backend.performance.index_hint_engine import (
    IndexHintEngine,
    IndexRecommendation,
    get_index_hint_engine,
)
from backend.performance.cache_invalidation import (
    CacheInvalidationEngine,
    InvalidationEvent,
    get_cache_invalidation_engine,
)
from backend.performance.performance_orchestrator import (
    PerformanceOrchestrator,
    PerformanceResult,
    get_performance_orchestrator,
)

__all__ = [
    # Semantic Cache
    "SemanticCache",
    "SemanticCacheKey",
    "get_semantic_cache",
    # Query Reuse
    "QueryReuseEngine",
    "ReusableResult",
    "get_query_reuse_engine",
    # Precomputation
    "PrecomputationEngine",
    "PrecomputeJob",
    "get_precomputation_engine",
    "COMMON_PRECOMPUTE_JOBS",
    # Index Hints
    "IndexHintEngine",
    "IndexRecommendation",
    "get_index_hint_engine",
    # Cache Invalidation
    "CacheInvalidationEngine",
    "InvalidationEvent",
    "get_cache_invalidation_engine",
    # Orchestrator
    "PerformanceOrchestrator",
    "PerformanceResult",
    "get_performance_orchestrator",
]

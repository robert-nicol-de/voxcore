"""
Metrics API Endpoints — Expose metrics to frontend

These endpoints power the production dashboard and monitoring views.
"""

from fastapi import APIRouter, Query
from typing import Optional, List, Dict, Any

from backend.observability.metrics_service import get_metrics_service
from backend.observability.alerting_service import get_alerting_service

router = APIRouter(prefix="/api/metrics", tags=["metrics"])


@router.get("/summary")
async def get_metrics_summary() -> Dict[str, Any]:
    """
    Get overall system metrics summary.
    
    Used by: Dashboard system health panel
    Refreshes: Every 5 seconds
    """
    metrics_service = get_metrics_service()
    system_metrics = metrics_service.get_system_metrics()
    
    return {
        "avg_latency_ms": round(system_metrics.avg_latency_ms, 2),
        "p95_latency_ms": round(system_metrics.p95_latency_ms, 2),
        "p99_latency_ms": round(system_metrics.p99_latency_ms, 2),
        "error_rate": round(system_metrics.error_rate, 1),
        "throughput_qps": round(system_metrics.throughput_qps, 2),
        "active_jobs": system_metrics.active_jobs,
        "queue_depth": system_metrics.queue_depth,
        "cache_hit_rate": round(system_metrics.cache_hit_rate, 1),
        "timestamp": system_metrics.timestamp,
    }


@router.get("/health")
async def get_health_status() -> Dict[str, Any]:
    """
    Quick health check for system status.
    
    Returns: HEALTHY | DEGRADED | UNHEALTHY
    """
    metrics_service = get_metrics_service()
    system = metrics_service.get_system_metrics()
    
    # Determine health
    if system.error_rate > 10:
        status = "unhealthy"
    elif system.error_rate > 5 or system.avg_latency_ms > 3000:
        status = "degraded"
    else:
        status = "healthy"
    
    return {
        "status": status,
        "error_rate": round(system.error_rate, 1),
        "avg_latency_ms": round(system.avg_latency_ms, 2),
        "queue_depth": system.queue_depth,
    }


@router.get("/queries/recent")
async def get_recent_queries(limit: int = Query(20, ge=1, le=100)) -> List[Dict[str, Any]]:
    """
    Get recent query metrics.
    
    Used by: Debug panel, query history
    """
    metrics_service = get_metrics_service()
    queries = metrics_service.get_query_metrics(limit=limit)
    
    return [
        {
            "query_id": q.query_id,
            "execution_time_ms": round(q.execution_time_ms, 2),
            "cost_score": q.cost_score,
            "rows_returned": q.rows_returned,
            "cache_hit": q.cache_hit,
            "status": q.status,
            "user_id": q.user_id,
            "org_id": q.org_id,
            "timestamp": q.timestamp,
        }
        for q in queries
    ]


@router.get("/queries/top-cost")
async def get_top_cost_queries(limit: int = Query(10, ge=1, le=50)) -> List[Dict[str, Any]]:
    """
    Get most expensive queries (cost score).
    
    Used by: Cost tracking panel
    Helps identify: Expensive user behavior
    """
    metrics_service = get_metrics_service()
    queries = metrics_service.get_top_cost_queries(limit=limit)
    
    return [
        {
            "query_id": q.query_id,
            "cost_score": q.cost_score,
            "execution_time_ms": round(q.execution_time_ms, 2),
            "rows_returned": q.rows_returned,
            "user_id": q.user_id,
            "org_id": q.org_id,
            "status": q.status,
        }
        for q in queries
    ]


@router.get("/queries/top-slow")
async def get_top_slow_queries(limit: int = Query(10, ge=1, le=50)) -> List[Dict[str, Any]]:
    """
    Get slowest queries (by execution time).
    
    Used by: Performance panel
    Helps identify: Query optimization opportunities
    """
    metrics_service = get_metrics_service()
    queries = metrics_service.get_top_slow_queries(limit=limit)
    
    return [
        {
            "query_id": q.query_id,
            "execution_time_ms": round(q.execution_time_ms, 2),
            "cost_score": q.cost_score,
            "rows_returned": q.rows_returned,
            "user_id": q.user_id,
            "org_id": q.org_id,
        }
        for q in queries
    ]


@router.get("/queries/failed")
async def get_failed_queries(limit: int = Query(20, ge=1, le=100)) -> List[Dict[str, Any]]:
    """
    Get recent failed queries.
    
    Used by: Error tracking, debugging
    """
    metrics_service = get_metrics_service()
    queries = metrics_service.get_failed_queries(limit=limit)
    
    return [
        {
            "query_id": q.query_id,
            "status": q.status,
            "execution_time_ms": round(q.execution_time_ms, 2),
            "user_id": q.user_id,
            "org_id": q.org_id,
            "timestamp": q.timestamp,
        }
        for q in queries
    ]


@router.get("/business/by-org")
async def get_business_metrics() -> List[Dict[str, Any]]:
    """
    Get business metrics by organization.
    
    Shows: Query volume, average cost, unique users per org
    """
    metrics_service = get_metrics_service()
    metrics = metrics_service.get_business_metrics()
    
    return [
        {
            "org_id": m.org_id,
            "total_queries": m.total_queries,
            "avg_cost": round(m.avg_cost, 1),
            "total_cost": round(m.total_cost, 1),
        }
        for m in metrics
    ]


@router.get("/business/org/{org_id}")
async def get_org_metrics(org_id: str) -> Dict[str, Any]:
    """
    Get detailed metrics for specific organization.
    
    Shows: Total queries, cost, latency, users, errors, masked columns
    """
    metrics_service = get_metrics_service()
    org_metrics = metrics_service.get_org_metrics(org_id)
    
    return org_metrics


@router.get("/user/{user_id}")
async def get_user_metrics(user_id: str) -> Dict[str, Any]:
    """
    Get metrics for specific user.
    
    Shows: Query count, average cost/latency, errors
    """
    metrics_service = get_metrics_service()
    user_metrics = metrics_service.get_user_metrics(user_id)
    
    return user_metrics


@router.get("/governance")
async def get_governance_metrics() -> Dict[str, Any]:
    """
    Get governance activity metrics.
    
    Shows: Policies triggered, blocked queries, masked columns
    """
    metrics_service = get_metrics_service()
    governance = metrics_service.get_governance_metrics()
    
    return {
        "policies_triggered": governance.policies_triggered,
        "policies_blocked": governance.policies_blocked,
        "columns_masked": governance.columns_masked,
        "rbac_denials": governance.rbac_denials,
        "cost_limit_hits": governance.cost_limit_hits,
        "timestamp": governance.timestamp,
    }


@router.get("/alerts/recent")
async def get_recent_alerts(limit: int = Query(50, ge=1, le=200)) -> List[Dict[str, Any]]:
    """
    Get recent alerts.
    
    Used by: Alert dashboard, operational awareness
    """
    alerting_service = get_alerting_service()
    return alerting_service.get_recent_alerts(limit=limit)


@router.get("/alerts/critical")
async def get_critical_alerts() -> List[Dict[str, Any]]:
    """
    Get all critical alerts.
    
    Used by: Incident response, on-call dashboard
    """
    alerting_service = get_alerting_service()
    return alerting_service.get_critical_alerts()


@router.get("/performance/latency")
async def get_latency_percentiles() -> Dict[str, Any]:
    """
    Get latency distribution (percentiles).
    
    Used by: Performance charts
    """
    metrics_service = get_metrics_service()
    system = metrics_service.get_system_metrics()
    
    return {
        "avg_ms": round(system.avg_latency_ms, 2),
        "p95_ms": round(system.p95_latency_ms, 2),
        "p99_ms": round(system.p99_latency_ms, 2),
        "timestamp": system.timestamp,
    }


@router.get("/cache/hit-rate")
async def get_cache_metrics() -> Dict[str, Any]:
    """
    Get cache performance metrics.
    
    Shows: Cache hit rate percentage
    """
    metrics_service = get_metrics_service()
    system = metrics_service.get_system_metrics()
    
    return {
        "cache_hit_rate": round(system.cache_hit_rate, 1),
        "throughput_qps": round(system.throughput_qps, 2),
        "timestamp": system.timestamp,
    }


@router.get("/debug/full")
async def get_debug_view() -> Dict[str, Any]:
    """
    Complete debug view — all available metrics.
    
    Used by: Internal ops team, troubleshooting
    This is the "command center" view for engineers.
    """
    metrics_service = get_metrics_service()
    alerting_service = get_alerting_service()
    
    system = metrics_service.get_system_metrics()
    recent_queries = metrics_service.get_query_metrics(limit=50)
    
    return {
        "system": {
            "avg_latency_ms": round(system.avg_latency_ms, 2),
            "p95_latency_ms": round(system.p95_latency_ms, 2),
            "p99_latency_ms": round(system.p99_latency_ms, 2),
            "error_rate": round(system.error_rate, 1),
            "throughput_qps": round(system.throughput_qps, 2),
            "active_jobs": system.active_jobs,
            "queue_depth": system.queue_depth,
            "cache_hit_rate": round(system.cache_hit_rate, 1),
        },
        "recent_queries": [
            {
                "query_id": q.query_id,
                "execution_time_ms": round(q.execution_time_ms, 2),
                "cost_score": q.cost_score,
                "rows_returned": q.rows_returned,
                "cache_hit": q.cache_hit,
                "status": q.status,
                "user_id": q.user_id,
                "org_id": q.org_id,
                "timestamp": q.timestamp,
            }
            for q in recent_queries
        ],
        "alerts": {
            "critical": alerting_service.get_critical_alerts(),
            "recent": alerting_service.get_recent_alerts(limit=20),
        },
        "governance": metrics_service.get_governance_metrics().__dict__,
    }

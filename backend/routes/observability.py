"""
STEP 10 — Observability: Dashboard API

FastAPI endpoints for observability dashboard.
Expose all metrics, logs, query history, system health.
"""

from fastapi import APIRouter, Query
from datetime import datetime, timedelta
from typing import Optional

from backend.observability.metrics_collector import get_metrics_collector
from backend.observability.query_tracker import get_query_tracker
from backend.observability.structured_logger import (
    query_logger, policy_logger, performance_logger, error_logger
)


router = APIRouter(prefix="/api/observability", tags=["observability"])


# System Health Endpoints

@router.get("/health")
async def get_system_health():
    """Get overall system health status"""
    metrics = get_metrics_collector()
    health = metrics.get_system_health()
    
    return {
        "status": health.status,
        "message": f"System is {health.status}",
        "details": {
            "uptime_seconds": health.uptime_seconds,
            "memory_percent": health.memory_percent,
            "cpu_percent": health.cpu_percent,
            "active_connections": health.active_connections,
            "pending_jobs": health.pending_jobs,
            "last_error": health.last_error
        }
    }


@router.get("/metrics/latency")
async def get_latency_metrics():
    """Get query latency metrics (min, max, mean, median, p95, p99)"""
    metrics = get_metrics_collector()
    latency = metrics.get_latency_metrics()
    
    return {
        "min_ms": latency.min_ms,
        "max_ms": latency.max_ms,
        "mean_ms": latency.mean_ms,
        "median_ms": latency.median_ms,
        "p95_ms": latency.p95_ms,
        "p99_ms": latency.p99_ms,
        "sample_count": latency.count
    }


@router.get("/metrics/errors")
async def get_error_metrics():
    """Get error rate and breakdown"""
    metrics = get_metrics_collector()
    errors = metrics.get_error_metrics()
    
    return {
        "total_errors": errors.total_errors,
        "error_rate_percent": round(errors.error_rate_percent, 2),
        "errors_by_type": errors.errors_by_type,
        "last_error": errors.last_error,
        "last_error_time": errors.last_error_time
    }


@router.get("/metrics/cache")
async def get_cache_metrics():
    """Get cache hit rate and performance"""
    metrics = get_metrics_collector()
    cache = metrics.get_cache_metrics()
    
    return {
        "hits": cache.hits,
        "misses": cache.misses,
        "hit_rate_percent": round(cache.hit_rate_percent, 2),
        "avg_hit_time_ms": round(cache.avg_hit_time_ms, 2),
        "avg_miss_time_ms": round(cache.avg_miss_time_ms, 2)
    }


@router.get("/metrics/queue")
async def get_queue_metrics():
    """Get queue wait times and job status"""
    metrics = get_metrics_collector()
    queue = metrics.get_queue_metrics()
    
    return {
        "waiting_count": queue.waiting_count,
        "processing_count": queue.processing_count,
        "avg_wait_time_ms": round(queue.avg_wait_time_ms, 2),
        "max_wait_time_ms": round(queue.max_wait_time_ms, 2),
        "processed_count": queue.processed_count
    }


@router.get("/metrics/cost")
async def get_cost_metrics():
    """Get cost metrics (total, by role, by org)"""
    metrics = get_metrics_collector()
    cost = metrics.get_cost_metrics()
    
    return {
        "total_cost": round(cost.total_cost, 2),
        "avg_cost_per_query": round(cost.avg_cost_per_query, 4),
        "max_cost": round(cost.max_cost, 2),
        "cost_by_role": {role: round(c, 2) for role, c in cost.cost_by_role.items()},
        "cost_by_org": {org: round(c, 2) for org, c in cost.cost_by_org.items()}
    }


@router.get("/metrics/summary")
async def get_metrics_summary():
    """Get all metrics in one call"""
    metrics = get_metrics_collector()
    
    latency = metrics.get_latency_metrics()
    errors = metrics.get_error_metrics()
    cache = metrics.get_cache_metrics()
    queue = metrics.get_queue_metrics()
    cost = metrics.get_cost_metrics()
    health = metrics.get_system_health()
    
    return {
        "health": {
            "status": health.status,
            "active_connections": health.active_connections,
            "pending_jobs": health.pending_jobs
        },
        "latency": {
            "mean_ms": round(latency.mean_ms, 2),
            "p99_ms": round(latency.p99_ms, 2),
            "sample_count": latency.count
        },
        "errors": {
            "rate_percent": round(errors.error_rate_percent, 2),
            "total_count": errors.total_errors
        },
        "cache": {
            "hit_rate_percent": round(cache.hit_rate_percent, 2)
        },
        "cost": {
            "total": round(cost.total_cost, 2),
            "avg_per_query": round(cost.avg_cost_per_query, 4)
        }
    }


# Query History Endpoints

@router.get("/queries/recent")
async def get_recent_queries(limit: int = Query(50, ge=1, le=1000)):
    """Get recent queries"""
    tracker = get_query_tracker()
    queries = tracker.get_recent_queries(limit=limit)
    
    return {
        "count": len(queries),
        "queries": [q.to_dict() for q in queries]
    }


@router.get("/queries/{query_id}")
async def get_query_details(query_id: str):
    """Get detailed information about specific query"""
    tracker = get_query_tracker()
    query = tracker.get_query(query_id)
    
    if not query:
        return {"error": "Query not found", "query_id": query_id}
    
    return query.to_dict()


@router.get("/queries/failed")
async def get_failed_queries(limit: int = Query(50, ge=1, le=1000)):
    """Get failed queries"""
    tracker = get_query_tracker()
    queries = tracker.get_failed_queries(limit=limit)
    
    return {
        "count": len(queries),
        "queries": [q.to_dict() for q in queries]
    }


@router.get("/queries/slow")
async def get_slow_queries(
    threshold_ms: float = Query(1000, ge=0),
    limit: int = Query(50, ge=1, le=1000)
):
    """Get slow queries (over threshold)"""
    tracker = get_query_tracker()
    queries = tracker.get_slow_queries(threshold_ms=threshold_ms, limit=limit)
    
    return {
        "count": len(queries),
        "threshold_ms": threshold_ms,
        "queries": [q.to_dict() for q in queries]
    }


@router.get("/queries/high-cost")
async def get_high_cost_queries(
    threshold: float = Query(10.0, ge=0),
    limit: int = Query(50, ge=1, le=1000)
):
    """Get high-cost queries"""
    tracker = get_query_tracker()
    queries = tracker.get_high_cost_queries(threshold=threshold, limit=limit)
    
    return {
        "count": len(queries),
        "cost_threshold": threshold,
        "queries": [q.to_dict() for q in queries]
    }


@router.get("/queries/by-org/{org_id}")
async def get_org_queries(org_id: str, limit: int = Query(100, ge=1, le=1000)):
    """Get queries for specific organization"""
    tracker = get_query_tracker()
    queries = tracker.get_queries_by_org(org_id, limit=limit)
    
    stats = metrics_collector.get_metrics_by_org(org_id) if queries else {}
    
    return {
        "org_id": org_id,
        "query_count": len(queries),
        "stats": stats,
        "queries": [q.to_dict() for q in queries]
    }


@router.get("/queries/by-user/{user_id}")
async def get_user_queries(user_id: str, limit: int = Query(100, ge=1, le=1000)):
    """Get queries for specific user"""
    tracker = get_query_tracker()
    queries = tracker.get_queries_by_user(user_id, limit=limit)
    
    return {
        "user_id": user_id,
        "query_count": len(queries),
        "queries": [q.to_dict() for q in queries]
    }


# Job Status Endpoints

@router.get("/jobs/active")
async def get_active_jobs():
    """Get currently active jobs"""
    metrics = get_metrics_collector()
    jobs = metrics.get_active_jobs()
    
    return {
        "active_count": len(jobs),
        "jobs": jobs
    }


@router.get("/jobs/by-status/{status}")
async def get_jobs_by_status(status: str):
    """Get jobs by status (queued, processing, completed)"""
    metrics = get_metrics_collector()
    jobs = metrics.get_active_jobs()
    
    filtered = [j for j in jobs if j["status"] == status]
    
    return {
        "status": status,
        "count": len(filtered),
        "jobs": filtered
    }


# Statistics Endpoints

@router.get("/stats/cache")
async def get_cache_statistics():
    """Get cache statistics"""
    tracker = get_query_tracker()
    stats = tracker.get_cache_stats()
    
    return stats


@router.get("/stats/errors")
async def get_error_statistics():
    """Get error statistics"""
    tracker = get_query_tracker()
    stats = tracker.get_error_stats()
    
    return stats


# Dashboard Data Endpoints

@router.get("/dashboard/overview")
async def get_dashboard_overview():
    """Get complete dashboard overview data"""
    metrics = get_metrics_collector()
    tracker = get_query_tracker()
    
    # System health
    health = metrics.get_system_health()
    
    # Recent metrics
    latency = metrics.get_latency_metrics()
    errors = metrics.get_error_metrics()
    cache = metrics.get_cache_metrics()
    queue = metrics.get_queue_metrics()
    cost = metrics.get_cost_metrics()
    
    # Recent data
    recent_queries = tracker.get_recent_queries(limit=10)
    failed_queries = tracker.get_failed_queries(limit=5)
    slow_queries = tracker.get_slow_queries(limit=5)
    active_jobs = metrics.get_active_jobs()
    
    return {
        "timestamp": datetime.utcnow().isoformat(),
        "system": {
            "health": health.status,
            "active_connections": health.active_connections,
            "pending_jobs": health.pending_jobs
        },
        "metrics": {
            "latency": {
                "mean_ms": round(latency.mean_ms, 2),
                "p95_ms": round(latency.p95_ms, 2),
                "p99_ms": round(latency.p99_ms, 2)
            },
            "errors": {
                "rate": round(errors.error_rate_percent, 2),
                "count": errors.total_errors
            },
            "cache": {
                "hit_rate": round(cache.hit_rate_percent, 2)
            },
            "cost": {
                "total": round(cost.total_cost, 2),
                "avg": round(cost.avg_cost_per_query, 4)
            }
        },
        "recent_activity": {
            "recent_queries": [q.to_dict() for q in recent_queries],
            "failed_queries": [q.to_dict() for q in failed_queries],
            "slow_queries": [q.to_dict() for q in slow_queries],
            "active_jobs_count": len(active_jobs)
        }
    }


@router.get("/dashboard/cost-analysis")
async def get_cost_analysis():
    """Get cost analysis by org and role"""
    metrics = get_metrics_collector()
    cost = metrics.get_cost_metrics()
    
    return {
        "total_cost": round(cost.total_cost, 2),
        "avg_per_query": round(cost.avg_cost_per_query, 4),
        "by_org": {org: round(c, 2) for org, c in cost.cost_by_org.items()},
        "by_role": {role: round(c, 2) for role, c in cost.cost_by_role.items()}
    }


@router.get("/dashboard/system-health")
async def get_system_health_detailed():
    """Get detailed system health information"""
    metrics = get_metrics_collector()
    health = metrics.get_system_health()
    queue = metrics.get_queue_metrics()
    
    return {
        "status": health.status,
        "timestamp": datetime.utcnow().isoformat(),
        "resources": {
            "memory_percent": health.memory_percent,
            "cpu_percent": health.cpu_percent,
            "active_connections": health.active_connections
        },
        "queue": {
            "waiting": queue.waiting_count,
            "processing": queue.processing_count,
            "avg_wait_ms": round(queue.avg_wait_time_ms, 2)
        },
        "last_error": health.last_error
    }


# Get global metrics collector for use in endpoints
metrics_collector = get_metrics_collector()

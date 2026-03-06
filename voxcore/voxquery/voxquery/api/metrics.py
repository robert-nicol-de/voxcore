"""Metrics API endpoints for monitoring repair success rates"""

import logging
from fastapi import APIRouter, Query
from typing import Optional

from ..core import repair_metrics

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/metrics", tags=["metrics"])


@router.get("/repair-stats")
async def get_repair_stats(hours: Optional[int] = Query(24, ge=1, le=720)):
    """Get repair statistics for the specified time window
    
    Returns:
    - total_queries: Total queries processed
    - queries_needing_repair: Queries that failed validation
    - repair_rate_percent: % of queries needing repair
    - repair_attempts: Number of repair attempts
    - repair_successes: Number of successful repairs
    - repair_failures: Number of failed repairs
    - repair_success_rate_percent: % of repairs that passed re-validation
    - execution_successes: Number of repaired queries that executed successfully
    - execution_failures: Number of repaired queries that failed execution
    - execution_success_rate_percent: % of repaired queries that executed successfully
    - pattern_counts: Count of each repair pattern triggered
    - pattern_success_rates: Success rate for each pattern
    - window_start: Start of time window (ISO format)
    - window_end: End of time window (ISO format)
    """
    try:
        metrics = repair_metrics.get_metrics(hours)
        return metrics.to_dict()
    except Exception as e:
        logger.error(f"Error getting repair stats: {e}", exc_info=True)
        return {
            "error": str(e),
            "message": "Failed to retrieve repair statistics"
        }


@router.get("/top-patterns")
async def get_top_patterns(
    limit: int = Query(3, ge=1, le=10),
    hours: Optional[int] = Query(24, ge=1, le=720)
):
    """Get top N repair patterns by frequency
    
    Returns:
    - patterns: List of (pattern_name, count) tuples
    """
    try:
        patterns = repair_metrics.get_top_patterns(limit, hours)
        return {
            "patterns": [
                {
                    "name": pattern,
                    "count": count
                }
                for pattern, count in patterns
            ],
            "window_hours": hours,
            "limit": limit
        }
    except Exception as e:
        logger.error(f"Error getting top patterns: {e}", exc_info=True)
        return {
            "error": str(e),
            "message": "Failed to retrieve top patterns"
        }


@router.get("/health")
async def metrics_health():
    """Health check for metrics system"""
    try:
        tracker = repair_metrics.get_metrics_tracker()
        return {
            "status": "healthy",
            "events_tracked": len(tracker.events),
            "window_hours": tracker.window_hours
        }
    except Exception as e:
        logger.error(f"Error in metrics health check: {e}", exc_info=True)
        return {
            "status": "unhealthy",
            "error": str(e)
        }

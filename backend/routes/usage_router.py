"""
Usage Tracking API Routes

Endpoints:
- GET /api/sessions/{session_id}/usage - Get session usage metrics
- GET /api/sessions/{session_id}/usage/summary - Get usage summary with stats
- GET /api/sessions/{session_id}/usage/cost-estimate - Get cost estimate for billing
- GET /api/sessions/{session_id}/usage/queries - Get query execution log
- POST /api/sessions/{session_id}/usage/record - Record a query execution

Integration: Called after query execution in query_service
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from services.usage_tracker import get_usage_tracker

router = APIRouter(prefix="/api/sessions", tags=["usage"])


@router.get("/{session_id}/usage")
async def get_session_usage(session_id: str):
    """
    Get current usage metrics for a session.
    
    Returns:
    {
        "session_id": "",
        "user_id": null,
        "workspace_id": null,
        "created_at": "2024-03-10T...",
        "queries_count": 5,
        "rows_scanned_total": 50000,
        "execution_time_total": 2500,
        "cost_spent": 0.15
    }
    """
    tracker = get_usage_tracker()
    usage = tracker.get_session_usage(session_id)
    
    if not usage:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return usage


@router.get("/{session_id}/usage/summary")
async def get_session_summary(session_id: str):
    """
    Get aggregated usage summary with execution statistics.
    
    Returns:
    {
        ...usage_metrics,
        "avg_execution_time_ms": 500,
        "min_execution_time_ms": 100,
        "max_execution_time_ms": 2000,
        "total_executions": 5
    }
    """
    tracker = get_usage_tracker()
    summary = tracker.get_session_summary(session_id)
    
    if not summary:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return summary


@router.get("/{session_id}/usage/cost-estimate")
async def get_cost_estimate(session_id: str):
    """
    Get cost estimate for the session (for billing purposes).
    
    Cost model:
    - Base: $0.01 per query
    - Rows: $0.001 per 10,000 rows
    - Time: $0.01 per 100ms
    
    Returns:
    {
        "queries_count": 5,
        "rows_scanned_total": 50000,
        "execution_time_total": 2500,
        "cost_from_governance": 0.15,
        "estimated_query_cost": 0.05,
        "estimated_row_cost": 0.005,
        "estimated_time_cost": 0.25,
        "total_estimated_cost": 0.455
    }
    """
    tracker = get_usage_tracker()
    estimate = tracker.get_cost_estimate(session_id)
    
    if not estimate:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return estimate


@router.get("/{session_id}/usage/queries")
async def get_query_log(
    session_id: str,
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0)
):
    """
    Get detailed query execution log for a session.
    
    Returns:
    [
        {
            "id": 1,
            "session_id": "...",
            "query_hash": "abc123",
            "executed_at": "2024-03-10T...",
            "rows_scanned": 1000,
            "execution_time_ms": 250,
            "cost": 0.01,
            "status": "success",
            "sql": "SELECT ..."
        },
        ...
    ]
    """
    tracker = get_usage_tracker()
    
    # Verify session exists
    usage = tracker.get_session_usage(session_id)
    if not usage:
        raise HTTPException(status_code=404, detail="Session not found")
    
    queries = tracker.get_session_queries(session_id, limit=limit, offset=offset)
    return queries


@router.post("/{session_id}/usage/record")
async def record_query(
    session_id: str,
    rows_scanned: int = 0,
    execution_time_ms: int = 0,
    cost: float = 0.0,
    status: str = "success",
    sql: Optional[str] = None,
    query_hash: Optional[str] = None
):
    """
    Record a query execution and update session totals.
    
    Called after each query execution to track usage metrics.
    
    Request body:
    {
        "rows_scanned": 1000,
        "execution_time_ms": 250,
        "cost": 0.01,
        "status": "success",
        "sql": "SELECT ... FROM ...",
        "query_hash": "abc123def456"
    }
    
    Returns: Updated session usage
    """
    tracker = get_usage_tracker()
    
    # Verify session exists
    usage = tracker.get_session_usage(session_id)
    if not usage:
        # Auto-create session if it doesn't exist
        tracker.create_session(session_id)
    
    # Record the query
    updated = tracker.record_query(
        session_id=session_id,
        rows_scanned=rows_scanned,
        execution_time_ms=execution_time_ms,
        cost=cost,
        status=status,
        sql=sql,
        query_hash=query_hash
    )
    
    return {
        "status": "recorded",
        "session_usage": updated
    }


@router.post("/{session_id}/usage/create")
async def create_session(
    session_id: str,
    user_id: Optional[str] = None,
    workspace_id: Optional[str] = None
):
    """
    Create or reset a session for usage tracking.
    
    Called when starting a new analysis session.
    """
    tracker = get_usage_tracker()
    session = tracker.create_session(session_id, user_id, workspace_id)
    
    return {
        "status": "created",
        "session": session
    }


@router.delete("/{session_id}/usage")
async def delete_session(session_id: str):
    """Delete a session and all its query logs."""
    tracker = get_usage_tracker()
    success = tracker.delete_session(session_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return {"status": "deleted", "session_id": session_id}

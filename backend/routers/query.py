

from fastapi import APIRouter, Request, HTTPException
from pydantic import BaseModel
from backend.services.session_singleton import session_service
from backend.services.query_job_queue import get_job, get_worker_stats

router = APIRouter()


class QueryRequest(BaseModel):
    text: str
    session_id: str = None
    mode: str = None  # "demo" or "live"


def build_job_response(job_id, status, result=None, error=None):
    """
    Build a response for job status queries.
    
    Args:
        job_id: Job ID
        status: Job status (queued, running, completed, failed, blocked)
        result: Result data if completed
        error: Error message if failed
        
    Returns:
        API response dict
    """
    return {
        "job_id": job_id,
        "status": status,
        "data": result.get("data") if result and isinstance(result, dict) else result,
        "cost_score": result.get("cost_score", 0) if result and isinstance(result, dict) else 0,
        "cost_level": result.get("cost_level", "unknown") if result and isinstance(result, dict) else "unknown",
        "error": error,
    }


@router.post("/query")
async def submit_query(request: QueryRequest):
    """
    Submit a query for asynchronous execution.
    
    🔄 STEP 2: Async Execution
    - Returns immediately with job_id
    - Query runs in background thread pool
    - Client polls /api/jobs/{job_id} for status
    - Never blocks the main request
    
    Returns:
        {
            "job_id": "uuid",
            "status": "queued",
            "message": "Query submitted successfully"
        }
    """
    try:
        session_id, session = session_service.get_or_create_session(
            request.session_id,
            mode=request.mode or "demo"
        )

        user_id = session.get("user_id") or "anonymous"
        db_connection = session.get("db")
        
        if not db_connection:
            raise Exception("No database connection available")

        # 🔄 Submit to job queue (non-blocking)
        from voxcore.engine.query_orchestrator import submit_query_job, QueryPriority
        
        job_id = submit_query_job(
            question=request.text,
            sql="SELECT 1",  # TODO: SQL should come from LLM
            db_connection=db_connection,
            user_id=user_id,
            session_id=session_id,
            workspace_id=session.get("workspace_id"),
            priority=QueryPriority.HIGH,
        )

        return {
            "job_id": job_id,
            "status": "queued",
            "message": "Query submitted successfully. Poll /api/jobs/{job_id} for status."
        }

    except Exception as e:
        return {
            "job_id": None,
            "status": "failed",
            "error": str(e)
        }


@router.get("/jobs/{job_id}")
async def get_query_status(job_id: str):
    """
    Poll job status.
    
    Returns job state: queued, running, completed, failed, or blocked
    
    Returns:
        {
            "job_id": "uuid",
            "status": "completed",
            "data": [...],
            "cost_score": 35,
            "cost_level": "safe",
            "error": null
        }
    """
    job = get_job(job_id)
    
    if not job:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")
    
    status = job.get("status", "unknown")
    result = job.get("result")
    error = job.get("error")
    
    return build_job_response(job_id, status, result, error)


@router.get("/jobs")
async def get_worker_health():
    """
    Get worker pool health metrics.
    
    Returns:
        {
            "queued_queries": 5,
            "running_queries": 2,
            "completed_jobs": 142,
            "blocked_jobs": 3,
            "completed_today": 142,
            "blocked_queries": 3
        }
    """
    return get_worker_stats()


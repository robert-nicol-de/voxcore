import time

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from backend.services.risk_engine import calculate_risk
from backend.services.query_inspector import block_if_dangerous
from backend.services.query_metrics import log_query
from backend.services.rate_limiter import limiter
from backend.services import approval_queue as queue


router = APIRouter()


class QueryRequest(BaseModel):
    query: str
    agent: str = "anonymous"  # identifies the AI agent or user submitting the query


@router.post("/query")
@limiter.limit("100/minute")
def run_query(request: Request, payload: QueryRequest):
    start = time.perf_counter()
    query = payload.query

    # --- Risk scoring (graded: LOW / MEDIUM / HIGH / CRITICAL) ---
    try:
        risk_result = block_if_dangerous(query)  # raises 403 only for CRITICAL
    except HTTPException:
        execution_time = time.perf_counter() - start
        log_query(
            company_id=1,
            user_id=1,
            query=query,
            execution_time=execution_time,
            risk_level="CRITICAL",
            blocked=True,
        )
        raise

    risk_level = risk_result["risk_level"]
    risk_score = risk_result["risk_score"]
    requires_approval = risk_result["requires_approval"]

    # HIGH → enqueue for human approval, do not execute
    if requires_approval:
        execution_time = time.perf_counter() - start
        log_query(
            company_id=1,
            user_id=1,
            query=query,
            execution_time=execution_time,
            risk_level=risk_level,
            blocked=False,
        )
        # Persist to approval queue (best-effort; don't fail the request if DB is down)
        queued_id: int | None = None
        try:
            row = queue.submit(
                query_text=query,
                risk_score=risk_score,
                risk_level=risk_level,
                reasons=risk_result["reasons"],
                ai_agent=payload.agent if hasattr(payload, 'agent') else 'anonymous',
            )
            queued_id = row.get("id")
        except Exception as _queue_err:
            print(f"[!] Approval queue insert failed: {_queue_err}")
        return {
            "status": "approval_required",
            "queue_id": queued_id,
            "risk_score": risk_score,
            "risk_level": risk_level,
            "requires_approval": True,
            "reasons": risk_result["reasons"],
            "message": "Query held for admin review. Check /api/approval/pending.",
        }

    # LOW / MEDIUM → run through AI risk engine
    risk = calculate_risk(query)
    execution_time = time.perf_counter() - start
    log_query(
        company_id=1,
        user_id=1,
        query=query,
        execution_time=execution_time,
        risk_level=risk_level,
        blocked=risk.get("status") == "BLOCKED",
    )

    if risk.get("status") == "BLOCKED":
        return {
            "status": "blocked",
            "risk": risk
        }

    return {
        "status": "allowed",
        "risk_score": risk_score,
        "risk_level": risk_level,
        "requires_approval": False,
        "reasons": risk_result["reasons"],
        "ai_risk": risk,
    }
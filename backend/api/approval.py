from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

from backend.services import approval_queue as queue

router = APIRouter(prefix="/api/approval", tags=["approval-queue"])


# ── list pending ──────────────────────────────────────────────────────────────

@router.get("/pending")
def get_pending():
    """Return all queries awaiting human approval."""
    try:
        return {"pending": queue.list_pending()}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


# ── single record ─────────────────────────────────────────────────────────────

@router.get("/{query_id}")
def get_query(query_id: int):
    row = queue.get_by_id(query_id)
    if not row:
        raise HTTPException(status_code=404, detail="Query not found")
    return row


# ── approve ───────────────────────────────────────────────────────────────────

class ReviewRequest(BaseModel):
    reviewed_by: Optional[str] = "admin"


@router.post("/{query_id}/approve")
def approve_query(query_id: int, body: ReviewRequest):
    """Mark a pending query as approved."""
    try:
        row = queue.approve(query_id, reviewed_by=body.reviewed_by or "admin")
        return {"status": "approved", "query": row}
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


# ── reject ────────────────────────────────────────────────────────────────────

@router.post("/{query_id}/reject")
def reject_query(query_id: int, body: ReviewRequest):
    """Mark a pending query as rejected."""
    try:
        row = queue.reject(query_id, reviewed_by=body.reviewed_by or "admin")
        return {"status": "rejected", "query": row}
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))

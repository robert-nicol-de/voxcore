import time

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from backend.services.risk_engine import calculate_risk
from backend.services.query_inspector import block_if_dangerous
from backend.services.query_metrics import log_query
from backend.services.rate_limiter import limiter


router = APIRouter()


class QueryRequest(BaseModel):
    query: str


@router.post("/query")
@limiter.limit("100/minute")
def run_query(request: Request, payload: QueryRequest):
    start = time.perf_counter()
    query = payload.query
    try:
        block_if_dangerous(query)
    except HTTPException:
        execution_time = time.perf_counter() - start
        log_query(
            company_id=1,
            user_id=1,
            query=query,
            execution_time=execution_time,
            risk_level="HIGH",
            blocked=True,
        )
        raise

    risk = calculate_risk(query)
    execution_time = time.perf_counter() - start
    log_query(
        company_id=1,
        user_id=1,
        query=query,
        execution_time=execution_time,
        risk_level=risk.get("status", "LOW"),
        blocked=risk.get("status") == "BLOCKED",
    )

    if risk.get("status") == "BLOCKED":
        return {
            "status": "blocked",
            "risk": risk
        }

    return {
        "status": "allowed",
        "risk": risk
    }
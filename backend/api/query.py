import time

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from backend.services.risk_engine import calculate_risk
from backend.services.query_inspector import block_if_dangerous
from backend.services.query_metrics import log_query
from backend.services.rate_limiter import limiter
from backend.services import approval_queue as queue
from backend.services.policy_engine import apply_policies
from backend.services.sql_analysis import analyze_sql
from backend.services.safety_validator import validate_query_safety
from backend.services.audit_logger import log_audit_event


router = APIRouter()


class QueryRequest(BaseModel):
    query: str
    agent: str = "anonymous"  # identifies the AI agent or user submitting the query
    company_id: str = "default"


@router.post("/query")
@limiter.limit("100/minute")
def run_query(request: Request, payload: QueryRequest):
    start = time.perf_counter()
    query = payload.query

    # 1) Query Inspector: Parse SQL first.
    analysis = analyze_sql(query)

    # 2) Policy Engine enforcement.
    policy_result = apply_policies(payload.company_id, query, analysis=analysis)
    if policy_result["blocked"]:
        execution_time = time.perf_counter() - start
        log_query(
            company_id=1,
            user_id=1,
            query=query,
            execution_time=execution_time,
            risk_level="POLICY_BLOCK",
            blocked=True,
        )
        log_audit_event(
            {
                "company_id": payload.company_id,
                "agent": payload.agent,
                "status": "blocked",
                "stage": "policy_engine",
                "query_type": analysis.get("query_type"),
                "tables": analysis.get("tables"),
                "columns": analysis.get("columns"),
                "query": query,
                "reasons": policy_result["reasons"],
            }
        )
        return {
            "status": "blocked",
            "blocked_by": "policy_engine",
            "message": "Query blocked by VoxCore policy",
            "reasons": policy_result["reasons"],
            "analysis": analysis,
            "original_query": policy_result["original_query"],
            "effective_query": policy_result["rewritten_query"],
        }

    query = policy_result["rewritten_query"]

    # 3) Safety Validation.
    safety = validate_query_safety(query, analysis)
    if not safety["safe"]:
        execution_time = time.perf_counter() - start
        log_query(
            company_id=1,
            user_id=1,
            query=query,
            execution_time=execution_time,
            risk_level="SAFETY_BLOCK",
            blocked=True,
        )
        log_audit_event(
            {
                "company_id": payload.company_id,
                "agent": payload.agent,
                "status": "blocked",
                "stage": "safety_validation",
                "query_type": analysis.get("query_type"),
                "tables": analysis.get("tables"),
                "columns": analysis.get("columns"),
                "query": query,
                "reasons": safety["reasons"],
            }
        )
        return {
            "status": "blocked",
            "blocked_by": "safety_validation",
            "message": "Query blocked by VoxCore safety validation",
            "reasons": safety["reasons"],
            "analysis": analysis,
            "original_query": payload.query,
            "effective_query": query,
        }

    # 4) Policy-based approval mode.
    if policy_result.get("requires_approval"):
        execution_time = time.perf_counter() - start
        log_query(
            company_id=1,
            user_id=1,
            query=query,
            execution_time=execution_time,
            risk_level="APPROVAL_REQUIRED",
            blocked=False,
        )
        queued_id: int | None = None
        approval_reasons = policy_result.get("approval_reasons", [])
        try:
            row = queue.submit(
                query_text=query,
                risk_score=70,
                risk_level="APPROVAL_REQUIRED",
                reasons=approval_reasons,
                ai_agent=payload.agent if hasattr(payload, 'agent') else 'anonymous',
            )
            queued_id = row.get("id")
        except Exception as _queue_err:
            print(f"[!] Approval queue insert failed: {_queue_err}")

        log_audit_event(
            {
                "company_id": payload.company_id,
                "agent": payload.agent,
                "status": "approval_required",
                "stage": "policy_engine",
                "query_type": analysis.get("query_type"),
                "tables": analysis.get("tables"),
                "columns": analysis.get("columns"),
                "query": query,
                "reasons": approval_reasons,
                "queue_id": queued_id,
            }
        )
        return {
            "status": "approval_required",
            "queue_id": queued_id,
            "requires_approval": True,
            "message": "AI query pending approval",
            "reasons": approval_reasons,
            "analysis": analysis,
            "original_query": payload.query,
            "effective_query": query,
        }

    # 5) Additional risk scoring + optional approval queue.
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
        log_audit_event(
            {
                "company_id": payload.company_id,
                "agent": payload.agent,
                "status": "blocked",
                "stage": "query_inspector",
                "query_type": analysis.get("query_type"),
                "tables": analysis.get("tables"),
                "columns": analysis.get("columns"),
                "query": query,
                "reasons": ["Critical risk detected by query inspector"],
            }
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
        log_audit_event(
            {
                "company_id": payload.company_id,
                "agent": payload.agent,
                "status": "approval_required",
                "stage": "risk_engine",
                "query_type": analysis.get("query_type"),
                "tables": analysis.get("tables"),
                "columns": analysis.get("columns"),
                "query": query,
                "reasons": risk_result["reasons"],
                "queue_id": queued_id,
            }
        )
        return {
            "status": "approval_required",
            "queue_id": queued_id,
            "risk_score": risk_score,
            "risk_level": risk_level,
            "requires_approval": True,
            "reasons": risk_result["reasons"],
            "analysis": analysis,
            "original_query": payload.query,
            "effective_query": query,
            "message": "Query held for admin review. Check /api/approval/pending.",
        }

    # 6) Database execution simulation/risk stage.
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
        log_audit_event(
            {
                "company_id": payload.company_id,
                "agent": payload.agent,
                "status": "blocked",
                "stage": "execution_guard",
                "query_type": analysis.get("query_type"),
                "tables": analysis.get("tables"),
                "columns": analysis.get("columns"),
                "query": query,
                "reasons": ["Execution guard blocked query"],
            }
        )
        return {
            "status": "blocked",
            "analysis": analysis,
            "risk": risk
        }

    log_audit_event(
        {
            "company_id": payload.company_id,
            "agent": payload.agent,
            "status": "allowed",
            "stage": "execution",
            "query_type": analysis.get("query_type"),
            "tables": analysis.get("tables"),
            "columns": analysis.get("columns"),
            "query": query,
            "reasons": risk_result["reasons"],
        }
    )

    return {
        "status": "allowed",
        "company_id": payload.company_id,
        "analysis": analysis,
        "risk_score": risk_score,
        "risk_level": risk_level,
        "requires_approval": False,
        "reasons": risk_result["reasons"],
        "ai_risk": risk,
        "original_query": payload.query,
        "effective_query": query,
    }
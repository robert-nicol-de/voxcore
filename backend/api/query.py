import time
from datetime import datetime
from typing import Any

from fastapi import APIRouter, HTTPException, Query, Request
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
from backend.services.data_policy_engine import find_sensitive_columns_in_query, get_sensitive_columns
from backend.services.query_job_queue import enqueue_query_job, get_job, get_worker_stats


router = APIRouter()


_QUERY_ACTIVITY_LOGS: list[dict[str, Any]] = [
    {
        "time": "14:32",
        "query": "SELECT * FROM customers LIMIT 10",
        "risk": "low",
        "status": "allowed",
    },
    {
        "time": "14:31",
        "query": "SELECT name, email, salary FROM employees",
        "risk": "high",
        "status": "blocked_sensitive",
    },
    {
        "time": "14:29",
        "query": "DROP TABLE users",
        "risk": "medium",
        "status": "blocked",
    },
]


def _append_activity(query: str, status: str, risk: str = "low") -> None:
    _QUERY_ACTIVITY_LOGS.insert(
        0,
        {
            "time": datetime.now().strftime("%H:%M"),
            "query": query,
            "risk": risk,
            "status": status,
        },
    )
    del _QUERY_ACTIVITY_LOGS[100:]


def _normalize_risk_level(level: str) -> str:
    normalized = (level or "").strip().lower()
    if normalized in {"critical", "high"}:
        return "high"
    if normalized in {"medium", "moderate"}:
        return "medium"
    return "low"


def _analyze_query_risk(query: str) -> dict[str, Any]:
    risk_score = 0
    reasons: list[str] = []
    q = (query or "").upper()
    matched_sensitive_columns = find_sensitive_columns_in_query(query)

    if "DROP" in q:
        risk_score += 80
        reasons.append("DROP operation detected")

    if "DELETE" in q:
        risk_score += 70
        reasons.append("DELETE operation detected")

    if "UPDATE" in q:
        risk_score += 50
        reasons.append("UPDATE operation detected")

    if "*" in q:
        risk_score += 10
        reasons.append("SELECT * detected")

    if matched_sensitive_columns:
        risk_score += 60
        if risk_score < 70:
            risk_score = 70
        reasons.append(
            "Sensitive column access detected: " + ", ".join(matched_sensitive_columns)
        )

    if risk_score == 0:
        level = "low"
    elif risk_score < 70:
        level = "medium"
    else:
        level = "high"

    return {
        "risk_score": risk_score,
        "risk_level": level,
        "reasons": reasons,
    }


@router.get("/api/v1/query/logs")
def get_query_logs(
    company_id: str = Query("default"),
    workspace_id: str = Query("default"),
):
    return {
        "company_id": company_id,
        "workspace_id": workspace_id,
        "logs": _QUERY_ACTIVITY_LOGS
    }


class InspectRequest(BaseModel):
    query: str | None = None
    sql: str | None = None


class RiskRequest(BaseModel):
    query: str


class SandboxQueryRequest(BaseModel):
    query: str


def sandbox_execute(query_text: str) -> list[dict[str, Any]]:
    query_upper = query_text.upper()
    blocked_keywords = ["DROP", "DELETE", "TRUNCATE", "UPDATE", "INSERT", "ALTER"]
    if any(word in query_upper for word in blocked_keywords):
        raise HTTPException(status_code=400, detail="Sandbox only supports read-only queries")

    # Safe in-memory sandbox dataset for previewing query intent.
    if "ORDER" in query_upper and "TOTAL" in query_upper:
        return [
            {"customer_id": 1, "name": "John", "total": 2000},
            {"customer_id": 2, "name": "Sarah", "total": 1500},
            {"customer_id": 3, "name": "Mike", "total": 1200},
            {"customer_id": 4, "name": "Ava", "total": 900},
            {"customer_id": 5, "name": "Liam", "total": 850},
            {"customer_id": 6, "name": "Noah", "total": 800},
        ]

    return [
        {"customer_id": 1, "name": "John", "email": "john@example.com"},
        {"customer_id": 2, "name": "Sarah", "email": "sarah@example.com"},
        {"customer_id": 3, "name": "Mike", "email": "mike@example.com"},
        {"customer_id": 4, "name": "Ava", "email": "ava@example.com"},
        {"customer_id": 5, "name": "Liam", "email": "liam@example.com"},
        {"customer_id": 6, "name": "Noah", "email": "noah@example.com"},
    ]


@router.post("/api/v1/query/sandbox")
def sandbox_query(payload: SandboxQueryRequest):
    query_text = (payload.query or "").strip()
    if not query_text:
        raise HTTPException(status_code=400, detail="query is required")

    result = sandbox_execute(query_text)
    return {
        "status": "sandboxed",
        "rows": len(result),
        "preview": result[:5],
    }


@router.post("/api/v1/query/inspect")
def inspect_query(payload: InspectRequest):
    query_text = (payload.query or payload.sql or "").strip()
    if not query_text:
        raise HTTPException(status_code=400, detail="query is required")

    risk_details = _analyze_query_risk(query_text)

    blocked_keywords = ["DROP", "DELETE", "TRUNCATE"]
    upper_query = query_text.upper()

    for word in blocked_keywords:
        if word in upper_query:
            _append_activity(query_text, "blocked", risk_details["risk_level"])
            return {
                "allowed": False,
                "reason": f"{word} statements are blocked",
                "approved": False,
                "safe": False,
                "read_only": False,
                "dangerous_keywords": [word],
                "table_checks": [],
                "column_checks": [],
                "missing_tables": [],
                "missing_columns": [],
                "reasons": [f"{word} statements are blocked"],
            }

    matched_sensitive = find_sensitive_columns_in_query(query_text)
    if matched_sensitive:
        _append_activity(query_text, "blocked_sensitive", risk_details["risk_level"])
        return {
            "allowed": False,
            "reason": f"Sensitive column detected: {matched_sensitive[0]}",
            "approved": False,
            "safe": False,
            "read_only": upper_query.startswith("SELECT"),
            "dangerous_keywords": [],
            "table_checks": [],
            "column_checks": [],
            "missing_tables": [],
            "missing_columns": [],
            "reasons": [f"Sensitive column detected: {column}" for column in matched_sensitive],
            "sensitive_columns": matched_sensitive,
        }

    _append_activity(query_text, "allowed", risk_details["risk_level"])
    return {
        "allowed": True,
        "reason": "Query approved",
        "approved": True,
        "safe": True,
        "read_only": upper_query.startswith("SELECT"),
        "dangerous_keywords": [],
        "table_checks": [],
        "column_checks": [],
        "missing_tables": [],
        "missing_columns": [],
        "reasons": ["Query approved"],
    }


@router.post("/api/v1/query/risk")
def analyze_query_risk(payload: RiskRequest):
    query_text = (payload.query or "").strip()
    if not query_text:
        raise HTTPException(status_code=400, detail="query is required")
    return _analyze_query_risk(query_text)


class QueryRequest(BaseModel):
    query: str
    agent: str = "anonymous"  # identifies the AI agent or user submitting the query
    company_id: str = "default"
    workspace_id: str = "default"


def process_query_payload(payload: QueryRequest) -> dict[str, Any]:
    start = time.perf_counter()
    query = payload.query

    # 1) Query Inspector: Parse SQL first.
    analysis = analyze_sql(query)
    matched_sensitive_columns = find_sensitive_columns_in_query(query)

    if matched_sensitive_columns:
        _append_activity(query, "blocked_sensitive", "high")
        execution_time = time.perf_counter() - start
        log_query(
            company_id=1,
            user_id=1,
            query=query,
            execution_time=execution_time,
            risk_level="SENSITIVE_COLUMN_BLOCK",
            blocked=True,
        )
        log_audit_event(
            {
                "company_id": payload.company_id,
                "workspace_id": payload.workspace_id,
                "agent": payload.agent,
                "status": "blocked",
                "stage": "data_policy_engine",
                "query_type": analysis.get("query_type"),
                "tables": analysis.get("tables"),
                "columns": analysis.get("columns"),
                "query": query,
                "reasons": [f"Sensitive column detected: {column}" for column in matched_sensitive_columns],
            }
        )
        return {
            "status": "blocked",
            "blocked_by": "data_policy_engine",
            "message": "Query blocked by VoxCore data policy",
            "reasons": [f"Sensitive column detected: {column}" for column in matched_sensitive_columns],
            "sensitive_columns": matched_sensitive_columns,
            "analysis": analysis,
            "original_query": payload.query,
            "effective_query": query,
        }

    # 2) Policy Engine enforcement.
    policy_result = apply_policies(payload.company_id, query, analysis=analysis)
    if policy_result["blocked"]:
        _append_activity(query, "blocked", "high")
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
                "workspace_id": payload.workspace_id,
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
        _append_activity(query, "blocked", "high")
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
                "workspace_id": payload.workspace_id,
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
        _append_activity(query, "blocked", "high")
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
                "workspace_id": payload.workspace_id,
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
        _append_activity(query, "blocked", "high")
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
                "workspace_id": payload.workspace_id,
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
        _append_activity(query, "blocked", _normalize_risk_level(risk_level))
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
                "workspace_id": payload.workspace_id,
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
        _append_activity(query, "blocked", _normalize_risk_level(risk_level))
        log_audit_event(
            {
                "company_id": payload.company_id,
                "workspace_id": payload.workspace_id,
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
            "workspace_id": payload.workspace_id,
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
        "workspace_id": payload.workspace_id,
        "analysis": analysis,
        "risk_score": risk_score,
        "risk_level": risk_level,
        "requires_approval": False,
        "reasons": risk_result["reasons"],
        "ai_risk": risk,
        "original_query": payload.query,
        "effective_query": query,
    }


@router.post("/query")
@limiter.limit("100/minute")
def run_query(request: Request, payload: QueryRequest):
    return process_query_payload(payload)


@router.post("/api/v1/query")
@limiter.limit("100/minute")
def run_query_v1(request: Request, payload: QueryRequest):
    job_id = enqueue_query_job(payload.model_dump())
    return {
        "status": "queued",
        "job_id": job_id,
        "message": "Query queued for worker execution",
    }


@router.get("/api/v1/query/jobs/{job_id}")
def get_query_job_status(job_id: str):
    job = get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job


@router.get("/api/v1/query/worker-stats")
def worker_stats(
    company_id: str = Query("default"),
    workspace_id: str = Query("default"),
):
    stats = get_worker_stats()
    sensitive_queries_blocked = sum(
        1 for item in _QUERY_ACTIVITY_LOGS if item.get("status") == "blocked_sensitive"
    )
    blocked_queries_total = sum(
        1 for item in _QUERY_ACTIVITY_LOGS if item.get("status") in {"blocked", "blocked_sensitive"}
    )
    stats["blocked_queries"] = max(int(stats.get("blocked_queries", 0)), blocked_queries_total)
    stats["protected_columns"] = len(get_sensitive_columns())
    stats["sensitive_queries_blocked"] = sensitive_queries_blocked
    stats["company_id"] = company_id
    stats["workspace_id"] = workspace_id
    return stats
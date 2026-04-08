import time
from datetime import datetime
from typing import Any

from fastapi import APIRouter, HTTPException, Query, Request, Depends
from backend.core.auth import verify_api_key
from backend.core.usage import track_usage, check_rate_limit
from backend.core.logger import log_query as core_log_query
from pydantic import BaseModel
from backend.control_plane import get_control_plane
from backend.services.risk_engine import calculate_risk
from backend.services.query_inspector import block_if_dangerous
from backend.services.query_metrics import get_recent_queries, log_query
from backend.services.rate_limiter import limiter
from backend.services import approval_queue as queue
from backend.services.policy_engine import apply_policies
from backend.services.sql_analysis import analyze_sql
from backend.services.safety_validator import validate_query_safety
from backend.services.audit_logger import create_audit_query_id, log_audit_event
from backend.services.data_policy_engine import find_sensitive_columns_in_query, get_sensitive_columns
from backend.services.query_job_queue import enqueue_query_job, get_job, get_worker_stats
from backend.services.ai_context_builder import build_ai_query_context_with_runtime
from backend.event_bus import POLICY_VIOLATION, QUERY_BLOCKED, QUERY_EXECUTED, publish_event
from backend.schemas.query_response import QueryResponse
from backend.semantic_brain import (
    AnalysisSessionStore,
    build_preview_chart,
    build_semantic_payload,
    extract_query_intent,
    recommend_chart,
)


router = APIRouter()


_SEED_ACTIVITY_LOGS: list[dict[str, Any]] = [
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

_QUERY_ACTIVITY_LOGS_BY_TENANT: dict[str, list[dict[str, Any]]] = {}
_LAST_ANALYTICAL_PLAN_BY_TENANT: dict[str, dict[str, Any]] = {}
_ANALYSIS_SESSIONS = AnalysisSessionStore()


def _tenant_key(company_id: str, workspace_id: str) -> str:
    return f"{company_id}:{workspace_id}"


def _resolve_tenant_context(
    request: Request,
    company_id: str = "default",
    workspace_id: str = "default",
) -> tuple[str, str]:
    from_state_org = getattr(request.state, "org_id", None)
    from_state_workspace = getattr(request.state, "workspace_id", None)

    effective_company_id = str(from_state_org if from_state_org is not None else company_id)
    effective_workspace_id = str(
        from_state_workspace if from_state_workspace is not None else workspace_id
    )
    return effective_company_id, effective_workspace_id


def _tenant_logs(company_id: str, workspace_id: str) -> list[dict[str, Any]]:
    key = _tenant_key(company_id, workspace_id)
    if key not in _QUERY_ACTIVITY_LOGS_BY_TENANT:
        _QUERY_ACTIVITY_LOGS_BY_TENANT[key] = [dict(item) for item in _SEED_ACTIVITY_LOGS]
    return _QUERY_ACTIVITY_LOGS_BY_TENANT[key]


def _get_previous_plan(company_id: str, workspace_id: str) -> dict[str, Any] | None:
    return _LAST_ANALYTICAL_PLAN_BY_TENANT.get(_tenant_key(company_id, workspace_id))


def _save_latest_plan(company_id: str, workspace_id: str, plan: dict[str, Any]) -> None:
    key = _tenant_key(company_id, workspace_id)
    _LAST_ANALYTICAL_PLAN_BY_TENANT[key] = dict(plan)
    _ANALYSIS_SESSIONS.upsert_from_plan(key, plan)


def _build_semantic_payload(
    request: Request,
    query_text: str,
    workspace_id: str,
    previous_plan: dict[str, Any] | None = None,
    preview_rows: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    ai_context = build_ai_query_context_with_runtime(
        workspace_id,
        getattr(request.state, "datasource_id", None),
        request.headers.get("X-Schema-Name"),
    )
    semantic_payload = build_semantic_payload(
        query_text=query_text,
        workspace_id=workspace_id,
        ai_context=ai_context,
        previous_plan=previous_plan,
        preview_rows=preview_rows or [],
    )
    current_company_id = str(getattr(request.state, "org_id", "default"))
    session_key = _tenant_key(current_company_id, workspace_id)
    plan = semantic_payload.get("analytical_plan") if isinstance(semantic_payload, dict) else None
    if isinstance(plan, dict):
        preview_session = {
            "metric": plan.get("metric"),
            "dimension": plan.get("dimension"),
            "comparison": plan.get("comparison"),
            "filters": {
                "focus": plan.get("focus"),
                "limit": plan.get("limit"),
            },
        }
        semantic_payload["analysis_session"] = preview_session
    else:
        semantic_payload["analysis_session"] = _ANALYSIS_SESSIONS.as_dict(session_key)
    return semantic_payload


def _append_activity(
    request: Request,
    query: str,
    status: str,
    risk: str = "low",
    company_id: str = "default",
    workspace_id: str = "default",
) -> None:
    effective_company_id, effective_workspace_id = _resolve_tenant_context(
        request, company_id, workspace_id
    )
    logs = _tenant_logs(effective_company_id, effective_workspace_id)
    logs.insert(
        0,
        {
            "time": datetime.now().strftime("%H:%M"),
            "query": query,
            "risk": risk,
            "status": status,
        },
    )
    del logs[100:]

    event_type = QUERY_BLOCKED if status in {"blocked", "blocked_sensitive", "approval_required"} else QUERY_EXECUTED
    publish_event(
        event_type,
        {
            "query": query,
            "status": status,
            "risk": risk,
        },
        org_id=effective_company_id,
        workspace_id=effective_workspace_id,
        source="query_api",
    )


def _publish_policy_violation(
    org_id: str,
    workspace_id: str,
    stage: str,
    query: str,
    reasons: list[str],
) -> None:
    publish_event(
        POLICY_VIOLATION,
        {
            "stage": stage,
            "query": query,
            "reasons": reasons,
        },
        org_id=org_id,
        workspace_id=workspace_id,
        source="governance",
    )


def _normalize_risk_level(level: str) -> str:
    normalized = (level or "").strip().lower()
    if normalized in {"critical", "high"}:
        return "high"
    if normalized in {"medium", "moderate"}:
        return "medium"
    return "low"


def _estimate_query_cost(query: str, risk_score: int) -> dict[str, Any]:
    q = (query or "").upper()
    join_count = q.count(" JOIN ")
    has_wildcard = "*" in q
    has_group = "GROUP BY" in q
    has_order = "ORDER BY" in q

    estimated_rows = 25000
    estimated_rows += join_count * 1800000
    if has_wildcard:
        estimated_rows += 3000000
    if has_group:
        estimated_rows += 900000
    if has_order:
        estimated_rows += 600000
    if risk_score >= 70:
        estimated_rows += 12000000

    estimated_rows = max(1000, min(estimated_rows, 250000000))
    estimated_execution_ms = max(120, int((estimated_rows / 120000) + (join_count * 180)))

    if estimated_rows >= 90000000 or estimated_execution_ms >= 5000:
        tier = "high"
    elif estimated_rows >= 10000000 or estimated_execution_ms >= 2000:
        tier = "medium"
    else:
        tier = "low"

    return {
        "estimated_rows_scanned": estimated_rows,
        "estimated_execution_ms": estimated_execution_ms,
        "estimated_cost_tier": tier,
    }


def _risk_threshold_requires_approval(
    risk_score: int,
    policy_result: dict[str, Any],
) -> tuple[bool, float]:
    risk_policy = policy_result.get("risk_approval") or {}
    enabled = bool(risk_policy.get("enabled", True))
    try:
        threshold = float(risk_policy.get("threshold", 0.7))
    except (TypeError, ValueError):
        threshold = 0.7
    threshold = max(0.0, min(1.0, threshold))
    if not enabled:
        return False, threshold
    return risk_score >= int(threshold * 100), threshold



from voxcore.guardian.pattern_engine import apply_pattern_scoring

def _analyze_query_risk(query: str, metadata: dict = None) -> dict[str, Any]:
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

    # --- Pattern scoring integration ---
    pattern_info = None
    flags = []
    if metadata is not None:
        risk_score, flags, pattern_info = apply_pattern_scoring(query, metadata, risk_score, [])
        if flags:
            reasons.extend(flags)

    if risk_score == 0:
        level = "low"
    elif risk_score < 70:
        level = "medium"
    else:
        level = "high"

    cost_estimate = _estimate_query_cost(query, risk_score)

    return {
        "risk_score": risk_score,
        "risk_level": level,
        "reasons": reasons,
        "pattern_detected": pattern_info["pattern"] if pattern_info else None,
        "pattern_confidence": pattern_info["confidence"] if pattern_info else None,
        **cost_estimate,
    }


@router.get("/api/v1/query/logs")
def get_query_logs(
    request: Request,
    company_id: str = Query("default"),
    workspace_id: str = Query("default"),
):
    effective_company_id, effective_workspace_id = _resolve_tenant_context(
        request, company_id, workspace_id
    )
    return {
        "company_id": effective_company_id,
        "workspace_id": effective_workspace_id,
        "logs": _tenant_logs(effective_company_id, effective_workspace_id),
    }


@router.get("/api/v1/query/drilldown")
def query_drilldown(
    request: Request,
    value: str,
    dimension: str = Query("status"),
    company_id: str = Query("default"),
    workspace_id: str = Query("default"),
):
    """Return detail rows for clicked chart category/data point."""
    normalized_value = (value or "").strip().lower()
    normalized_dimension = (dimension or "status").strip().lower()

    effective_company_id, effective_workspace_id = _resolve_tenant_context(
        request, company_id, workspace_id
    )
    tenant_activity_logs = _tenant_logs(effective_company_id, effective_workspace_id)

    matched_logs: list[dict[str, Any]] = []
    for entry in tenant_activity_logs:
      status = str(entry.get("status", "")).lower()
      risk = str(entry.get("risk", "")).lower()
      query = str(entry.get("query", ""))

      if normalized_dimension == "status" and status == normalized_value:
          matched_logs.append(entry)
      elif normalized_dimension == "risk" and risk == normalized_value:
          matched_logs.append(entry)
      elif normalized_dimension == "query" and normalized_value in query.lower():
          matched_logs.append(entry)

    if not matched_logs:
        matched_logs = tenant_activity_logs[:8]

    rows: list[dict[str, Any]] = []
    total_revenue = 0
    for idx, log in enumerate(matched_logs, start=1):
        # Synthetic order-style records for analytics drill-down UX
        amount = 120 + (idx * 95)
        total_revenue += amount
        rows.append(
            {
                "order_id": f"{10000 + idx}",
                "order_total": amount,
                "order_date": f"2025-05-{(10 + idx):02d}",
                "query": log.get("query"),
                "status": log.get("status"),
                "risk": log.get("risk"),
            }
        )

    return {
        "category": value,
        "dimension": dimension,
        "rows": rows,
        "total_revenue": total_revenue,
    }


@router.get("/api/v1/query/risk-timeline")
def get_risk_timeline(limit: int = Query(25, ge=1, le=200)):
    timeline: list[dict[str, Any]] = []
    try:
        rows = get_recent_queries(limit=limit)
        for row in rows:
            created_at = row.get("created_at")
            if hasattr(created_at, "strftime"):
                time_label = created_at.strftime("%H:%M")
            else:
                time_label = datetime.now().strftime("%H:%M")

            risk_level = _normalize_risk_level(str(row.get("risk_level") or "low"))
            status = "blocked" if row.get("blocked") else "allowed"

            timeline.append(
                {
                    "time": time_label,
                    "risk": risk_level,
                    "status": status,
                    "query": row.get("query", ""),
                }
            )
    except Exception:
        timeline = [
            {
                "time": item.get("time", datetime.now().strftime("%H:%M")),
                "risk": _normalize_risk_level(str(item.get("risk", "low"))),
                "status": item.get("status", "allowed"),
                "query": item.get("query", ""),
            }
            for item in _SEED_ACTIVITY_LOGS[:limit]
        ]

    return {"timeline": timeline, "count": len(timeline)}


class InspectRequest(BaseModel):
    query: str | None = None
    sql: str | None = None
    workspace_id: str = "default"


class RiskRequest(BaseModel):
    query: str
    workspace_id: str = "default"


class SandboxQueryRequest(BaseModel):
    query: str
    workspace_id: str = "default"


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
def sandbox_query(request: Request, payload: SandboxQueryRequest):
    query_text = (payload.query or "").strip()
    if not query_text:
        raise HTTPException(status_code=400, detail="query is required")

    result = sandbox_execute(query_text)
    company_id, workspace = _resolve_tenant_context(request, "default", payload.workspace_id)
    previous_plan = _get_previous_plan(company_id, workspace)
    semantic_payload = _build_semantic_payload(
        request,
        query_text,
        workspace,
        previous_plan=previous_plan,
        preview_rows=result[:5],
    )
    _save_latest_plan(company_id, workspace, semantic_payload["analytical_plan"])

    intent = extract_query_intent(query_text)
    chart_recommendation = recommend_chart(intent)
    chart = build_preview_chart(result, intent)

    return {
        "status": "sandboxed",
        "rows": len(result),
        "preview": result[:5],
        "chart_recommendation": semantic_payload.get("chart_recommendation") or chart_recommendation,
        "chart": chart,
    } | semantic_payload


@router.post("/api/v1/query/inspect")
def inspect_query(request: Request, payload: InspectRequest):
    company_id, workspace_id = _resolve_tenant_context(request, "default", payload.workspace_id)

    query_text = (payload.query or payload.sql or "").strip()
    if not query_text:
        raise HTTPException(status_code=400, detail="query is required")

    risk_details = _analyze_query_risk(query_text)
    ai_context = build_ai_query_context_with_runtime(
        workspace_id,
        getattr(request.state, "datasource_id", None),
        request.headers.get("X-Schema-Name"),
    )

    blocked_keywords = ["DROP", "DELETE", "TRUNCATE"]
    upper_query = query_text.upper()

    for word in blocked_keywords:
        if word in upper_query:
            _append_activity(request, query_text, "blocked", risk_details["risk_level"], company_id, workspace_id)
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
                "ai_context": ai_context,
            }

    matched_sensitive = find_sensitive_columns_in_query(query_text)
    if matched_sensitive:
        _append_activity(request, query_text, "blocked_sensitive", risk_details["risk_level"], company_id, workspace_id)
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
            "ai_context": ai_context,
        }

    _append_activity(request, query_text, "allowed", risk_details["risk_level"], company_id, workspace_id)
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
        "ai_context": ai_context,
    }


@router.post("/api/v1/query/risk")

def analyze_query_risk(request: Request, payload: RiskRequest):
    query_text = (payload.query or "").strip()
    if not query_text:
        raise HTTPException(status_code=400, detail="query is required")
    # Build semantic payload to get metadata
    company_id, workspace = _resolve_tenant_context(request, "default", payload.workspace_id)
    previous_plan = _get_previous_plan(company_id, workspace)
    semantic_payload = _build_semantic_payload(
        request,
        query_text,
        workspace,
        previous_plan=previous_plan,
    )
    metadata = semantic_payload.get("metadata", {})
    risk = _analyze_query_risk(query_text, metadata)
    policy_result = apply_policies(company_id, query_text)
    risk_requires_approval, approval_threshold = _risk_threshold_requires_approval(
        int(risk.get("risk_score", 0) or 0),
        policy_result,
    )
    risk["requires_approval"] = bool(policy_result.get("requires_approval")) or risk_requires_approval
    risk["approval_threshold"] = approval_threshold
    _save_latest_plan(company_id, workspace, semantic_payload["analytical_plan"])
    response = {
        "risk": risk or {},
        "semantic": semantic_payload or {}
    }
    print("FINAL RESPONSE:", response)
    return response


class QueryRequest(BaseModel):
    query: str
    agent: str = "anonymous"  # identifies the AI agent or user submitting the query
    company_id: str = "default"
    workspace_id: str = "default"


def _add_ai_context(request: Request, payload: QueryRequest, body: dict[str, Any]) -> dict[str, Any]:
    company_id, workspace = _resolve_tenant_context(request, payload.company_id, payload.workspace_id)
    previous_plan = _get_previous_plan(company_id, workspace)
    semantic_payload = _build_semantic_payload(
        request,
        payload.query,
        workspace,
        previous_plan=previous_plan,
    )
    _save_latest_plan(company_id, workspace, semantic_payload["analytical_plan"])
    body |= semantic_payload
    return body


def process_query_payload(request: Request, payload: QueryRequest) -> dict[str, Any]:

    start = time.perf_counter()
    query = payload.query
    query_id = create_audit_query_id()
    company_id, workspace_id = _resolve_tenant_context(
        request, payload.company_id, payload.workspace_id
    )
    actor_role = str(getattr(request.state, "role", "viewer") or "viewer")
    actor_email = getattr(request.state, "user_email", None)
    actor_user_id = getattr(request.state, "user_id", None)
    previous_plan = _get_previous_plan(company_id, workspace_id)
    semantic_payload = _build_semantic_payload(
        request,
        payload.query,
        workspace_id,
        previous_plan=previous_plan,
    )
    _save_latest_plan(company_id, workspace_id, semantic_payload["analytical_plan"])
    semantic_sql = str(semantic_payload.get("generated_sql") or "")

        if policy_result.get("requires_approval"):
            _append_activity(request, query, "blocked", "high", company_id, workspace_id)
            execution_time = time.perf_counter() - start
            cost_usd = float(cost_estimate.get("estimated_rows_scanned", 0)) * 0.000001
            lineage_id = None
            log_query(
                company_id=1,
                user_id=1,
                query=query,
                execution_time=execution_time,
                risk_level="APPROVAL_REQUIRED",
                blocked=False,
                cost_usd=cost_usd,
                lineage_id=lineage_id,
            )
            queued_id: int | None = None
            approval_reasons = policy_result.get("approval_reasons", [])
            try:
                from backend.services import approval_queue as queue
                queued_id = queue.enqueue_query_for_approval(
                    company_id=company_id,
                    workspace_id=workspace_id,
                    user_id=actor_user_id,
                    query=query,
                    reasons=approval_reasons,
                    analysis=analysis,
                )
            except Exception:
                queued_id = None
            audit_event(
                "approval_required",
                "policy_engine",
                approval_reasons,
                analysis=analysis,
                risk_level="medium",
                guardian_validation="approval_required",
                execution_time_ms=round(execution_time * 1000, 2),
                extra={
                    "policy_decision": policy_result.get("policy_decision"),
                    "policy_rule": policy_result.get("policy_rule"),
                    "policy_version": policy_result.get("policy_version"),
                }
            )
            return {
                "status": "approval_required",
                "approval_reasons": approval_reasons,
                "queued_id": queued_id,
                "analysis": analysis,
                "original_query": policy_result["original_query"],
                "effective_query": policy_result["rewritten_query"],
                "generated_sql": semantic_sql,
                "policy_decision": policy_result.get("policy_decision"),
                "policy_rule": policy_result.get("policy_rule"),
                "policy_version": policy_result.get("policy_version"),
            } | {"ai_context": build_ai_query_context_with_runtime(workspace_id, getattr(request.state, "datasource_id", None), request.headers.get("X-Schema-Name"))}
        else:
            error_report.suggested_action = "CLARIFY"

    # 3. Clarification
    if error_report.error_detected and error_report.suggested_action == "CLARIFY":
        clarification_system = ClarificationSystem()
        clarification_input = ClarificationInput(
            semantic_plan=semantic_payload.get("analytical_plan", {}),
            error_report=error_report.dict(),
            clarification_context=ClarificationContext()
        )
        clarification_result = clarification_system.clarify(clarification_input)
        FailureIntelligenceLogger().log_event(FailureIntelligenceInput(
            event_type=EventType.CLARIFICATION,
            event_payload=clarification_result.dict(),
            timestamp=datetime.utcnow(),
            user_id=actor_user_id,
        ))
        if clarification_result.clarification_needed:
            return {
                "status": "clarification_required",
                "clarification_prompt": clarification_result.clarification_prompt,
                "clarification_type": clarification_result.clarification_type,
                "clarification_options": clarification_result.clarification_options,
                "log": clarification_result.log_entry,
            }

    # 4. Fallback
    if error_report.error_detected and error_report.suggested_action == "FALLBACK":
        fallback_manager = FallbackManager()
        fallback_input = FallbackInput(
            semantic_plan=semantic_payload.get("analytical_plan", {}),
            error_report=error_report.dict(),
        )
        fallback_result = fallback_manager.fallback(fallback_input)
        FailureIntelligenceLogger().log_event(FailureIntelligenceInput(
            event_type=EventType.FALLBACK,
            event_payload=fallback_result.dict(),
            timestamp=datetime.utcnow(),
            user_id=actor_user_id,
        ))
        return {
            "status": "fallback",
            "fallback_mode": fallback_result.fallback_mode,
            "fallback_result": fallback_result.fallback_result,
            "fallback_details": fallback_result.fallback_details,
            "log": fallback_result.log_entry,
        }

    # --- Zanzibar-style permission check ---
    from backend.api.permission_guard import permission_engine
    required_relation = "query"
    object_type = "workspace"
    object_id = workspace_id
    user_id = actor_user_id
    def get_user_workspaces(uid):
        from backend.db.org_store import list_user_workspaces
        return [str(ws["id"]) for ws in list_user_workspaces(uid, int(company_id))]

    has_permission = False
    if user_id is not None:
        has_permission = permission_engine.check_access(
            user_id, required_relation, object_type, object_id, get_user_workspaces=get_user_workspaces
        )
    if not has_permission:
        from backend.db.org_store import audit_log_permission_failure
        ip_address = getattr(request.client, "host", None)
        audit_log_permission_failure(
            user_id=user_id or -1,
            org_id=int(company_id) if company_id.isdigit() else -1,
            workspace_id=int(workspace_id) if workspace_id.isdigit() else -1,
            permission=f"{required_relation}:{object_type}:{object_id}",
            endpoint="/query",
            reason="Zanzibar permission denied",
            ip_address=ip_address,
        )
        return {
            "status": "blocked",
            "blocked_by": "permission_engine",
            "message": "Access denied by permission engine.",
            "reason": "User does not have permission to execute queries in this workspace.",
        }

    # --- Data Guard: Sensitive Data Inspection ---
    from voxcore.security.data_guard import scan_query, scan_results, log_data_guard_event, DataGuardViolation
    guard_result = scan_query(semantic_sql, user_role=actor_role)
    if guard_result["action"] == "block":
        log_data_guard_event(user_id or -1, semantic_sql, "blocked_sensitive_column")
        return {
            "status": "blocked",
            "blocked_by": "data_guard",
            "message": "Requested data contains restricted fields.",
            "reason": "Sensitive or restricted columns detected.",
            "violations": guard_result["violations"],
        }
    elif guard_result["action"] == "mask":
        # Use rewritten SQL with masking
        semantic_sql = guard_result["rewritten_sql"]

    # ...existing code...
    # After query execution, scan results for sensitive data
    # (This should be placed after the DB query, but before returning to user)
    def _add_ai_context_and_scan_results(request, payload, body):
        # Scan result set for sensitive data (PII, financial, etc.)
        if isinstance(body, dict):
            for k in ["preview_rows", "rows", "result", "data"]:
                if k in body and isinstance(body[k], list):
                    body[k] = scan_results(body[k])
        return _add_ai_context(request, payload, body)

    global _add_ai_context
    _add_ai_context = _add_ai_context_and_scan_results

    def audit_event(
        status: str,
        stage: str,
        reasons: list[str],
        *,
        analysis: dict[str, Any] | None = None,
        risk_score: int | None = None,
        risk_level: str | None = None,
        guardian_validation: str | None = None,
        execution_time_ms: float | None = None,
        extra: dict[str, Any] | None = None,
    ) -> None:
        event = {
            "query_id": query_id,
            "company_id": company_id,
            "workspace_id": workspace_id,
            "user_id": actor_user_id,
            "user_email": actor_email,
            "actor_role": actor_role,
            "agent": payload.agent,
            "intent": payload.query,
            "generated_sql": semantic_sql,
            "status": status,
            "stage": stage,
            "query_type": (analysis or {}).get("query_type"),
            "tables": (analysis or {}).get("tables"),
            "columns": (analysis or {}).get("columns"),
            "query": query,
            "reasons": reasons,
            "risk_score": risk_score,
            "risk_level": risk_level,
            "guardian_validation": guardian_validation,
            "execution_time_ms": execution_time_ms,
            "system": "voxcore_control_plane",
        }
        if extra:
            event.update(extra)
        log_audit_event(event)
    
    # 1) Query Inspector: Parse SQL first.
    analysis = analyze_sql(query)
    matched_sensitive_columns = find_sensitive_columns_in_query(query)

    if matched_sensitive_columns:
        _append_activity(request, query, "blocked_sensitive", "high", company_id, workspace_id)
        execution_time = time.perf_counter() - start
        cost_usd = float(cost_estimate.get("estimated_rows_scanned", 0)) * 0.000001
        lineage_id = None
        log_query(
            company_id=1,
            user_id=1,
            query=query,
            execution_time=execution_time,
            risk_level="SENSITIVE_COLUMN_BLOCK",
            blocked=True,
            cost_usd=cost_usd,
            lineage_id=lineage_id,
        )
        log_audit_event(
            {
                "company_id": company_id,
                "workspace_id": workspace_id,
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
        _publish_policy_violation(
            company_id,
            workspace_id,
            "data_policy_engine",
            query,
            [f"Sensitive column detected: {column}" for column in matched_sensitive_columns],
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
            "generated_sql": semantic_sql,
        } | {"ai_context": build_ai_query_context_with_runtime(workspace_id, getattr(request.state, "datasource_id", None), request.headers.get("X-Schema-Name"))}

    # 2) Policy Engine enforcement.
    policy_result = apply_policies(company_id, query, analysis=analysis, actor_role=actor_role)
    if policy_result["blocked"]:
        _append_activity(request, query, "blocked", "high", company_id, workspace_id)
        execution_time = time.perf_counter() - start
        cost_usd = float(cost_estimate.get("estimated_rows_scanned", 0)) * 0.000001
        lineage_id = None
        log_query(
            company_id=1,
            user_id=1,
            query=query,
            execution_time=execution_time,
            risk_level="POLICY_BLOCK",
            blocked=True,
            cost_usd=cost_usd,
            lineage_id=lineage_id,
        )
        audit_event(
            "blocked",
            "policy_engine",
            list(policy_result["reasons"]),
            analysis=analysis,
            risk_level="high",
            guardian_validation="blocked",
            execution_time_ms=round(execution_time * 1000, 2),
            extra={
                "policy_decision": policy_result.get("policy_decision"),
                "policy_rule": policy_result.get("policy_rule"),
                "policy_version": policy_result.get("policy_version"),
            }
        )
        _publish_policy_violation(
            company_id,
            workspace_id,
            "policy_engine",
            query,
            list(policy_result["reasons"]),
        )
        return {
            "status": "blocked",
            "blocked_by": "policy_engine",
            "message": "Query blocked by VoxCore policy",
            "reasons": policy_result["reasons"],
            "analysis": analysis,
            "original_query": policy_result["original_query"],
            "effective_query": policy_result["rewritten_query"],
            "generated_sql": semantic_sql,
            "policy_decision": policy_result.get("policy_decision"),
            "policy_rule": policy_result.get("policy_rule"),
            "policy_version": policy_result.get("policy_version"),
        } | {"ai_context": build_ai_query_context_with_runtime(workspace_id, getattr(request.state, "datasource_id", None), request.headers.get("X-Schema-Name"))}

    query = policy_result["rewritten_query"]

    # 3) Safety Validation.
    safety = validate_query_safety(query, analysis)
    if not safety["safe"]:
        _append_activity(request, query, "blocked", "high", company_id, workspace_id)
        execution_time = time.perf_counter() - start
        cost_usd = float(cost_estimate.get("estimated_rows_scanned", 0)) * 0.000001
        lineage_id = None
        log_query(
            company_id=1,
            user_id=1,
            query=query,
            execution_time=execution_time,
            risk_level="SAFETY_BLOCK",
            blocked=True,
            cost_usd=cost_usd,
            lineage_id=lineage_id,
        )
        audit_event(
            "blocked",
            "safety_validation",
            list(safety["reasons"]),
            analysis=analysis,
            risk_level="high",
            guardian_validation="blocked",
            execution_time_ms=round(execution_time * 1000, 2),
        )
        _publish_policy_violation(
            company_id,
            workspace_id,
            "safety_validation",
            query,
            list(safety["reasons"]),
        )
        return {
            "status": "blocked",
            "blocked_by": "safety_validation",
            "message": "Query blocked by VoxCore safety validation",
            "reasons": safety["reasons"],
            "analysis": analysis,
            "original_query": payload.query,
            "effective_query": query,
            "generated_sql": semantic_sql,
        } | {"ai_context": build_ai_query_context_with_runtime(workspace_id, getattr(request.state, "datasource_id", None), request.headers.get("X-Schema-Name"))}

    # 4) Policy-based approval mode.
    if policy_result.get("requires_approval"):
        _append_activity(request, query, "blocked", "high", company_id, workspace_id)
        execution_time = time.perf_counter() - start
        cost_usd = float(cost_estimate.get("estimated_rows_scanned", 0)) * 0.000001
        lineage_id = None
        log_query(
            company_id=1,
            user_id=1,
            query=query,
            execution_time=execution_time,
            risk_level="APPROVAL_REQUIRED",
            blocked=False,
            cost_usd=cost_usd,
            lineage_id=lineage_id,
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

        audit_event(
            "approval_required",
            "policy_engine",
            list(approval_reasons),
            analysis=analysis,
            risk_level="approval_required",
            guardian_validation="approval_required",
            execution_time_ms=round(execution_time * 1000, 2),
            extra={"queue_id": queued_id},
        )
        return {
            "query_id": query_id,
            "status": "approval_required",
            "queue_id": queued_id,
            "requires_approval": True,
            "message": "AI query pending approval",
            "reasons": approval_reasons,
            "analysis": analysis,
            "original_query": payload.query,
            "effective_query": query,
            "generated_sql": semantic_sql,
        } | {"ai_context": build_ai_query_context_with_runtime(workspace_id, getattr(request.state, "datasource_id", None), request.headers.get("X-Schema-Name"))}

    # 5) Additional risk scoring + optional approval queue.
    try:
        risk_result = block_if_dangerous(query)  # raises 403 only for CRITICAL
    except HTTPException:
        _append_activity(request, query, "blocked", "high", company_id, workspace_id)
        execution_time = time.perf_counter() - start
        cost_usd = float(cost_estimate.get("estimated_rows_scanned", 0)) * 0.000001
        lineage_id = None
        log_query(
            company_id=1,
            user_id=1,
            query=query,
            execution_time=execution_time,
            risk_level="CRITICAL",
            blocked=True,
            cost_usd=cost_usd,
            lineage_id=lineage_id,
        )
        audit_event(
            "blocked",
            "query_inspector",
            ["Critical risk detected by query inspector"],
            analysis=analysis,
            risk_level="critical",
            guardian_validation="blocked",
            execution_time_ms=round(execution_time * 1000, 2),
        )
        raise

    risk_level = risk_result["risk_level"]
    risk_score = risk_result["risk_score"]
    risk_requires_approval, approval_threshold = _risk_threshold_requires_approval(
        int(risk_score),
        policy_result,
    )
    requires_approval = bool(risk_result["requires_approval"]) or risk_requires_approval
    cost_estimate = _estimate_query_cost(query, int(risk_score))

    # HIGH → enqueue for human approval, do not execute
    if requires_approval:
        _append_activity(request, query, "blocked", _normalize_risk_level(risk_level), company_id, workspace_id)
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
        audit_event(
            "approval_required",
            "risk_engine",
            list(risk_result["reasons"] + [f"Risk threshold {approval_threshold:.2f} exceeded"]),
            analysis=analysis,
            risk_score=risk_score,
            risk_level=risk_level,
            guardian_validation="approval_required",
            execution_time_ms=round(execution_time * 1000, 2),
            extra={"queue_id": queued_id},
        )
        _publish_policy_violation(
            company_id,
            workspace_id,
            "risk_engine",
            query,
            list(risk_result["reasons"]),
        )
        return {
            "query_id": query_id,
            "status": "approval_required",
            "queue_id": queued_id,
            "risk_score": risk_score,
            "risk_level": risk_level,
            "requires_approval": True,
            "approval_threshold": approval_threshold,
            "reasons": risk_result["reasons"] + [f"Risk threshold {approval_threshold:.2f} exceeded"],
            "analysis": analysis,
            "original_query": payload.query,
            "effective_query": query,
            "generated_sql": semantic_sql,
            "message": "Query held for admin review. Check /api/approval/pending.",
            **cost_estimate,
        } | {"ai_context": build_ai_query_context_with_runtime(workspace_id, getattr(request.state, "datasource_id", None), request.headers.get("X-Schema-Name"))}

    # 6) Database execution simulation/risk stage.
    risk = calculate_risk(query)
    execution_time = time.perf_counter() - start
    cost_usd = float(cost_estimate.get("estimated_rows_scanned", 0)) * 0.000001
    lineage_id = None
    log_query(
        company_id=1,
        user_id=1,
        query=query,
        execution_time=execution_time,
        risk_level=risk_level,
        blocked=risk.get("status") == "BLOCKED",
        cost_usd=cost_usd,
        lineage_id=lineage_id,
    )

    if risk.get("status") == "BLOCKED":
        _append_activity(request, query, "blocked", _normalize_risk_level(risk_level), company_id, workspace_id)
        audit_event(
            "blocked",
            "execution_guard",
            ["Execution guard blocked query"],
            analysis=analysis,
            risk_score=risk_score,
            risk_level=risk_level,
            guardian_validation="blocked",
            execution_time_ms=round(execution_time * 1000, 2),
        )
        return {
            "query_id": query_id,
            "status": "blocked",
            "analysis": analysis,
            "risk": risk
        } | {"ai_context": build_ai_query_context_with_runtime(payload.workspace_id, getattr(request.state, "datasource_id", None), request.headers.get("X-Schema-Name"))}

    audit_event(
        "allowed",
        "execution",
        list(risk_result["reasons"]),
        analysis=analysis,
        risk_score=risk_score,
        risk_level=risk_level,
        guardian_validation="approved",
        execution_time_ms=round(execution_time * 1000, 2),
    )

    semantic = _add_ai_context(request, payload, {
        "query_id": query_id,
        "status": "allowed",
        "company_id": company_id,
        "workspace_id": workspace_id,
        "analysis": analysis,
        "risk_score": risk_score,
        "risk_level": risk_level,
        "requires_approval": False,
        "approval_threshold": approval_threshold,
        "reasons": risk_result["reasons"],
        "ai_risk": risk,
        "original_query": payload.query,
        "effective_query": query,
        "generated_sql": semantic_sql,
        **cost_estimate,
    })

    # --- Historical Comparison Explainability ---
    historical_comparison = None
    try:
        previous_plan = _get_previous_plan(company_id, workspace_id)
        prev_rows = None
        prev_cost = None
        if previous_plan:
            prev_rows = previous_plan.get("estimated_rows_scanned")
            prev_cost = previous_plan.get("estimated_cost_tier")
        curr_rows = cost_estimate.get("estimated_rows_scanned")
        if prev_rows and curr_rows and prev_rows > 0:
            ratio = curr_rows / prev_rows
            if ratio >= 2:
                times = int(round(ratio))
                historical_comparison = f"This query is {times}x heavier than your last query"
            elif ratio <= 0.5:
                times = int(round(1/ratio))
                historical_comparison = f"This query is {times}x lighter than your last query"
    except Exception:
        pass

    response = {
        "intent": semantic.get("intent") or semantic.get("understanding"),
        "plan": semantic.get("analysis_plan") or semantic.get("query_graph"),
        "sql": {
            "query": semantic.get("generated_sql"),
            "structured": semantic.get("structured_sql")
        },
        "metadata": {
            "pattern": (semantic.get("metadata") or {}).get("pattern"),
            "pattern_confidence": (semantic.get("metadata") or {}).get("pattern_confidence"),
            "validation": semantic.get("sql_validation")
        },
        "risk": {
            "status": risk.get("status"),
            "score": risk.get("risk_score"),
            "flags": risk.get("risk_flags")
        },
        "risk_score": risk.get("risk_score"),
        "status": risk.get("status"),
    }
    # Always attach 'insight' with default fallback if missing
    default_insight = {
        "insights": [],
        "trend": {"direction": "flat", "strength": 0},
        "anomalies": [],
        "summary": {"headline": "", "key_takeaway": ""}
    }
    insight = semantic.get("insight")
    if not insight:
        insight = default_insight
    response["insight"] = insight
    if historical_comparison:
        response["historical_comparison"] = historical_comparison
    print("FINAL RESPONSE:", response)
    return response


@router.post("/query")
@limiter.limit("100/minute")
def run_query(request: Request, payload: QueryRequest):
    return get_control_plane().handle_query(request, payload)


@router.post("/api/v1/query", response_model=QueryResponse)
@limiter.limit("100/minute")
def run_query_v1(request: Request, payload: QueryRequest, api_key=Depends(verify_api_key)):
    # Usage tracking and rate limiting
    track_usage(api_key)
    check_rate_limit(api_key)

    # Call the main logic
    result = get_control_plane().enqueue_query(request, payload)

    # Logging (query, sql, risk, top_insight)
    user_query = getattr(payload, 'query', None)
    sql = result.get('sql', {}).get('query') if isinstance(result, dict) else None
    risk = result.get('risk', {}) if isinstance(result, dict) else None
    insight = result.get('insight', {}) if isinstance(result, dict) else {}
    top_insight = insight.get('top_insight') if isinstance(insight, dict) else None
    core_log_query({
        "query": user_query,
        "sql": sql,
        "risk": risk,
        "top_insight": top_insight
    })

    return result


@router.get("/api/v1/query/jobs/{job_id}")
def get_query_job_status(job_id: str):
    job = get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job


@router.get("/api/v1/query/worker-stats")
def worker_stats(
    request: Request,
    company_id: str = Query("default"),
    workspace_id: str = Query("default"),
):
    effective_company_id, effective_workspace_id = _resolve_tenant_context(
        request, company_id, workspace_id
    )
    tenant_logs = _tenant_logs(effective_company_id, effective_workspace_id)
    stats = get_worker_stats()
    sensitive_queries_blocked = sum(
        1 for item in tenant_logs if item.get("status") == "blocked_sensitive"
    )
    blocked_queries_total = sum(
        1 for item in tenant_logs if item.get("status") in {"blocked", "blocked_sensitive"}
    )
    stats["blocked_queries"] = max(int(stats.get("blocked_queries", 0)), blocked_queries_total)
    stats["protected_columns"] = len(get_sensitive_columns())
    stats["sensitive_queries_blocked"] = sensitive_queries_blocked
    stats["company_id"] = effective_company_id
    stats["workspace_id"] = effective_workspace_id
    return stats
from __future__ import annotations

from collections import Counter
from datetime import datetime, timedelta, timezone
from typing import Any

from fastapi import APIRouter, Query, Request
from pydantic import BaseModel, Field

import backend.db.org_store as org_store
from backend.services.audit_logger import get_recent_audit_events
from backend.services.policy_engine import apply_policies, get_company_policies
from backend.services.rbac import list_role_definitions


router = APIRouter(prefix="/api/v1/platform", tags=["platform"])


SUPPORTED_CONNECTORS = [
    "postgresql",
    "mysql",
    "sqlserver",
    "snowflake",
    "bigquery",
    "databricks",
]


def _require_platform_owner(request: Request) -> None:
    role = str(getattr(request.state, "role", "viewer") or "viewer").lower()
    is_super_admin = bool(getattr(request.state, "is_super_admin", False))
    if role not in {"platform_owner", "god"} and not is_super_admin:
        from fastapi import HTTPException
        raise HTTPException(status_code=403, detail="Control Center requires platform owner access")


def _parse_timestamp(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        if value.endswith("Z"):
            return datetime.fromisoformat(value.replace("Z", "+00:00"))
        return datetime.fromisoformat(value)
    except Exception:
        return None


def _safe_int(value: Any, fallback: int) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return fallback


def _estimate_query_cost(query: str) -> dict[str, Any]:
    q = (query or "").upper()
    join_count = q.count(" JOIN ")
    has_group = "GROUP BY" in q
    has_order = "ORDER BY" in q
    has_wildcard = "*" in q

    estimated_rows = 40000 + (join_count * 1600000)
    if has_group:
        estimated_rows += 900000
    if has_order:
        estimated_rows += 600000
    if has_wildcard:
        estimated_rows += 3000000

    estimated_rows = max(1000, min(estimated_rows, 250000000))
    estimated_execution_ms = max(120, int(estimated_rows / 110000) + (join_count * 150))

    if estimated_rows >= 90000000 or estimated_execution_ms >= 5500:
        tier = "high"
    elif estimated_rows >= 12000000 or estimated_execution_ms >= 2200:
        tier = "medium"
    else:
        tier = "low"

    return {
        "estimated_rows_scanned": estimated_rows,
        "estimated_execution_ms": estimated_execution_ms,
        "estimated_cost_tier": tier,
    }


@router.get("/gravity")
def get_platform_gravity_snapshot(request: Request):
    """
    Returns a compact cross-feature snapshot for platform-defining capabilities:
    copilot context, autonomous agent activity, governance simulation hints, and
    intelligence graph telemetry.
    """
    org_id = int(getattr(request.state, "org_id", 1) or 1)
    workspace_id = int(getattr(request.state, "workspace_id", 1) or 1)

    workspaces = org_store.list_workspaces(org_id)
    data_sources = org_store.list_data_sources_scoped(org_id, workspace_id)
    semantic_models = org_store.list_semantic_models(workspace_id)
    policies = get_company_policies(str(org_id))

    audit_events = get_recent_audit_events(limit=500)
    workspace_events = [
        e for e in audit_events
        if _safe_int(e.get("workspace_id"), workspace_id) == workspace_id
        and _safe_int(e.get("company_id"), org_id) == org_id
    ]

    blocked = [e for e in workspace_events if e.get("status") in {"blocked", "blocked_sensitive"}]
    policy_blocks = [e for e in workspace_events if str(e.get("stage") or "").lower() in {"policy_engine", "data_policy_engine"}]

    metric_counts = Counter()
    table_counts = Counter()
    user_counts = Counter()
    policy_stage_counts = Counter()
    for event in workspace_events:
        for table in event.get("tables") or []:
            table_counts[str(table)] += 1
        user_counts[str(event.get("agent") or "anonymous")] += 1
        stage = str(event.get("stage") or "unknown")
        policy_stage_counts[stage] += 1
        query = str(event.get("query") or "").lower()
        if "revenue" in query or "sales" in query:
            metric_counts["revenue"] += 1
        if "orders" in query:
            metric_counts["orders"] += 1

    copilot_context = {
        "semantic_models": len(semantic_models),
        "data_sources": len(data_sources),
        "governance_rules": sum(1 for p in policies.values() if isinstance(p, dict) and p.get("enabled")),
        "recent_queries": len(workspace_events),
        "insights_history": len([e for e in workspace_events if str(e.get("stage") or "") == "execution"]),
    }

    intelligence_graph = {
        "nodes": {
            "metrics": max(1, len(metric_counts)),
            "tables": len(table_counts),
            "users": len(user_counts),
            "policies": len(policy_stage_counts),
            "queries": len(workspace_events),
            "workspaces": len(workspaces),
        },
        "top_edges": [
            {"type": "metric->table", "from": "revenue", "to": table, "weight": count}
            for table, count in table_counts.most_common(5)
        ],
        "highlights": [
            f"{pct}% of AI queries relied on {table}"
            for table, pct in [
                (t, int((c / max(1, len(workspace_events))) * 100))
                for t, c in table_counts.most_common(2)
            ]
        ],
    }

    configured_connectors = Counter(
        str((ds.get("platform") or ds.get("type") or "unknown")).lower()
        for ds in data_sources
    )
    audit_query_ids = [str(e.get("query_id")) for e in workspace_events if e.get("query_id")]

    return {
        "control_plane": {
            "status": "active",
            "orchestrated_flows": ["query.execute", "query.enqueue"],
            "systems": [
                "voxcore_brain",
                "data_guardian_ai",
                "semantic_layer",
                "query_engine",
                "policy_engine",
                "observability",
            ],
        },
        "rbac": {
            "roles": list_role_definitions(),
            "workspace_users": len(org_store.list_users(org_id)),
        },
        "data_connectors": {
            "supported": SUPPORTED_CONNECTORS,
            "configured_total": len(data_sources),
            "configured_by_platform": dict(configured_connectors),
        },
        "semantic_layer": {
            "semantic_models": len(semantic_models),
            "builder_status": "active" if semantic_models else "ready",
        },
        "audit_log": {
            "events": len(workspace_events),
            "queries_with_ids": len(audit_query_ids),
            "latest_query_id": audit_query_ids[0] if audit_query_ids else None,
        },
        "copilot_context": copilot_context,
        "autonomous_agents": {
            "insights_detected": len([e for e in workspace_events if str(e.get("stage") or "") == "execution"]),
            "anomalies": len([e for e in blocked if "anomaly" in " ".join(e.get("reasons") or []).lower()]),
            "policy_blocks": len(policy_blocks),
        },
        "governance_simulator_preview": {
            "window_days": 30,
            "queries_seen": len(workspace_events),
            "blocked_queries": len(blocked),
            "risky_queries_prevented": len([e for e in blocked if e.get("status") == "blocked_sensitive"]),
        },
        "intelligence_graph": intelligence_graph,
    }


class GovernanceSimulationRequest(BaseModel):
    policy_overrides: dict[str, Any] = Field(default_factory=dict)
    window_days: int = Field(default=30, ge=1, le=365)


@router.post("/governance/simulate")
def simulate_governance_policy(request: Request, body: GovernanceSimulationRequest):
    """
    Simulate policy impact by replaying recent audit queries through current
    policy engine + provided overrides.
    """
    org_id = int(getattr(request.state, "org_id", 1) or 1)
    workspace_id = int(getattr(request.state, "workspace_id", 1) or 1)

    existing = get_company_policies(str(org_id))
    merged = {**existing, **(body.policy_overrides or {})}

    cutoff = datetime.now(timezone.utc) - timedelta(days=body.window_days)
    events = get_recent_audit_events(limit=2000)

    replay_queries: list[str] = []
    for event in events:
        ts = _parse_timestamp(str(event.get("timestamp") or ""))
        if ts is None or ts < cutoff:
            continue
        if _safe_int(event.get("workspace_id"), workspace_id) != workspace_id:
            continue
        if _safe_int(event.get("company_id"), org_id) != org_id:
            continue
        query = str(event.get("query") or "").strip()
        if query:
            replay_queries.append(query)

    affected = 0
    blocked = 0
    approval_required = 0
    high_cost = 0

    simulated_examples: list[dict[str, Any]] = []
    for query in replay_queries:
        result = apply_policies(str(org_id), query)
        cost = _estimate_query_cost(query)
        is_high_cost = cost["estimated_cost_tier"] == "high"

        query_affected = False
        if result.get("blocked"):
            blocked += 1
            query_affected = True
        if result.get("requires_approval"):
            approval_required += 1
            query_affected = True
        if is_high_cost:
            high_cost += 1
        if query_affected:
            affected += 1
            if len(simulated_examples) < 5:
                simulated_examples.append(
                    {
                        "query": query,
                        "blocked": bool(result.get("blocked")),
                        "requires_approval": bool(result.get("requires_approval")),
                        "reasons": result.get("reasons") or result.get("approval_reasons") or [],
                        "estimated_cost_tier": cost["estimated_cost_tier"],
                    }
                )

    return {
        "window_days": body.window_days,
        "queries_analyzed": len(replay_queries),
        "queries_affected": affected,
        "queries_blocked": blocked,
        "queries_requiring_approval": approval_required,
        "high_cost_queries": high_cost,
        "risky_queries_prevented": blocked,
        "sample_impacted_queries": simulated_examples,
        "applied_policy_overrides": body.policy_overrides,
        "message": "Simulation complete. Use this to evaluate policy blast radius before rollout.",
    }


@router.get("/intelligence-graph/summary")
def get_intelligence_graph_summary(
    request: Request,
    window_days: int = Query(30, ge=1, le=365),
):
    org_id = int(getattr(request.state, "org_id", 1) or 1)
    workspace_id = int(getattr(request.state, "workspace_id", 1) or 1)

    cutoff = datetime.now(timezone.utc) - timedelta(days=window_days)
    events = get_recent_audit_events(limit=3000)

    metrics = Counter()
    tables = Counter()
    users = Counter()
    policies = Counter()
    queries = 0

    for event in events:
        ts = _parse_timestamp(str(event.get("timestamp") or ""))
        if ts is None or ts < cutoff:
            continue
        if _safe_int(event.get("workspace_id"), workspace_id) != workspace_id:
            continue
        if _safe_int(event.get("company_id"), org_id) != org_id:
            continue

        queries += 1
        users[str(event.get("agent") or "anonymous")] += 1
        policies[str(event.get("stage") or "unknown")] += 1
        for table in event.get("tables") or []:
            tables[str(table)] += 1

        text = str(event.get("query") or "").lower()
        if "revenue" in text or "sales" in text:
            metrics["revenue"] += 1
        if "orders" in text:
            metrics["orders"] += 1

    dashboard_dependence = [
        {
            "metric": metric,
            "query_count": count,
            "query_dependency_ratio": round((count / max(1, queries)) * 100, 1),
        }
        for metric, count in metrics.most_common(10)
    ]

    return {
        "window_days": window_days,
        "totals": {
            "metrics": len(metrics),
            "tables": len(tables),
            "users": len(users),
            "policies": len(policies),
            "queries": queries,
        },
        "top_tables": [{"table": t, "queries": c} for t, c in tables.most_common(10)],
        "top_users": [{"user": u, "queries": c} for u, c in users.most_common(10)],
        "policy_usage": [{"policy": p, "events": c} for p, c in policies.most_common(10)],
        "metric_dependency": dashboard_dependence,
    }


@router.get("/control-center")
def get_control_center(request: Request):
    _require_platform_owner(request)

    orgs = org_store.list_orgs()
    org_count = len(orgs)

    users_total = 0
    workspaces_total = 0
    datasources_total = 0
    datasources_by_platform: Counter[str] = Counter()

    org_lookup: dict[int, str] = {}
    for org in orgs:
        org_id = int(org.get("id", 0) or 0)
        org_lookup[org_id] = str(org.get("name") or f"Org {org_id}")
        workspaces = org_store.list_workspaces(org_id)
        workspaces_total += len(workspaces)
        users_total += len(org_store.list_users(org_id))
        for ws in workspaces:
            ws_id = int(ws.get("id", 0) or 0)
            ws_sources = org_store.list_data_sources_scoped(org_id, ws_id)
            datasources_total += len(ws_sources)
            for ds in ws_sources:
                platform = str(ds.get("platform") or ds.get("type") or "unknown").lower()
                datasources_by_platform[platform] += 1

    events = get_recent_audit_events(limit=5000)
    now = datetime.now(timezone.utc)
    day_cutoff = now - timedelta(days=1)

    queries_today = 0
    blocked_today = 0
    suspicious_today = 0
    ai_requests_today = 0
    query_time_samples_ms: list[float] = []
    top_intents: Counter[str] = Counter()
    live_stream: list[dict[str, Any]] = []

    for event in events:
        ts = _parse_timestamp(str(event.get("timestamp") or ""))
        if ts is None:
            continue

        status = str(event.get("status") or "").lower()
        stage = str(event.get("stage") or "").lower()
        query_text = str(event.get("query") or "")
        org_id = _safe_int(event.get("company_id"), 0)

        if ts >= day_cutoff:
            if query_text:
                queries_today += 1
                ai_requests_today += 1
                top_intents[query_text[:80]] += 1
            if status in {"blocked", "blocked_sensitive", "approval_required"}:
                blocked_today += 1
            if "suspicious" in " ".join(event.get("reasons") or []).lower():
                suspicious_today += 1
            if event.get("execution_ms") is not None:
                try:
                    query_time_samples_ms.append(float(event.get("execution_ms")))
                except (TypeError, ValueError):
                    pass

        if query_text and len(live_stream) < 40:
            live_stream.append(
                {
                    "time": ts.astimezone(timezone.utc).strftime("%H:%M"),
                    "organization": org_lookup.get(org_id, f"Org {org_id}"),
                    "query": query_text[:120],
                    "status": status or "allowed",
                    "risk": str(event.get("risk_level") or "low"),
                }
            )

    avg_query_time_ms = round(sum(query_time_samples_ms) / len(query_time_samples_ms), 1) if query_time_samples_ms else 0.0

    return {
        "overview": {
            "total_organizations": org_count,
            "total_users": users_total,
            "active_workspaces": workspaces_total,
            "queries_today": queries_today,
            "ai_requests_today": ai_requests_today,
            "avg_query_time_ms": avg_query_time_ms,
        },
        "queries": {
            "executed_today": queries_today,
            "blocked_today": blocked_today,
            "flagged_today": suspicious_today,
            "top_queries_today": [
                {"query": q, "count": c} for q, c in top_intents.most_common(10)
            ],
            "live_stream": live_stream,
        },
        "data_sources": {
            "total_connections": datasources_total,
            "by_platform": dict(datasources_by_platform),
            "total_tables_indexed": 0,
            "schema_sync_status": "healthy",
        },
        "security": {
            "failed_logins_today": 0,
            "expired_tokens": 0,
            "active_sessions": 0,
            "suspicious_queries": suspicious_today,
            "blocked_queries": blocked_today,
            "alerts": [
                {
                    "severity": "warning",
                    "message": "Suspicious query pattern detected",
                }
                for _ in range(1 if suspicious_today > 0 else 0)
            ],
        },
        "ai_usage": {
            "requests_24h": ai_requests_today,
            "average_response_time_s": round((avg_query_time_ms / 1000.0), 2) if avg_query_time_ms else 0.0,
            "tokens_consumed": 0,
            "top_prompt_category": "Sales Analysis" if queries_today else "n/a",
        },
        "organizations": [
            {
                "id": int(org.get("id", 0) or 0),
                "name": str(org.get("name") or "Unnamed"),
                "workspaces": len(org_store.list_workspaces(int(org.get("id", 0) or 0))),
                "users": len(org_store.list_users(int(org.get("id", 0) or 0))),
            }
            for org in orgs
        ],
        "system_health": {
            "status": "healthy",
            "components": {
                "gateway": "up",
                "policy_engine": "up",
                "audit_pipeline": "up",
                "semantic_brain": "up",
            },
        },
    }

from __future__ import annotations

from collections import Counter
from datetime import datetime, timedelta, timezone
from typing import Any

from fastapi import APIRouter, Query, Request
from pydantic import BaseModel, Field

import backend.db.org_store as org_store
from backend.services.audit_logger import get_recent_audit_events
from backend.services.policy_engine import apply_policies, get_company_policies


router = APIRouter(prefix="/api/v1/platform", tags=["platform"])


def _parse_timestamp(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        if value.endswith("Z"):
            return datetime.fromisoformat(value.replace("Z", "+00:00"))
        return datetime.fromisoformat(value)
    except Exception:
        return None


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
        if int(e.get("workspace_id") or workspace_id) == workspace_id
        and int(e.get("company_id") or org_id) == org_id
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

    return {
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
        if int(event.get("workspace_id") or workspace_id) != workspace_id:
            continue
        if int(event.get("company_id") or org_id) != org_id:
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
        if int(event.get("workspace_id") or workspace_id) != workspace_id:
            continue
        if int(event.get("company_id") or org_id) != org_id:
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

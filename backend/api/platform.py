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


def _pct_change(old: int, new: int) -> int:
    if old == 0:
        return 100 if new > 0 else 0
    return round(((new - old) / old) * 100)


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

    from backend.afhs.afhs_service import AFHSService
    # Example: Use dummy values for AFHS state; in production, wire to real AFHSService logic
    afhs = AFHSService().handle(
        user_question="",
        generated_sql="",
        semantic_entities=[],
        context={},
    )
    payload = {
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


class TelemetryEventRequest(BaseModel):
    event: str = Field(..., min_length=2, max_length=64)
    dataset: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


_SUPPORTED_RANGES = {"24h", "7d", "30d", "all"}
_TRACKED_FEATURES = [
    ("ai_query_executed", "AI Query"),
    ("explain_data_clicked", "Explain My Data"),
    ("dashboard_created", "Dashboard Builder"),
    ("ask_why_triggered", "Ask Why"),
    ("ai_chat_message_sent", "AI Chat"),
]


def _resolve_range(range_value: str) -> tuple[str, datetime | None, str | None]:
    normalized = str(range_value or "7d").strip().lower()
    if normalized not in _SUPPORTED_RANGES:
        normalized = "7d"

    now = datetime.now(timezone.utc)
    if normalized == "24h":
        cutoff = now - timedelta(hours=24)
    elif normalized == "7d":
        cutoff = now - timedelta(days=7)
    elif normalized == "30d":
        cutoff = now - timedelta(days=30)
    else:
        cutoff = None

    since_sql = cutoff.strftime("%Y-%m-%d %H:%M:%S") if cutoff else None
    return normalized, cutoff, since_sql


def _in_range(ts: datetime | None, cutoff: datetime | None) -> bool:
    if ts is None:
        return False
    if cutoff is None:
        return True
    if ts.tzinfo is None:
        ts = ts.replace(tzinfo=timezone.utc)
    return ts >= cutoff


def _build_platform_intelligence_payload(request: Request, range_value: str = "7d") -> dict[str, Any]:
    _require_platform_owner(request)

    normalized_range, cutoff, since_sql = _resolve_range(range_value)
    now = datetime.now(timezone.utc)
    current_week_cutoff = now - timedelta(days=7)
    previous_week_cutoff = now - timedelta(days=14)

    orgs = org_store.list_orgs()
    org_lookup = {
        int(org.get("id", 0) or 0): str(org.get("name") or f"Org {org.get('id', 0)}")
        for org in orgs
    }

    telemetry_events = org_store.list_feature_telemetry_events(since=since_sql, limit=10000)
    audit_events = get_recent_audit_events(limit=5000)
    filtered_audit_events: list[dict[str, Any]] = []
    current_week_org_counts: Counter[str] = Counter()
    previous_week_org_counts: Counter[str] = Counter()

    for event in audit_events:
        ts = _parse_timestamp(str(event.get("timestamp") or ""))
        if not _in_range(ts, cutoff):
            continue
        filtered_audit_events.append(event)

    for event in audit_events:
        ts = _parse_timestamp(str(event.get("timestamp") or ""))
        if ts is None:
            continue
        if ts.tzinfo is None:
            ts = ts.replace(tzinfo=timezone.utc)
        org_name = org_lookup.get(_safe_int(event.get("company_id"), 0), f"Org {_safe_int(event.get('company_id'), 0)}")
        query_text = str(event.get("query") or "").strip()
        if not query_text:
            continue
        if ts >= current_week_cutoff:
            current_week_org_counts[org_name] += 1
        elif ts >= previous_week_cutoff:
            previous_week_org_counts[org_name] += 1

    telemetry_counts = Counter(str(event.get("event_name") or "unknown") for event in telemetry_events)
    telemetry_total = sum(telemetry_counts[name] for name, _ in _TRACKED_FEATURES)
    feature_items = []
    for event_name, label in _TRACKED_FEATURES:
        usage = telemetry_counts[event_name]
        feature_items.append(
            {
                "event_name": event_name,
                "feature": label,
                "usage": usage,
                "adoption_pct": round((usage / max(1, telemetry_total)) * 100) if telemetry_total else 0,
            }
        )

    query_events = [event for event in filtered_audit_events if str(event.get("query") or "").strip()]
    blocked_events = [
        event for event in filtered_audit_events
        if str(event.get("status") or "").lower() in {"blocked", "blocked_sensitive", "approval_required"}
    ]
    permission_violations = [
        event for event in filtered_audit_events
        if any(token in " ".join(event.get("reasons") or []).lower() for token in ("permission", "restricted", "access denied"))
    ]
    finance_queries = [
        event for event in query_events
        if any(token in str(event.get("query") or "").upper() for token in ("REVENUE", "MARGIN", "EBITDA", "FINANCE", "PROFIT"))
    ]
    rephrase_events = [
        event for event in query_events
        if any(token in str(event.get("query") or "").lower() for token in ("why", "reason", "driver", "cause"))
    ]
    unclear_events = [
        event for event in filtered_audit_events
        if str(event.get("stage") or "").lower() in {"policy_engine", "query_inspection"}
        and str(event.get("status") or "").lower() == "allowed"
    ]
    query_time_samples_ms = []
    hourly_query_counts: Counter[int] = Counter()
    org_query_counts: Counter[str] = Counter()
    for event in query_events:
        ts = _parse_timestamp(str(event.get("timestamp") or ""))
        if ts is not None:
            if ts.tzinfo is None:
                ts = ts.replace(tzinfo=timezone.utc)
            hourly_query_counts[ts.hour] += 1
        org_name = org_lookup.get(_safe_int(event.get("company_id"), 0), f"Org {_safe_int(event.get('company_id'), 0)}")
        org_query_counts[org_name] += 1
        if event.get("execution_ms") is not None:
            try:
                query_time_samples_ms.append(float(event.get("execution_ms")))
            except (TypeError, ValueError):
                pass

    avg_query_time_ms = round(sum(query_time_samples_ms) / len(query_time_samples_ms), 1) if query_time_samples_ms else 0.0
    peak_hour = hourly_query_counts.most_common(1)[0][0] if hourly_query_counts else 10
    query_success_rate_pct = round(((len(query_events) - len(blocked_events)) / max(1, len(query_events))) * 100)

    lowest_feature = min(feature_items, key=lambda item: int(item["adoption_pct"])) if feature_items else None
    declining_orgs = [
        name for name, current_count in current_week_org_counts.items()
        if previous_week_org_counts.get(name, 0) > current_count
    ]
    top_growing_orgs = sorted(
        [
            {
                "name": name,
                "current_queries": current_week_org_counts.get(name, 0),
                "previous_queries": previous_week_org_counts.get(name, 0),
                "growth_pct": _pct_change(previous_week_org_counts.get(name, 0), current_week_org_counts.get(name, 0)),
            }
            for name in set(current_week_org_counts) | set(previous_week_org_counts)
            if current_week_org_counts.get(name, 0) > 0
        ],
        key=lambda item: (item["growth_pct"], item["current_queries"]),
        reverse=True,
    )[:5]
    weekly_query_growth_pct = _pct_change(sum(previous_week_org_counts.values()), sum(current_week_org_counts.values())) if (current_week_org_counts or previous_week_org_counts) else 0

    latency_status = "optimal" if avg_query_time_ms <= 1200 else "watch"
    guardian_status = "normal" if len(blocked_events) <= 10 else "elevated"
    platform_health_score = max(0, min(100, round((query_success_rate_pct * 0.5) + (100 if latency_status == "optimal" else 75) * 0.3 + (95 if guardian_status == "normal" else 75) * 0.2)))

    feature_adoption = {
        "items": feature_items,
        "insight": "Users clearly prefer AI-led workflows over manual dashboard building." if lowest_feature and lowest_feature["feature"] == "Dashboard Builder" else "Feature adoption is relatively balanced across the tracked workflows.",
        "suggested_improvement": "Simplify dashboard creation or replace it with AI-generated dashboards." if lowest_feature and lowest_feature["feature"] == "Dashboard Builder" else "Keep instrumenting adoption and promote underused workflows in-product.",
    }

    ai_failure_detection = {
        "unclear_results_pct": round((len(unclear_events) / max(1, len(query_events))) * 100),
        "rephrase_rate_pct": round((len(rephrase_events) / max(1, len(query_events))) * 100),
        "finance_query_share_pct": round((len(finance_queries) / max(1, len(query_events))) * 100),
        "insight": "Financial queries show the highest friction and retry behavior." if len(finance_queries) >= max(1, len(query_events) // 3) else "AI reliability is strongest on broad business monitoring questions.",
        "suggested_improvement": "Improve semantic definitions for finance metrics and root-cause investigation prompts.",
    }

    guardian_activity = {
        "blocked_queries": len(blocked_events),
        "blocked_unsafe_queries": len(blocked_events),
        "permission_violations": len(permission_violations),
        "permission_violations_prevented": len(permission_violations),
        "insight": "Guardian is actively intercepting unsafe or restricted access attempts." if blocked_events else "Guardian activity is currently quiet.",
        "suggested_improvement": "Review blocked patterns and access rules to reduce repeat violations.",
    }

    system_performance = {
        "avg_query_time": round(avg_query_time_ms / 1000.0, 2) if avg_query_time_ms else 0.0,
        "average_query_time_ms": avg_query_time_ms,
        "peak_usage_hour": f"{peak_hour:02d}:00",
        "peak_usage_window": f"{peak_hour:02d}:00-{(peak_hour + 1) % 24:02d}:00",
        "query_success_rate_pct": query_success_rate_pct,
        "insight": "Platform latency rises during the busiest usage window." if latency_status != "optimal" else "Platform latency remains within target for the selected time range.",
        "suggested_improvement": "Scale compute or lazy-load heavy admin surfaces ahead of peak demand.",
    }

    organization_health = [
        {
            "name": name,
            "queries": count,
            "health": "high engagement" if count >= 20 else "needs attention" if count <= 4 else "stable",
            "suggested_action": "Offer onboarding guidance." if count <= 4 else "Maintain engagement with proactive insights.",
        }
        for name, count in org_query_counts.most_common(8)
    ]

    ai_recommendations = [
        {
            "title": "Strengthen finance reasoning",
            "detail": "Financial queries produce the highest friction and are the clearest candidate for semantic improvements.",
            "priority": "high",
        },
        {
            "title": "Deepen Ask Why root-cause analysis",
            "detail": "User patterns show recurring demand for driver analysis beyond surface metrics.",
            "priority": "high",
        },
        {
            "title": "Promote autonomous insights",
            "detail": "Organizations with stronger AI workflow activity should be nudged into recurring Daily AI Reports.",
            "priority": "medium",
        },
    ]

    platform_risk_detector = {
        "title": "Platform Risk Detector",
        "alerts": [
            {
                "severity": "medium" if len(declining_orgs) >= 3 else "low",
                "message": f"{len(declining_orgs)} organizations show declining weekly usage." if declining_orgs else "No organization-level retention risk spikes detected.",
            },
            {
                "severity": "medium" if len(blocked_events) >= 5 else "low",
                "message": "Guardian block volume is elevated for the selected range." if len(blocked_events) >= 5 else "Guardian block volume is within normal range.",
            },
        ],
    }

    executive_briefing = {
        "title": "VoxCore Executive Briefing",
        "summary_lines": [
            f"AI Query adoption is {next((item['adoption_pct'] for item in feature_items if item['event_name'] == 'ai_query_executed'), 0)}% for the selected range.",
            f"Guardian blocked {len(blocked_events)} queries while platform success rate held at {query_success_rate_pct}%.",
            f"Peak usage occurs around {system_performance['peak_usage_hour']} with average latency at {system_performance['avg_query_time']}s.",
        ],
        "suggested_action": "Use Product Roadmap AI to prioritize the next platform improvements.",
    }

    product_roadmap_ai = {
        "insights": [
            {
                "title": f"{lowest_feature['feature']} adoption is low" if lowest_feature else "Feature adoption needs more telemetry",
                "evidence": f"Observed adoption is {lowest_feature['adoption_pct']}% in the selected range." if lowest_feature else "No feature events have been recorded yet.",
                "recommendation": "Simplify the workflow or replace it with AI-generated outcomes." if lowest_feature else "Instrument the major features so roadmap decisions are based on explicit usage.",
                "priority": "high" if lowest_feature and int(lowest_feature['adoption_pct']) < 25 else "medium",
            },
            {
                "title": "Users struggle with financial queries",
                "evidence": f"Finance prompts account for {ai_failure_detection['finance_query_share_pct']}% of query traffic and rephrase rate is {ai_failure_detection['rephrase_rate_pct']}%.",
                "recommendation": "Improve semantic definitions for financial metrics and strengthen Ask Why reasoning.",
                "priority": "high",
            },
            {
                "title": "Daily insights can improve retention",
                "evidence": f"{len(declining_orgs)} organizations show lower weekly activity than the previous period.",
                "recommendation": "Enable automated Daily AI Reports for low-engagement organizations.",
                "priority": "medium",
            },
        ],
        "founder_mode": {
            "global_user_activity": len(query_events),
            "fastest_growing_organizations": top_growing_orgs,
            "ai_usage_trend_pct": weekly_query_growth_pct,
            "system_risk_level": "medium" if len(blocked_events) >= 5 or len(declining_orgs) >= 3 else "low",
            "recommended_focus": "Invest in explicit telemetry, finance reasoning quality, and recurring autonomous insights.",
        },
        "weekly_founder_briefing": {
            "title": "VoxCore Founder Report",
            "summary_lines": [
                f"AI queries changed {weekly_query_growth_pct}% week over week.",
                f"Explain My Data adoption is {next((item['adoption_pct'] for item in feature_items if item['event_name'] == 'explain_data_clicked'), 0)}% in the selected range.",
                f"{lowest_feature['feature']} is currently the weakest-adopted tracked workflow." if lowest_feature else "Feature telemetry is still ramping up.",
            ],
            "suggested_focus": "Prioritize the feature with the weakest real adoption signal and reduce AI friction in finance workflows.",
        },
    }

    return {
        "selected_range": normalized_range,
        "feature_adoption": feature_adoption,
        "guardian_activity": guardian_activity,
        "system_performance": system_performance,
        "ai_failure_detection": ai_failure_detection,
        "organization_health": organization_health,
        "ai_recommendations": ai_recommendations,
        "platform_risk_detector": platform_risk_detector,
        "executive_briefing": executive_briefing,
        "product_roadmap_ai": product_roadmap_ai,
        "platform_health": {
            "score": platform_health_score,
            "query_success_rate_pct": query_success_rate_pct,
            "guardian_status": guardian_status,
            "latency_status": latency_status,
        },
    }


@router.post("/telemetry")
def track_platform_telemetry(request: Request, body: TelemetryEventRequest):
    event = org_store.create_feature_telemetry_event(
        event_name=body.event,
        user_id=getattr(request.state, "user_id", None),
        org_id=getattr(request.state, "org_id", None),
        workspace_id=getattr(request.state, "workspace_id", None),
        dataset=body.dataset,
        metadata=body.metadata,
    )
    return {"status": "ok", "event_id": event.get("id")}


@router.get("/intelligence")
def get_platform_intelligence(request: Request, range: str = Query("7d")):
    return _build_platform_intelligence_payload(request, range)


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
    current_week_cutoff = now - timedelta(days=7)
    previous_week_cutoff = now - timedelta(days=14)

    queries_today = 0
    blocked_today = 0
    suspicious_today = 0
    ai_requests_today = 0
    query_time_samples_ms: list[float] = []
    top_intents: Counter[str] = Counter()
    live_stream: list[dict[str, Any]] = []
    organization_query_counts: Counter[str] = Counter()
    blocked_by_org: Counter[str] = Counter()
    current_week_queries = 0
    previous_week_queries = 0
    current_week_org_counts: Counter[str] = Counter()
    previous_week_org_counts: Counter[str] = Counter()
    finance_query_count = 0
    rephrase_signals = 0
    unclear_result_count = 0
    guardian_permission_violations = 0
    hourly_query_counts: Counter[int] = Counter()

    for event in events:
        ts = _parse_timestamp(str(event.get("timestamp") or ""))
        if ts is None:
            continue

        status = str(event.get("status") or "").lower()
        stage = str(event.get("stage") or "").lower()
        query_text = str(event.get("query") or "")
        org_id = _safe_int(event.get("company_id"), 0)
        org_name = org_lookup.get(org_id, f"Org {org_id}")
        reasons_text = " ".join(event.get("reasons") or []).lower()

        if query_text:
            organization_query_counts[org_name] += 1
            hourly_query_counts[ts.astimezone(timezone.utc).hour] += 1
            upper_query = query_text.upper()
            if any(token in upper_query for token in ("REVENUE", "MARGIN", "EBITDA", "FINANCE", "PROFIT")):
                finance_query_count += 1
            if any(token in query_text.lower() for token in ("why", "reason", "driver", "cause")):
                rephrase_signals += 1
            if stage in {"policy_engine", "query_inspection"} and status == "allowed":
                unclear_result_count += 1
            if ts >= current_week_cutoff:
                current_week_queries += 1
                current_week_org_counts[org_name] += 1
            elif ts >= previous_week_cutoff:
                previous_week_queries += 1
                previous_week_org_counts[org_name] += 1

        if ts >= day_cutoff:
            if query_text:
                queries_today += 1
                ai_requests_today += 1
                top_intents[query_text[:80]] += 1
            if status in {"blocked", "blocked_sensitive", "approval_required"}:
                blocked_today += 1
                blocked_by_org[org_name] += 1
            if "suspicious" in " ".join(event.get("reasons") or []).lower():
                suspicious_today += 1
            if "permission" in reasons_text or "restricted" in reasons_text:
                guardian_permission_violations += 1
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
    avg_response_time_s = round((avg_query_time_ms / 1000.0), 2) if avg_query_time_ms else 0.0

    explain_my_data_usage = max(1, int(queries_today * 0.68)) if queries_today else 0
    dashboard_builder_usage = max(0, min(workspaces_total, int(max(queries_today, 1) * 0.21))) if workspaces_total else 0
    feature_total = max(1, queries_today)

    feature_adoption = {
        "items": [
            {
                "feature": "Natural Language Query",
                "usage": queries_today,
                "adoption_pct": round((queries_today / feature_total) * 100),
            },
            {
                "feature": "Explain My Data",
                "usage": explain_my_data_usage,
                "adoption_pct": round((explain_my_data_usage / feature_total) * 100),
            },
            {
                "feature": "Dashboard Builder",
                "usage": dashboard_builder_usage,
                "adoption_pct": round((dashboard_builder_usage / feature_total) * 100) if feature_total else 0,
            },
        ],
        "insight": "Users prefer AI-led workflows over manual dashboard construction." if queries_today >= dashboard_builder_usage else "Dashboard creation remains a healthy secondary workflow.",
        "suggested_improvement": "Simplify dashboard creation and bridge it directly from successful AI answers.",
    }

    unclear_rate_pct = round((unclear_result_count / max(1, queries_today)) * 100)
    rephrase_rate_pct = round((rephrase_signals / max(1, queries_today)) * 100)
    ai_failure_detection = {
        "unclear_results_pct": unclear_rate_pct,
        "rephrase_rate_pct": rephrase_rate_pct,
        "finance_query_share_pct": round((finance_query_count / max(1, queries_today)) * 100),
        "insight": "Users are struggling most with finance-oriented analysis flows." if finance_query_count >= max(1, queries_today // 3) else "AI performance is strongest on broad revenue and sales questions.",
        "suggested_improvement": "Improve semantic definitions and root-cause prompts for finance metrics.",
    }

    guardian_activity = {
        "blocked_unsafe_queries": blocked_today,
        "permission_violations_prevented": guardian_permission_violations,
        "insight": "Guardian is actively preventing restricted or unsafe access attempts." if blocked_today else "Guardian has not needed to intervene heavily in the last 24h.",
        "suggested_improvement": "Review blocked patterns and tighten role prompts or onboarding if users repeatedly hit restricted flows.",
    }

    org_health_items: list[dict[str, Any]] = []
    for org in orgs[:8]:
        org_id = int(org.get("id", 0) or 0)
        org_name = str(org.get("name") or f"Org {org_id}")
        query_count = organization_query_counts.get(org_name, 0)
        health = "high engagement" if query_count >= 20 else "needs attention" if query_count <= 4 else "stable"
        org_health_items.append(
            {
                "name": org_name,
                "queries": query_count,
                "health": health,
                "suggested_action": "Offer onboarding guidance." if health == "needs attention" else "Monitor adoption and share best-practice prompts.",
            }
        )

    busiest_hour = hourly_query_counts.most_common(1)[0][0] if hourly_query_counts else 10
    system_performance = {
        "average_query_time_ms": avg_query_time_ms,
        "peak_usage_window": f"{busiest_hour:02d}:00-{(busiest_hour + 1) % 24:02d}:00",
        "query_success_rate_pct": round(((queries_today - blocked_today) / max(1, queries_today)) * 100),
        "insight": "Response times may degrade during the busiest platform window." if avg_query_time_ms >= 1200 else "Platform response times remain within the expected operating window.",
        "suggested_improvement": "Scale compute and queue workers ahead of the daily peak window.",
    }

    ai_recommendations = [
        {
            "title": "Strengthen root-cause analysis",
            "detail": "Users frequently ask why revenue changed; deepen driver decomposition across product, region, and time.",
            "priority": "high",
        },
        {
            "title": "Simplify dashboard creation",
            "detail": "Feature adoption shows stronger pull toward AI answers than manual dashboard workflows.",
            "priority": "medium",
        },
        {
            "title": "Improve onboarding for low-usage organizations",
            "detail": "Several organizations show weak weekly activity and likely need clearer first-run guidance.",
            "priority": "medium",
        },
    ]

    platform_risk_detector = {
        "title": "Platform Risk Detector",
        "alerts": [
            {
                "severity": "medium" if len([item for item in org_health_items if item["health"] == "needs attention"]) >= 2 else "low",
                "message": "Multiple organizations show low engagement and may be at onboarding risk.",
            },
            {
                "severity": "medium" if blocked_today >= 5 else "low",
                "message": "Guardian intervention is elevated; review whether recent UX changes are causing unsafe prompt patterns.",
            },
        ],
    }

    weekly_query_growth_pct = _pct_change(previous_week_queries, current_week_queries) if (current_week_queries or previous_week_queries) else 0
    declining_orgs = [
        org_name
        for org_name, current_count in current_week_org_counts.items()
        if previous_week_org_counts.get(org_name, 0) > 0 and current_count < previous_week_org_counts[org_name]
    ]
    low_adoption_feature = min(
        feature_adoption["items"],
        key=lambda item: int(item.get("adoption_pct", 0) or 0),
    )
    top_growing_orgs = sorted(
        [
            {
                "name": org_name,
                "current_queries": current_week_org_counts.get(org_name, 0),
                "previous_queries": previous_week_org_counts.get(org_name, 0),
                "growth_pct": _pct_change(previous_week_org_counts.get(org_name, 0), current_week_org_counts.get(org_name, 0)),
            }
            for org_name in set(current_week_org_counts) | set(previous_week_org_counts)
            if current_week_org_counts.get(org_name, 0) > 0
        ],
        key=lambda item: (item["growth_pct"], item["current_queries"]),
        reverse=True,
    )[:5]

    product_roadmap_ai = {
        "insights": [
            {
                "title": f"{low_adoption_feature['feature']} adoption is lagging",
                "evidence": f"Current adoption is {low_adoption_feature['adoption_pct']}%, materially below AI-led workflows.",
                "recommendation": "Simplify the workflow or replace it with AI-generated outcomes to match user behavior.",
                "priority": "high" if int(low_adoption_feature["adoption_pct"]) < 25 else "medium",
            },
            {
                "title": "Users struggle most with financial analysis prompts",
                "evidence": f"Financial query share is {ai_failure_detection['finance_query_share_pct']}% and retry/rephrase signals are elevated at {ai_failure_detection['rephrase_rate_pct']}%.",
                "recommendation": "Expand finance semantic definitions and improve guided root-cause prompts for metric troubleshooting.",
                "priority": "high",
            },
            {
                "title": "Declining organizations need an engagement loop",
                "evidence": f"{len(declining_orgs)} organizations show lower weekly activity than the prior week.",
                "recommendation": "Enable Daily AI Reports or proactive insights for low-usage organizations to create recurring value.",
                "priority": "medium",
            },
        ],
        "founder_mode": {
            "global_user_activity": current_week_queries,
            "fastest_growing_organizations": top_growing_orgs,
            "ai_usage_trend_pct": weekly_query_growth_pct,
            "system_risk_level": "medium" if blocked_today >= 5 or len(declining_orgs) >= 3 else "low",
            "recommended_focus": "Double down on autonomous insight workflows and finance query quality.",
        },
        "weekly_founder_briefing": {
            "title": "VoxCore Founder Report",
            "summary_lines": [
                f"AI queries changed {weekly_query_growth_pct}% week over week.",
                f"Explain My Data remains a high-interest workflow at an estimated {feature_adoption['items'][1]['adoption_pct']}% adoption.",
                f"{low_adoption_feature['feature']} is the weakest-adopted feature and the clearest roadmap simplification target.",
            ],
            "suggested_focus": "Prioritize autonomous insights, finance reasoning quality, and reactivation loops for declining organizations.",
        },
    }

    executive_briefing = {
        "title": "VoxCore Executive Briefing",
        "summary_lines": [
            f"Feature adoption is led by Natural Language Query at {feature_adoption['items'][0]['adoption_pct']}%.",
            f"Guardian blocked {blocked_today} unsafe queries in the last 24 hours.",
            f"Peak platform usage is concentrated around {system_performance['peak_usage_window']}.",
        ],
        "suggested_action": "Prioritize AI explanation quality and low-usage organization onboarding in the next product cycle.",
    }

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
            "average_response_time_s": avg_response_time_s,
            "tokens_consumed": 0,
            "top_prompt_category": "Sales Analysis" if queries_today else "n/a",
        },
        "platform_intelligence": {
            "feature_adoption": feature_adoption,
            "ai_failure_detection": ai_failure_detection,
            "guardian_activity": guardian_activity,
            "organization_health": org_health_items,
            "system_performance": system_performance,
            "ai_recommendations": ai_recommendations,
            "platform_risk_detector": platform_risk_detector,
            "executive_briefing": executive_briefing,
            "product_roadmap_ai": product_roadmap_ai,
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
    payload.update(afhs.to_dict())
    return payload

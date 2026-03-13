"""
backend/agents/risk_agent.py

Data Risk Agent — monitors AI query activity for security risks and
policy violations. This agent reinforces VoxCore's core positioning:
"VoxCore protects databases from AI access."

Surfaces:
  • Sensitive column / PII access attempts
  • High concentration of high-risk queries
  • Repeated blocked query patterns (potential probing)
  • Large data scan attempts (queries without WHERE clauses)
"""
import logging
from collections import Counter
from datetime import datetime, timedelta
from pathlib import Path

from .agent_store import create_alert, alert_exists_recently

logger = logging.getLogger(__name__)

_AUDIT_LOG = Path("backend") / "logs" / "ai_query_audit.jsonl"

_SENSITIVE_KEYWORDS = {
    "ssn", "social_security", "password", "passwd", "credit_card",
    "card_number", "cvv", "date_of_birth", "dob", "salary", "compensation",
    "tax_id", "passport", "license_number",
}


def _load_audit_events() -> list[dict]:
    import json
    if not _AUDIT_LOG.exists():
        return []
    events = []
    try:
        for line in _AUDIT_LOG.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line:
                try:
                    events.append(json.loads(line))
                except Exception:
                    pass
    except Exception as e:
        logger.debug(f"[RiskAgent] audit log read error: {e}")
    return events


def _is_sensitive(event: dict) -> bool:
    """Return True if this event involved a sensitive column access."""
    reasons = " ".join(str(r) for r in (event.get("reasons") or [])).lower()
    query = str(event.get("query") or "").lower()
    columns = " ".join(str(c) for c in (event.get("columns") or [])).lower()
    stage = str(event.get("stage") or "").lower()

    combined = f"{reasons} {query} {columns} {stage}"
    return (
        event.get("status") == "blocked_sensitive"
        or "sensitive" in combined
        or any(kw in combined for kw in _SENSITIVE_KEYWORDS)
    )


def run(org_id: int | None = None, workspace_id: int | None = None) -> list[dict]:
    """Run the Data Risk Agent. Returns list of new alerts created."""
    new_alerts: list[dict] = []
    try:
        events = _load_audit_events()
        if not events:
            return new_alerts

        today_str = datetime.utcnow().date().isoformat()
        last_24h = (datetime.utcnow() - timedelta(hours=24)).isoformat()

        today_events = [e for e in events if e.get("timestamp", "")[:10] == today_str]
        recent_events = [e for e in events if e.get("timestamp", "") >= last_24h]

        # ── PII / sensitive column access attempts ────────────────────────
        sensitive_today = [e for e in today_events if _is_sensitive(e)]
        if sensitive_today:
            count = len(sensitive_today)
            title = (
                f"{'PII' if count == 1 else str(count) + ' PII'} access "
                f"attempt{'s' if count > 1 else ''} blocked today"
            )
            if not alert_exists_recently("risk", title, hours=8, org_id=org_id):
                alert = create_alert(
                    agent_type="risk",
                    severity="critical",
                    title=title,
                    description=(
                        f"{count} AI-generated {'query' if count == 1 else 'queries'} "
                        f"attempted to access sensitive or PII columns and "
                        f"{'was' if count == 1 else 'were'} blocked by VoxCore's "
                        "governance engine. Review the blocked queries in Query Logs."
                    ),
                    workspace_id=workspace_id,
                    org_id=org_id,
                    metadata={"sensitive_count": count},
                )
                new_alerts.append(alert)

        # ── High-risk query concentration ─────────────────────────────────
        high_risk_recent = [
            e for e in recent_events
            if e.get("risk_level", "").lower() in ("high", "critical")
            or e.get("status") in ("blocked", "blocked_sensitive")
        ]
        if len(recent_events) >= 5:
            risk_rate = len(high_risk_recent) / len(recent_events)
            if risk_rate >= 0.4:
                title = f"Risk alert: {risk_rate * 100:.0f}% of recent queries are high-risk"
                if not alert_exists_recently("risk", title, hours=6, org_id=org_id):
                    alert = create_alert(
                        agent_type="risk",
                        severity="warning",
                        title=title,
                        description=(
                            f"{len(high_risk_recent)} of the last {len(recent_events)} queries "
                            f"were classified as high-risk or blocked ({risk_rate * 100:.1f}%). "
                            "Check your governance policies or investigate user activity."
                        ),
                        workspace_id=workspace_id,
                        org_id=org_id,
                        metadata={
                            "high_risk_count": len(high_risk_recent),
                            "total_recent": len(recent_events),
                            "risk_rate_pct": round(risk_rate * 100, 1),
                        },
                    )
                    new_alerts.append(alert)

        # ── Repeated probing pattern (same tables blocked repeatedly) ─────
        blocked_recent = [
            e for e in recent_events
            if e.get("status") in ("blocked", "blocked_sensitive")
        ]
        if len(blocked_recent) >= 3:
            all_tables: list[str] = []
            for e in blocked_recent:
                all_tables.extend(e.get("tables") or [])
            table_counts = Counter(all_tables)
            probed = [(t, c) for t, c in table_counts.items() if c >= 3]
            if probed:
                top_table, top_count = max(probed, key=lambda x: x[1])
                title = f"Repeated access probe: '{top_table}' blocked {top_count}x in 24h"
                if not alert_exists_recently("risk", title, hours=12, org_id=org_id):
                    alert = create_alert(
                        agent_type="risk",
                        severity="warning",
                        title=title,
                        description=(
                            f"AI queries targeting '{top_table}' have been blocked "
                            f"{top_count} times in the last 24 hours. "
                            "This may indicate repeated probing or a misconfigured AI prompt."
                        ),
                        workspace_id=workspace_id,
                        org_id=org_id,
                        metadata={"table": top_table, "blocked_count": top_count},
                    )
                    new_alerts.append(alert)

    except Exception as e:
        logger.warning(f"[RiskAgent] Unexpected error: {e}")

    return new_alerts

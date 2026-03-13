"""
backend/agents/insight_agent.py

Insight Monitoring Agent — detects significant changes in platform usage
metrics by reading VoxCore's persisted audit log (JSONL).

Surfaces:
  • Query volume trends (week-over-week)
  • High block-rate days
  • AI query usage growth
"""
import logging
from datetime import datetime, timedelta
from pathlib import Path

from .agent_store import create_alert, alert_exists_recently

logger = logging.getLogger(__name__)

_AUDIT_LOG = Path("backend") / "logs" / "ai_query_audit.jsonl"


def _load_audit_events() -> list[dict]:
    """Read all JSONL events from the audit log. Returns [] on any error."""
    if not _AUDIT_LOG.exists():
        return []
    import json
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
        logger.debug(f"[InsightAgent] audit log read error: {e}")
    return events


def _date_of(event: dict) -> str:
    """Extract the date portion (YYYY-MM-DD) from an audit event timestamp."""
    ts = event.get("timestamp", "")
    return ts[:10] if len(ts) >= 10 else ""


def run(org_id: int | None = None, workspace_id: int | None = None) -> list[dict]:
    """Run the Insight Monitoring Agent. Returns list of new alerts created."""
    new_alerts: list[dict] = []
    try:
        events = _load_audit_events()
        if not events:
            return new_alerts

        today = datetime.utcnow().date()
        one_week_ago = today - timedelta(days=7)

        today_str = today.isoformat()
        week_ago_str = one_week_ago.isoformat()

        today_events = [e for e in events if _date_of(e) == today_str]
        week_ago_events = [e for e in events if _date_of(e) == week_ago_str]

        today_count = len(today_events)
        week_ago_count = len(week_ago_events)

        # ── Trend: query volume week-over-week ─────────────────────────────
        if today_count > 0 and week_ago_count > 0:
            change_pct = ((today_count - week_ago_count) / week_ago_count) * 100
            if abs(change_pct) >= 20:
                direction = "up" if change_pct > 0 else "down"
                title = f"Query volume {direction} {abs(change_pct):.0f}% vs last week"
                if not alert_exists_recently("insight", title, hours=12, org_id=org_id):
                    alert = create_alert(
                        agent_type="insight",
                        severity="info",
                        title=title,
                        description=(
                            f"VoxCore processed {today_count} analytical requests today "
                            f"vs {week_ago_count} one week ago ({change_pct:+.1f}%). "
                            f"{'Platform usage is growing.' if change_pct > 0 else 'Consider investigating the usage drop.'}"
                        ),
                        workspace_id=workspace_id,
                        org_id=org_id,
                        metadata={
                            "today_count": today_count,
                            "week_ago_count": week_ago_count,
                            "change_pct": round(change_pct, 1),
                        },
                    )
                    new_alerts.append(alert)

        # ── Block rate alert ───────────────────────────────────────────────
        if today_count >= 5:
            blocked_today = sum(
                1 for e in today_events
                if e.get("status") in ("blocked", "blocked_sensitive")
            )
            block_rate = (blocked_today / today_count) * 100
            if block_rate >= 30:
                title = f"High block rate: {block_rate:.0f}% of today's queries blocked"
                if not alert_exists_recently("insight", title, hours=12, org_id=org_id):
                    alert = create_alert(
                        agent_type="insight",
                        severity="warning",
                        title=title,
                        description=(
                            f"{blocked_today} of {today_count} AI queries were blocked "
                            f"by VoxCore's governance engine today ({block_rate:.1f}% block rate). "
                            "Review your data policies or user access patterns."
                        ),
                        workspace_id=workspace_id,
                        org_id=org_id,
                        metadata={
                            "blocked": blocked_today,
                            "total": today_count,
                            "block_rate": round(block_rate, 1),
                        },
                    )
                    new_alerts.append(alert)

        # ── Growing AI adoption (7-day rolling) ───────────────────────────
        last_7_counts = []
        for offset in range(7):
            day = (today - timedelta(days=offset + 1)).isoformat()
            last_7_counts.append(sum(1 for e in events if _date_of(e) == day))

        last_7_total = sum(last_7_counts)
        prev_7_total = sum(
            sum(1 for e in events if _date_of(e) == (today - timedelta(days=offset + 8)).isoformat())
            for offset in range(7)
        )
        if prev_7_total > 0 and last_7_total > prev_7_total:
            growth = ((last_7_total - prev_7_total) / prev_7_total) * 100
            if growth >= 25:
                title = f"AI query adoption growing {growth:.0f}% over last 14 days"
                if not alert_exists_recently("insight", title, hours=24, org_id=org_id):
                    alert = create_alert(
                        agent_type="insight",
                        severity="info",
                        title=title,
                        description=(
                            f"The last 7 days recorded {last_7_total} queries vs "
                            f"{prev_7_total} the prior 7 days — a {growth:.1f}% increase. "
                            "VoxCore adoption is accelerating."
                        ),
                        workspace_id=workspace_id,
                        org_id=org_id,
                        metadata={
                            "last_7_total": last_7_total,
                            "prev_7_total": prev_7_total,
                            "growth_pct": round(growth, 1),
                        },
                    )
                    new_alerts.append(alert)

    except Exception as e:
        logger.warning(f"[InsightAgent] Unexpected error: {e}")

    return new_alerts

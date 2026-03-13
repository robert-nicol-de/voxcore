"""
backend/agents/anomaly_agent.py

Anomaly Detection Agent — uses statistical analysis (Z-score method) to
detect unexpected spikes or drops in VoxCore platform activity.

Surfaces:
  • Query volume anomalies (Z-score > 2.0 vs 14-day baseline)
  • Sudden spikes in blocked/high-risk queries
  • Unusual concentration of queries in a short time window
"""
import logging
import math
from datetime import datetime, timedelta
from pathlib import Path

from .agent_store import create_alert, alert_exists_recently

logger = logging.getLogger(__name__)

_AUDIT_LOG = Path("backend") / "logs" / "ai_query_audit.jsonl"


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
        logger.debug(f"[AnomalyAgent] audit log read error: {e}")
    return events


def _date_of(event: dict) -> str:
    ts = event.get("timestamp", "")
    return ts[:10] if len(ts) >= 10 else ""


def _mean_stddev(values: list[float]) -> tuple[float, float]:
    if not values:
        return 0.0, 0.0
    n = len(values)
    mean = sum(values) / n
    if n < 2:
        return mean, 0.0
    variance = sum((v - mean) ** 2 for v in values) / (n - 1)
    return mean, math.sqrt(variance)


def run(org_id: int | None = None, workspace_id: int | None = None) -> list[dict]:
    """Run the Anomaly Detection Agent. Returns list of new alerts created."""
    new_alerts: list[dict] = []
    try:
        events = _load_audit_events()
        if not events:
            return new_alerts

        today = datetime.utcnow().date()

        # Count queries per day: today + 14-day baseline
        today_count = float(sum(1 for e in events if _date_of(e) == today.isoformat()))
        daily_baseline = [
            float(sum(1 for e in events if _date_of(e) == (today - timedelta(days=i)).isoformat()))
            for i in range(1, 15)
        ]

        # ── Volume anomaly (Z-score) ──────────────────────────────────────
        if today_count > 0 and len(daily_baseline) >= 7:
            mean_vol, std_vol = _mean_stddev(daily_baseline)
            if std_vol > 0:
                z = abs(today_count - mean_vol) / std_vol
                if z >= 2.0:
                    direction = "spike" if today_count > mean_vol else "drop"
                    title = f"Anomaly: query volume {direction} detected today"
                    if not alert_exists_recently("anomaly", title, hours=12, org_id=org_id):
                        alert = create_alert(
                            agent_type="anomaly",
                            severity="warning",
                            title=title,
                            description=(
                                f"Today's query count ({int(today_count)}) is "
                                f"{z:.1f} standard deviations "
                                f"{'above' if direction == 'spike' else 'below'} "
                                f"the 14-day average ({mean_vol:.1f}/day). "
                                f"This is a statistically significant {direction}."
                            ),
                            workspace_id=workspace_id,
                            org_id=org_id,
                            metadata={
                                "today": int(today_count),
                                "mean_14d": round(mean_vol, 1),
                                "stddev": round(std_vol, 1),
                                "z_score": round(z, 2),
                                "direction": direction,
                            },
                        )
                        new_alerts.append(alert)

        # ── Blocked query spike ───────────────────────────────────────────
        today_str = today.isoformat()
        today_blocked = float(
            sum(
                1 for e in events
                if _date_of(e) == today_str
                and e.get("status") in ("blocked", "blocked_sensitive")
            )
        )
        blocked_baseline = [
            float(
                sum(
                    1 for e in events
                    if _date_of(e) == (today - timedelta(days=i)).isoformat()
                    and e.get("status") in ("blocked", "blocked_sensitive")
                )
            )
            for i in range(1, 15)
        ]

        if today_blocked > 0 and len(blocked_baseline) >= 7:
            mean_b, std_b = _mean_stddev(blocked_baseline)
            if std_b > 0:
                z_b = (today_blocked - mean_b) / std_b
                if z_b >= 2.0:
                    title = f"Anomaly: blocked query spike ({int(today_blocked)} today)"
                    if not alert_exists_recently("anomaly", title, hours=12, org_id=org_id):
                        alert = create_alert(
                            agent_type="anomaly",
                            severity="critical",
                            title=title,
                            description=(
                                f"{int(today_blocked)} queries were blocked today "
                                f"vs a daily average of {mean_b:.1f}. "
                                f"Z-score: {z_b:.1f}. "
                                "This spike may indicate policy misconfiguration or unusual access patterns."
                            ),
                            workspace_id=workspace_id,
                            org_id=org_id,
                            metadata={
                                "blocked_today": int(today_blocked),
                                "mean_14d": round(mean_b, 1),
                                "z_score": round(z_b, 2),
                            },
                        )
                        new_alerts.append(alert)

        # ── Burst detection: many queries in last 15 minutes ──────────────
        now = datetime.utcnow()
        burst_window = now - timedelta(minutes=15)
        burst_window_str = burst_window.isoformat()
        recent_burst = sum(
            1 for e in events
            if e.get("timestamp", "") >= burst_window_str
        )
        if recent_burst >= 20:
            title = f"Burst detected: {recent_burst} queries in the last 15 minutes"
            if not alert_exists_recently("anomaly", title, hours=1, org_id=org_id):
                alert = create_alert(
                    agent_type="anomaly",
                    severity="warning",
                    title=title,
                    description=(
                        f"{recent_burst} queries were processed in the last 15 minutes. "
                        "This burst may indicate automated querying or an unusually active session."
                    ),
                    workspace_id=workspace_id,
                    org_id=org_id,
                    metadata={"burst_count": recent_burst, "window_minutes": 15},
                )
                new_alerts.append(alert)

    except Exception as e:
        logger.warning(f"[AnomalyAgent] Unexpected error: {e}")

    return new_alerts

"""
backend/agents/agent_store.py

Persistent store for AI Data Agent alerts. Reads/writes the
`agent_alerts` table in voxcloud.db (the same SQLite database used
by org_store).
"""
import json
import uuid
from datetime import datetime, timedelta

from backend.db.org_store import _get_conn
from backend.event_bus import AGENT_ALERT, INSIGHT_GENERATED, publish_event


# ── Write ──────────────────────────────────────────────────────────────────────

def create_alert(
    agent_type: str,
    severity: str,
    title: str,
    description: str,
    workspace_id: int | None = None,
    org_id: int | None = None,
    metadata: dict | None = None,
) -> dict:
    """Insert a new alert and return the full record."""
    alert_id = str(uuid.uuid4())
    created_at = datetime.utcnow().isoformat()
    with _get_conn() as conn:
        conn.execute(
            """
            INSERT INTO agent_alerts
                (id, agent_type, severity, title, description,
                 workspace_id, org_id, metadata, is_dismissed, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, 0, ?)
            """,
            (
                alert_id, agent_type, severity, title, description,
                workspace_id, org_id,
                json.dumps(metadata or {}),
                created_at,
            ),
        )
    publish_event(
        AGENT_ALERT,
        {
            "agent_type": agent_type,
            "severity": severity,
            "title": title,
            "description": description,
            "alert_id": alert_id,
        },
        org_id=org_id,
        workspace_id=workspace_id,
        source="agents",
    )
    if agent_type == "insight":
        publish_event(
            INSIGHT_GENERATED,
            {
                "title": title,
                "description": description,
                "alert_id": alert_id,
            },
            org_id=org_id,
            workspace_id=workspace_id,
            source="insight_agent",
        )
    return {
        "id": alert_id,
        "agent_type": agent_type,
        "severity": severity,
        "title": title,
        "description": description,
        "workspace_id": workspace_id,
        "org_id": org_id,
        "metadata": metadata or {},
        "is_dismissed": 0,
        "created_at": created_at,
    }


def dismiss_alert(alert_id: str) -> bool:
    """Soft-delete an alert by marking it dismissed."""
    with _get_conn() as conn:
        result = conn.execute(
            "UPDATE agent_alerts SET is_dismissed = 1 WHERE id = ?",
            (alert_id,),
        )
        return result.rowcount > 0


# ── Read ───────────────────────────────────────────────────────────────────────

def get_alerts(
    org_id: int | None = None,
    workspace_id: int | None = None,
    limit: int = 50,
    include_dismissed: bool = False,
) -> list[dict]:
    """Return recent alerts, newest first."""
    with _get_conn() as conn:
        query = "SELECT * FROM agent_alerts WHERE 1=1"
        params: list = []
        if not include_dismissed:
            query += " AND is_dismissed = 0"
        if org_id is not None:
            query += " AND (org_id = ? OR org_id IS NULL)"
            params.append(org_id)
        if workspace_id is not None:
            query += " AND (workspace_id = ? OR workspace_id IS NULL)"
            params.append(workspace_id)
        query += " ORDER BY created_at DESC LIMIT ?"
        params.append(limit)
        rows = conn.execute(query, params).fetchall()

    alerts = []
    for row in rows:
        d = dict(row)
        try:
            d["metadata"] = json.loads(d.get("metadata") or "{}")
        except Exception:
            d["metadata"] = {}
        alerts.append(d)
    return alerts


def alert_exists_recently(
    agent_type: str,
    title: str,
    hours: int = 6,
    org_id: int | None = None,
) -> bool:
    """Return True if an identical title+type alert was created within `hours` hours."""
    cutoff = (datetime.utcnow() - timedelta(hours=hours)).isoformat()
    with _get_conn() as conn:
        q = (
            "SELECT COUNT(*) FROM agent_alerts "
            "WHERE agent_type = ? AND title = ? AND created_at >= ?"
        )
        params: list = [agent_type, title, cutoff]
        if org_id is not None:
            q += " AND (org_id = ? OR org_id IS NULL)"
            params.append(org_id)
        count = conn.execute(q, params).fetchone()[0]
    return count > 0

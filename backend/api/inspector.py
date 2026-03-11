from fastapi import APIRouter
from backend.services.query_metrics import (
    get_recent_queries,
    get_risk_distribution,
    get_system_metrics,
)
from backend.services.approval_queue import list_pending
from backend.services.audit_logger import get_recent_audit_events

router = APIRouter()


@router.get("/api/inspector")
def inspector_dashboard():
    """Aggregated payload for the AI Query Inspector dashboard."""
    recent_queries = get_recent_queries(50)
    risk_distribution = get_risk_distribution()
    system_metrics = get_system_metrics()
    audit_events = get_recent_audit_events(100)

    # Serialize datetime objects
    serializable_queries = []
    for row in recent_queries:
        row_copy = dict(row)
        if row_copy.get("created_at"):
            row_copy["created_at"] = row_copy["created_at"].isoformat()
        serializable_queries.append(row_copy)

    pending_raw = list_pending()
    serializable_pending = []
    for row in pending_raw:
        row_copy = dict(row)
        if row_copy.get("created_at"):
            row_copy["submitted_at"] = row_copy["created_at"].isoformat()
        elif row_copy.get("submitted_at"):
            row_copy["submitted_at"] = row_copy["submitted_at"].isoformat()
        serializable_pending.append(row_copy)

    return {
        "recent_queries": serializable_queries,
        "pending_approvals": serializable_pending,
        "firewall_audit": audit_events,
        "risk_distribution": risk_distribution,
        "system_metrics": system_metrics,
    }

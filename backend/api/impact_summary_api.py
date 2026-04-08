from fastapi import APIRouter
from datetime import datetime, timedelta
from .action_api import ACTION_EXECUTIONS

router = APIRouter()

@router.get("/api/actions/impact-summary")
def impact_summary():
    # Only consider actions in the last 7 days
    now = datetime.utcnow()
    week_ago = now - timedelta(days=7)
    total_impact = 0.0
    success_count = 0
    fail_count = 0
    for e in ACTION_EXECUTIONS:
        try:
            if e.get("evaluated_at"):
                dt = datetime.fromisoformat(e["evaluated_at"])
                if dt < week_ago:
                    continue
            else:
                continue
            if e.get("status") == "completed":
                impact = e.get("impact", 0.0)
                total_impact += impact * 100
                if impact > 0:
                    success_count += 1
                else:
                    fail_count += 1
        except Exception:
            continue
    return {
        "total_impact": total_impact,
        "success_count": success_count,
        "fail_count": fail_count
    }

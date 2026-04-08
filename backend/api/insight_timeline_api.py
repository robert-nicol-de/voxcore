from voxcore.engine.insight_memory import InsightMemory

insight_memory = InsightMemory()

# Compatibility function for legacy imports
def get_timeline_events():
    return insight_memory.get_all_insights()
from fastapi import APIRouter
from typing import List, Dict
from datetime import datetime
from backend.api.action_api import ACTION_EXECUTIONS

router = APIRouter()

def build_timeline_for_insight(insight_id: str) -> List[Dict]:
    # Demo: build timeline from action executions for this insight
    events = []
    # 1. Insight detected (use first execution timestamp or fake)
    executions = [e for e in ACTION_EXECUTIONS if e.get("insight_id") == insight_id]
    if executions:
        first = min(executions, key=lambda e: e.get("created_at", ""))
        events.append({
            "id": f"insight-{insight_id}",
            "type": "insight",
            "title": f"Insight detected: {insight_id}",
            "timestamp": first.get("created_at", datetime.utcnow().isoformat())
        })
        # 2. Actions taken
        for e in executions:
            if e.get("auto"):
                events.append({
                    "id": f"auto-{e['execution_id']}",
                    "type": "auto_action",
                    "title": f"Auto Action: {e['action_id']}",
                    "timestamp": e.get("created_at", "")
                })
            else:
                events.append({
                    "id": f"action-{e['execution_id']}",
                    "type": "action",
                    "title": f"Action taken: {e['action_id']}",
                    "timestamp": e.get("created_at", "")
                })
            # 3. Result measured
            if e.get("status") == "completed" and e.get("impact") is not None:
                events.append({
                    "id": f"result-{e['execution_id']}",
                    "type": "result",
                    "title": f"Result: {e['metric']} changed",
                    "timestamp": e.get("evaluated_at", ""),
                    "impact": e.get("impact")
                })
    return sorted(events, key=lambda ev: ev["timestamp"])

@router.get("/api/insights/{insight_id}/timeline")
def get_insight_timeline(insight_id: str):
    return build_timeline_for_insight(insight_id)

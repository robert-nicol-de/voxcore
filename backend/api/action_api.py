
from fastapi import APIRouter, Request
from datetime import datetime
from typing import Dict, List
import uuid
import threading
import time

router = APIRouter()

# In-memory action log and executions (replace with DB in prod)
ACTION_LOG: List[Dict] = []
ACTION_EXECUTIONS: List[Dict] = []

def get_current_metric(insight_or_execution):
    # DEMO: Return a fake metric value (replace with real metric lookup)
    # Use insight_or_execution["metric"] and ["entity"] if present
    import random
    return 1200000 + random.randint(-100000, 200000)

def classify_impact(change):
    if change > 0.1:
        return "high_positive"
    elif change > 0:
        return "positive"
    elif change < -0.1:
        return "negative"
    else:
        return "neutral"

@router.post("/api/actions/execute")
async def execute_action(request: Request):
    data = await request.json()
    action_id = data.get("action_id")
    insight_id = data.get("insight_id")
    user_id = data.get("user_id")
    metric = data.get("metric", "revenue")
    entity = data.get("entity", "South region")
    baseline = get_current_metric({"metric": metric, "entity": entity})
    execution_id = str(uuid.uuid4())
    timestamp = datetime.utcnow().isoformat()
    entry = {
        "execution_id": execution_id,
        "action_id": action_id,
        "insight_id": insight_id,
        "user_id": user_id,
        "metric": metric,
        "entity": entity,
        "baseline_value": baseline,
        "current_value": None,
        "status": "pending",
        "created_at": timestamp,
        "evaluated_at": None,
        "impact": None,
        "result": None
    }
    ACTION_EXECUTIONS.append(entry)
    ACTION_LOG.append({
        "action_id": action_id,
        "insight_id": insight_id,
        "user_id": user_id,
        "executed": True,
        "timestamp": timestamp,
        "execution_id": execution_id
    })
    return {"status": "executed", "entry": entry}

@router.get("/api/actions/recent")
async def recent_actions():
    # Return last 10 actions
    return {"actions": ACTION_LOG[-10:][::-1]}

@router.get("/api/actions/executions/{insight_id}")
async def get_executions(insight_id: str):
    return {"executions": [e for e in ACTION_EXECUTIONS if e["insight_id"] == insight_id]}

# Outcome evaluator worker (runs in background)
def outcome_evaluator_worker():
    while True:
        time.sleep(60)  # Run every 1 min (demo)
        for e in ACTION_EXECUTIONS:
            if e["status"] == "pending":
                current = get_current_metric(e)
                change = (current - e["baseline_value"]) / e["baseline_value"]
                e["current_value"] = current
                e["impact"] = change
                e["status"] = "completed"
                e["evaluated_at"] = datetime.utcnow().isoformat()
                e["result"] = classify_impact(change)

# Start background worker thread
threading.Thread(target=outcome_evaluator_worker, daemon=True).start()

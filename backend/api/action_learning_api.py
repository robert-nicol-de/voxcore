# Action Learning Model and Aggregation Worker
from fastapi import APIRouter
from typing import Dict, List
from collections import defaultdict
from .action_api import ACTION_EXECUTIONS
import threading
import time

router = APIRouter()

# In-memory learning store (replace with DB in prod)
ACTION_LEARNING: Dict[str, Dict] = {}

def group_by_action_context(executions: List[Dict]) -> Dict[str, List[Dict]]:
    grouped = defaultdict(list)
    for e in executions:
        key = f"{e.get('action_id')}|{e.get('metric')}|{e.get('entity')}"
        grouped[key].append(e)
    return grouped

def calc_success(group: List[Dict]) -> float:
    if not group:
        return 0.0
    return sum(1 for e in group if e.get("impact", 0) > 0) / len(group)

def calc_avg_impact(group: List[Dict]) -> float:
    if not group:
        return 0.0
    return sum(e.get("impact", 0) for e in group) / len(group)

def upsert_learning_record(record: Dict):
    key = f"{record['action_type']}|{record['metric']}|{record['context']}"
    ACTION_LEARNING[key] = record

def update_action_learning():
    executions = [e for e in ACTION_EXECUTIONS if e.get("status") == "completed"]
    grouped = group_by_action_context(executions)
    for key, group in grouped.items():
        action_id, metric, context = key.split("|", 2)
        upsert_learning_record({
            "action_type": action_id,
            "metric": metric,
            "context": context,
            "executions": len(group),
            "success_rate": calc_success(group),
            "avg_impact": calc_avg_impact(group)
        })

# Background worker to update learning every 2 minutes
def action_learning_worker():
    while True:
        update_action_learning()
        time.sleep(120)

threading.Thread(target=action_learning_worker, daemon=True).start()

@router.get("/api/actions/learning/{action_id}/{metric}/{context}")
def get_action_learning(action_id: str, metric: str, context: str):
    key = f"{action_id}|{metric}|{context}"
    return ACTION_LEARNING.get(key, {})

@router.get("/api/actions/learning/all")
def get_all_action_learning():
    return list(ACTION_LEARNING.values())

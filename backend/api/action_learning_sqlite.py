import sqlite3
from datetime import datetime
from typing import Dict, List, Tuple
import threading
import time
from fastapi import APIRouter
from .action_api import ACTION_EXECUTIONS

DB_PATH = "backend/db/voxcore.db"
SCHEMA_PATH = "backend/db/schema_action_learning.sql"

router = APIRouter()

def init_db():
    conn = sqlite3.connect(DB_PATH)
    with open(SCHEMA_PATH, "r") as f:
        conn.executescript(f.read())
    conn.commit()
    conn.close()

init_db()

def upsert_learning(record: Dict):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        INSERT INTO action_learning (id, action_type, metric, dimension, context, executions, successes, failures, success_rate, avg_impact, last_updated)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(id) DO UPDATE SET
            executions=excluded.executions,
            successes=excluded.successes,
            failures=excluded.failures,
            success_rate=excluded.success_rate,
            avg_impact=excluded.avg_impact,
            last_updated=excluded.last_updated
    """, (
        record["id"], record["action_type"], record["metric"], record["dimension"], record["context"],
        record["executions"], record["successes"], record["failures"],
        record["success_rate"], record["avg_impact"], record["last_updated"]
    ))
    conn.commit()
    conn.close()

def get_all_learning() -> List[Dict]:
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT action_type, metric, dimension, context, executions, successes, failures, success_rate, avg_impact, last_updated FROM action_learning")
    rows = c.fetchall()
    conn.close()
    return [
        {
            "action_type": r[0], "metric": r[1], "dimension": r[2], "context": r[3],
            "executions": r[4], "successes": r[5], "failures": r[6],
            "success_rate": r[7], "avg_impact": r[8], "last_updated": r[9]
        } for r in rows
    ]

def get_learning(action_type: str, metric: str, dimension: str, context: str) -> Dict:
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT action_type, metric, dimension, context, executions, successes, failures, success_rate, avg_impact, last_updated FROM action_learning WHERE action_type=? AND metric=? AND dimension=? AND context=?",
              (action_type, metric, dimension, context))
    row = c.fetchone()
    conn.close()
    if row:
        return {
            "action_type": row[0], "metric": row[1], "dimension": row[2], "context": row[3],
            "executions": row[4], "successes": row[5], "failures": row[6],
            "success_rate": row[7], "avg_impact": row[8], "last_updated": row[9]
        }
    return {}

def group_by_action_context(executions: List[Dict]) -> Dict[Tuple, List[Dict]]:
    grouped = {}
    for e in executions:
        key = (
            e.get("action_id"),
            e.get("metric", "revenue"),
            e.get("dimension", "region"),
            e.get("entity", "default")
        )
        grouped.setdefault(key, []).append(e)
    return grouped

def update_learning():
    executions = [e for e in ACTION_EXECUTIONS if e.get("status") == "completed"]
    grouped = group_by_action_context(executions)
    for key, group in grouped.items():
        action_type, metric, dimension, context = key
        total = len(group)
        successes = sum(1 for g in group if g.get("impact", 0) > 0.05)
        failures = sum(1 for g in group if g.get("impact", 0) <= 0)
        avg_impact = sum(g.get("impact", 0) for g in group) / total if total else 0
        success_rate = successes / total if total else 0
        upsert_learning({
            "id": f"{action_type}|{metric}|{dimension}|{context}",
            "action_type": action_type,
            "metric": metric,
            "dimension": dimension,
            "context": context,
            "executions": total,
            "successes": successes,
            "failures": failures,
            "success_rate": success_rate,
            "avg_impact": avg_impact,
            "last_updated": datetime.utcnow().isoformat()
        })

def learning_worker():
    while True:
        update_learning()
        time.sleep(120)

threading.Thread(target=learning_worker, daemon=True).start()

@router.get("/api/actions/learning")
def api_get_all_learning():
    return get_all_learning()

@router.get("/api/actions/learning/{action_type}/{metric}/{dimension}/{context}")
def api_get_learning(action_type: str, metric: str, dimension: str, context: str):
    return get_learning(action_type, metric, dimension, context)

import sqlite3
from datetime import datetime
from typing import Dict, List
from fastapi import APIRouter, Body
import uuid

DB_PATH = "backend/db/voxcore.db"
SCHEMA_PATH = "backend/db/schema_auto_action_rules.sql"

router = APIRouter()

def init_db():
    conn = sqlite3.connect(DB_PATH)
    with open(SCHEMA_PATH, "r") as f:
        conn.executescript(f.read())
    conn.commit()
    conn.close()

init_db()

def upsert_auto_action_rule(rule: Dict):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        INSERT INTO auto_action_rules (
            id, action_type, metric, dimension, context,
            min_confidence, min_success_rate, min_avg_impact,
            enabled, mode, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(id) DO UPDATE SET
            min_confidence=excluded.min_confidence,
            min_success_rate=excluded.min_success_rate,
            min_avg_impact=excluded.min_avg_impact,
            enabled=excluded.enabled,
            mode=excluded.mode
    """, (
        rule["id"], rule["action_type"], rule["metric"], rule["dimension"], rule["context"],
        rule["min_confidence"], rule["min_success_rate"], rule["min_avg_impact"],
        int(rule["enabled"]), rule["mode"], rule["created_at"]
    ))
    conn.commit()
    conn.close()

def get_auto_action_rules() -> List[Dict]:
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT id, action_type, metric, dimension, context, min_confidence, min_success_rate, min_avg_impact, enabled, mode, created_at FROM auto_action_rules")
    rows = c.fetchall()
    conn.close()
    return [
        {
            "id": r[0], "action_type": r[1], "metric": r[2], "dimension": r[3], "context": r[4],
            "min_confidence": r[5], "min_success_rate": r[6], "min_avg_impact": r[7],
            "enabled": bool(r[8]), "mode": r[9], "created_at": r[10]
        } for r in rows
    ]

def get_matching_rules(insight: Dict) -> List[Dict]:
    # Simple match: action_type, metric, dimension, context
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        SELECT id, action_type, metric, dimension, context, min_confidence, min_success_rate, min_avg_impact, enabled, mode, created_at
        FROM auto_action_rules
        WHERE enabled=1 AND action_type=? AND metric=? AND context=?
    """, (
        insight["action_type"], insight["metric"], insight["context"]
    ))
    rows = c.fetchall()
    conn.close()
    return [
        {
            "id": r[0], "action_type": r[1], "metric": r[2], "dimension": r[3], "context": r[4],
            "min_confidence": r[5], "min_success_rate": r[6], "min_avg_impact": r[7],
            "enabled": bool(r[8]), "mode": r[9], "created_at": r[10]
        } for r in rows
    ]

@router.post("/api/actions/auto-rule")
def api_upsert_auto_rule(rule: Dict = Body(...)):
    rule_id = rule.get("id") or str(uuid.uuid4())
    rule["id"] = rule_id
    rule["created_at"] = rule.get("created_at") or datetime.utcnow().isoformat()
    upsert_auto_action_rule(rule)
    return {"status": "ok", "id": rule_id}

@router.get("/api/actions/auto-rules")
def api_get_auto_rules():
    return get_auto_action_rules()

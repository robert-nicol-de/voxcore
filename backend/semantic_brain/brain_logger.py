from __future__ import annotations

import json
import os
import uuid
import time
from typing import Any

_LOG_DIR  = os.path.join(os.path.dirname(__file__), "..", "logs")
_LOG_PATH = os.path.join(_LOG_DIR, "brain_queries.jsonl")


class BrainLogger:
    """
    Structured append-only query logger for the VoxCore Brain.

    Log entries are written as JSON Lines to ``backend/logs/brain_queries.jsonl``.

    Log entry shape::

        {
          "query_id":          "q3f8a12b",
          "timestamp":         "2026-03-15T12:00:00Z",
          "workspace_id":      1,
          "query_text":        "Sales YoY by district",
          "intent_type":       "time_comparison",
          "metric":            "sales",
          "dimension":         "district",
          "confidence":        0.92,
          "difficulty_level":  2,
          "sql_risk":          "low",
          "execution_time_ms": 142.7,
          "semantic_valid":    true,
          "sql_valid":         true,
          "issues":            []
        }

    All I/O is wrapped in try/except so a logging failure never blocks a query.
    """

    def __init__(self) -> None:
        os.makedirs(_LOG_DIR, exist_ok=True)

    def log(
        self,
        query_text: str,
        intent_type: str,
        metric: str,
        dimension: str,
        confidence: float,
        difficulty_level: int,
        sql_risk: str,
        execution_time_ms: float,
        semantic_valid: bool = True,
        sql_valid: bool = True,
        issues: list[str] | None = None,
        workspace_id: Any = None,
        extra: dict[str, Any] | None = None,
    ) -> str:
        """Write one structured log entry and return the generated query_id."""
        query_id = f"q{uuid.uuid4().hex[:8]}"
        entry: dict[str, Any] = {
            "query_id":          query_id,
            "timestamp":         time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "workspace_id":      workspace_id,
            "query_text":        (query_text or "")[:200],
            "intent_type":       intent_type,
            "metric":            metric,
            "dimension":         dimension,
            "confidence":        round(float(confidence), 3),
            "difficulty_level":  int(difficulty_level),
            "sql_risk":          sql_risk,
            "execution_time_ms": round(float(execution_time_ms), 1),
            "semantic_valid":    bool(semantic_valid),
            "sql_valid":         bool(sql_valid),
            "issues":            list(issues or []),
        }
        if extra:
            # Extra fields are appended but never overwrite core fields.
            for k, v in extra.items():
                if k not in entry:
                    entry[k] = v
        try:
            with open(_LOG_PATH, "a", encoding="utf-8") as fh:
                fh.write(json.dumps(entry, default=str) + "\n")
        except Exception:
            pass
        return query_id

    def recent(self, limit: int = 50) -> list[dict[str, Any]]:
        """Return the most recent *limit* log entries."""
        records: list[dict[str, Any]] = []
        try:
            if not os.path.exists(_LOG_PATH):
                return []
            with open(_LOG_PATH, "r", encoding="utf-8") as fh:
                for line in fh:
                    stripped = line.strip()
                    if stripped:
                        try:
                            records.append(json.loads(stripped))
                        except Exception:
                            pass
        except Exception:
            pass
        return records[-limit:]

from __future__ import annotations

import json
import os
import time
from typing import Any

_STORE_DIR = os.path.join(os.path.dirname(__file__), "training_data")
_KB_PATH   = os.path.join(_STORE_DIR, "knowledge_base.json")


class QueryKnowledgeStore:
    """
    File-backed store of successful query patterns for learning and recall.

    The knowledge base is a JSON object keyed by a canonical
    ``metric::dimension`` signature.  Each entry tracks success/failure counts
    so hit-rate can be estimated and used as a confidence signal.

    All I/O is wrapped in try/except so a missing or corrupt file never blocks
    a query.
    """

    def __init__(self) -> None:
        os.makedirs(_STORE_DIR, exist_ok=True)
        self._data: dict[str, Any] = self._load()

    # ── Persistence ────────────────────────────────────────────────────────
    def _load(self) -> dict[str, Any]:
        try:
            if os.path.exists(_KB_PATH):
                with open(_KB_PATH, "r", encoding="utf-8") as fh:
                    return json.load(fh)
        except Exception:
            pass
        return {}

    def _save(self) -> None:
        try:
            with open(_KB_PATH, "w", encoding="utf-8") as fh:
                json.dump(self._data, fh, indent=2, default=str)
        except Exception:
            pass

    # ── Key generation ─────────────────────────────────────────────────────
    @staticmethod
    def _sig(metric: str, dimension: str) -> str:
        return f"{(metric or '').lower().strip()}::{(dimension or '').lower().strip()}"

    # ── Public API ─────────────────────────────────────────────────────────
    def record_success(
        self,
        metric: str,
        dimension: str,
        intent_type: str,
        sql: str,
        query_text: str = "",
    ) -> None:
        """Increment the success counter for a metric+dimension pair."""
        sig = self._sig(metric, dimension)
        entry = self._data.get(sig) or {
            "metric":        metric,
            "dimension":     dimension,
            "intent_type":   intent_type,
            "sql":           sql,
            "query_text":    query_text,
            "success_count": 0,
            "fail_count":    0,
            "last_seen":     "",
        }
        entry["success_count"] = int(entry.get("success_count") or 0) + 1
        entry["last_seen"]     = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        if sql:
            entry["sql"] = sql
        self._data[sig] = entry
        self._save()

    def record_failure(self, metric: str, dimension: str) -> None:
        """Increment the failure counter for a metric+dimension pair."""
        sig = self._sig(metric, dimension)
        if sig in self._data:
            self._data[sig]["fail_count"] = int(self._data[sig].get("fail_count") or 0) + 1
            self._save()

    def find_pattern(self, metric: str, dimension: str) -> dict[str, Any] | None:
        """Return the stored pattern for this metric+dimension, or None."""
        return self._data.get(self._sig(metric, dimension))

    def success_rate(self, metric: str, dimension: str) -> float:
        """
        Return the observed success rate for a metric+dimension pair.
        Returns 0.75 (neutral prior) when no history is available.
        """
        entry = self.find_pattern(metric, dimension)
        if not entry:
            return 0.75
        total = int(entry.get("success_count") or 0) + int(entry.get("fail_count") or 0)
        return round(int(entry.get("success_count") or 0) / total, 2) if total > 0 else 0.75

    def list_patterns(self, limit: int = 20) -> list[dict[str, Any]]:
        """Return the most recently stored patterns (up to *limit*)."""
        return list(self._data.values())[:limit]

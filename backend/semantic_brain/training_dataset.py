from __future__ import annotations

import json
import os
import time
from typing import Any

_STORE_DIR   = os.path.join(os.path.dirname(__file__), "training_data")
_DATASET_PATH = os.path.join(_STORE_DIR, "dataset.jsonl")

_VALID_QUERY_TYPES = frozenset({
    "simple_aggregation",
    "time_comparison",
    "ranking",
    "multi_dimension",
    "diagnostic",
    "trend",
})


class TrainingDataset:
    """
    Append-only JSONL training dataset for VoxCore Brain.

    Each record captures a resolved query example that can be used for
    offline analysis, prompt-tuning, or rule refinement.

    Dataset entry shape::

        {
          "question":        "Top customers by revenue",
          "intent":          "ranking",
          "metric":          "revenue",
          "dimension":       "customer",
          "expected_sql":    "SELECT ...",
          "query_type":      "ranking",
          "confidence":      0.91,
          "difficulty_level": 2,
          "tags":            [],
          "recorded_at":     "2026-03-15T12:00:00Z"
        }

    Supported query_type values:
        simple_aggregation, time_comparison, ranking,
        multi_dimension, diagnostic, trend
    """

    def __init__(self) -> None:
        os.makedirs(_STORE_DIR, exist_ok=True)

    def record(
        self,
        question: str,
        intent_type: str,
        metric: str,
        dimension: str,
        sql: str,
        confidence: float = 1.0,
        difficulty_level: int = 1,
        tags: list[str] | None = None,
    ) -> None:
        """Append a training example to the dataset JSONL file."""
        query_type = intent_type if intent_type in _VALID_QUERY_TYPES else "simple_aggregation"
        entry: dict[str, Any] = {
            "question":        (question or "")[:500],
            "intent":          intent_type,
            "metric":          metric,
            "dimension":       dimension,
            "expected_sql":    (sql or "")[:2000],
            "query_type":      query_type,
            "confidence":      round(float(confidence), 3),
            "difficulty_level": int(difficulty_level),
            "tags":            tags or [],
            "recorded_at":     time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        }
        try:
            with open(_DATASET_PATH, "a", encoding="utf-8") as fh:
                fh.write(json.dumps(entry, default=str) + "\n")
        except Exception:
            pass

    def load(self, limit: int = 200) -> list[dict[str, Any]]:
        """Load the most recent *limit* training examples."""
        records: list[dict[str, Any]] = []
        try:
            if not os.path.exists(_DATASET_PATH):
                return []
            with open(_DATASET_PATH, "r", encoding="utf-8") as fh:
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

    def stats(self) -> dict[str, Any]:
        """Return aggregate statistics about the dataset."""
        records = self.load(limit=10_000)
        by_type:       dict[str, int] = {}
        by_difficulty: dict[str, int] = {}
        for rec in records:
            qt  = str(rec.get("query_type") or "unknown")
            lvl = str(rec.get("difficulty_level") or 1)
            by_type[qt]       = by_type.get(qt, 0) + 1
            by_difficulty[lvl] = by_difficulty.get(lvl, 0) + 1
        return {
            "total_examples":  len(records),
            "by_query_type":   by_type,
            "by_difficulty":   by_difficulty,
        }

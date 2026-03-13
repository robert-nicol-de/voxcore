from __future__ import annotations

from typing import Any


class SchemaIntelligence:
    def _score(self, query_tokens: set[str], candidate: str) -> float:
        c_tokens = set((candidate or "").lower().replace("_", " ").split())
        if not c_tokens:
            return 0.0
        overlap = len(query_tokens & c_tokens)
        return overlap / max(len(c_tokens), 1)

    def match_terms(self, query_text: str, snapshot: dict[str, Any], top_k: int = 5) -> list[dict[str, Any]]:
        query_tokens = set((query_text or "").lower().replace("_", " ").split())
        scored: list[dict[str, Any]] = []

        for metric in snapshot.get("metric_registry", [])[:80]:
            name = str(metric.get("name") or "")
            score = self._score(query_tokens, name)
            if score > 0:
                scored.append({"type": "metric", "name": name, "score": round(score, 3)})

        for dimension in snapshot.get("dimension_catalog", [])[:150]:
            name = str(dimension.get("dimension") or dimension.get("column") or "")
            score = self._score(query_tokens, name)
            if score > 0:
                scored.append({"type": "dimension", "name": name, "score": round(score, 3)})

        scored.sort(key=lambda item: float(item.get("score") or 0), reverse=True)
        return scored[:top_k]

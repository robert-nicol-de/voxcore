from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class AnalysisSession:
    current_metric: str | None = None
    current_dimension: str | None = None
    current_comparison: str | None = None
    current_filters: dict[str, Any] = field(default_factory=dict)


class AnalysisSessionStore:
    def __init__(self) -> None:
        self._sessions: dict[str, AnalysisSession] = {}

    def get(self, key: str) -> AnalysisSession | None:
        return self._sessions.get(key)

    def upsert_from_plan(self, key: str, plan: dict[str, Any]) -> AnalysisSession:
        session = self._sessions.get(key) or AnalysisSession()
        session.current_metric = str(plan.get("metric") or session.current_metric or "") or None
        session.current_dimension = str(plan.get("dimension") or session.current_dimension or "") or None
        session.current_comparison = str(plan.get("comparison") or session.current_comparison or "") or None
        filters = dict(session.current_filters)
        if plan.get("focus"):
            filters["focus"] = plan.get("focus")
        if plan.get("limit"):
            filters["limit"] = plan.get("limit")
        session.current_filters = filters
        self._sessions[key] = session
        return session

    def as_dict(self, key: str) -> dict[str, Any]:
        session = self._sessions.get(key)
        if not session:
            return {}
        return {
            "metric": session.current_metric,
            "dimension": session.current_dimension,
            "comparison": session.current_comparison,
            "filters": session.current_filters,
        }

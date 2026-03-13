from __future__ import annotations

import re
from typing import Any

from .time_intelligence import default_time_grain, detect_time_comparison


class AnalyticalPlanner:
    def build_plan(
        self,
        query_text: str,
        intent: dict[str, Any],
        metric_sql: str,
        dimension_info: dict[str, str] | None,
        time_dimensions: list[str],
    ) -> dict[str, Any]:
        comparison = intent.get("comparison") or detect_time_comparison(query_text)
        analysis_type = "comparison" if comparison else "trend" if intent.get("has_trend") else "ranking"

        dimension = str(intent.get("dimension") or "district")
        return {
            "analysis_type": analysis_type,
            "metric": str(intent.get("metric") or "revenue"),
            "metric_sql": metric_sql,
            "dimension": dimension,
            "dimension_table": str((dimension_info or {}).get("table") or ""),
            "dimension_column": str((dimension_info or {}).get("column") or dimension),
            "comparison": comparison,
            "time_dimension": time_dimensions[0] if time_dimensions else "order_date",
            "time_grain": default_time_grain(comparison),
            "aggregation": "sum",
            "focus": None,
        }

    def apply_followup_context(
        self,
        query_text: str,
        plan: dict[str, Any],
        previous_plan: dict[str, Any] | None,
    ) -> dict[str, Any]:
        if not previous_plan:
            return plan

        text = (query_text or "").strip().lower()
        has_followup_token = any(token in text for token in ["why", "what drove", "drill", "breakdown", "that", "this", "it", "show only", "only"])
        has_top_n = re.search(r"top\s+(\d{1,3})", text) is not None
        is_followup = has_followup_token or has_top_n
        if not is_followup:
            return plan

        enriched = dict(plan)
        for key in ["metric", "dimension", "comparison", "time_dimension", "time_grain", "dimension_table", "dimension_column", "metric_sql"]:
            previous_value = previous_plan.get(key)
            if previous_value is not None:
                enriched[key] = previous_value

        focus_match = re.search(r"(?:why\s+did|in|for)\s+([a-z0-9_\- ]{2,40})", text)
        if focus_match:
            enriched["focus"] = focus_match.group(1).strip().title()
        elif previous_plan.get("focus"):
            enriched["focus"] = previous_plan.get("focus")

        if "why" in text or "what drove" in text:
            enriched["analysis_type"] = "diagnostic"

        top_match = re.search(r"top\s+(\d{1,3})", text)
        if top_match:
            try:
                enriched["limit"] = max(1, int(top_match.group(1)))
            except Exception:
                enriched["limit"] = 10

        return enriched

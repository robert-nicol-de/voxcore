from __future__ import annotations

from typing import Any


class VisualizationEngine:
    def recommend_chart(self, plan: dict[str, Any]) -> dict[str, str]:
        analysis_type = str(plan.get("analysis_type") or "").lower()
        comparison = str(plan.get("comparison") or "").lower()

        if analysis_type == "trend":
            chart = "line"
        elif analysis_type == "comparison" or comparison in {"yoy", "mom", "qoq"}:
            chart = "bar"
        elif analysis_type == "ranking":
            chart = "horizontal_bar"
        elif analysis_type == "composition":
            chart = "stacked_bar"
        else:
            chart = "table"

        return {
            "chart_type": chart,
            "reason": f"{analysis_type or 'comparison'} analysis maps best to {chart} visualization.",
        }

    def build_preview_chart(
        self,
        preview_rows: list[dict[str, Any]],
        intent: dict[str, Any],
        recommendation: dict[str, str],
    ) -> dict[str, Any] | None:
        if not preview_rows:
            return None

        first = preview_rows[0]
        if not isinstance(first, dict) or not first:
            return None

        dimension_hint = str(intent.get("dimension") or "").lower()
        metric_hint = str(intent.get("metric") or "").lower()
        keys = list(first.keys())
        dimension_key = next((k for k in keys if dimension_hint and dimension_hint in k.lower()), keys[0])

        numeric_keys = [
            key
            for key in keys
            if isinstance(first.get(key), (int, float)) and not isinstance(first.get(key), bool)
        ]
        metric_key = next((k for k in numeric_keys if metric_hint and metric_hint in k.lower()), None)
        if not metric_key and numeric_keys:
            metric_key = numeric_keys[0]
        if not metric_key:
            return None

        points = preview_rows[:12]
        return {
            "type": recommendation.get("chart_type", "bar"),
            "title": f"{str(intent.get('dimension') or dimension_key).capitalize()} {str(intent.get('metric') or metric_key).capitalize()}".strip(),
            "xAxis": {"data": [str(row.get(dimension_key, "")) for row in points], "name": dimension_key},
            "yAxis": {"name": metric_key},
            "series": [{"name": metric_key, "data": [float(row.get(metric_key, 0) or 0) for row in points]}],
        }

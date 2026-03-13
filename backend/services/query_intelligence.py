from __future__ import annotations

import re
from typing import Any


_DIMENSION_HINTS = [
    "district",
    "region",
    "country",
    "state",
    "city",
    "category",
    "segment",
    "product",
    "customer",
    "month",
    "year",
]

_METRIC_HINTS = [
    "sales",
    "revenue",
    "amount",
    "profit",
    "margin",
    "orders",
    "count",
    "growth",
    "yoy",
]


def _is_sql_like(text: str) -> bool:
    value = (text or "").strip().lower()
    return bool(re.search(r"\b(select|with|insert|update|delete|from|group by)\b", value))


def extract_schema_summary(ai_context: dict[str, Any], max_lines: int = 8) -> list[str]:
    prompt_context = str((ai_context or {}).get("prompt_context") or "").strip()
    if not prompt_context:
        return []

    summary_lines: list[str] = []
    for line in prompt_context.splitlines():
        if "(" in line and ")" in line and "/" in line:
            summary_lines.append(line.strip())
        if len(summary_lines) >= max_lines:
            break
    return summary_lines


def extract_query_intent(query_text: str) -> dict[str, Any]:
    text = (query_text or "").strip()
    lowered = text.lower()

    metric = "sales" if "sales" in lowered else "revenue" if "revenue" in lowered else "amount"
    for hint in _METRIC_HINTS:
        if hint in lowered:
            metric = hint
            break

    dimension = "time"
    for hint in _DIMENSION_HINTS:
        if hint in lowered:
            dimension = hint
            break

    comparison = None
    if "yoy" in lowered or "year over year" in lowered or "year-over-year" in lowered:
        comparison = "YoY"
    elif "mom" in lowered or "month over month" in lowered or "month-over-month" in lowered:
        comparison = "MoM"

    has_trend = any(token in lowered for token in ["trend", "over time", "timeline"]) or dimension in {
        "month",
        "year",
    }

    return {
        "metric": metric,
        "dimension": dimension,
        "comparison": comparison,
        "has_trend": has_trend,
        "is_sql_input": _is_sql_like(text),
    }


def recommend_chart(intent: dict[str, Any]) -> dict[str, str]:
    comparison = str(intent.get("comparison") or "")
    dimension = str(intent.get("dimension") or "")
    has_trend = bool(intent.get("has_trend"))

    if comparison == "YoY":
        chart_type = "bar" if dimension not in {"month", "year", "time"} else "line"
        reason = "Year-over-year comparisons are best shown as grouped trends."
    elif has_trend:
        chart_type = "line"
        reason = "Trend questions are clearer with a line chart."
    elif dimension in {"region", "district", "category", "product", "customer", "segment"}:
        chart_type = "bar"
        reason = "Categorical breakdowns are most readable as bars."
    else:
        chart_type = "bar"
        reason = "Defaulting to bar for categorical analytics readability."

    return {
        "chart_type": chart_type,
        "reason": reason,
    }


def suggest_sql(query_text: str, intent: dict[str, Any]) -> str:
    if intent.get("is_sql_input"):
        return query_text

    metric = str(intent.get("metric") or "sales")
    dimension = str(intent.get("dimension") or "district")
    comparison = str(intent.get("comparison") or "")

    if comparison == "YoY":
        return (
            "SELECT {dimension},\n"
            "       EXTRACT(YEAR FROM sale_date) AS year,\n"
            "       SUM({metric}) AS total_{metric}\n"
            "FROM sales\n"
            "GROUP BY {dimension}, EXTRACT(YEAR FROM sale_date)\n"
            "ORDER BY {dimension}, year"
        ).format(dimension=dimension, metric=metric)

    return (
        "SELECT {dimension}, SUM({metric}) AS total_{metric}\n"
        "FROM sales\n"
        "GROUP BY {dimension}\n"
        "ORDER BY total_{metric} DESC\n"
        "LIMIT 10"
    ).format(dimension=dimension, metric=metric)


def build_understanding(intent: dict[str, Any]) -> dict[str, str]:
    metric = str(intent.get("metric") or "sales").capitalize()
    dimension = str(intent.get("dimension") or "district").capitalize()
    comparison = str(intent.get("comparison") or "None")

    return {
        "metric": metric,
        "dimension": dimension,
        "comparison": comparison,
        "summary": f"Metric: {metric} | Dimension: {dimension} | Comparison: {comparison}",
    }


def build_preview_chart(preview_rows: list[dict[str, Any]], intent: dict[str, Any]) -> dict[str, Any] | None:
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
        k
        for k in keys
        if isinstance(first.get(k), (int, float))
        and not isinstance(first.get(k), bool)
    ]
    metric_key = next((k for k in numeric_keys if metric_hint and metric_hint in k.lower()), None)
    if not metric_key and numeric_keys:
        metric_key = numeric_keys[0]

    if not metric_key:
        return None

    points = preview_rows[:12]
    x_data = [str(row.get(dimension_key, "")) for row in points]
    y_data = [float(row.get(metric_key, 0) or 0) for row in points]

    chart_meta = recommend_chart(intent)
    title_suffix = f"{intent.get('comparison')} " if intent.get("comparison") else ""

    return {
        "type": chart_meta["chart_type"],
        "title": f"{str(intent.get('dimension') or dimension_key).capitalize()} {title_suffix}{str(intent.get('metric') or metric_key).capitalize()}".strip(),
        "xAxis": {"data": x_data, "name": dimension_key},
        "yAxis": {"name": metric_key},
        "series": [{"name": metric_key, "data": y_data}],
    }

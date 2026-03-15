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


def is_sql_like(text: str) -> bool:
    value = (text or "").strip().lower()
    return bool(re.search(r"\b(select|with|insert|update|delete|from|group by)\b", value))


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
    elif "qoq" in lowered or "quarter over quarter" in lowered or "quarter-over-quarter" in lowered:
        comparison = "QoQ"

    has_trend = any(token in lowered for token in ["trend", "over time", "timeline"]) or dimension in {
        "month",
        "year",
    }

    # Derive a coarse intent_type for downstream consumers
    if comparison:
        intent_type = "time_comparison"
    elif any(token in lowered for token in ["top ", "bottom ", "highest", "lowest", "ranking"]):
        intent_type = "ranking"
    elif any(token in lowered for token in ["why", "what drove", "driver", "explain"]):
        intent_type = "diagnostic"
    elif has_trend:
        intent_type = "trend"
    else:
        intent_type = "aggregate"

    return {
        "metric": metric,
        "dimension": dimension,
        "comparison": comparison,
        "has_trend": has_trend,
        "is_sql_input": is_sql_like(text),
        "intent_type": intent_type,
    }

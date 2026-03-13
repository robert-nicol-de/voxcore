from __future__ import annotations


def detect_time_comparison(query_text: str) -> str | None:
    text = (query_text or "").strip().lower()
    if "year over year" in text or "year-over-year" in text or "yoy" in text:
        return "YoY"
    if "month over month" in text or "month-over-month" in text or "mom" in text:
        return "MoM"
    if "quarter over quarter" in text or "quarter-over-quarter" in text or "qoq" in text:
        return "QoQ"
    if "rolling" in text or "moving average" in text:
        return "Rolling"
    return None


def default_time_grain(comparison: str | None) -> str:
    if comparison == "YoY":
        return "year"
    if comparison == "QoQ":
        return "quarter"
    return "month"

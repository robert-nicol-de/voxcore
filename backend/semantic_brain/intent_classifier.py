from __future__ import annotations

import re
from typing import Any

# ── Intent type signal patterns ────────────────────────────────────────────────
_INTENT_PATTERNS: dict[str, list[tuple[str, float]]] = {
    "time_comparison": [
        (r"\byoy\b|\byear.over.year\b|\byear on year\b", 0.95),
        (r"\bmom\b|\bmonth.over.month\b|\bmonth on month\b", 0.95),
        (r"\bqoq\b|\bquarter.over.quarter\b|\bquarter on quarter\b", 0.95),
        (r"\bcompare\b.{0,40}(?:last|prior|previous)\b", 0.80),
        (r"\bvs\.?\s+(?:last|prior|previous)\b", 0.80),
    ],
    "ranking": [
        (r"\btop\s+\d+\b", 0.95),
        (r"\bbottom\s+\d+\b", 0.90),
        (r"\bhighest\b|\blowest\b|\bbest\b|\bworst\b", 0.85),
        (r"\branking\b|\branked\b|\bleaders\b|\blaggards\b", 0.85),
    ],
    "trend": [
        (r"\btrend\b|\bover time\b|\btimeline\b", 0.85),
        (r"\bmonthly\b|\bweekly\b|\bdaily\b|\bannual\b|\bquarterly\b", 0.80),
        (r"\bgrowth trajectory\b|\bmoving average\b", 0.80),
    ],
    "diagnostic": [
        (r"\bwhy\b|\bwhat drove\b|\bcause\b|\bdriver\b", 0.90),
        (r"\bexplain\b|\bdiagnose\b|\broot cause\b", 0.85),
        (r"\bbreakdown\b.{0,30}\bwhy\b", 0.80),
    ],
    "multi_dimension": [
        (r"\bby\b.{1,40}\band\b.{1,40}\bby\b", 0.80),
        (r"\bsegmented by\b|\bbroken down by\b.{0,40}\band\b", 0.80),
        (r"\bacross\b.{1,40}\band\b.{1,40}\bacross\b", 0.75),
    ],
    "aggregate": [],
}

# ── Entity hint vocabularies ───────────────────────────────────────────────────
_METRIC_VOCAB: dict[str, list[str]] = {
    "revenue":   ["revenue", "income", "receipts"],
    "sales":     ["sales", "total sales", "net sales"],
    "orders":    ["orders", "order count", "number of orders", "order volume"],
    "profit":    ["profit", "net profit", "gross profit", "earnings"],
    "margin":    ["margin", "profit margin", "gross margin"],
    "units":     ["units", "unit sales", "quantity", "qty", "volume"],
    "customers": ["customers", "customer count", "unique customers", "clients"],
    "growth":    ["growth", "growth rate"],
    "amount":    ["amount", "total amount", "value"],
    "count":     ["count", "number of", "total number"],
}

_DIMENSION_VOCAB: dict[str, list[str]] = {
    "region":    ["region", "regions"],
    "district":  ["district", "districts"],
    "country":   ["country", "countries", "nation"],
    "category":  ["category", "categories", "product category"],
    "product":   ["product", "products"],
    "customer":  ["customer", "client"],
    "segment":   ["segment", "segments"],
    "city":      ["city", "cities"],
    "state":     ["state", "province"],
    "channel":   ["channel", "channels", "sales channel"],
    "team":      ["team", "teams", "sales team"],
    "rep":       ["rep", "sales rep", "salesperson"],
}


def classify_intent(query_text: str) -> dict[str, Any]:
    """
    Classify intent, extract entities, and compute confidence for a natural
    language query.

    Returns:
        intent_type  — primary intent category
        confidence   — float 0.0–1.0 overall confidence
        metric       — best-match metric entity
        dimension    — best-match dimension entity
        time_analysis — detected time analysis type or None
        entities     — all matched metrics, dimensions, time_analysis
        ambiguous    — True if multiple metrics match at similar confidence
        clarification_needed  — True if confidence < 0.65 or ambiguous
        clarification_prompt  — clarification question if needed, else None
    """
    text = (query_text or "").strip()
    lowered = text.lower()

    # ── Intent classification ─────────────────────────────────────────────
    intent_scores: dict[str, float] = {}
    for intent_type, patterns in _INTENT_PATTERNS.items():
        for pattern, score in patterns:
            if re.search(pattern, lowered):
                intent_scores[intent_type] = max(intent_scores.get(intent_type, 0.0), score)

    if not intent_scores:
        if " by " in lowered or " per " in lowered:
            intent_scores["aggregate"] = 0.72
        else:
            intent_scores["aggregate"] = 0.60

    primary_intent = max(intent_scores, key=lambda k: intent_scores[k])
    intent_confidence = intent_scores[primary_intent]

    # ── Metric extraction ─────────────────────────────────────────────────
    matched_metrics: list[str] = []
    for key, tokens in _METRIC_VOCAB.items():
        for token in tokens:
            if token in lowered:
                matched_metrics.append(key)
                break
    primary_metric = matched_metrics[0] if matched_metrics else "sales"
    metric_confidence = 0.90 if matched_metrics else 0.55
    ambiguous = len(set(matched_metrics)) > 1

    # ── Dimension extraction ──────────────────────────────────────────────
    matched_dimensions: list[str] = []
    for key, tokens in _DIMENSION_VOCAB.items():
        for token in tokens:
            if token in lowered:
                matched_dimensions.append(key)
                break
    primary_dimension = matched_dimensions[0] if matched_dimensions else None

    # ── Time analysis ─────────────────────────────────────────────────────
    time_analysis: str | None = None
    if re.search(r"\byoy\b|\byear.over.year\b|\byear on year\b", lowered):
        time_analysis = "year_over_year"
    elif re.search(r"\bmom\b|\bmonth.over.month\b|\bmonth on month\b", lowered):
        time_analysis = "month_over_month"
    elif re.search(r"\bqoq\b|\bquarter.over.quarter\b", lowered):
        time_analysis = "quarter_over_quarter"
    elif re.search(r"\btrend\b|\bover time\b|\btimeline\b", lowered):
        time_analysis = "trend"

    # ── Composite confidence ──────────────────────────────────────────────
    overall_confidence = round(intent_confidence * 0.60 + metric_confidence * 0.40, 2)

    clarification_needed = overall_confidence < 0.65 or ambiguous
    clarification_prompt: str | None = None
    if ambiguous:
        options = " or ".join(list(dict.fromkeys(matched_metrics))[:3])
        dim_hint = f" by {primary_dimension}" if primary_dimension else ""
        clarification_prompt = f"Do you mean {options}{dim_hint}?"
    elif overall_confidence < 0.65:
        clarification_prompt = (
            f'Could you clarify what metric you\'re interested in for: "{text[:80]}"?'
        )

    return {
        "intent_type": primary_intent,
        "confidence": overall_confidence,
        "metric": primary_metric,
        "dimension": primary_dimension,
        "time_analysis": time_analysis,
        "entities": {
            "metrics": list(dict.fromkeys(matched_metrics)),
            "dimensions": list(dict.fromkeys(matched_dimensions)),
            "time_analysis": time_analysis,
        },
        "ambiguous": ambiguous,
        "clarification_needed": clarification_needed,
        "clarification_prompt": clarification_prompt,
    }

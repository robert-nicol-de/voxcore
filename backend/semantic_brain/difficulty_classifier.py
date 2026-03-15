from __future__ import annotations

import re
from typing import Any

# ── Signal patterns ────────────────────────────────────────────────────────────
# Level 3 — Advanced: multi-criteria filters, joins, exclusions, nested logic
_LEVEL_3: list[str] = [
    r"\bexcluding\b|\bexcept\b|\bwithout\b",
    r"\bwhere\b.{0,80}\band\b.{0,80}\bwhere\b",   # double WHERE conditions
    r"\bjoin\b|\bmerge\b|\bleft join\b|\binner join\b",
    r"\bsubquery\b|\bcte\b",
    r"top\s+\d+.{0,40}(?:by|per|within)\b",
    r"\byoy\b.{0,60}\bby\b.{0,60}\bby\b",         # YoY + 2 groupings
    r"\bdiagnos\w+\b|\broot cause\b|\bwhat drove\b",
]

# Level 2 — Intermediate: time comparisons, trends, ranked results
_LEVEL_2: list[str] = [
    r"\byoy\b|\byear.over.year\b|\byear on year\b",
    r"\bmom\b|\bmonth.over.month\b",
    r"\bqoq\b|\bquarter.over.quarter\b",
    r"\btrend\b|\bover time\b|\btimeline\b",
    r"\bcompare\b.{0,40}(?:period|quarter|year|month)\b",
    r"\bby\b.{1,40}\band\b.{1,40}\bby\b",          # two group-by dimensions
    r"top\s+\d+",
    r"\bmonthly\b|\bweekly\b|\bdaily\b|\bannual\b",
]


def classify_difficulty(
    query_text: str,
    plan: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Classify query complexity into one of three levels.

    Level 1 — Simple
        Single metric aggregated by a single dimension; no time comparison.

    Level 2 — Intermediate
        Time comparison (YoY / MoM / QoQ), trend analysis, ranked results,
        or multi-dimension grouping.

    Level 3 — Advanced
        Joins, exclusions, nested conditions, diagnostic / root-cause analysis,
        or multi-step aggregation logic.

    Returns:
        level           — int 1 / 2 / 3
        label           — "simple" | "intermediate" | "advanced"
        reasoning       — short explanation
        reasoning_depth — "shallow" | "moderate" | "deep"
    """
    lowered = (query_text or "").strip().lower()

    # ── Level 3 check ─────────────────────────────────────────────────────
    for pattern in _LEVEL_3:
        if re.search(pattern, lowered):
            return {
                "level":           3,
                "label":           "advanced",
                "reasoning":       (
                    "Query involves complex conditions, exclusions, joins, "
                    "or multi-step diagnostic analysis."
                ),
                "reasoning_depth": "deep",
            }

    if plan:
        analysis_type = str(plan.get("analysis_type") or "")
        has_comparison = bool(plan.get("comparison"))
        has_filter     = bool(plan.get("focus"))
        if analysis_type == "diagnostic" or (has_comparison and has_filter):
            return {
                "level":           3,
                "label":           "advanced",
                "reasoning":       (
                    "Diagnostic plan with both a period comparison and a data filter."
                ),
                "reasoning_depth": "deep",
            }

    # ── Level 2 check ─────────────────────────────────────────────────────
    for pattern in _LEVEL_2:
        if re.search(pattern, lowered):
            return {
                "level":           2,
                "label":           "intermediate",
                "reasoning":       (
                    "Query involves time comparison, trend analysis, ranked results, "
                    "or multiple grouping dimensions."
                ),
                "reasoning_depth": "moderate",
            }

    if plan and bool(plan.get("comparison")):
        return {
            "level":           2,
            "label":           "intermediate",
            "reasoning":       "Query includes a period-over-period comparison.",
            "reasoning_depth": "moderate",
        }

    # ── Level 1 — default ─────────────────────────────────────────────────
    return {
        "level":           1,
        "label":           "simple",
        "reasoning":       (
            "Single metric aggregated by a single grouping dimension."
        ),
        "reasoning_depth": "shallow",
    }

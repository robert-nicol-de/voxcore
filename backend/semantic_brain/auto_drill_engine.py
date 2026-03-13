from __future__ import annotations

from typing import Any


DRILL_DIMENSIONS = [
    "product_category",
    "customer_segment",
    "sales_rep",
]


class AutoDrillEngine:
    def suggest_drills(self, analysis_plan: dict[str, Any], top_focus: str | None = None) -> list[dict[str, str]]:
        parent_dimension = str(analysis_plan.get("dimension") or "district")
        focus = str(top_focus or analysis_plan.get("focus") or "").strip()
        drills: list[dict[str, str]] = []
        for dim in DRILL_DIMENSIONS:
            drills.append(
                {
                    "from": parent_dimension,
                    "to": dim,
                    "question": (
                        f"Break down {focus or parent_dimension} by {dim}"
                        if focus
                        else f"Break down by {dim}"
                    ),
                }
            )
        return drills

    def summarize_driver_hints(self, analysis_plan: dict[str, Any], insights: dict[str, Any]) -> list[str]:
        top_performer = str(insights.get("top_performer") or "Top segment")
        focus = top_performer.split(" ")[0] if top_performer else "Top segment"
        return [
            f"{focus} -> Electronics may be a primary growth driver",
            f"{focus} -> Enterprise customer segment may explain uplift",
            f"{focus} -> Sales rep mix can be validated next",
        ]

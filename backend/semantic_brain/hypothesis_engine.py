from __future__ import annotations

from typing import Any


class HypothesisEngine:
    def generate_hypotheses(self, analysis_plan: dict[str, Any]) -> list[str]:
        hypotheses: list[str] = []
        dimension = str(analysis_plan.get("dimension") or "").lower()
        metric = str(analysis_plan.get("metric") or "").lower()
        comparison = str(analysis_plan.get("comparison") or "").lower()

        if dimension == "district":
            hypotheses.append("West district growth may be driven by Electronics category")
            hypotheses.append("Compare district performance by customer segment")

        if metric in {"revenue", "sales", "sum_sales_amount"}:
            hypotheses.append("Enterprise customers may be contributing to YoY increase")
            hypotheses.append("Promotions in Q3 may explain growth spikes")

        if comparison in {"yoy", "mom", "qoq"}:
            hypotheses.append("Check whether growth is concentrated in one seasonal period")

        deduped: list[str] = []
        seen: set[str] = set()
        for item in hypotheses:
            key = item.strip().lower()
            if key and key not in seen:
                seen.add(key)
                deduped.append(item)
        return deduped[:5]

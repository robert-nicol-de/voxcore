from __future__ import annotations

from typing import Any


class InsightRanker:
    def rank(self, insights: dict[str, Any], hypotheses: list[str], patterns: dict[str, Any]) -> list[dict[str, Any]]:
        ranked: list[dict[str, Any]] = []

        if insights.get("top_performer"):
            ranked.append({"text": f"Top performer: {insights['top_performer']}", "importance": 0.92})
        if insights.get("largest_decline"):
            ranked.append({"text": f"Largest decline: {insights['largest_decline']}", "importance": 0.88})
        if insights.get("anomaly"):
            ranked.append({"text": str(insights["anomaly"]), "importance": 0.9})

        for idx, item in enumerate(hypotheses[:3]):
            ranked.append({"text": item, "importance": max(0.55, 0.82 - idx * 0.06)})

        anomalies = patterns.get("anomalies") or []
        if anomalies:
            ranked.append({"text": f"Detected {len(anomalies)} anomaly point(s)", "importance": 0.86})
        if patterns.get("seasonality"):
            ranked.append({"text": str(patterns["seasonality"]), "importance": 0.8})

        ranked.sort(key=lambda item: float(item.get("importance") or 0), reverse=True)
        return ranked[:8]

from __future__ import annotations

from math import sqrt
from typing import Any


class PatternDetectionEngine:
    def detect_patterns(self, rows: list[dict[str, Any]], plan: dict[str, Any] = None, metadata: dict[str, Any] = None) -> dict[str, Any]:
        patterns = {}

        # --- Rolling Growth Detection ---
        if plan is not None:
            if (
                plan.get("calculations")
                and any(c.get("type") in ["growth", "growth_rate"] for c in plan["calculations"])
                and plan.get("time_logic", {}).get("comparison", {}).get("mode") == "rolling"
                and plan.get("time_logic", {}).get("grain") == "month"
            ):
                patterns["main_pattern"] = "rolling_growth"
                patterns["confidence"] = 0.9

        # --- Legacy/statistical pattern detection (existing logic) ---
        if rows:
            first = rows[0]
            numeric_keys = [
                key
                for key in first.keys()
                if isinstance(first.get(key), (int, float)) and not isinstance(first.get(key), bool)
            ]
            if numeric_keys:
                metric_key = numeric_keys[0]
                values = [float(row.get(metric_key) or 0) for row in rows]
                if values:
                    mean = sum(values) / len(values)
                    variance = sum((value - mean) ** 2 for value in values) / max(len(values), 1)
                    std = sqrt(variance)

                    anomalies = [
                        {
                            "index": idx,
                            "value": value,
                            "z_score": round((value - mean) / std, 2) if std > 0 else 0,
                        }
                        for idx, value in enumerate(values)
                        if std > 0 and abs(value - mean) > 2 * std
                    ]

                    spikes = [
                        {
                            "index": idx,
                            "value": value,
                        }
                        for idx, value in enumerate(values)
                        if value > mean + std
                    ]

                    seasonality = None
                    if len(values) >= 12:
                        seasonality = "Potential seasonality detected from recurring monthly-like periodicity."

                    correlation_hint = None
                    if len(numeric_keys) >= 2:
                        correlation_hint = f"Potential correlation between {numeric_keys[0]} and {numeric_keys[1]} should be validated."

                    patterns["anomalies"] = anomalies[:5]
                    patterns["seasonality"] = seasonality
                    patterns["spikes"] = spikes[:5]
                    patterns["correlation_hint"] = correlation_hint

        print("DETECTED PATTERNS:", patterns)
        return patterns

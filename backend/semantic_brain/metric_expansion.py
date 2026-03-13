from __future__ import annotations


class MetricExpansionEngine:
    _RELATED = {
        "sales": ["profit", "orders", "avg_order_value"],
        "revenue": ["profit", "orders", "avg_order_value"],
        "profit": ["revenue", "orders", "avg_order_value"],
        "orders": ["revenue", "profit", "avg_order_value"],
    }

    def expand(self, metric: str) -> list[str]:
        key = (metric or "").strip().lower()
        return self._RELATED.get(key, ["profit", "orders", "avg_order_value"])

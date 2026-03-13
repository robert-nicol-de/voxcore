from __future__ import annotations

from typing import Any


class MetricRegistry:
    def __init__(self, metrics: dict[str, dict[str, str]] | None = None) -> None:
        self.metrics: dict[str, dict[str, str]] = metrics or {
            "revenue": {
                "sql": "SUM(sales_amount)",
                "description": "Total revenue",
            },
            "orders": {
                "sql": "COUNT(order_id)",
                "description": "Total order count",
            },
            "avg_order_value": {
                "sql": "SUM(sales_amount) / NULLIF(COUNT(order_id), 0)",
                "description": "Average order value",
            },
        }

    @classmethod
    def from_semantic_models(cls, semantic_models: list[dict[str, Any]]) -> "MetricRegistry":
        registry = cls()
        for model in semantic_models:
            definition = model.get("definition") if isinstance(model, dict) else None
            if not isinstance(definition, dict):
                continue
            model_metrics = definition.get("metrics")
            if not isinstance(model_metrics, dict):
                continue
            for metric_name, payload in model_metrics.items():
                item = payload if isinstance(payload, dict) else {}
                registry.metrics[str(metric_name)] = {
                    "sql": str(item.get("sql") or item.get("expression") or ""),
                    "description": str(item.get("description") or ""),
                }
        return registry

    def get_metric(self, name: str) -> dict[str, str] | None:
        return self.metrics.get((name or "").strip().lower())

    def to_prompt_lines(self, max_items: int = 12) -> list[str]:
        lines: list[str] = []
        for key in list(self.metrics.keys())[:max_items]:
            payload = self.metrics[key]
            lines.append(f"- {key} = {payload.get('sql', '')}")
        return lines

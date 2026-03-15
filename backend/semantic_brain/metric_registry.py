"""
VoxCore Metric Registry
======================

Defines the MetricRegistry class for managing and describing available metrics in the semantic layer.
Supports loading from semantic models, lookup, and prompt formatting.

USAGE EXAMPLE:
    registry = MetricRegistry()
    metric = registry.get_metric("revenue")
    print(metric["sql"])

    # From semantic models:
    registry = MetricRegistry.from_semantic_models(models)
    print(registry.to_prompt_lines())
"""

from __future__ import annotations
from typing import Any

class MetricRegistry:
    """
    Registry for metrics, supporting lookup and prompt formatting.
    """
    def __init__(self, metrics: dict[str, dict[str, str]] | None = None) -> None:
        """
        Initialize the registry with a dictionary of metrics.
        """
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
        """
        Build a MetricRegistry from a list of semantic model dicts.
        """
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
        """
        Look up a metric by name (case-insensitive).
        Returns a dict with 'sql' and 'description', or None if not found.
        """
        return self.metrics.get((name or "").strip().lower())

    def to_prompt_lines(self, max_items: int = 12) -> list[str]:
        """
        Return a list of prompt lines describing the first N metrics.
        """
        lines: list[str] = []
        for key in list(self.metrics.keys())[:max_items]:
            payload = self.metrics[key]
            lines.append(f"- {key} = {payload.get('sql', '')}")
        return lines

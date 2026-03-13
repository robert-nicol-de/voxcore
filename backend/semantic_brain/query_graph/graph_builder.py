from __future__ import annotations

from typing import Any

from .graph_nodes import (
    ComparisonNode,
    DimensionNode,
    FilterNode,
    GraphNode,
    LimitNode,
    MetricNode,
    TimeGrainNode,
    VisualizationNode,
)


class QueryGraphBuilder:
    """
    Converts an analytical plan (and optional chart recommendation) into a
    list of typed graph nodes — the source of truth for SQL generation,
    visualization, insight narratives, and follow-up questions.

    Each node represents one analytical operation:
        metric      → what is being measured
        dimension   → how the metric is grouped
        time_grain  → the temporal resolution
        comparison  → period-over-period type (YoY / MoM / QoQ)
        filter      → a WHERE constraint applied to data
        limit       → TOP N rows
        visualization → recommended chart type
    """

    def build(
        self,
        plan: dict[str, Any],
        chart_recommendation: dict[str, str] | None = None,
    ) -> list[dict[str, Any]]:
        """Build and return the query graph as a list of node dicts.

        Each element in the list is the serialised dict form of a ``GraphNode``
        subclass so that it is JSON-serialisable out of the box.
        """
        nodes: list[GraphNode] = []

        # ── Metric ────────────────────────────────────────────────────────────
        metric_name = str(plan.get("metric") or "revenue")
        metric_sql = str(plan.get("metric_sql") or "SUM(sales_amount)")
        aggregation = str(plan.get("aggregation") or "sum")
        nodes.append(MetricNode(name=metric_name, sql=metric_sql, aggregation=aggregation))

        # ── Dimension ─────────────────────────────────────────────────────────
        dimension = str(plan.get("dimension") or "")
        if dimension:
            nodes.append(
                DimensionNode(
                    name=dimension,
                    table=str(plan.get("dimension_table") or ""),
                    column=str(plan.get("dimension_column") or dimension),
                )
            )

        # ── Time Grain ────────────────────────────────────────────────────────
        time_grain = str(plan.get("time_grain") or "")
        time_col = str(plan.get("time_dimension") or "order_date")
        if time_grain:
            nodes.append(TimeGrainNode(value=time_grain, time_column=time_col))

        # ── Comparison ────────────────────────────────────────────────────────
        comparison = str(plan.get("comparison") or "")
        if comparison:
            nodes.append(ComparisonNode(value=comparison))

        # ── Filters (from plan focus or explicit filters) ─────────────────────
        focus = str(plan.get("focus") or "").strip()
        if focus:
            nodes.append(FilterNode(column=dimension, operator="=", filter_value=focus))

        # ── Limit (TOP N) ─────────────────────────────────────────────────────
        try:
            limit_val = max(1, min(200, int(plan.get("limit") or 10)))
        except Exception:
            limit_val = 10
        nodes.append(LimitNode(value=limit_val))

        # ── Visualization ─────────────────────────────────────────────────────
        if chart_recommendation:
            chart_type = str(chart_recommendation.get("type") or chart_recommendation.get("chart_type") or "bar_chart")
            chart_title = str(chart_recommendation.get("title") or chart_recommendation.get("reason") or "")
            nodes.append(VisualizationNode(chart_type=chart_type, title=chart_title))

        return [node.to_dict() for node in nodes]

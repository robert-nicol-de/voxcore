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
        execution_order = 1
        previous_node_ids: list[str] = []

        def next_node_id(node_type: str) -> str:
            return f"{node_type}_{len(nodes) + 1}"

        # ── Metric ────────────────────────────────────────────────────────────
        metric_name = str(plan.get("metric") or "revenue")
        metric_sql = str(plan.get("metric_sql") or "SUM(sales_amount)")
        aggregation = str(plan.get("aggregation") or "sum")
        metric_node = MetricNode(
            node_id=next_node_id("metric"),
            execution_order=execution_order,
            name=metric_name,
            sql=metric_sql,
            aggregation=aggregation,
        )
        nodes.append(metric_node)
        previous_node_ids = [metric_node.id]
        execution_order += 1

        # ── Dimension ─────────────────────────────────────────────────────────
        dimension = str(plan.get("dimension") or "")
        if dimension:
            dimension_node = DimensionNode(
                node_id=next_node_id("dimension"),
                execution_order=execution_order,
                depends_on=previous_node_ids,
                name=dimension,
                table=str(plan.get("dimension_table") or ""),
                column=str(plan.get("dimension_column") or dimension),
            )
            nodes.append(dimension_node)
            previous_node_ids = [dimension_node.id]
            execution_order += 1

        # ── Time Grain ────────────────────────────────────────────────────────
        time_grain = str(plan.get("time_grain") or "")
        time_col = str(plan.get("time_dimension") or "order_date")
        if time_grain:
            time_node = TimeGrainNode(
                node_id=next_node_id("time_grain"),
                execution_order=execution_order,
                depends_on=previous_node_ids,
                value=time_grain,
                time_column=time_col,
            )
            nodes.append(time_node)
            previous_node_ids = [time_node.id]
            execution_order += 1

        # ── Comparison ────────────────────────────────────────────────────────
        comparison = str(plan.get("comparison") or "")
        if comparison:
            comparison_node = ComparisonNode(
                node_id=next_node_id("comparison"),
                execution_order=execution_order,
                depends_on=previous_node_ids,
                value=comparison,
            )
            nodes.append(comparison_node)
            previous_node_ids = [comparison_node.id]
            execution_order += 1

        # ── Filters (from plan focus or explicit filters) ─────────────────────
        focus = str(plan.get("focus") or "").strip()
        if focus:
            filter_node = FilterNode(
                node_id=next_node_id("filter"),
                execution_order=execution_order,
                depends_on=previous_node_ids,
                column=dimension,
                operator="=",
                filter_value=focus,
            )
            nodes.append(filter_node)
            previous_node_ids = [filter_node.id]
            execution_order += 1

        # ── Limit (TOP N) ─────────────────────────────────────────────────────
        try:
            limit_val = max(1, min(200, int(plan.get("limit") or 10)))
        except Exception:
            limit_val = 10
        limit_node = LimitNode(
            node_id=next_node_id("limit"),
            execution_order=execution_order,
            depends_on=previous_node_ids,
            value=limit_val,
        )
        nodes.append(limit_node)
        previous_node_ids = [limit_node.id]
        execution_order += 1

        # ── Visualization ─────────────────────────────────────────────────────
        if chart_recommendation:
            chart_type = str(chart_recommendation.get("type") or chart_recommendation.get("chart_type") or "bar_chart")
            chart_title = str(chart_recommendation.get("title") or chart_recommendation.get("reason") or "")
            nodes.append(
                VisualizationNode(
                    node_id=next_node_id("visualization"),
                    execution_order=execution_order,
                    depends_on=previous_node_ids,
                    chart_type=chart_type,
                    title=chart_title,
                )
            )

        return [node.to_dict() for node in nodes]

from __future__ import annotations

from typing import Any


def _find(nodes: list[dict[str, Any]], node_type: str) -> dict[str, Any] | None:
    """Return the first node matching *node_type*, or ``None``."""
    for node in nodes:
        if node.get("type") == node_type:
            return node
    return None


def _grain_to_extract(grain: str) -> str:
    """Map a grain string to the SQL EXTRACT field name."""
    return {
        "year": "YEAR",
        "month": "MONTH",
        "quarter": "QUARTER",
        "day": "DAY",
    }.get(grain.lower(), "YEAR")


class QueryGraphExecutor:
    """
    Compiles a query graph (list of node dicts produced by QueryGraphBuilder)
    into multiple concrete analytical artifacts:

        compile_sql()              → deterministic SQL string
        to_chart_recommendation()  → chart type + title dict
        to_insight_hints()         → plain-text insight context strings
        to_followup_questions()    → suggested follow-up question strings
        to_drilldowns()            → dimension drill-path strings
        to_explanation()           → human-readable explanation of the graph

    All methods are pure and stateless — they read the graph and return a
    result without modifying any shared state.
    """

    # ── SQL compilation ────────────────────────────────────────────────────

    def compile_sql(self, nodes: list[dict[str, Any]]) -> str:
        """Compile the graph nodes into a deterministic SQL query."""
        metric = _find(nodes, "metric")
        dimension = _find(nodes, "dimension")
        time_grain = _find(nodes, "time_grain")
        comparison = _find(nodes, "comparison")
        limit_node = _find(nodes, "limit")
        filter_node = _find(nodes, "filter")

        metric_sql = (metric or {}).get("sql") or "SUM(sales_amount)"
        dim_col = (dimension or {}).get("column") or (dimension or {}).get("name") or "district"
        time_col = (time_grain or {}).get("time_column") or "order_date"
        comparison_val = (comparison or {}).get("value") or ""
        raw_limit = (limit_node or {}).get("value")
        try:
            limit_val = max(1, min(200, int(raw_limit or 10)))
        except Exception:
            limit_val = 10

        where_clause = ""
        if filter_node:
            col = filter_node.get("column") or ""
            op = filter_node.get("operator") or "="
            val = filter_node.get("filter_value")
            if col and val is not None:
                safe_val = str(val).replace("'", "''")
                where_clause = f"\nWHERE {col} {op} '{safe_val}'"

        if comparison_val == "YoY":
            grain_fn = _grain_to_extract((time_grain or {}).get("value") or "year")
            return (
                f"SELECT {dim_col},\n"
                f"       {grain_fn}({time_col}) AS year,\n"
                f"       {metric_sql} AS metric_value,\n"
                f"       ({metric_sql} - LAG({metric_sql}) OVER (\n"
                f"           PARTITION BY {dim_col}\n"
                f"           ORDER BY {grain_fn}({time_col})\n"
                f"       )) AS yoy_delta\n"
                f"FROM sales{where_clause}\n"
                f"GROUP BY {dim_col}, {grain_fn}({time_col})\n"
                f"ORDER BY {dim_col}, year"
            )

        if comparison_val == "MoM":
            return (
                f"SELECT {dim_col},\n"
                f"       EXTRACT(MONTH FROM {time_col}) AS month,\n"
                f"       {metric_sql} AS metric_value\n"
                f"FROM sales{where_clause}\n"
                f"GROUP BY {dim_col}, EXTRACT(MONTH FROM {time_col})\n"
                f"ORDER BY {dim_col}, month"
            )

        if comparison_val == "QoQ":
            return (
                f"SELECT {dim_col},\n"
                f"       EXTRACT(QUARTER FROM {time_col}) AS quarter,\n"
                f"       {metric_sql} AS metric_value\n"
                f"FROM sales{where_clause}\n"
                f"GROUP BY {dim_col}, EXTRACT(QUARTER FROM {time_col})\n"
                f"ORDER BY {dim_col}, quarter"
            )

        if time_grain:
            grain_fn = _grain_to_extract((time_grain or {}).get("value") or "year")
            return (
                f"SELECT {dim_col},\n"
                f"       {grain_fn}({time_col}) AS time_period,\n"
                f"       {metric_sql} AS metric_value\n"
                f"FROM sales{where_clause}\n"
                f"GROUP BY {dim_col}, {grain_fn}({time_col})\n"
                f"ORDER BY {dim_col}, time_period"
            )

        return (
            f"SELECT {dim_col},\n"
            f"       {metric_sql} AS metric_value\n"
            f"FROM sales{where_clause}\n"
            f"GROUP BY {dim_col}\n"
            f"ORDER BY metric_value DESC\n"
            f"LIMIT {limit_val}"
        )

    # ── Chart recommendation ───────────────────────────────────────────────

    def to_chart_recommendation(self, nodes: list[dict[str, Any]]) -> dict[str, str]:
        """Read the visualization node from the graph and return a chart dict."""
        viz = _find(nodes, "visualization")
        if viz:
            return {
                "type": str(viz.get("chart_type") or "bar_chart"),
                "title": str(viz.get("title") or ""),
            }
        comparison = _find(nodes, "comparison")
        time_grain = _find(nodes, "time_grain")
        if comparison:
            return {"type": "bar_chart", "title": f"{comparison.get('value')} Comparison"}
        if time_grain:
            return {"type": "line_chart", "title": "Trend Over Time"}
        return {"type": "bar_chart", "title": "Metric by Dimension"}

    # ── Insight hints ──────────────────────────────────────────────────────

    def to_insight_hints(self, nodes: list[dict[str, Any]]) -> list[str]:
        """Generate plain-text insight context strings from the graph."""
        hints: list[str] = []
        metric = _find(nodes, "metric")
        comparison = _find(nodes, "comparison")
        dimension = _find(nodes, "dimension")
        time_grain = _find(nodes, "time_grain")
        limit_node = _find(nodes, "limit")

        m_name = (metric or {}).get("name") or "metric"
        d_name = (dimension or {}).get("name") or "dimension"
        c_val = (comparison or {}).get("value") or ""
        t_val = (time_grain or {}).get("value") or ""

        if metric and dimension:
            hints.append(f"Analyzing {m_name} broken down by {d_name}.")
        if comparison:
            hints.append(f"Applying {c_val} period-over-period comparison to detect growth or decline.")
        if time_grain:
            hints.append(f"Temporal resolution is {t_val} — aggregating data at the {t_val} level.")
        if limit_node:
            n = (limit_node or {}).get("value") or 10
            hints.append(f"Returning the top {n} results ranked by {m_name}.")
        return hints

    # ── Follow-up questions ────────────────────────────────────────────────

    def to_followup_questions(self, nodes: list[dict[str, Any]]) -> list[str]:
        """Generate relevant follow-up question suggestions from the graph."""
        questions: list[str] = []
        dimension = _find(nodes, "dimension")
        metric = _find(nodes, "metric")
        comparison = _find(nodes, "comparison")

        d_name = (dimension or {}).get("name") or "dimension"
        m_name = (metric or {}).get("name") or "metric"
        c_val = (comparison or {}).get("value") or ""

        if dimension:
            questions.append(f"Which {d_name} had the fastest growth this quarter?")
            questions.append(f"Break down {d_name} by product_category")
            questions.append(f"Break down {d_name} by customer_segment")
        if metric:
            questions.append(f"Show {m_name} trend by month")
        if comparison:
            questions.append(f"Why did {c_val} performance differ across {d_name}?")

        seen: set[str] = set()
        deduped: list[str] = []
        for q in questions:
            k = q.lower().strip()
            if k not in seen:
                seen.add(k)
                deduped.append(q)
        return deduped[:4]

    # ── Drilldowns ─────────────────────────────────────────────────────────

    def to_drilldowns(self, nodes: list[dict[str, Any]]) -> list[str]:
        """Generate dimension drilldown path strings from the graph."""
        dimension = _find(nodes, "dimension")
        if not dimension:
            return []
        d_name = (dimension or {}).get("name") or "dimension"
        return [
            f"{d_name} → product_category",
            f"{d_name} → customer_segment",
            f"{d_name} → sales_rep",
        ]

    # ── Human-readable explanation ─────────────────────────────────────────

    def to_explanation(self, nodes: list[dict[str, Any]]) -> str:
        """Return a one-paragraph explanation of what the graph represents."""
        metric = _find(nodes, "metric")
        dimension = _find(nodes, "dimension")
        comparison = _find(nodes, "comparison")
        time_grain = _find(nodes, "time_grain")
        limit_node = _find(nodes, "limit")

        m_name = (metric or {}).get("name") or "the metric"
        d_name = (dimension or {}).get("name") or "the dimension"
        c_val = (comparison or {}).get("value") or ""
        t_val = (time_grain or {}).get("value") or ""
        limit_n = (limit_node or {}).get("value") or 10

        parts: list[str] = [f"This query measures {m_name} grouped by {d_name}."]
        if c_val:
            parts.append(f"It applies a {c_val} comparison to track changes over time.")
        if t_val:
            parts.append(f"Data is aggregated at the {t_val} level.")
        parts.append(f"Results are limited to the top {limit_n} rows.")
        return " ".join(parts)

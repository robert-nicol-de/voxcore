from __future__ import annotations

from typing import Any


class SqlComponentBuilder:
    """
    Builds SQL by assembling structured, named components first, then compiling
    them into a final SQL string.

    This prevents malformed SQL, hallucinated columns, and missing GROUP BY
    clauses by making every clause an explicit, inspectable data structure
    before the final string is produced.

    Usage::

        builder = SqlComponentBuilder()
        sql, components = builder.build_and_compile(plan)
    """

    def build_components(self, plan: dict[str, Any]) -> dict[str, Any]:
        """Return a structured dict of SQL components derived from *plan*."""
        metric_sql   = str(plan.get("metric_sql")      or "SUM(sales_amount)")
        metric_name  = str(plan.get("metric")           or "metric")
        dim_col      = str(plan.get("dimension_column") or plan.get("dimension") or "district")
        dim_table    = str(plan.get("dimension_table")  or "").strip()
        time_col     = str(plan.get("time_dimension")   or "order_date")
        comparison   = str(plan.get("comparison")       or "")
        time_grain   = str(plan.get("time_grain")       or "")
        focus        = str(plan.get("focus")            or "").strip()
        try:
            limit_val = max(1, min(200, int(plan.get("limit") or 10)))
        except Exception:
            limit_val = 10

        metric_alias = f"total_{metric_name}".lower().replace(" ", "_")

        # ── SELECT ─────────────────────────────────────────────────────────────
        select_cols: list[str] = [dim_col]
        time_period_alias: str | None = None

        if comparison == "YoY":
            select_cols.append(f"EXTRACT(YEAR FROM {time_col}) AS year")
            time_period_alias = "year"
        elif comparison == "MoM":
            select_cols.append(f"EXTRACT(MONTH FROM {time_col}) AS month")
            time_period_alias = "month"
        elif comparison == "QoQ":
            select_cols.append(f"EXTRACT(QUARTER FROM {time_col}) AS quarter")
            time_period_alias = "quarter"
        elif time_grain:
            select_cols.append(
                f"EXTRACT({time_grain.upper()} FROM {time_col}) AS time_period"
            )
            time_period_alias = "time_period"

        select_cols.append(f"{metric_sql} AS {metric_alias}")

        # YoY delta window function
        windows: list[str] = []
        if comparison == "YoY":
            windows.append(
                f"({metric_sql} - LAG({metric_sql}) OVER "
                f"(PARTITION BY {dim_col} ORDER BY EXTRACT(YEAR FROM {time_col}))) "
                f"AS yoy_delta"
            )

        # ── FROM / JOINs ───────────────────────────────────────────────────────
        from_table = "sales"
        joins: list[str] = []
        if dim_table and dim_table.lower() not in ("", "sales"):
            joins.append(
                f"{dim_table} ON sales.{dim_col}_id = {dim_table}.id"
            )

        # ── WHERE ──────────────────────────────────────────────────────────────
        where_clauses: list[str] = []
        if focus:
            safe_focus = focus.replace("'", "''")
            where_clauses.append(f"{dim_col} = '{safe_focus}'")

        # ── GROUP BY ───────────────────────────────────────────────────────────
        group_by: list[str] = [dim_col]
        if comparison == "YoY":
            group_by.append(f"EXTRACT(YEAR FROM {time_col})")
        elif comparison == "MoM":
            group_by.append(f"EXTRACT(MONTH FROM {time_col})")
        elif comparison == "QoQ":
            group_by.append(f"EXTRACT(QUARTER FROM {time_col})")
        elif time_grain:
            group_by.append(f"EXTRACT({time_grain.upper()} FROM {time_col})")

        # ── ORDER BY ───────────────────────────────────────────────────────────
        if comparison in ("YoY", "MoM", "QoQ") and time_period_alias:
            order_by = [dim_col, time_period_alias]
        else:
            order_by = [f"{metric_alias} DESC"]

        # ── LIMIT (not applicable for time series with OVER) ──────────────────
        limit: int | None = None if comparison else limit_val

        return {
            "select":   select_cols + windows,
            "from":     from_table,
            "joins":    joins,
            "where":    where_clauses,
            "group_by": group_by,
            "order_by": order_by,
            "limit":    limit,
        }

    def compile(self, components: dict[str, Any]) -> str:
        """Compile structured SQL components into a final SQL string."""
        select_part = ",\n       ".join(components["select"])
        from_part   = str(components["from"])
        joins_part  = (
            "\nJOIN " + "\nJOIN ".join(components["joins"])
            if components.get("joins") else ""
        )
        where_part  = (
            "\nWHERE " + "\n  AND ".join(components["where"])
            if components.get("where") else ""
        )
        group_part  = (
            "\nGROUP BY " + ", ".join(components["group_by"])
            if components.get("group_by") else ""
        )
        order_part  = (
            "\nORDER BY " + ", ".join(components["order_by"])
            if components.get("order_by") else ""
        )
        limit_part  = (
            f"\nLIMIT {components['limit']}"
            if components.get("limit") else ""
        )

        return (
            f"SELECT {select_part}\n"
            f"FROM {from_part}"
            f"{joins_part}"
            f"{where_part}"
            f"{group_part}"
            f"{order_part}"
            f"{limit_part}"
        )

    def build_and_compile(
        self, plan: dict[str, Any]
    ) -> tuple[str, dict[str, Any]]:
        """Build components then compile to SQL.  Returns ``(sql, components)``."""
        components = self.build_components(plan)
        return self.compile(components), components

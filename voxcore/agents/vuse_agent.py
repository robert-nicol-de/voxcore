from voxcore.engine.sql_optimizer import SQLAliasManager, SQLAliasApplier, SQLOptimizer

class VUSEAgent:
    def run(self, plan: dict) -> dict:
        base_table = plan["base_table"]
        joins = plan.get("joins", [])

        metrics = plan["data_requirements"]["metrics"]
        dimensions = plan["data_requirements"].get("dimensions", [])
        time_def = plan["data_requirements"].get("time")

        calculations = plan.get("calculations", [])
        grouping = plan.get("grouping", [])
        ordering = plan.get("ordering", [])
        time_logic = plan.get("time_logic", {})

        # --- ALIAS SYSTEM ---
        alias_manager = SQLAliasManager()
        alias_applier = SQLAliasApplier()
        alias_map = alias_manager.generate_aliases(base_table, joins)
        joins = alias_applier.apply(plan, alias_map)
        base_alias = alias_map[base_table]

        # --- STEP 1: BUILD SELECT CLAUSE ---
        select_parts = []
        group_by_parts = []

        # Dimensions
        for d in dimensions:
            alias = alias_map[d["table"]]
            col = f"{alias}.{d['name']}"
            col_alias = d["name"].lower()
            select_parts.append(f"{col} AS {col_alias}")
            group_by_parts.append(col)

        # Time
        grain = time_logic.get("grain")
        if grain and time_def:
            alias = alias_map[time_def["table"]]
            time_col = f"{alias}.{time_def['column']}"
            time_expr = f"DATE_TRUNC('{grain}', {time_col})"
            select_parts.append(f"{time_expr} AS {grain}")
            group_by_parts.append(time_expr)

        # Metrics
        metric_aliases = []
        for m in metrics:
            alias = alias_map[m["table"]]
            col = f"{alias}.{m['name']}"
            agg = m.get("aggregation", "SUM")
            col_alias = m["name"].lower()
            select_parts.append(f"{agg}({col}) AS {col_alias}")
            metric_aliases.append(col_alias)

        # --- STEP 2: BUILD FROM + JOIN ---
        from_clause = f"FROM {base_table} {base_alias}"
        join_clauses = []
        for j in joins:
            join_clauses.append(f"JOIN {j['table']} {j['alias']} ON {j['join']}")

        # --- STEP 3: BASE CTE ---
        base_cte = f"""
base_data AS (
    SELECT
        {', '.join(select_parts)}
    {from_clause}
    {' '.join(join_clauses)}
    {('GROUP BY ' + ', '.join(group_by_parts)) if group_by_parts else ''}
)
"""

        # --- STEP 4: WINDOW / CALCULATION LAYER ---
        use_window = False
        window_cte = ""
        final_select_parts = []
        if calculations:
            use_window = True
            metric = metric_aliases[0]
            window_cte = f""",
window_layer AS (
    SELECT
        *,
        LAG({metric}) OVER (ORDER BY {grain}) AS prev_{metric}
    FROM base_data
)
"""
            final_select_parts = [
                "*",
                f"CASE \n    WHEN prev_{metric} IS NULL OR prev_{metric} = 0 THEN NULL\n    ELSE ({metric} - prev_{metric}) / prev_{metric}\nEND AS {metric}_growth"
            ]

        # --- STEP 5: FINAL SELECT ---
        if use_window:
            final_select = f"""
SELECT
    {', '.join(final_select_parts)}
FROM window_layer
"""
        else:
            final_select = f"""
SELECT
    *
FROM base_data
"""

        # --- STEP 6: ORDER BY ---
        if ordering:
            order_clause = ", ".join([
                f"{o['field']} {o['direction'].upper()}" for o in ordering
            ])
            final_select += f"\nORDER BY {order_clause}"

        # --- STEP 7: LIMIT ---
        limit = plan.get("limit", {}).get("value")
        if limit:
            final_select += f"\nLIMIT {limit}"

        # --- STEP 8: FULL SQL ---
        sql = f"WITH {base_cte}{window_cte}{final_select}"

        # --- STEP 9: OPTIMIZE SQL ---
        optimizer = SQLOptimizer()
        sql = optimizer.optimize(sql)

        return {
            "sql": sql,
            "pattern": "join_aware",
            "tables_used": [base_table] + [j["table"] for j in joins],
            "columns_used": [m["name"] for m in metrics] + [d["name"] for d in dimensions],
            "chart": self._infer_chart(plan)
        }

    def _infer_chart(self, plan):
        time_logic = plan.get("time_logic", {})
        if time_logic.get("grain"):
            return {
                "type": "line",
                "x": time_logic["grain"],
                "y": plan["data_requirements"]["metrics"][0]["name"].lower()
            }
        dims = plan["data_requirements"].get("dimensions", [])
        if dims:
            return {
                "type": "bar",
                "x": dims[0]["name"].lower(),
                "y": plan["data_requirements"]["metrics"][0]["name"].lower()
            }
        return {"type": "table"}

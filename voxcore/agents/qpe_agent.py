
import uuid

class QPEAgent:
    def __init__(self, semantic_model, join_resolver, join_graph):
        self.semantic = semantic_model
        self.join_resolver = join_resolver
        self.graph = join_graph

class QPEAgent:
    def run(self, intent: dict) -> dict:
        entities = intent["entities"]
        metrics = entities["metrics"]
        dimensions = entities["dimensions"]
        time_range = entities.get("time_range", {})
        comparison = entities.get("comparison")

        # --- STEP 1: RESOLVE METRICS ---
        metric_defs = []
        tables_needed = set()
        for m in metrics:
            m_key = m.lower()
            if m_key not in self.semantic["metrics"]:
                raise Exception(f"Unknown metric: {m}")
            m_def = self.semantic["metrics"][m_key]
            metric_defs.append(m_def)
            tables_needed.add(m_def["table"])

        # --- STEP 2: RESOLVE DIMENSIONS ---
        dimension_defs = []
        for d in dimensions:
            d_key = d.lower()
            if d_key == "time":
                continue
            if d_key not in self.semantic["dimensions"]:
                raise Exception(f"Unknown dimension: {d}")
            d_def = self.semantic["dimensions"][d_key]
            dimension_defs.append(d_def)
            tables_needed.add(d_def["table"])

        # --- STEP 3: RESOLVE TIME COLUMN ---
        time_def = None
        for t_name, t_def in self.semantic["time_columns"].items():
            time_def = t_def
            tables_needed.add(t_def["table"])
            break

        # --- STEP 4: DETERMINE BASE TABLE ---
        base_table = metric_defs[0]["table"]

        # --- STEP 5: BUILD JOIN PATH ---

        joins = []
        join_ambiguities = []
        for table in tables_needed:
            if table == base_table:
                continue
            join_result = self.join_resolver.find_join(self.graph, base_table, table)
            if join_result["ambiguous"]:
                join_ambiguities.append({
                    "from": base_table,
                    "to": table,
                    "candidates": join_result["candidates"],
                    "clarification_prompt": f"Multiple join paths found from {base_table} to {table}. Please specify which table or path to use."
                })
            joins.extend(join_result["path"])
        unique_joins = {j["join"]: j for j in joins}.values()

        # --- STEP 6: BUILD DATA REQUIREMENTS ---
        metric_plan = [
            {
                "name": m["column"],
                "aggregation": m.get("aggregation", "SUM"),
                "table": m["table"]
            }
            for m in metric_defs
        ]
        dimension_plan = [
            {
                "name": d["column"],
                "table": d["table"]
            }
            for d in dimension_defs
        ]

        # --- STEP 7: TIME LOGIC ---
        grain = "month" if "time" in dimensions else None

        # --- STEP 8: CALCULATIONS ---
        calculations = []
        if intent["intent_type"] in ["growth", "trend_analysis"]:
            for m in metric_plan:
                calculations.append({
                    "type": "growth",
                    "metric": m["name"]
                })

        # --- STEP 9: BUILD PLAN ---
        plan = {
            "plan_id": str(uuid.uuid4()),
            "intent_id": intent["intent_id"],
            "base_table": base_table,
            "data_requirements": {
                "metrics": metric_plan,
                "dimensions": dimension_plan,
                "time": time_def
            },
            "joins": list(unique_joins),
            "time_logic": {
                "current_period": time_range.get("value"),
                "comparison_period": None,
                "grain": grain
            },
            "calculations": calculations,
            "grouping": [d["name"] for d in dimension_plan] + ([grain] if grain else []),
            "ordering": [
                {
                    "field": grain or (dimension_plan[0]["name"] if dimension_plan else None),
                    "direction": "asc"
                }
            ],
            "limit": {
                "value": 1000,
                "enforced": False
            }
        }
        if join_ambiguities:
            plan["ambiguity"] = {
                "type": "join_path",
                "details": join_ambiguities,
                "clarification_prompt": join_ambiguities[0]["clarification_prompt"] if join_ambiguities else "Ambiguous join path detected. Please clarify."
            }
        return plan

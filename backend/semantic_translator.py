from typing import Any, Dict, Optional

class SemanticTranslator:
    def __init__(self, registry, knowledge_graph=None):
        self.registry = registry
        self.graph = knowledge_graph

    def translate(self, semantic_query: Dict[str, Any]) -> Dict[str, Any]:
        metric_name = semantic_query.get("metric")
        dimension_name = semantic_query.get("dimension")
        time_config = semantic_query.get("time", {})

        metric = self.registry.get_metric(metric_name)
        dimension = self.registry.get_dimension(dimension_name)

        metric_expr = self._build_metric_expression(metric)
        dimension_field = dimension["sourceField"]

        joins = self._resolve_joins(metric, dimension)

        return {
            "select": [
                {"type": "dimension", "field": dimension_field},
                {"type": "metric", "expression": metric_expr, "alias": metric_name}
            ],
            "group_by": [dimension_field],
            "time_filter": self._build_time_filter(time_config),
            "joins": joins
        }

    # --- METRIC ---
    def _build_metric_expression(self, metric: Dict[str, Any]) -> str:
        agg = metric["aggregation"].upper()
        field = metric["sourceFields"][0]
        return f"{agg}({field})"

    # --- TIME ---
    def _build_time_filter(self, time_config: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "field": self.registry.time["defaultField"],
            "range": time_config.get("range")
        }

    # --- RELATIONSHIPS ---
    def _resolve_joins(self, metric: Dict[str, Any], dimension: Dict[str, Any]):
        metric_table = metric["sourceFields"][0].split(".")[0]
        dimension_table = dimension["sourceField"].split(".")[0]

        if metric_table == dimension_table:
            return []

        # Use knowledge graph if available
        if self.graph:
            path = self.graph.find_join_path(metric_table, dimension_table)
            return self._convert_path_to_joins(path)

        # fallback to direct relationships
        joins = []
        for rel in self.registry.get_relationships():
            if metric_table in rel["to"] and dimension_table in rel["from"]:
                joins.append(rel)
        return joins

    def _convert_path_to_joins(self, path):
        joins = []
        for i in range(len(path) - 1):
            joins.append({
                "from": path[i],
                "to": path[i + 1]
            })
        return joins

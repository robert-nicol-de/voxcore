from __future__ import annotations

from typing import Any

import backend.db.org_store as store

from .analytical_planner import AnalyticalPlanner
from .auto_drill_engine import AutoDrillEngine
from .context_injector import build_context_prompt
from .dimension_catalog import DimensionCatalog
from .hypothesis_engine import HypothesisEngine
from .insight_ranker import InsightRanker
from .intent_parser import extract_query_intent
from .metric_expansion import MetricExpansionEngine
from .metric_registry import MetricRegistry
from .pattern_detection import PatternDetectionEngine
from .relationship_graph import RelationshipGraph
from .schema_intelligence import SchemaIntelligence
from .visualization_engine import VisualizationEngine
from .query_graph import QueryGraphBuilder, QueryGraphExecutor

_NUMERIC_HINTS = ["int", "integer", "float", "double", "real", "numeric", "decimal", "money"]
_TIME_HINTS = ["date", "time", "timestamp", "year", "month", "quarter"]


class SemanticBrainService:
    def __init__(self) -> None:
        self.planner = AnalyticalPlanner()
        self.visualization = VisualizationEngine()
        self.hypothesis_engine = HypothesisEngine()
        self.auto_drill_engine = AutoDrillEngine()
        self.pattern_engine = PatternDetectionEngine()
        self.insight_ranker = InsightRanker()
        self.metric_expansion = MetricExpansionEngine()
        self.schema_intelligence = SchemaIntelligence()
        self.graph_builder = QueryGraphBuilder()
        self.graph_executor = QueryGraphExecutor()

    def build_snapshot(self, workspace_id: Any, ai_context: dict[str, Any] | None = None) -> dict[str, Any]:
        try:
            ws = int(str(workspace_id))
        except Exception:
            ws = 1

        schema_rows = store.list_workspace_schema_snapshot(ws, max_tables=80, max_columns_per_table=40)
        semantic_models = store.list_semantic_models(ws)

        metric_registry = MetricRegistry.from_semantic_models(semantic_models)
        dimension_catalog = DimensionCatalog.from_semantic_models_and_schema(semantic_models, schema_rows)
        relationship_graph = RelationshipGraph.from_schema(schema_rows)

        time_dimensions: list[str] = []
        for table in schema_rows:
            table_name = str(table.get("table_name") or "")
            if not table_name:
                continue
            for col in table.get("columns", []):
                col_name = str(col.get("column_name") or "")
                data_type = str(col.get("data_type") or "").lower()
                if not col_name:
                    continue
                if any(token in col_name.lower() for token in _TIME_HINTS) or any(token in data_type for token in _TIME_HINTS):
                    fq_col = f"{table_name}.{col_name}"
                    if fq_col not in time_dimensions:
                        time_dimensions.append(fq_col)

                if any(token in data_type for token in _NUMERIC_HINTS):
                    metric_name = f"sum_{col_name}".lower()
                    if metric_name not in metric_registry.metrics:
                        metric_registry.metrics[metric_name] = {
                            "sql": f"SUM({table_name}.{col_name})",
                            "description": f"Sum of {col_name}",
                        }

        return {
            "workspace_id": ws,
            "metric_registry": [
                {"name": key, "sql": value.get("sql", ""), "description": value.get("description", ""), "source": "semantic_brain"}
                for key, value in list(metric_registry.metrics.items())[:80]
            ],
            "dimension_catalog": [
                {
                    "dimension": key,
                    "table": value.get("table", ""),
                    "column": value.get("column", key),
                    "type": "categorical",
                    "source": "semantic_brain",
                }
                for key, value in list(dimension_catalog.dimensions.items())[:150]
            ],
            "time_intelligence": {
                "time_dimensions": time_dimensions[:20],
                "supported_comparisons": ["YoY", "MoM", "QoQ", "Rolling"],
            },
            "business_logic_rules": [
                "Only approved read-safe SQL can execute.",
                "High-risk operations require governance approval.",
            ],
            "relationship_graph": [
                {"from": source, "to": target}
                for source, target in list(relationship_graph.relationships)[:120]
            ],
            "semantic_models": [
                {
                    "id": model.get("id"),
                    "name": model.get("name"),
                    "description": model.get("description") or "",
                }
                for model in semantic_models[:20]
            ],
            "schema_context_tables": len(schema_rows),
            "prompt_context": (ai_context or {}).get("prompt_context") if isinstance(ai_context, dict) else "",
        }

    def build_analytical_plan(
        self,
        query_text: str,
        snapshot: dict[str, Any],
        intent: dict[str, Any] | None = None,
        previous_plan: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        intent = intent or extract_query_intent(query_text)

        metric_name = str(intent.get("metric") or "revenue").lower()
        metric_map = {
            str(item.get("name") or "").lower(): item
            for item in snapshot.get("metric_registry", [])
            if isinstance(item, dict)
        }
        dim_name = str(intent.get("dimension") or "district").lower()
        dim_map = {
            str(item.get("dimension") or item.get("column") or "").lower(): item
            for item in snapshot.get("dimension_catalog", [])
            if isinstance(item, dict)
        }

        metric_item = metric_map.get(metric_name, {"sql": "SUM(sales_amount)"})
        dim_item = dim_map.get(dim_name)
        time_dimensions = (snapshot.get("time_intelligence") or {}).get("time_dimensions") or []

        base_plan = self.planner.build_plan(
            query_text=query_text,
            intent=intent,
            metric_sql=str(metric_item.get("sql") or "SUM(sales_amount)"),
            dimension_info=dim_item,
            time_dimensions=time_dimensions,
        )
        return self.planner.apply_followup_context(query_text, base_plan, previous_plan)

    def recommend_visualization(self, plan: dict[str, Any]) -> dict[str, str]:
        return self.visualization.recommend_chart(plan)

    def generate_sql(self, plan: dict[str, Any], fallback_sql: str = "") -> str:
        metric_sql = str(plan.get("metric_sql") or "SUM(sales_amount)")
        dimension_col = str(plan.get("dimension_column") or plan.get("dimension") or "district")
        comparison = str(plan.get("comparison") or "")
        time_dimension = str(plan.get("time_dimension") or "order_date")
        try:
            limit_value = max(1, min(200, int(plan.get("limit") or 10)))
        except Exception:
            limit_value = 10

        if comparison == "YoY":
            return (
                f"SELECT {dimension_col},\n"
                f"       EXTRACT(YEAR FROM {time_dimension}) AS year,\n"
                f"       {metric_sql} AS metric_value,\n"
                f"       ({metric_sql} - LAG({metric_sql}) OVER (PARTITION BY {dimension_col} ORDER BY EXTRACT(YEAR FROM {time_dimension}))) AS yoy_delta\n"
                f"FROM sales\n"
                f"GROUP BY {dimension_col}, EXTRACT(YEAR FROM {time_dimension})\n"
                f"ORDER BY {dimension_col}, year"
            )

        if comparison == "MoM":
            return (
                f"SELECT {dimension_col},\n"
                f"       EXTRACT(MONTH FROM {time_dimension}) AS month,\n"
                f"       {metric_sql} AS metric_value\n"
                f"FROM sales\n"
                f"GROUP BY {dimension_col}, EXTRACT(MONTH FROM {time_dimension})\n"
                f"ORDER BY {dimension_col}, month"
            )

        if fallback_sql:
            return fallback_sql

        return (
            f"SELECT {dimension_col}, {metric_sql} AS metric_value\n"
            f"FROM sales\n"
            f"GROUP BY {dimension_col}\n"
            f"ORDER BY metric_value DESC\n"
            f"LIMIT {limit_value}"
        )

    def detect_insights(self, plan: dict[str, Any], preview_rows: list[dict[str, Any]]) -> dict[str, Any]:
        if not preview_rows:
            return {
                "top_performer": None,
                "largest_decline": None,
                "anomaly": None,
                "overall_trend": "unknown",
                "narrative": "No result rows yet. Run the query to generate insights.",
            }

        first = preview_rows[0]
        numeric_keys = [
            key
            for key in first.keys()
            if isinstance(first.get(key), (int, float)) and not isinstance(first.get(key), bool)
        ]
        metric_key = numeric_keys[0] if numeric_keys else None
        if not metric_key:
            return {
                "top_performer": None,
                "largest_decline": None,
                "anomaly": None,
                "overall_trend": "mixed",
                "narrative": f"Loaded {len(preview_rows)} rows.",
            }

        dimension = str(plan.get("dimension") or "dimension")
        top_row = max(preview_rows, key=lambda row: float(row.get(metric_key) or 0))
        low_row = min(preview_rows, key=lambda row: float(row.get(metric_key) or 0))

        top_name = top_row.get(dimension) or top_row.get("district") or top_row.get("name") or "top segment"
        top_value = float(top_row.get(metric_key) or 0)
        low_name = low_row.get(dimension) or low_row.get("district") or low_row.get("name") or "lowest segment"
        low_value = float(low_row.get(metric_key) or 0)

        values = [float(row.get(metric_key) or 0) for row in preview_rows]
        avg = sum(values) / len(values)
        anomaly = None
        if abs(top_value - avg) > (0.5 * max(avg, 1.0)):
            anomaly = f"{top_name} deviates strongly from the mean ({top_value:.2f} vs {avg:.2f})."

        overall_trend = "positive" if sum(1 for value in values if value > 0) >= max(1, int(len(values) * 0.6)) else "mixed"
        largest_decline = f"{low_name} {low_value:.2f}" if low_value < 0 else None

        narrative = [f"{top_name} is the top performer at {top_value:.2f} {metric_key}."]
        if largest_decline:
            narrative.append(f"{low_name} is declining at {low_value:.2f}.")
        if anomaly:
            narrative.append(anomaly)
        narrative.append(f"Overall trend appears {overall_trend}.")

        return {
            "top_performer": f"{top_name} {top_value:.2f}",
            "largest_decline": largest_decline,
            "anomaly": anomaly,
            "overall_trend": overall_trend,
            "narrative": " ".join(narrative),
        }

    def generate_suggested_questions(self, plan: dict[str, Any], insights: dict[str, Any] | None = None) -> list[str]:
        metric = str(plan.get("metric") or "revenue")
        dimension = str(plan.get("dimension") or "district")
        comparison = str(plan.get("comparison") or "")
        focus = str(plan.get("focus") or "").strip()

        suggestions = [
            f"Which {dimension} had the fastest growth this quarter?",
            f"Show {comparison or 'trend'} {metric} by month".strip(),
            f"Compare {dimension} performance by profit margin",
        ]

        if focus:
            suggestions.insert(0, f"What product categories drove growth in {focus}?")
        else:
            top = (insights or {}).get("top_performer")
            if isinstance(top, str) and top:
                top_name = top.split(" ")[0]
                suggestions.insert(0, f"Why did {top_name} perform so strongly?")

        deduped: list[str] = []
        seen: set[str] = set()
        for suggestion in suggestions:
            key = suggestion.strip().lower()
            if key and key not in seen:
                seen.add(key)
                deduped.append(suggestion)
        return deduped[:4]

    def build_semantic_context_prompt(self, snapshot: dict[str, Any]) -> str:
        metric_lines = [
            f"- {item.get('name', 'metric')} = {item.get('sql', '')}"
            for item in snapshot.get("metric_registry", [])[:12]
        ]
        dimension_lines = [
            f"- {item.get('dimension', item.get('column', 'dimension'))} ({item.get('table', '')}.{item.get('column', '')})"
            for item in snapshot.get("dimension_catalog", [])[:20]
        ]
        time_dimension = ((snapshot.get("time_intelligence") or {}).get("time_dimensions") or ["order_date"])[0]
        return build_context_prompt(metric_lines, dimension_lines, time_dimension)

    def build_understanding(self, intent: dict[str, Any]) -> dict[str, str]:
        metric = str(intent.get("metric") or "sales").capitalize()
        dimension = str(intent.get("dimension") or "district").capitalize()
        comparison = str(intent.get("comparison") or "None")
        return {
            "metric": metric,
            "dimension": dimension,
            "comparison": comparison,
            "summary": f"Metric: {metric} | Dimension: {dimension} | Comparison: {comparison}",
        }

    def extract_schema_summary(self, ai_context: dict[str, Any], max_lines: int = 8) -> list[str]:
        prompt_context = str((ai_context or {}).get("prompt_context") or "").strip()
        if not prompt_context:
            return []

        lines: list[str] = []
        for line in prompt_context.splitlines():
            if "(" in line and ")" in line and "/" in line:
                lines.append(line.strip())
            if len(lines) >= max_lines:
                break
        return lines

    def suggest_sql(self, query_text: str, intent: dict[str, Any]) -> str:
        if intent.get("is_sql_input"):
            return query_text

        metric = str(intent.get("metric") or "sales")
        dimension = str(intent.get("dimension") or "district")
        comparison = str(intent.get("comparison") or "")

        if comparison == "YoY":
            return (
                "SELECT {dimension},\n"
                "       EXTRACT(YEAR FROM sale_date) AS year,\n"
                "       SUM({metric}) AS total_{metric}\n"
                "FROM sales\n"
                "GROUP BY {dimension}, EXTRACT(YEAR FROM sale_date)\n"
                "ORDER BY {dimension}, year"
            ).format(dimension=dimension, metric=metric)

        return (
            "SELECT {dimension}, SUM({metric}) AS total_{metric}\n"
            "FROM sales\n"
            "GROUP BY {dimension}\n"
            "ORDER BY total_{metric} DESC\n"
            "LIMIT 10"
        ).format(dimension=dimension, metric=metric)

    def build_preview_chart(self, preview_rows: list[dict[str, Any]], intent: dict[str, Any], plan: dict[str, Any]) -> dict[str, Any] | None:
        recommendation = self.recommend_visualization(plan)
        return self.visualization.build_preview_chart(preview_rows, intent, recommendation)

    def build_payload(
        self,
        query_text: str,
        workspace_id: Any,
        ai_context: dict[str, Any],
        previous_plan: dict[str, Any] | None = None,
        preview_rows: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        intent = extract_query_intent(query_text)
        snapshot = self.build_snapshot(workspace_id, ai_context)
        plan = self.build_analytical_plan(query_text, snapshot, intent, previous_plan)
        generated_sql = self.generate_sql(plan, fallback_sql=self.suggest_sql(query_text, intent))
        preview = preview_rows or []
        insights = self.detect_insights(plan, preview)
        hypotheses = self.hypothesis_engine.generate_hypotheses(plan)
        patterns = self.pattern_engine.detect_patterns(preview)
        auto_drill = self.auto_drill_engine.suggest_drills(
            plan,
            top_focus=str(insights.get("top_performer") or ""),
        )
        driver_hints = self.auto_drill_engine.summarize_driver_hints(plan, insights)
        ranked_insights = self.insight_ranker.rank(insights, hypotheses, patterns)
        related_metrics = self.metric_expansion.expand(str(plan.get("metric") or ""))
        schema_matches = self.schema_intelligence.match_terms(query_text, snapshot)

        chart_rec = self.recommend_visualization(plan)
        query_graph = self.graph_builder.build(plan, chart_rec)
        graph_sql = self.graph_executor.compile_sql(query_graph)
        graph_insight_hints = self.graph_executor.to_insight_hints(query_graph)
        graph_followups = self.graph_executor.to_followup_questions(query_graph)
        graph_drilldowns = self.graph_executor.to_drilldowns(query_graph)
        graph_explanation = self.graph_executor.to_explanation(query_graph)

        return {
            "ai_context": ai_context,
            "schema_summary": self.extract_schema_summary(ai_context),
            "schema_intelligence": schema_matches,
            "intent": intent,
            "understanding": self.build_understanding(intent),
            "analysis_plan": plan,
            "analytical_plan": plan,
            "chart_recommendation": chart_rec,
            "generated_sql": generated_sql,
            "query_graph": {
                "nodes": query_graph,
                "compiled_sql": graph_sql,
                "insight_hints": graph_insight_hints,
                "followup_questions": graph_followups,
                "drilldowns": graph_drilldowns,
                "explanation": graph_explanation,
            },
            "semantic_brain": {
                "metric_registry": snapshot.get("metric_registry", [])[:12],
                "dimension_catalog": snapshot.get("dimension_catalog", [])[:20],
                "relationship_graph": snapshot.get("relationship_graph", [])[:20],
                "time_intelligence": snapshot.get("time_intelligence", {}),
                "business_logic_rules": snapshot.get("business_logic_rules", [])[:10],
            },
            "semantic_context_prompt": self.build_semantic_context_prompt(snapshot),
            "insights": insights,
            "insight_summary": str(insights.get("narrative") or "No clear insights yet."),
            "ranked_insights": ranked_insights,
            "hypotheses": hypotheses,
            "auto_drill": auto_drill,
            "driver_hints": driver_hints,
            "patterns": patterns,
            "related_metrics": related_metrics,
            "suggested_questions": self.generate_suggested_questions(plan, insights),
        }

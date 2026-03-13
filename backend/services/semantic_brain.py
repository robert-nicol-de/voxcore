from __future__ import annotations

import re
from typing import Any

import backend.db.org_store as store


NUMERIC_TYPES = {
    "int",
    "integer",
    "bigint",
    "smallint",
    "float",
    "double",
    "real",
    "numeric",
    "decimal",
    "money",
}

TIME_HINTS = ["date", "time", "timestamp", "year", "month", "quarter"]


def _normalize(text: Any) -> str:
    return str(text or "").strip().lower()


def _looks_numeric(type_name: str) -> bool:
    value = _normalize(type_name)
    return any(token in value for token in NUMERIC_TYPES)


def _is_time_column(name: str, type_name: str) -> bool:
    n = _normalize(name)
    t = _normalize(type_name)
    return any(h in n for h in TIME_HINTS) or any(h in t for h in TIME_HINTS)


def _extract_metrics_from_model(definition: dict[str, Any]) -> list[dict[str, Any]]:
    metrics: list[dict[str, Any]] = []
    model_metrics = definition.get("metrics") if isinstance(definition, dict) else None
    if isinstance(model_metrics, dict):
        for metric_name, payload in model_metrics.items():
            item = payload if isinstance(payload, dict) else {}
            metrics.append(
                {
                    "name": metric_name,
                    "sql": item.get("sql") or item.get("expression") or "",
                    "description": item.get("description") or "",
                    "source": "semantic_model",
                }
            )
    return metrics


def _extract_dimensions_from_model(definition: dict[str, Any]) -> list[dict[str, Any]]:
    dims: list[dict[str, Any]] = []
    model_dims = definition.get("dimensions") if isinstance(definition, dict) else None
    if isinstance(model_dims, dict):
        for dim_name, payload in model_dims.items():
            item = payload if isinstance(payload, dict) else {}
            dims.append(
                {
                    "dimension": dim_name,
                    "table": item.get("table") or "",
                    "column": item.get("column") or dim_name,
                    "type": item.get("type") or "categorical",
                    "source": "semantic_model",
                }
            )
    return dims


def _registry_from_schema(schema_rows: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, str]], list[str]]:
    metric_registry: list[dict[str, Any]] = []
    dimension_catalog: list[dict[str, Any]] = []
    relationship_graph: list[dict[str, str]] = []
    time_dimensions: list[str] = []

    primary_keys: dict[str, str] = {}
    foreign_key_candidates: list[tuple[str, str, str]] = []

    for table in schema_rows:
        table_name = str(table.get("table_name") or "")
        if not table_name:
            continue
        for col in table.get("columns", []):
            column_name = str(col.get("column_name") or "")
            data_type = str(col.get("data_type") or "")
            if not column_name:
                continue

            fq_col = f"{table_name}.{column_name}"
            if col.get("primary_key"):
                primary_keys[fq_col] = table_name

            if column_name.endswith("_id"):
                foreign_key_candidates.append((table_name, column_name, fq_col))

            if _looks_numeric(data_type):
                metric_registry.append(
                    {
                        "name": f"sum_{column_name}",
                        "sql": f"SUM({fq_col})",
                        "description": f"Sum of {column_name}",
                        "source": "schema_inferred",
                    }
                )

            if _is_time_column(column_name, data_type):
                if fq_col not in time_dimensions:
                    time_dimensions.append(fq_col)
            else:
                dimension_catalog.append(
                    {
                        "dimension": column_name,
                        "table": table_name,
                        "column": column_name,
                        "type": "categorical",
                        "source": "schema_inferred",
                    }
                )

    for table_name, column_name, fq_col in foreign_key_candidates:
        base = column_name[:-3]
        target = None
        for pk_col, pk_table in primary_keys.items():
            if pk_table == table_name:
                continue
            pk_name = pk_col.split(".", 1)[1]
            if pk_name == column_name or pk_name == f"{base}_id" or pk_name == "id":
                target = pk_col
                break
        if target:
            relationship_graph.append({"from": fq_col, "to": target})

    return metric_registry, dimension_catalog, relationship_graph, time_dimensions


def build_semantic_brain_snapshot(workspace_id: Any, ai_context: dict[str, Any] | None = None) -> dict[str, Any]:
    try:
        ws = int(str(workspace_id))
    except Exception:
        ws = 1

    schema_rows = store.list_workspace_schema_snapshot(ws, max_tables=80, max_columns_per_table=40)
    semantic_models = store.list_semantic_models(ws)

    metrics: list[dict[str, Any]] = []
    dimensions: list[dict[str, Any]] = []
    business_rules: list[str] = []

    for model in semantic_models:
        definition = model.get("definition") if isinstance(model, dict) else {}
        if not isinstance(definition, dict):
            definition = {}
        metrics.extend(_extract_metrics_from_model(definition))
        dimensions.extend(_extract_dimensions_from_model(definition))
        rules = definition.get("business_rules")
        if isinstance(rules, list):
            business_rules.extend([str(rule) for rule in rules if str(rule).strip()])

    schema_metrics, schema_dims, rel_graph, time_dims = _registry_from_schema(schema_rows)

    metric_registry = metrics + [m for m in schema_metrics if m["name"] not in {x["name"] for x in metrics}]

    dimension_keys = {(d["table"], d["column"]) for d in dimensions}
    dimension_catalog = dimensions + [d for d in schema_dims if (d["table"], d["column"]) not in dimension_keys]

    if not business_rules:
        business_rules = [
            "Only approved read-safe SQL can execute.",
            "High-risk operations require governance approval.",
        ]

    return {
        "workspace_id": ws,
        "metric_registry": metric_registry[:80],
        "dimension_catalog": dimension_catalog[:150],
        "time_intelligence": {
            "time_dimensions": time_dims[:20],
            "supported_comparisons": ["YoY", "MoM", "QoQ", "Rolling"],
        },
        "business_logic_rules": business_rules[:30],
        "relationship_graph": rel_graph[:120],
        "semantic_models": [
            {
                "id": m.get("id"),
                "name": m.get("name"),
                "description": m.get("description") or "",
            }
            for m in semantic_models[:20]
        ],
        "schema_context_tables": len(schema_rows),
        "prompt_context": (ai_context or {}).get("prompt_context") if isinstance(ai_context, dict) else "",
    }


def _detect_comparison(text: str) -> str | None:
    value = _normalize(text)
    if "year over year" in value or "year-over-year" in value or "yoy" in value:
        return "YoY"
    if "month over month" in value or "month-over-month" in value or "mom" in value:
        return "MoM"
    if "quarter over quarter" in value or "qoq" in value:
        return "QoQ"
    if "rolling" in value or "moving average" in value:
        return "Rolling"
    return None


def build_analytical_plan(query_text: str, brain: dict[str, Any], intent: dict[str, Any] | None = None) -> dict[str, Any]:
    text = _normalize(query_text)
    intent = intent or {}

    metrics = brain.get("metric_registry") or []
    dims = brain.get("dimension_catalog") or []
    time_dimensions = (brain.get("time_intelligence") or {}).get("time_dimensions") or []

    metric_name = _normalize(intent.get("metric")) or "revenue"
    for m in metrics:
        candidate = _normalize(m.get("name"))
        if candidate and (candidate == metric_name or candidate in text or metric_name in candidate):
            metric_name = m.get("name")
            break

    dim_name = _normalize(intent.get("dimension")) or "district"
    dim_table = ""
    dim_column = dim_name
    for d in dims:
        candidate = _normalize(d.get("dimension") or d.get("column"))
        if candidate and (candidate == dim_name or candidate in text):
            dim_name = d.get("dimension") or d.get("column") or dim_name
            dim_table = d.get("table") or ""
            dim_column = d.get("column") or dim_name
            break

    comparison = intent.get("comparison") or _detect_comparison(text)
    time_grain = "year" if comparison == "YoY" else "month" if comparison == "MoM" else "quarter" if comparison == "QoQ" else "month"
    analysis_type = "comparison" if comparison else "trend" if intent.get("has_trend") else "ranking"

    time_dimension = time_dimensions[0] if time_dimensions else "order_date"

    return {
        "analysis_type": analysis_type,
        "metric": metric_name,
        "dimension": dim_name,
        "dimension_table": dim_table,
        "dimension_column": dim_column,
        "comparison": comparison,
        "time_dimension": time_dimension,
        "time_grain": time_grain,
        "focus": None,
    }


def apply_followup_context(query_text: str, plan: dict[str, Any], previous_plan: dict[str, Any] | None = None) -> dict[str, Any]:
    if not previous_plan:
        return plan

    text = _normalize(query_text)
    is_followup = any(
        token in text
        for token in [
            "why",
            "what drove",
            "drill",
            "breakdown",
            "that",
            "this",
            "it",
        ]
    )
    if not is_followup:
        return plan

    enriched = dict(plan)
    if not enriched.get("metric"):
        enriched["metric"] = previous_plan.get("metric")
    if not enriched.get("dimension"):
        enriched["dimension"] = previous_plan.get("dimension")
    if not enriched.get("comparison"):
        enriched["comparison"] = previous_plan.get("comparison")
    if not enriched.get("time_dimension"):
        enriched["time_dimension"] = previous_plan.get("time_dimension")
    if not enriched.get("time_grain"):
        enriched["time_grain"] = previous_plan.get("time_grain")

    focus_match = re.search(r"(?:why\s+did|in|for)\s+([a-z0-9_\- ]{2,40})", text)
    if focus_match:
        enriched["focus"] = focus_match.group(1).strip().title()
    elif previous_plan.get("focus"):
        enriched["focus"] = previous_plan.get("focus")

    if "why" in text or "what drove" in text:
        enriched["analysis_type"] = "diagnostic"

    return enriched


def recommend_visualization(plan: dict[str, Any]) -> dict[str, str]:
    analysis_type = _normalize(plan.get("analysis_type"))
    comparison = _normalize(plan.get("comparison"))

    if analysis_type == "trend":
        chart = "line"
    elif analysis_type == "comparison" or comparison in {"yoy", "mom", "qoq"}:
        chart = "bar"
    elif analysis_type == "ranking":
        chart = "horizontal_bar"
    elif analysis_type == "composition":
        chart = "stacked_bar"
    else:
        chart = "bar"

    return {
        "chart_type": chart,
        "reason": f"{analysis_type or 'comparison'} analysis maps best to {chart} visualization.",
    }


def generate_semantic_sql(plan: dict[str, Any], brain: dict[str, Any], fallback_sql: str = "") -> str:
    metric_name = str(plan.get("metric") or "revenue")
    dimension_col = str(plan.get("dimension_column") or plan.get("dimension") or "district")
    comparison = str(plan.get("comparison") or "")
    time_dimension = str(plan.get("time_dimension") or "order_date")
    time_grain = str(plan.get("time_grain") or "year")

    metric_sql = "SUM(sales_amount)"
    for m in brain.get("metric_registry", []):
        if _normalize(m.get("name")) == _normalize(metric_name):
            sql_expr = str(m.get("sql") or "").strip()
            if sql_expr:
                metric_sql = sql_expr
            break

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
        f"LIMIT 10"
    )


def generate_insight_summary(plan: dict[str, Any], preview_rows: list[dict[str, Any]]) -> str:
    insights = detect_insights(plan, preview_rows)
    if not insights.get("narrative"):
        return "No clear insights yet."
    return str(insights.get("narrative"))


def detect_insights(plan: dict[str, Any], preview_rows: list[dict[str, Any]]) -> dict[str, Any]:
    if not preview_rows:
        return {
            "top_performer": None,
            "largest_decline": None,
            "anomaly": None,
            "overall_trend": "unknown",
            "narrative": "No result rows yet. Run the query to generate insights.",
        }

    metric = str(plan.get("metric") or "metric")
    dimension = str(plan.get("dimension") or "dimension")

    numeric_keys = [
        key
        for key in preview_rows[0].keys()
        if isinstance(preview_rows[0].get(key), (int, float)) and not isinstance(preview_rows[0].get(key), bool)
    ]
    metric_key = numeric_keys[0] if numeric_keys else None
    if not metric_key:
        return {
            "top_performer": None,
            "largest_decline": None,
            "anomaly": None,
            "overall_trend": "mixed",
            "narrative": f"Loaded {len(preview_rows)} rows for {dimension} breakdown.",
        }

    top_row = max(preview_rows, key=lambda row: float(row.get(metric_key) or 0))
    top_dimension = top_row.get(dimension) or top_row.get("district") or top_row.get("name") or top_row.get("customer_id") or "top segment"
    top_value = float(top_row.get(metric_key) or 0)

    low_row = min(preview_rows, key=lambda row: float(row.get(metric_key) or 0))
    low_dimension = low_row.get(dimension) or low_row.get("district") or low_row.get("name") or "lowest segment"
    low_value = float(low_row.get(metric_key) or 0)

    values = [float(row.get(metric_key) or 0) for row in preview_rows]
    avg = sum(values) / len(values)
    anomaly = None
    if abs(top_value - avg) > (0.5 * max(avg, 1.0)):
        anomaly = f"{top_dimension} deviates strongly from the mean ({top_value:.2f} vs {avg:.2f})."

    overall_trend = "positive" if sum(1 for v in values if v > 0) >= max(1, int(len(values) * 0.6)) else "mixed"
    decline = None
    if low_value < 0:
        decline = f"{low_dimension} {low_value:.2f}"

    narrative_parts = [
        f"{top_dimension} is the top performer at {top_value:.2f} {metric_key}.",
    ]
    if decline:
        narrative_parts.append(f"{low_dimension} is declining at {low_value:.2f}.")
    if anomaly:
        narrative_parts.append(anomaly)
    narrative_parts.append(f"Overall trend appears {overall_trend}.")

    return {
        "top_performer": f"{top_dimension} {top_value:.2f}",
        "largest_decline": decline,
        "anomaly": anomaly,
        "overall_trend": overall_trend,
        "narrative": " ".join(narrative_parts),
    }


def generate_suggested_questions(plan: dict[str, Any], insights: dict[str, Any] | None = None) -> list[str]:
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
    for item in suggestions:
        key = _normalize(item)
        if key and key not in seen:
            seen.add(key)
            deduped.append(item)
    return deduped[:4]


def build_semantic_context_prompt(brain: dict[str, Any], max_metrics: int = 12, max_dimensions: int = 20) -> str:
    metric_lines = []
    for metric in (brain.get("metric_registry") or [])[:max_metrics]:
        name = metric.get("name") or "metric"
        sql = metric.get("sql") or ""
        metric_lines.append(f"- {name} = {sql}")

    dim_lines = []
    for dim in (brain.get("dimension_catalog") or [])[:max_dimensions]:
        name = dim.get("dimension") or dim.get("column") or "dimension"
        table = dim.get("table") or ""
        column = dim.get("column") or name
        dim_lines.append(f"- {name} ({table}.{column})")

    time_dims = (brain.get("time_intelligence") or {}).get("time_dimensions") or []
    time_lines = [f"- {value}" for value in time_dims[:8]]

    sections = []
    if metric_lines:
        sections.append("Available metrics:\n" + "\n".join(metric_lines))
    if dim_lines:
        sections.append("Available dimensions:\n" + "\n".join(dim_lines))
    if time_lines:
        sections.append("Time dimensions:\n" + "\n".join(time_lines))

    if not sections:
        return "No semantic context available yet."
    return "\n\n".join(sections)

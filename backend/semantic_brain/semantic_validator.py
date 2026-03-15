from __future__ import annotations

from typing import Any

_ALLOWED_AGGREGATIONS = frozenset({"sum", "count", "avg", "min", "max", "count_distinct"})

# Fallback dimension suggestions when the requested dimension isn't in the catalog
_FALLBACK_MAP: dict[str, list[str]] = {
    "district":  ["region", "area", "zone", "territory"],
    "region":    ["district", "area", "zone"],
    "country":   ["region", "territory", "market"],
    "city":      ["district", "region", "area"],
    "category":  ["segment", "type", "group", "product_type"],
    "product":   ["item", "sku", "product_name"],
    "customer":  ["client", "account", "customer_name"],
    "channel":   ["segment", "source", "sales_channel"],
    "team":      ["rep", "sales_team", "group"],
    "rep":       ["team", "salesperson", "account_manager"],
}


class SemanticValidator:
    """
    Validate an analytical plan against the live semantic snapshot before SQL
    generation.  Returns a confidence-rated result with fallback suggestions.
    """

    def validate(
        self,
        plan: dict[str, Any],
        snapshot: dict[str, Any],
    ) -> dict[str, Any]:
        metric_name  = str(plan.get("metric")      or "").lower().strip()
        dimension_nm = str(plan.get("dimension")   or "").lower().strip()
        aggregation  = str(plan.get("aggregation") or "sum").lower().strip()
        time_dim     = str(plan.get("time_dimension") or "").lower().strip()
        dim_table    = str(plan.get("dimension_table") or "").lower().strip()

        metric_registry  = [str(i.get("name") or "").lower().strip() for i in snapshot.get("metric_registry", [])]
        dim_catalog      = [
            str(i.get("dimension") or i.get("column") or "").lower().strip()
            for i in snapshot.get("dimension_catalog", [])
        ]
        time_dimensions  = (snapshot.get("time_intelligence") or {}).get("time_dimensions", [])
        relationship_graph = snapshot.get("relationship_graph", [])

        # ── Metric validation ────────────────────────────────────────────────
        metric_valid = bool(metric_name) and (
            metric_name in metric_registry
            or any(metric_name in key for key in metric_registry)
        )

        # ── Dimension validation + fallback ───────────────────────────────────
        dimension_valid = bool(dimension_nm) and (
            dimension_nm in dim_catalog
            or any(dimension_nm in key for key in dim_catalog)
        )
        dimension_fallback: str | None = None
        if not dimension_valid and dimension_nm:
            for candidate in _FALLBACK_MAP.get(dimension_nm, []):
                if any(candidate in key for key in dim_catalog):
                    dimension_fallback = candidate
                    break
            if not dimension_fallback and dim_catalog:
                dimension_fallback = dim_catalog[0]

        # ── Aggregation validation ────────────────────────────────────────────
        aggregation_valid = aggregation in _ALLOWED_AGGREGATIONS

        # ── Join validity ─────────────────────────────────────────────────────
        join_valid = True
        if dim_table and relationship_graph:
            known_tables: set[str] = set()
            for edge in relationship_graph:
                for side in ("from", "to"):
                    known_tables.add(str(edge.get(side) or "").lower().split(".")[0])
            if known_tables:
                join_valid = any(dim_table in t for t in known_tables)

        # ── Time dimension support ────────────────────────────────────────────
        time_supported = bool(time_dimensions) or bool(time_dim)

        # ── Issue list ────────────────────────────────────────────────────────
        issues: list[str] = []
        if not metric_valid:
            issues.append(f"Metric '{metric_name}' not found in the metric registry.")
        if not dimension_valid:
            fb_hint = f"  Suggested fallback: '{dimension_fallback}'." if dimension_fallback else ""
            issues.append(f"Dimension '{dimension_nm}' not found in the dimension catalog.{fb_hint}")
        if not aggregation_valid:
            issues.append(
                f"Aggregation '{aggregation}' is not in the allowed set: "
                f"{sorted(_ALLOWED_AGGREGATIONS)}."
            )
        if plan.get("comparison") and not time_supported:
            issues.append("Time-based comparison requested but no time dimension is available.")

        overall_valid = metric_valid and dimension_valid and aggregation_valid

        # ── Semantic confidence ───────────────────────────────────────────────
        score = (
            (1.0 if metric_valid     else 0.30)
            + (1.0 if dimension_valid  else 0.40)
            + (1.0 if aggregation_valid else 0.80)
            + (1.0 if join_valid        else 0.70)
        ) / 4.0

        return {
            "metric_valid":      metric_valid,
            "dimension_valid":   dimension_valid,
            "aggregation_valid": aggregation_valid,
            "join_valid":        join_valid,
            "time_supported":    time_supported,
            "overall_valid":     overall_valid,
            "dimension_fallback": dimension_fallback,
            "issues":            issues,
            "semantic_confidence": round(score, 2),
        }

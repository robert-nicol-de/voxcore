from __future__ import annotations

import re
from typing import Any

# Patterns that indicate dangerous / mutating SQL operations
_DANGEROUS: list[str] = [
    r"\bdrop\b",
    r"\bdelete\b",
    r"\binsert\b",
    r"\bupdate\b",
    r"\btruncate\b",
    r"\balter\b",
    r"\bcreate\b",
    r"\bgrant\b",
    r"\brevoke\b",
    r"\bexec(?:ute)?\b",
    r"\bxp_\w+",
    r"--",
    r"/\*",
    r";\s*\w",   # statement chaining after first statement
]


def validate_sql(
    sql: str,
    components: dict[str, Any] | None = None,
    snapshot: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Run a safety and structural validation pass on *sql*.

    Checks:
    - No dangerous / mutating SQL commands (DDL, DML, exec)
    - SELECT statement present
    - FROM clause present
    - Aggregation functions are balanced with GROUP BY (auto-repair if possible)
    - Columns referenced against snapshot dimension catalog (soft warning)

    Returns:
        sql_valid       — False only when a dangerous pattern is found
        risk_level      — "low" | "medium" | "high"
        issues          — list of issue description strings
        corrected_sql   — auto-repaired SQL (or original if nothing changed)
        auto_repaired   — True when a repair was applied
    """
    lowered = (sql or "").lower().strip()
    issues: list[str] = []
    corrected_sql = sql
    auto_repaired = False

    # ── Dangerous pattern check ────────────────────────────────────────────
    danger_hits: list[str] = []
    for pattern in _DANGEROUS:
        if re.search(pattern, lowered):
            danger_hits.append(pattern)
    if danger_hits:
        for hit in danger_hits:
            issues.append(f"Dangerous SQL pattern detected: '{hit}'.")

    # ── Structural checks ──────────────────────────────────────────────────
    if not re.search(r"\bselect\b", lowered):
        issues.append("SQL does not contain a SELECT statement.")

    if not re.search(r"\bfrom\b", lowered):
        issues.append("SQL does not contain a FROM clause.")

    # ── Aggregation / GROUP BY balance ────────────────────────────────────
    has_aggregate = bool(re.search(r"\b(sum|count|avg|min|max)\s*\(", lowered))
    has_group_by  = bool(re.search(r"\bgroup\s+by\b", lowered))
    has_window    = bool(re.search(r"\bover\s*\(", lowered))

    if has_aggregate and not has_group_by and not has_window:
        issues.append(
            "SQL uses an aggregation function but is missing a GROUP BY clause."
        )
        # Auto-repair: infer dimension column from first SELECT item
        dim_match = re.search(r"select\s+(\w+)\s*,", lowered)
        if dim_match:
            dim_col = dim_match.group(1)
            corrected_sql = corrected_sql.rstrip() + f"\nGROUP BY {dim_col}"
            auto_repaired = True

    # ── Soft column validation against snapshot ────────────────────────────
    if snapshot and components:
        catalog_cols: set[str] = {
            str(i.get("column") or i.get("dimension") or "").lower()
            for i in snapshot.get("dimension_catalog", [])
        }
        # Only warn — do not block — on unrecognised group-by columns
        for col_expr in components.get("group_by", []):
            bare = col_expr.lower().split("(")[-1].strip(" )")
            if (
                bare
                and bare not in catalog_cols
                and bare not in {"year", "month", "quarter", "time_period", "day"}
            ):
                issues.append(
                    f"Column '{bare}' in GROUP BY was not found in the dimension catalog "
                    f"(may be acceptable if it comes from the table directly)."
                )

    # ── Risk classification ────────────────────────────────────────────────
    if danger_hits:
        risk_level = "high"
    elif issues:
        risk_level = "medium"
    else:
        risk_level = "low"

    sql_valid = risk_level != "high"

    return {
        "sql_valid":     sql_valid,
        "risk_level":    risk_level,
        "issues":        issues,
        "corrected_sql": corrected_sql,
        "auto_repaired": auto_repaired,
    }

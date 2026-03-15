from __future__ import annotations

import re
from typing import Any

_COL_NOT_FOUND  = re.compile(
    r"column ['\"]?(\w+)['\"]? (?:does not exist|not found|invalid column)",
    re.IGNORECASE,
)
_TABLE_NOT_FOUND = re.compile(
    r"(?:table|relation|object) ['\"]?(\w+)['\"]? (?:does not exist|not found|invalid object)",
    re.IGNORECASE,
)
_MAX_RETRIES = 3


class CorrectionEngine:
    """
    Automatic SQL correction loop for the VoxCore Brain.

    When Data Guardian rejects a query or execution fails, this engine:
    1. Parses the error message to identify the failure type.
    2. Consults the semantic snapshot for suitable replacements.
    3. Rebuilds the SQL with corrections applied.
    4. Tracks retry attempts and gives up after MAX_RETRIES.

    Usage::

        engine = CorrectionEngine()
        result = engine.attempt_correction(sql, error_msg, plan, snapshot, attempt=1)
        if result["correction_applied"]:
            retry_with(result["corrected_sql"])
    """

    max_retries: int = _MAX_RETRIES

    def attempt_correction(
        self,
        sql: str,
        error_message: str,
        plan: dict[str, Any],
        snapshot: dict[str, Any],
        attempt: int = 1,
    ) -> dict[str, Any]:
        """
        Attempt to auto-correct *sql* based on *error_message*.

        Returns:
            corrected_sql           — repaired SQL (or original if nothing changed)
            correction_applied      — True when at least one fix was made
            correction_description  — human-readable summary of changes
            retry_attempts          — current attempt index
            give_up                 — True when MAX_RETRIES is exceeded
        """
        if attempt > self.max_retries:
            return {
                "corrected_sql":           sql,
                "correction_applied":      False,
                "correction_description":  (
                    "Maximum correction attempts reached.  "
                    "Please refine your query manually."
                ),
                "retry_attempts": attempt,
                "give_up":        True,
            }

        corrected_sql  = sql
        corrections:    list[str] = []

        # ── Column not found ───────────────────────────────────────────────
        col_match = _COL_NOT_FOUND.search(error_message)
        if col_match:
            missing = col_match.group(1).lower()
            replacement = self._find_column_replacement(missing, snapshot)
            if replacement and replacement != missing:
                corrected_sql = re.sub(
                    rf"\b{re.escape(missing)}\b",
                    replacement,
                    corrected_sql,
                    flags=re.IGNORECASE,
                )
                corrections.append(f"Column '{missing}' → '{replacement}'.")

        # ── Table / relation not found ─────────────────────────────────────
        tbl_match = _TABLE_NOT_FOUND.search(error_message)
        if tbl_match:
            missing = tbl_match.group(1).lower()
            replacement = self._find_table_replacement(missing, snapshot)
            if replacement and replacement != missing:
                corrected_sql = re.sub(
                    rf"\b{re.escape(missing)}\b",
                    replacement,
                    corrected_sql,
                    flags=re.IGNORECASE,
                )
                corrections.append(f"Table '{missing}' → '{replacement}'.")

        # ── Missing GROUP BY ───────────────────────────────────────────────
        err_low = error_message.lower()
        if ("group by" in err_low or "aggregate" in err_low) and "GROUP BY" not in corrected_sql.upper():
            dim_col = str(plan.get("dimension_column") or plan.get("dimension") or "district")
            corrected_sql = corrected_sql.rstrip() + f"\nGROUP BY {dim_col}"
            corrections.append(f"Added missing GROUP BY {dim_col}.")

        correction_applied      = bool(corrections)
        correction_description  = (
            "; ".join(corrections)
            if corrections
            else "No automatic correction could be determined for this error."
        )

        return {
            "corrected_sql":          corrected_sql,
            "correction_applied":     correction_applied,
            "correction_description": correction_description,
            "retry_attempts":         attempt,
            "give_up":                False,
        }

    # ── Helpers ────────────────────────────────────────────────────────────
    def _find_column_replacement(
        self, missing: str, snapshot: dict[str, Any]
    ) -> str | None:
        candidates: list[str] = []
        for item in snapshot.get("dimension_catalog", []):
            for field in ("column", "dimension"):
                val = str(item.get(field) or "").lower()
                if val:
                    candidates.append(val)
        return self._best_match(missing, candidates)

    def _find_table_replacement(
        self, missing: str, snapshot: dict[str, Any]
    ) -> str | None:
        tables: set[str] = set()
        for edge in snapshot.get("relationship_graph", []):
            for side in ("from", "to"):
                tables.add(str(edge.get(side) or "").lower().split(".")[0])
        return self._best_match(missing, list(tables))

    @staticmethod
    def _best_match(target: str, candidates: list[str]) -> str | None:
        if not candidates:
            return None
        tgt = target.lower()
        if tgt in candidates:
            return tgt
        # Prefix / suffix match
        for c in candidates:
            if c.startswith(tgt) or tgt.startswith(c):
                return c
        # Shared-character heuristic
        best: str | None = None
        best_score = 0
        for c in candidates:
            score = sum(1 for ch in tgt if ch in c)
            if score > best_score:
                best_score = score
                best = c
        return best if best_score > 2 else None

"""
VoxCore Risk Scoring Engine

Assigns a numeric risk score (0-100) and level to every SQL query.
Decision logic:
  LOW      (0-29)  → run automatically
  MEDIUM   (30-59) → run + warning returned to caller
  HIGH     (60-84) → require approval before execution
  CRITICAL (85-100)→ block immediately
"""

from typing import TypedDict


class RiskResult(TypedDict):
    risk_score: int
    risk_level: str
    requires_approval: bool
    blocked: bool
    reasons: list


# Ordered rules: first match wins for the highest score bucket
_RULES: list[tuple[str, int, str]] = [
    # CRITICAL
    ("drop table",      95, "DROP TABLE will permanently destroy a table"),
    ("drop database",   97, "DROP DATABASE will destroy the entire database"),
    ("drop schema",     93, "DROP SCHEMA will destroy an entire schema"),
    ("truncate",        88, "TRUNCATE removes all rows without logging"),
    ("alter system",    90, "ALTER SYSTEM modifies server-level configuration"),
    # HIGH
    ("delete from",     80, "DELETE FROM will remove rows permanently"),
    ("drop index",      70, "DROP INDEX will remove an index permanently"),
    ("drop view",       65, "DROP VIEW will remove a view"),
    ("drop function",   65, "DROP FUNCTION will remove a function"),
    # MEDIUM
    ("update ",         60, "UPDATE modifies existing rows"),
    ("insert into",     40, "INSERT INTO adds new rows"),
    ("alter table",     45, "ALTER TABLE modifies table structure"),
    ("create table",    30, "CREATE TABLE modifies schema"),
    ("create index",    30, "CREATE INDEX modifies schema"),
]


def _classify(score: int) -> tuple[str, bool, bool]:
    """Return (risk_level, requires_approval, blocked)."""
    if score >= 85:
        return "CRITICAL", True, True
    if score >= 60:
        return "HIGH", True, False
    if score >= 30:
        return "MEDIUM", False, False
    return "LOW", False, False


def score_query(sql: str) -> RiskResult:
    sql_lower = sql.lower()
    matched_score = 10
    reasons: list[str] = []

    for keyword, score, reason in _RULES:
        if keyword in sql_lower:
            if score > matched_score:
                matched_score = score
            reasons.append(reason)

    # De-duplicate while preserving order
    seen: set[str] = set()
    unique_reasons: list[str] = []
    for r in reasons:
        if r not in seen:
            seen.add(r)
            unique_reasons.append(r)

    if not unique_reasons:
        unique_reasons = ["No destructive patterns detected"]

    risk_level, requires_approval, blocked = _classify(matched_score)

    return RiskResult(
        risk_score=matched_score,
        risk_level=risk_level,
        requires_approval=requires_approval,
        blocked=blocked,
        reasons=unique_reasons,
    )

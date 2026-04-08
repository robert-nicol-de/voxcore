import json
import re
from pathlib import Path
from typing import Any, Dict, List

from backend.services.data_policy_engine import get_sensitive_columns
from backend.services.rbac import normalize_role


_DEFAULT_POLICY: Dict[str, Any] = {
    "block_destructive_queries": {
        "enabled": True,
        "blocked_keywords": ["drop", "truncate", "alter", "delete"],
    },
    "protect_sensitive_columns": {
        "enabled": True,
        "blocked_columns": get_sensitive_columns(),
    },
    "read_only_ai_mode": {
        "enabled": False,
        "allowed_statements": ["select", "with"],
    },
    "query_result_limits": {
        "enabled": False,
        "max_rows": 1000,
    },
    "query_approval_mode": {
        "enabled": False,
        "require_for_query_types": ["select"],
        "require_for_tables": [],
    },
    "risk_based_approval": {
        "enabled": True,
        "threshold": 0.7,
    },
    "role_based_access": {
        "enabled": True,
        "rules": [
            {
                "role": "ai_analyst",
                "blocked_tables": ["payroll", "salaries", "employee_salary", "compensation"],
                "blocked_columns": ["salary", "bonus", "ssn"],
            },
            {
                "role": "viewer",
                "require_approval": True,
                "blocked_tables": [],
                "blocked_columns": [],
            },
        ],
    },
}


def _policies_root() -> Path:
    return Path("data") / "companies"


def _policy_path(company_id: str) -> Path:
    return _policies_root() / str(company_id) / "policies.json"


def _deep_merge(defaults: Dict[str, Any], incoming: Dict[str, Any]) -> Dict[str, Any]:
    merged: Dict[str, Any] = dict(defaults)
    for key, value in incoming.items():
        if key in merged and isinstance(merged[key], dict) and isinstance(value, dict):
            merged[key] = _deep_merge(merged[key], value)
        else:
            merged[key] = value
    return merged


def get_company_policies(company_id: str) -> Dict[str, Any]:
    path = _policy_path(company_id)
    if not path.exists():
        return dict(_DEFAULT_POLICY)

    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return dict(_DEFAULT_POLICY)

    return _deep_merge(_DEFAULT_POLICY, data)


def save_company_policies(company_id: str, policies: Dict[str, Any]) -> Dict[str, Any]:
    merged = _deep_merge(_DEFAULT_POLICY, policies)
    path = _policy_path(company_id)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(merged, indent=2), encoding="utf-8")
    return merged


def _find_sensitive_columns(sql: str, blocked_columns: List[str]) -> List[str]:
    found: List[str] = []
    lower_sql = sql.lower()
    for column in blocked_columns:
        pattern = rf"\b{re.escape(column.lower())}\b"
        if re.search(pattern, lower_sql):
            found.append(column)
    return sorted(set(found))


def _statement_starts_with(sql: str) -> str:
    stripped = sql.strip().lstrip("(")
    match = re.match(r"^([a-zA-Z]+)", stripped)
    return match.group(1).lower() if match else ""


def _append_limit(sql: str, max_rows: int) -> str:
    lower_sql = sql.lower()
    if " limit " in lower_sql or re.search(r"\btop\s+\d+\b", lower_sql):
        return sql

    clean_sql = sql.rstrip()
    if clean_sql.endswith(";"):
        return f"{clean_sql[:-1]} LIMIT {max_rows};"
    return f"{clean_sql} LIMIT {max_rows}"


def apply_policies(
    company_id: str,
    sql: str,
    analysis: Dict[str, Any] | None = None,
    actor_role: str | None = None,
) -> Dict[str, Any]:
    policies = get_company_policies(company_id)
    reasons: List[str] = []
    analysis = analysis or {}

    query_type = str(analysis.get("query_type", _statement_starts_with(sql).upper() or "UNKNOWN")).upper()
    analyzed_columns = [str(c).lower() for c in analysis.get("columns", [])]
    analyzed_tables = [str(t).lower() for t in analysis.get("tables", [])]

    destructive = policies.get("block_destructive_queries", {})
    if destructive.get("enabled", False):
        for keyword in destructive.get("blocked_keywords", []):
            if re.search(rf"\b{re.escape(str(keyword).lower())}\b", sql.lower()):
                reasons.append(f"Destructive operation detected: {keyword.upper()}")

    sensitive = policies.get("protect_sensitive_columns", {})
    if sensitive.get("enabled", False):
        blocked_cols = [str(x) for x in sensitive.get("blocked_columns", [])]
        found = _find_sensitive_columns(sql, blocked_cols)
        if analyzed_columns:
            found.extend([c for c in blocked_cols if c.lower() in analyzed_columns])
        for col in found:
            reasons.append(f"Sensitive field detected: {col}")

    read_only = policies.get("read_only_ai_mode", {})
    statement = query_type.lower()
    if read_only.get("enabled", False):
        allowed = [str(x).lower() for x in read_only.get("allowed_statements", ["select", "with"])]
        if statement not in allowed:
            reasons.append(f"Read-only mode blocks statement type: {statement or 'unknown'}")

    blocked = len(reasons) > 0
    rewritten_query = sql

    # --- Policy explainability ---
    policy_decision = "allow"
    policy_rule = None
    if blocked:
        policy_decision = "blocked"
        # Pick first reason as rule, or use a code
        if reasons:
            if "Sensitive field detected" in reasons[0]:
                policy_rule = "SENSITIVE_DATA_RULE_V2"
            elif "Destructive operation detected" in reasons[0]:
                policy_rule = "DESTRUCTIVE_QUERY_RULE_V1"
            elif "Read-only mode blocks" in reasons[0]:
                policy_rule = "READ_ONLY_RULE_V1"
            elif "Role" in reasons[0]:
                policy_rule = "ROLE_BASED_ACCESS_RULE_V1"
            else:
                policy_rule = "GENERIC_BLOCK_RULE"
        else:
            policy_rule = "GENERIC_BLOCK_RULE"
    elif requires_approval:
        policy_decision = "require_approval"
        policy_rule = "APPROVAL_REQUIRED_RULE_V1"
    elif rewritten_query != sql:
        policy_decision = "rewrite"
        policy_rule = "QUERY_REWRITE_RULE_V1"

    policy_version = "2026-03-30"

    row_limit = policies.get("query_result_limits", {})
    if not blocked and row_limit.get("enabled", False):
        max_rows = int(row_limit.get("max_rows", 1000) or 1000)
        if statement in {"select", "with"}:
            rewritten_query = _append_limit(sql, max_rows)

    approval = policies.get("query_approval_mode", {})
    requires_approval = False
    approval_reasons: List[str] = []
    if not blocked and approval.get("enabled", False):
        required_types = [str(x).lower() for x in approval.get("require_for_query_types", [])]
        required_tables = [str(x).lower() for x in approval.get("require_for_tables", [])]

        if required_types and statement in required_types:
            requires_approval = True
            approval_reasons.append(f"Approval required for query type: {statement.upper()}")

        if required_tables:
            hit_tables = [t for t in analyzed_tables if t in required_tables]
            if hit_tables:
                requires_approval = True
                approval_reasons.append(
                    "Approval required for protected table(s): " + ", ".join(sorted(set(hit_tables)))
                )

    role_access = policies.get("role_based_access", {})
    normalized_role = normalize_role(actor_role)
    if role_access.get("enabled", False) and normalized_role:
        for rule in role_access.get("rules", []):
            if normalize_role(str(rule.get("role", ""))) != normalized_role:
                continue

            blocked_tables = [str(x).lower() for x in rule.get("blocked_tables", [])]
            blocked_columns = [str(x).lower() for x in rule.get("blocked_columns", [])]

            table_hits = [table for table in analyzed_tables if table in blocked_tables]
            column_hits = [column for column in analyzed_columns if column in blocked_columns]

            if blocked_columns:
                column_hits.extend(
                    col for col in _find_sensitive_columns(sql, blocked_columns) if col.lower() not in column_hits
                )

            for table in sorted(set(table_hits)):
                reasons.append(f"Role {normalized_role} cannot access table: {table}")
            for column in sorted(set(column_hits)):
                reasons.append(f"Role {normalized_role} cannot access column: {column}")

            if bool(rule.get("require_approval")):
                requires_approval = True
                approval_reasons.append(f"Role {normalized_role} requires approval for this query")

    risk_approval = policies.get("risk_based_approval", {})
    risk_threshold_raw = risk_approval.get("threshold", 0.7)
    try:
        risk_threshold = float(risk_threshold_raw)
    except (TypeError, ValueError):
        risk_threshold = 0.7
    risk_threshold = max(0.0, min(1.0, risk_threshold))

    # Determine columns to mask for this user/query
    columns_to_mask = set()
    # Blocked columns from role-based access
    for rule in role_access.get("rules", []):
        if normalize_role(str(rule.get("role", ""))) != normalized_role:
            continue
        blocked_columns = [str(x).lower() for x in rule.get("blocked_columns", [])]
        for col in analyzed_columns:
            if col in blocked_columns:
                columns_to_mask.add(col)
    # Sensitive columns for non-admins
    if sensitive.get("enabled", False) and normalized_role != "admin":
        blocked_cols = [str(x).lower() for x in sensitive.get("blocked_columns", [])]
        for col in analyzed_columns:
            if col in blocked_cols:
                columns_to_mask.add(col)

    return {
        "blocked": blocked,
        "reasons": reasons,
        "original_query": sql,
        "rewritten_query": rewritten_query,
        "analysis": {
            "query_type": query_type,
            "tables": analyzed_tables,
            "columns": analyzed_columns,
        },
        "requires_approval": requires_approval,
        "approval_reasons": approval_reasons,
        "actor_role": normalized_role,
        "risk_approval": {
            "enabled": bool(risk_approval.get("enabled", True)),
            "threshold": risk_threshold,
        },
        "policies": policies,
        "columns_to_mask": sorted(columns_to_mask),
        "policy_decision": policy_decision,
        "policy_rule": policy_rule,
        "policy_version": policy_version,
    }


def suggest_sensitive_columns(columns: List[str]) -> List[str]:
    patterns = ["email", "ssn", "credit", "card", "password", "token", "secret", "dob"]
    result: List[str] = []
    for col in columns:
        lc = col.lower()
        if any(p in lc for p in patterns):
            result.append(col)
    return sorted(set(result))

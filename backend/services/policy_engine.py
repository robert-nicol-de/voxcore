import json
import re
from pathlib import Path
from typing import Any, Dict, List


_DEFAULT_POLICY: Dict[str, Any] = {
    "block_destructive_queries": {
        "enabled": True,
        "blocked_keywords": ["drop", "truncate", "alter", "delete"],
    },
    "protect_sensitive_columns": {
        "enabled": False,
        "blocked_columns": ["ssn", "credit_card", "password", "email"],
    },
    "read_only_ai_mode": {
        "enabled": False,
        "allowed_statements": ["select", "with"],
    },
    "query_result_limits": {
        "enabled": False,
        "max_rows": 1000,
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


def apply_policies(company_id: str, sql: str) -> Dict[str, Any]:
    policies = get_company_policies(company_id)
    reasons: List[str] = []

    destructive = policies.get("block_destructive_queries", {})
    if destructive.get("enabled", False):
        for keyword in destructive.get("blocked_keywords", []):
            if re.search(rf"\b{re.escape(str(keyword).lower())}\b", sql.lower()):
                reasons.append(f"Destructive operation detected: {keyword.upper()}")

    sensitive = policies.get("protect_sensitive_columns", {})
    if sensitive.get("enabled", False):
        blocked_cols = [str(x) for x in sensitive.get("blocked_columns", [])]
        found = _find_sensitive_columns(sql, blocked_cols)
        for col in found:
            reasons.append(f"Sensitive field detected: {col}")

    read_only = policies.get("read_only_ai_mode", {})
    statement = _statement_starts_with(sql)
    if read_only.get("enabled", False):
        allowed = [str(x).lower() for x in read_only.get("allowed_statements", ["select", "with"])]
        if statement not in allowed:
            reasons.append(f"Read-only mode blocks statement type: {statement or 'unknown'}")

    blocked = len(reasons) > 0
    rewritten_query = sql

    row_limit = policies.get("query_result_limits", {})
    if not blocked and row_limit.get("enabled", False):
        max_rows = int(row_limit.get("max_rows", 1000) or 1000)
        if statement in {"select", "with"}:
            rewritten_query = _append_limit(sql, max_rows)

    return {
        "blocked": blocked,
        "reasons": reasons,
        "original_query": sql,
        "rewritten_query": rewritten_query,
        "policies": policies,
    }


def suggest_sensitive_columns(columns: List[str]) -> List[str]:
    patterns = ["email", "ssn", "credit", "card", "password", "token", "secret", "dob"]
    result: List[str] = []
    for col in columns:
        lc = col.lower()
        if any(p in lc for p in patterns):
            result.append(col)
    return sorted(set(result))

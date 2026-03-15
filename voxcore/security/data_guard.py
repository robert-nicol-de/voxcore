"""
VoxCore Data Guard Layer
- Sensitive column registry
- Sensitivity levels and masking
- SQL inspection and rewriting
- Result scanning
- Policy engine integration
- Guard event logging

This module enforces data safety and compliance before and after query execution.
"""
import re
from typing import List, Dict, Any, Optional

# --- Sensitivity Levels ---
SENSITIVITY_LEVELS = [
    "public",
    "internal",
    "sensitive",
    "highly_sensitive",
    "restricted",
]

# --- Sensitive Column Registry (DB-backed, but in-memory for now) ---
# In production, this would query the sensitive_columns table.
SENSITIVE_COLUMNS = [
    {"table": "users", "column": "email", "sensitivity": "pii", "masking_rule": "mask_email"},
    {"table": "employees", "column": "salary", "sensitivity": "financial", "masking_rule": "mask_currency"},
    {"table": "employees", "column": "ssn", "sensitivity": "highly_sensitive", "masking_rule": None},
]

# --- Masking Functions (examples) ---
def mask_email(email: str) -> str:
    if not email or "@" not in email:
        return "***"
    name, domain = email.split("@", 1)
    return name[:2] + "***@" + domain

def mask_currency(value: Any) -> str:
    try:
        return "$***"
    except Exception:
        return "***"

MASKING_FUNCTIONS = {
    "mask_email": mask_email,
    "mask_currency": mask_currency,
}

# --- SQL Parsing Helpers (placeholder, use sqlglot or similar in prod) ---
def extract_columns(sql: str) -> List[Dict[str, str]]:
    # Dummy: extract columns from SELECT ... FROM ...
    # Replace with real SQL parser for production
    pattern = re.compile(r"SELECT (.+?) FROM (\w+)", re.IGNORECASE)
    m = pattern.search(sql)
    if not m:
        return []
    cols = [c.strip() for c in m.group(1).split(",")]
    table = m.group(2)
    return [{"table": table, "column": col} for col in cols]

def is_sensitive(table: str, column: str) -> Optional[Dict[str, Any]]:
    for entry in SENSITIVE_COLUMNS:
        if entry["table"] == table and entry["column"] == column:
            return entry
    return None

# --- Data Guard Core ---
class DataGuardViolation(Exception):
    def __init__(self, message, violation_type=None):
        super().__init__(message)
        self.violation_type = violation_type

def scan_query(sql: str, user_role: str = "viewer") -> Dict[str, Any]:
    """
    Inspect SQL for sensitive columns and enforce policies.
    Returns dict with 'action': 'allow'|'mask'|'block', 'rewritten_sql', 'violations'.
    """
    columns = extract_columns(sql)
    violations = []
    rewritten_sql = sql
    action = "allow"
    for col in columns:
        entry = is_sensitive(col["table"], col["column"])
        if entry:
            level = entry["sensitivity"]
            rule = entry.get("masking_rule")
            # Example policy: block highly_sensitive, mask sensitive, allow public
            if level in ("highly_sensitive", "restricted"):
                violations.append({"column": col, "level": level, "action": "block"})
                action = "block"
            elif level in ("sensitive", "financial", "pii") and rule:
                # Mask column in SQL (placeholder logic)
                rewritten_sql = rewritten_sql.replace(col["column"], f"{rule}({col['column']})")
                violations.append({"column": col, "level": level, "action": "mask"})
                action = "mask"
    return {"action": action, "rewritten_sql": rewritten_sql, "violations": violations}

def scan_results(results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Scan result set for PII/financial patterns. Block or mask as needed.
    """
    email_regex = re.compile(r"[\w\.-]+@[\w\.-]+", re.IGNORECASE)
    cc_regex = re.compile(r"\b(?:\d[ -]*?){13,16}\b")
    ssn_regex = re.compile(r"\b\d{3}-\d{2}-\d{4}\b")
    for row in results:
        for k, v in row.items():
            if isinstance(v, str):
                if email_regex.match(v):
                    row[k] = mask_email(v)
                elif cc_regex.match(v) or ssn_regex.match(v):
                    row[k] = "***"
    return results

def scan_prompt(prompt: str) -> Optional[str]:
    # Simple keyword-based guard
    suspicious = ["salary", "ssn", "credit card", "bank account"]
    for word in suspicious:
        if word in prompt.lower():
            return f"Prompt contains sensitive keyword: {word}"
    return None

# --- Policy Engine Integration (placeholder) ---
# In production, integrate with permission engine and org policies.

def log_data_guard_event(user_id: int, query: str, violation_type: str):
    # In production, log to data_guard_events table
    print(f"[DataGuard] User {user_id} violation: {violation_type} in query: {query}")

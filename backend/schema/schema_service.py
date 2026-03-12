"""
Schema service — orchestrates drivers, caching, and sensitive-column detection.

Flow:
    1. Check Redis cache  (schema_cache:{workspace}:{connection})
    2. Load connection config from disk
    3. Dispatch to the correct driver
    4. Annotate columns with PII / sensitive flags
    5. Write result to Redis
    6. Return universal schema dict

All drivers read system metadata only — no user table rows are ever touched.
"""
from __future__ import annotations

import re
from typing import Any, Dict, List, Optional

from backend.db.connection_manager import ConnectionManager
from backend.schema import cache as schema_cache
from backend.schema.drivers import (
    mysql_driver,
    postgres_driver,
    sqlserver_driver,
    sqlite_driver,
)

connection_manager = ConnectionManager()

# ---------------------------------------------------------------------------
# Sensitive-column patterns
# ---------------------------------------------------------------------------

_SENSITIVE_RULES: List[tuple[re.Pattern[str], str]] = [
    # PII
    (re.compile(r"email|e_?mail",            re.I), "PII"),
    (re.compile(r"phone|mobile|cell",        re.I), "PII"),
    (re.compile(r"address|postal|zip|city",  re.I), "PII"),
    (re.compile(r"dob|birth|date_of_birth",  re.I), "PII"),
    (re.compile(r"first_?name|last_?name|full_?name", re.I), "PII"),
    # Sensitive / secret
    (re.compile(r"ssn|social_?security|national_?id|passport|license", re.I), "sensitive"),
    (re.compile(r"credit_?card|card_?number|cvv|ccv",                  re.I), "sensitive"),
    (re.compile(r"password|passwd",                                     re.I), "sensitive"),
    (re.compile(r"(api_?key|secret|token|private_?key)",               re.I), "sensitive"),
]


def _flag_sensitive(column_name: str) -> Optional[str]:
    for pattern, label in _SENSITIVE_RULES:
        if pattern.search(column_name):
            return label
    return None


def _annotate(tables: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    for table in tables:
        for col in table.get("columns", []):
            col["sensitive"] = _flag_sensitive(col["name"])
    return tables


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def discover_full_schema(
    company_id: str,
    workspace_id: str,
    connection_name: str,
) -> Dict[str, Any]:
    """
    Return the full universal schema dict, using Redis cache when available.

    Raises:
        FileNotFoundError  — connection config not found on disk
        ValueError         — unsupported database type
        RuntimeError / Exception — driver-level failure (propagated to router)
    """
    cached = schema_cache.get_cached(workspace_id, connection_name)
    if cached is not None:
        return cached

    config = connection_manager.load_connection(
        company_id,
        connection_name,
        decrypt_password=True,
        workspace_id=workspace_id,
    )

    db_type       = str(config.get("type", "")).strip().lower()
    database_name = str(config.get("database", "")).strip()

    if db_type == "sqlite":
        # SQLite uses the database field as a file path; no network connection needed.
        result = sqlite_driver.get_schema(database_name)
    else:
        conn = connection_manager.get_connection(config)
        try:
            if db_type == "sqlserver":
                result = sqlserver_driver.get_schema(conn, database_name)
            elif db_type in {"postgres", "postgresql"}:
                result = postgres_driver.get_schema(conn, database_name)
            elif db_type == "mysql":
                result = mysql_driver.get_schema(conn, database_name)
            else:
                raise ValueError(
                    f"Schema discovery is not supported for database type: {db_type!r}. "
                    "Supported types: sqlserver, postgres, mysql, sqlite."
                )
        finally:
            try:
                conn.close()
            except Exception:
                pass

    result["tables"] = _annotate(result.get("tables", []))
    schema_cache.set_cached(workspace_id, connection_name, result)
    return result


def get_ai_context(schema: Dict[str, Any], max_tables: int = 50) -> str:
    """
    Return a compact schema string for injection into AI prompts.

    Format:
        customers(id, email, phone)
        orders(id, customer_id, total)
    """
    lines = []
    for table in schema.get("tables", [])[:max_tables]:
        col_names = [c["name"] for c in table.get("columns", [])]
        lines.append(f"{table['name']}({', '.join(col_names)})")
    return "\n".join(lines)

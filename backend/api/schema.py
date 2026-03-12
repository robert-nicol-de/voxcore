"""
Schema API router.

Endpoints:
    GET /api/v1/schema/databases        — list saved connections for the workspace
    GET /api/v1/schema/tables           — table names only (lazy-load, Redis-cached)
    GET /api/v1/schema/table/{table}    — columns for one table (lazy-load, Redis-cached)
    GET /api/v1/schema/discover         — full schema (backward-compat alias)

All schema reads go through `schema_service.discover_full_schema`, which delegates
to the correct metadata driver and never touches user table rows.
"""
from typing import List, Optional

from fastapi import APIRouter, HTTPException, Query

from backend.db.connection_manager import ConnectionManager
from backend.schema.schema_service import discover_full_schema
from backend.services.security_redaction import sanitize_exception_message

router = APIRouter()
_connection_manager = ConnectionManager()

MAX_TABLES = 1000


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _list_connections(company_id: str, workspace_id: str) -> List[str]:
    return _connection_manager.list_connections(company_id, workspace_id=workspace_id)


def _resolve_connection(
    company_id: str,
    workspace_id: str,
    connection_name: Optional[str],
) -> str:
    if connection_name and connection_name.strip():
        return connection_name.strip()
    available = _list_connections(company_id, workspace_id)
    if not available:
        raise HTTPException(
            status_code=400,
            detail="No saved connections found. Connect a database first.",
        )
    return available[0]


def _run_discover(company_id: str, workspace_id: str, conn_name: str) -> dict:
    """Shared wrapper that converts service exceptions to HTTP errors."""
    try:
        return discover_full_schema(company_id, workspace_id, conn_name)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Schema discovery failed: {sanitize_exception_message(exc)}",
        )


# ---------------------------------------------------------------------------
# GET /api/v1/schema/databases
# ---------------------------------------------------------------------------

@router.get("/api/v1/schema/databases")
def list_databases(
    company_id:   str = Query("default"),
    workspace_id: str = Query("default"),
):
    """Return the list of saved connection names for the given workspace."""
    connections = _list_connections(company_id, workspace_id)
    return {"databases": connections, "count": len(connections)}


# ---------------------------------------------------------------------------
# GET /api/v1/schema/tables  — table names only (lazy-load)
# ---------------------------------------------------------------------------

@router.get("/api/v1/schema/tables")
def list_tables(
    company_id:      str           = Query("default"),
    workspace_id:    str           = Query("default"),
    connection_name: Optional[str] = Query(None),
    limit:           int           = Query(MAX_TABLES, ge=1, le=MAX_TABLES),
):
    """
    Return table names (and schema names) for the selected connection.
    Columns are NOT included — fetch them per-table to keep responses small.
    """
    conn_name = _resolve_connection(company_id, workspace_id, connection_name)
    result    = _run_discover(company_id, workspace_id, conn_name)

    tables = result.get("tables", [])[:limit]
    return {
        "connection": conn_name,
        "database":   result.get("database", ""),
        "tables":     [{"name": t["name"], "schema": t.get("schema", "")} for t in tables],
        "count":      len(tables),
    }


# ---------------------------------------------------------------------------
# GET /api/v1/schema/table/{table_name}  — per-table column detail
# ---------------------------------------------------------------------------

@router.get("/api/v1/schema/table/{table_name}")
def get_table_columns(
    table_name:      str,
    company_id:      str           = Query("default"),
    workspace_id:    str           = Query("default"),
    connection_name: Optional[str] = Query(None),
):
    """
    Return columns (with type, nullability, PK flag, and sensitive label)
    for a single table.  Called only when the user clicks a table row.
    """
    conn_name = _resolve_connection(company_id, workspace_id, connection_name)
    result    = _run_discover(company_id, workspace_id, conn_name)

    matched = next(
        (t for t in result.get("tables", []) if t["name"].lower() == table_name.lower()),
        None,
    )
    if matched is None:
        raise HTTPException(
            status_code=404,
            detail=f"Table '{table_name}' not found in schema.",
        )

    columns = matched.get("columns", [])[:200]
    return {
        "table":   matched["name"],
        "schema":  matched.get("schema", ""),
        "columns": columns,
        "count":   len(columns),
    }


# ---------------------------------------------------------------------------
# GET /api/v1/schema/discover  — full schema (backward-compat)
# ---------------------------------------------------------------------------

@router.get("/api/v1/schema/discover")
def discover_schema(
    company_id:      str           = Query("default"),
    workspace_id:    str           = Query("default"),
    connection_name: Optional[str] = Query(None),
):
    """Full schema dump kept for backward compatibility with existing callers."""
    conn_name = _resolve_connection(company_id, workspace_id, connection_name)
    result    = _run_discover(company_id, workspace_id, conn_name)
    return {
        "schema":   result.get("tables", []),
        "database": result.get("database", ""),
    }


# ---------------------------------------------------------------------------
# Legacy alias kept so old frontend SchemaExplorer component still works
# (it calls /api/v1/schema/tables with response shape { tables: string[] })
# ---------------------------------------------------------------------------
# (already covered above — /api/v1/schema/tables returns the same shape)

# Preserve backward-compat — this was _fetch_sqlserver_schema etc.
# Those private helpers are now in backend/schema/drivers/*.py

from typing import Any, Dict, List

from fastapi import APIRouter, HTTPException, Query

from backend.db.connection_manager import ConnectionManager

router = APIRouter()
connection_manager = ConnectionManager()


def _fetch_sqlserver_schema(conn) -> List[Dict[str, Any]]:
    sql = """
    SELECT TABLE_NAME, COLUMN_NAME, DATA_TYPE
    FROM INFORMATION_SCHEMA.COLUMNS
    WHERE TABLE_SCHEMA = 'dbo'
    ORDER BY TABLE_NAME, ORDINAL_POSITION
    """
    with conn.cursor() as cur:
        cur.execute(sql)
        rows = cur.fetchall()

    tables: Dict[str, List[Dict[str, str]]] = {}
    for row in rows:
        table_name = str(row[0])
        column_name = str(row[1])
        data_type = str(row[2])
        tables.setdefault(table_name, []).append(
            {"name": column_name, "type": data_type}
        )

    return [{"table": table, "columns": columns} for table, columns in tables.items()]


def _fetch_postgres_schema(conn) -> List[Dict[str, Any]]:
    sql = """
    SELECT c.table_name, c.column_name, c.data_type
    FROM information_schema.columns c
    JOIN information_schema.tables t
      ON c.table_name = t.table_name
     AND c.table_schema = t.table_schema
    WHERE c.table_schema = 'public'
      AND t.table_type = 'BASE TABLE'
    ORDER BY c.table_name, c.ordinal_position
    """
    with conn.cursor() as cur:
        cur.execute(sql)
        rows = cur.fetchall()

    tables: Dict[str, List[Dict[str, str]]] = {}
    for row in rows:
        table_name = str(row[0])
        column_name = str(row[1])
        data_type = str(row[2])
        tables.setdefault(table_name, []).append(
            {"name": column_name, "type": data_type}
        )

    return [{"table": table, "columns": columns} for table, columns in tables.items()]


def _fetch_mysql_schema(conn, database_name: str) -> List[Dict[str, Any]]:
    sql = """
    SELECT TABLE_NAME, COLUMN_NAME, DATA_TYPE
    FROM INFORMATION_SCHEMA.COLUMNS
    WHERE TABLE_SCHEMA = %s
    ORDER BY TABLE_NAME, ORDINAL_POSITION
    """
    with conn.cursor() as cur:
        cur.execute(sql, (database_name,))
        rows = cur.fetchall()

    tables: Dict[str, List[Dict[str, str]]] = {}
    for row in rows:
        table_name = str(row[0])
        column_name = str(row[1])
        data_type = str(row[2])
        tables.setdefault(table_name, []).append(
            {"name": column_name, "type": data_type}
        )

    return [{"table": table, "columns": columns} for table, columns in tables.items()]


def _resolve_connection_name(company_id: str, requested_connection_name: str | None) -> str:
    if requested_connection_name and requested_connection_name.strip():
        return requested_connection_name.strip()

    available = connection_manager.list_connections(company_id)
    if not available:
        raise HTTPException(
            status_code=400,
            detail="No saved connections found. Save a connection first.",
        )

    return available[0]


@router.get("/api/v1/schema/discover")
def discover_schema(
    company_id: str = Query("default"),
    connection_name: str | None = Query(None),
):
    resolved_connection_name = _resolve_connection_name(company_id, connection_name)

    try:
        config = connection_manager.load_connection(
            company_id,
            resolved_connection_name,
            decrypt_password=True,
        )
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))

    db_type = str(config.get("type", "")).strip().lower()
    database_name = str(config.get("database", "")).strip()

    try:
        conn = connection_manager.get_connection(config)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Connection failed: {str(e)}")

    try:
        if db_type == "sqlserver":
            tables = _fetch_sqlserver_schema(conn)
        elif db_type in {"postgres", "postgresql"}:
            tables = _fetch_postgres_schema(conn)
        elif db_type == "mysql":
            if not database_name:
                raise HTTPException(status_code=400, detail="Database name is required for MySQL schema discovery")
            tables = _fetch_mysql_schema(conn, database_name)
        else:
            raise HTTPException(status_code=400, detail=f"Schema discovery not implemented for database type: {db_type}")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Schema discovery failed: {str(e)}")
    finally:
        try:
            conn.close()
        except Exception:
            pass

    return {"schema": tables}

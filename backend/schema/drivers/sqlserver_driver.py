"""
SQL Server schema driver.

Reads metadata exclusively from sys.* system views — never touches user data.
Includes: table schema, column type, nullability, and primary-key detection.
"""
from typing import Any, Dict, List

MAX_TABLES = 1000
MAX_COLUMNS_PER_TABLE = 200

# sys.tables + sys.schemas for schema, sys.columns for columns,
# sys.types for type name, INFORMATION_SCHEMA PKs for primary-key flag.
_SQL = """
SELECT TOP 200000
    s.name          AS schema_name,
    t.name          AS table_name,
    c.name          AS column_name,
    ty.name         AS data_type,
    c.is_nullable,
    CASE
        WHEN pk.column_name IS NOT NULL THEN 1
        ELSE 0
    END             AS is_primary_key
FROM sys.tables t
JOIN sys.schemas s  ON t.schema_id = s.schema_id
JOIN sys.columns c  ON t.object_id = c.object_id
JOIN sys.types   ty ON c.user_type_id = ty.user_type_id
LEFT JOIN (
    SELECT kcu.table_schema, kcu.table_name, kcu.column_name
    FROM INFORMATION_SCHEMA.TABLE_CONSTRAINTS  tc
    JOIN INFORMATION_SCHEMA.KEY_COLUMN_USAGE   kcu
      ON tc.constraint_name  = kcu.constraint_name
     AND tc.table_schema     = kcu.table_schema
    WHERE tc.constraint_type = 'PRIMARY KEY'
) pk ON s.name = pk.table_schema
     AND t.name = pk.table_name
     AND c.name = pk.column_name
WHERE t.is_ms_shipped = 0
ORDER BY s.name, t.name, c.column_id
"""


def get_schema(conn, database_name: str = "") -> Dict[str, Any]:
    """Return the universal schema dict for a SQL Server connection."""
    tables: Dict[str, Dict[str, Any]] = {}

    with conn.cursor() as cur:
        cur.execute(_SQL)
        for row in cur.fetchall():
            schema_name = str(row[0])
            table_name  = str(row[1])
            key = f"{schema_name}.{table_name}"

            if key not in tables:
                if len(tables) >= MAX_TABLES:
                    break
                tables[key] = {
                    "name":    table_name,
                    "schema":  schema_name,
                    "columns": [],
                }

            if len(tables[key]["columns"]) < MAX_COLUMNS_PER_TABLE:
                tables[key]["columns"].append({
                    "name":        str(row[2]),
                    "type":        str(row[3]),
                    "nullable":    bool(row[4]),
                    "primary_key": bool(row[5]),
                })

    return {
        "database": database_name,
        "tables":   list(tables.values()),
    }

"""
PostgreSQL schema driver.

Reads metadata from information_schema — never touches user rows.
Excludes pg_catalog and information_schema system schemas.
"""
from typing import Any, Dict

MAX_TABLES = 1000
MAX_COLUMNS_PER_TABLE = 200

_SQL = """
SELECT
    c.table_schema,
    c.table_name,
    c.column_name,
    c.data_type,
    (c.is_nullable = 'YES')                         AS is_nullable,
    (pk.column_name IS NOT NULL)                    AS is_primary_key
FROM information_schema.columns c
JOIN information_schema.tables t
  ON c.table_name   = t.table_name
 AND c.table_schema = t.table_schema
LEFT JOIN (
    SELECT kcu.table_schema, kcu.table_name, kcu.column_name
    FROM information_schema.table_constraints  tc
    JOIN information_schema.key_column_usage   kcu
      ON tc.constraint_name   = kcu.constraint_name
     AND tc.constraint_schema = kcu.constraint_schema
    WHERE tc.constraint_type = 'PRIMARY KEY'
) pk ON c.table_schema = pk.table_schema
     AND c.table_name   = pk.table_name
     AND c.column_name  = pk.column_name
WHERE c.table_schema NOT IN ('pg_catalog', 'information_schema')
  AND t.table_type = 'BASE TABLE'
ORDER BY c.table_schema, c.table_name, c.ordinal_position
LIMIT 200000
"""


def get_schema(conn, database_name: str = "") -> Dict[str, Any]:
    """Return the universal schema dict for a PostgreSQL connection."""
    tables: Dict[str, Dict[str, Any]] = {}

    with conn.cursor() as cur:
        cur.execute(_SQL)
        for row in cur.fetchall():
            schema_name = str(row[0])
            table_name  = str(row[1])
            # Use plain table name for 'public' schema to keep UI clean
            key = table_name if schema_name == "public" else f"{schema_name}.{table_name}"

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

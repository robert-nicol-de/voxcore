"""
MySQL schema driver.

Reads metadata from information_schema.columns filtered to the target
database — never executes queries against user tables.
"""
from typing import Any, Dict

MAX_TABLES = 1000
MAX_COLUMNS_PER_TABLE = 200

_SQL = """
SELECT
    c.table_name,
    c.column_name,
    c.data_type,
    (c.is_nullable = 'YES') AS is_nullable,
    (c.column_key   = 'PRI') AS is_primary_key
FROM information_schema.columns c
WHERE c.table_schema = %s
ORDER BY c.table_name, c.ordinal_position
LIMIT 200000
"""


def get_schema(conn, database_name: str) -> Dict[str, Any]:
    """Return the universal schema dict for a MySQL connection."""
    tables: Dict[str, Dict[str, Any]] = {}

    with conn.cursor() as cur:
        cur.execute(_SQL, (database_name,))
        for row in cur.fetchall():
            table_name = str(row[0])

            if table_name not in tables:
                if len(tables) >= MAX_TABLES:
                    break
                tables[table_name] = {
                    "name":    table_name,
                    "schema":  "",
                    "columns": [],
                }

            if len(tables[table_name]["columns"]) < MAX_COLUMNS_PER_TABLE:
                tables[table_name]["columns"].append({
                    "name":        str(row[1]),
                    "type":        str(row[2]),
                    "nullable":    bool(row[3]),
                    "primary_key": bool(row[4]),
                })

    return {
        "database": database_name,
        "tables":   list(tables.values()),
    }

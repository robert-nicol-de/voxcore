"""
SQLite schema driver.

Uses sqlite_master + PRAGMA table_info — reads metadata only,
never queries user table rows.
"""
import sqlite3
from typing import Any, Dict

MAX_TABLES = 1000
MAX_COLUMNS_PER_TABLE = 200


def get_schema(database_path: str) -> Dict[str, Any]:
    """
    Return the universal schema dict for a SQLite database file.

    PRAGMA table_info columns:
        cid | name | type | notnull | dflt_value | pk
    pk > 0 means the column is part of the primary key.
    """
    conn = sqlite3.connect(database_path, timeout=3)
    try:
        cur = conn.cursor()
        cur.execute(
            "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
        )
        table_names = [row[0] for row in cur.fetchall()[:MAX_TABLES]]

        tables = []
        for tbl in table_names:
            # table_info is safe — it reads the schema, not user rows
            cur.execute(f'PRAGMA table_info("{tbl}")')
            columns = []
            for row in cur.fetchall()[:MAX_COLUMNS_PER_TABLE]:
                columns.append({
                    "name":        str(row[1]),
                    "type":        str(row[2]) if row[2] else "TEXT",
                    "nullable":    not bool(row[3]),   # notnull=1 → nullable=False
                    "primary_key": int(row[5]) > 0,    # pk>0 → primary key
                })
            tables.append({
                "name":    tbl,
                "schema":  "",
                "columns": columns,
            })
    finally:
        conn.close()

    return {
        "database": database_path,
        "tables":   tables,
    }

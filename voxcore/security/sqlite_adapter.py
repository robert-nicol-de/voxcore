# SQLite DB adapter for PermissionEngine
import sqlite3
from pathlib import Path

class SQLiteAdapter:
    def __init__(self, db_path: Path):
        self.db_path = db_path

    def fetch_one(self, query, params=None):
        conn = sqlite3.connect(str(self.db_path), check_same_thread=False)
        conn.row_factory = sqlite3.Row
        try:
            cur = conn.execute(query, params or [])
            return cur.fetchone()
        finally:
            conn.close()

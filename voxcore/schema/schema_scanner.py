import sqlite3

class SchemaScanner:
    def scan(self, db_path):
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # --- TABLES ---
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]

        schema = {}

        for table in tables:
            # --- COLUMNS ---
            cursor.execute(f"PRAGMA table_info({table})")
            cols = cursor.fetchall()

            columns = []
            for col in cols:
                col_name = col[1]
                col_type = col[2]

                columns.append({
                    "name": col_name,
                    "type": col_type,
                    "is_primary": col[5] == 1,
                    "semantic_type": self.detect_semantic_type(col_name, col_type)
                })

            # --- ROW COUNT (optional but powerful) ---
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                row_count = cursor.fetchone()[0]
            except:
                row_count = None

            schema[table] = {
                "columns": columns,
                "row_count": row_count
            }

        conn.close()
        return schema

    # 🔥 THIS is where intelligence starts
    def detect_semantic_type(self, name, col_type):
        n = name.lower()

        if "date" in n or "time" in n:
            return "time"

        if "id" in n:
            return "id"

        if any(x in n for x in ["amount", "revenue", "balance", "price"]):
            return "metric"

        if any(x in n for x in ["name", "type", "category", "region", "status"]):
            return "dimension"

        return "unknown"

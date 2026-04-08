import sqlite3

class ExecutionEngine:
    def run(self, sql: str, db_path: str):
        try:
            conn = sqlite3.connect(db_path)
            conn.row_factory = sqlite3.Row

            cursor = conn.cursor()
            cursor.execute(sql)

            rows = cursor.fetchall()

            result = [dict(row) for row in rows]

            conn.close()

            return {
                "status": "success",
                "rows": result,
                "row_count": len(result)
            }

        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }

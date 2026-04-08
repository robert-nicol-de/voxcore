from voxcore.connectors.base import BaseConnector
from voxcore.connectors.registry import register_connector

@register_connector("sqlserver")
class SQLServerConnector(BaseConnector):
    def connect(self):
        import pyodbc  # lazy import
        conn_str = (
            f"DRIVER={{ODBC Driver 17 for SQL Server}};"
            f"SERVER={self.config['host']};"
            f"DATABASE={self.config['database']};"
            f"UID={self.config['user']};"
            f"PWD={self.config['password']};"
            "TrustServerCertificate=yes;"
        )
        return pyodbc.connect(conn_str, timeout=5)

    def test_connection(self):
        try:
            conn = self.connect()
            conn.close()
            return True
        except Exception as e:
            return {"success": False, "error": str(e)}

    def get_schema(self):
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 
                TABLE_NAME, COLUMN_NAME
            FROM INFORMATION_SCHEMA.COLUMNS
        """)
        schema = {}
        for table, column in cursor.fetchall():
            schema.setdefault(table, []).append(column)
        conn.close()
        return schema

    def execute_query(self, query: str):
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute(query)
        columns = [col[0] for col in cursor.description] if cursor.description else []
        rows = cursor.fetchall()
        data = [dict(zip(columns, row)) for row in rows]
        conn.close()
        return data

    def _build_connection_string(self):
        # 🪟 Windows Authentication
        if self.config.get("trusted_connection"):
            return (
                "DRIVER={ODBC Driver 17 for SQL Server};"
                f"SERVER={self.config['host']};"
                f"DATABASE={self.config['database']};"
                "Trusted_Connection=yes;"
            )

        # 🔐 SQL Authentication (password should already be decrypted)
        return (
            "DRIVER={ODBC Driver 17 for SQL Server};"
            f"SERVER={self.config['host']};"
            f"DATABASE={self.config['database']};"
            f"UID={self.config['user']};"
            f"PWD={self.config['password']};"
            "TrustServerCertificate=yes;"
        )

    def test_connection(self):
        try:
            conn = self.connect()
            conn.close()
            return {"success": True}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def get_schema(self):
        conn = self.connect()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT TABLE_NAME, COLUMN_NAME
                FROM INFORMATION_SCHEMA.COLUMNS
            """)

            schema = {}
            for table, column in cursor.fetchall():
                schema.setdefault(table, []).append(column)

            return {"tables": schema}

        finally:
            conn.close()

    def execute_query(self, query: str):
        conn = self.connect()
        try:
            cursor = conn.cursor()
            cursor.execute(query)

            # Handle SELECT queries
            if cursor.description:
                columns = [col[0] for col in cursor.description]
                rows = cursor.fetchall()

                data = [dict(zip(columns, row)) for row in rows]
                return {
                    "rows": len(data),
                    "data": data
                }

            # Handle non-SELECT
            return {"message": "Query executed successfully"}

        finally:
            conn.close()

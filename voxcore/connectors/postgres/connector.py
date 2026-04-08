from voxcore.connectors.base import BaseConnector
from voxcore.connectors.registry import register_connector

@register_connector("postgres")
class PostgresConnector(BaseConnector):
    def connect(self):
        import psycopg2  # lazy import
        return psycopg2.connect(**self.config)

    def test_connection(self):
        try:
            conn = self.connect()
            conn.close()
            return True
        except:
            return False

    def get_schema(self):
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT table_name, column_name
            FROM information_schema.columns
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
        data = cursor.fetchall()
        conn.close()
        return data

from voxcore.connectors.base import BaseConnector
from voxcore.connectors.registry import register_connector

@register_connector("snowflake")
class SnowflakeConnector(BaseConnector):
    def connect(self):
        import snowflake.connector  # lazy import
        return snowflake.connector.connect(**self.config)

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
        cursor.execute("SHOW TABLES")
        tables = [row[1] for row in cursor.fetchall()]
        schema = {}
        for table in tables:
            cursor.execute(f"DESCRIBE TABLE {table}")
            columns = [row[0] for row in cursor.fetchall()]
            schema[table] = columns
        conn.close()
        return schema

    def execute_query(self, query: str):
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute(query)
        data = cursor.fetchall()
        conn.close()
        return data

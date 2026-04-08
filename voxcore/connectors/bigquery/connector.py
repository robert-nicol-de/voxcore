from voxcore.connectors.base import BaseConnector
from voxcore.connectors.registry import register_connector

@register_connector("bigquery")
class BigQueryConnector(BaseConnector):
    def connect(self):
        from google.cloud import bigquery  # lazy import
        return bigquery.Client()

    def test_connection(self):
        try:
            client = self.connect()
            list(client.list_datasets())
            return True
        except:
            return False

    def execute_query(self, query: str):
        client = self.connect()
        result = client.query(query)
        return [dict(row) for row in result]

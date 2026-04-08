import pandas as pd
from voxcore.connectors.base import BaseConnector
from voxcore.connectors.registry import register_connector

@register_connector("file")
class FileConnector(BaseConnector):
    def connect(self):
        return self.config["path"]

    def test_connection(self):
        import os
        return os.path.exists(self.config["path"])

    def get_schema(self):
        df = pd.read_csv(self.config["path"])
        return {"columns": list(df.columns)}

    def execute_query(self, query: str):
        df = pd.read_csv(self.config["path"])
        return df.head(100).to_dict(orient="records")

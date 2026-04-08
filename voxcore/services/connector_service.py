from voxcore.connectors.factory import create_connector
from voxcore.connectors.guard import enforce_connector_access
from voxcore.engine.core import VoxCoreEngine

class ConnectorService:
    def __init__(self):
        self.engine = VoxCoreEngine()

    def test(self, user, connector_type, config):
        enforce_connector_access(user, connector_type)
        connector = create_connector(connector_type, config)
        return connector.test_connection()

    def get_schema(self, user, connector_type, config):
        enforce_connector_access(user, connector_type)
        connector = create_connector(connector_type, config)
        return connector.get_schema()

    def query(self, user, connector_type, config, query):
        enforce_connector_access(user, connector_type)
        connector = create_connector(connector_type, config)
        connection = connector.connect()
        result = self.engine.execute_query(
            question=query,
            generated_sql=query,  # If you have SQL generation, replace with generated SQL
            platform=connector_type,
            user_id=user["id"],
            connection=connection
        )
        return result

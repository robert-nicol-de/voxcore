# SQL Execution Router for VoxCore
# Routes validated SQL to the correct database connector

class ExecutionRouter:
    def __init__(self, connection_registry):
        self.connection_registry = connection_registry

    def execute(self, sql: str, connection_name: str):
        conn = self.connection_registry.get(connection_name)
        if not conn:
            raise ValueError(f"Connection '{connection_name}' not found.")
        # Example: call the connector's execute method
        return conn.execute(sql)

# Example connection_registry: {"sales_db": SnowflakeConnector(...), ...}

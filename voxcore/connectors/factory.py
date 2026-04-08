from voxcore.connectors.registry import get_connector

def create_connector(connector_type: str, config: dict):
    connector_cls = get_connector(connector_type)
    if not connector_cls:
        raise ValueError(f"Connector '{connector_type}' not found")
    return connector_cls(config)

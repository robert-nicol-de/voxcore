CONNECTOR_REGISTRY = {}

def register_connector(name):
    def wrapper(cls):
        CONNECTOR_REGISTRY[name] = cls
        return cls
    return wrapper

def get_connector(name):
    return CONNECTOR_REGISTRY.get(name)

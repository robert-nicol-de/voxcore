# Permission engine import for query API
from voxcore.security.permission_engine import PermissionEngine
from backend.db import org_store

# Singleton instance (could be improved for DI)
permission_engine = PermissionEngine(org_store)

# VoxCore Zanzibar-Style Permission Engine
# Core relationship-based permission logic


from typing import Tuple, Any
from voxcore.security.redis_cache import RedisCache


class PermissionEngine:
    def __init__(self, db, cache_ttl=300, max_depth=5):
        self.db = db
        self.cache = RedisCache()
        self.cache_ttl = cache_ttl
        self.max_depth = max_depth

    def relationship_exists(self, subject: Tuple[str, Any], relation: str, obj: Tuple[str, Any]) -> bool:
        query = """
        SELECT 1 FROM relationships
        WHERE subject_type = ?
          AND subject_id = ?
          AND relation = ?
          AND object_type = ?
          AND object_id = ?
        LIMIT 1
        """
        params = (subject[0], subject[1], relation, obj[0], obj[1])
        fetch_one = getattr(self.db, "fetch_one", None)
        if not callable(fetch_one):
            return False
        try:
            result = fetch_one(query, params)
        except Exception:
            return False
        return result is not None

    def check_access(self, user_id: Any, relation: str, object_type: str, object_id: Any, get_user_workspaces=None, depth=0) -> bool:
        if depth > self.max_depth:
            return False
        cache_key = f"perm:{user_id}:{relation}:{object_type}:{object_id}"
        cached = self.cache.get(cache_key)
        if cached == "1":
            return True

        # Direct permission
        if self.relationship_exists(("user", user_id), relation, (object_type, object_id)):
            self.cache.setex(cache_key, self.cache_ttl, "1")
            return True
        # Workspace inheritance
        if get_user_workspaces:
            workspaces = get_user_workspaces(user_id)
            if object_type == "workspace" and str(object_id) in {str(ws) for ws in workspaces}:
                self.cache.setex(cache_key, self.cache_ttl, "1")
                return True
            for ws in workspaces:
                # Recursive check with depth limit
                if self.relationship_exists(("workspace", ws), relation, (object_type, object_id)):
                    self.cache.setex(cache_key, self.cache_ttl, "1")
                    return True
                # Example: extend here for deeper graph traversal if needed
                # if self.check_access(ws, relation, object_type, object_id, get_user_workspaces, depth=depth+1):
                #     return True
        return False

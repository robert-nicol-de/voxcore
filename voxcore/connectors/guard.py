from voxcore.connectors.policies import CONNECTOR_ACCESS

def enforce_connector_access(user, connector_type: str):
    user_tier = getattr(user, "tier", "free") if hasattr(user, "tier") else user.get("tier", "free")
    allowed_tiers = CONNECTOR_ACCESS.get(connector_type)
    if not allowed_tiers:
        raise ValueError(f"Unknown connector: {connector_type}")
    if user_tier not in allowed_tiers:
        raise PermissionError(
            f"{connector_type} requires {allowed_tiers}, but user has {user_tier}"
        )
    # RBAC check (optional, see below)
    if hasattr(user, "has_permission"):
        if not user.has_permission("data.query"):
            raise PermissionError("User lacks data.query permission")
    elif isinstance(user, dict):
        if "permissions" in user and "data.query" not in user["permissions"]:
            raise PermissionError("User lacks data.query permission")

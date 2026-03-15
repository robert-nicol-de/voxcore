def get_user_permissions(user) -> list[str]:
    """Return all permissions for a user object (role-based)."""
    return get_role_permissions(getattr(user, "role", None))
def require_permission(permission: str):
    """FastAPI dependency to enforce a specific permission string."""
    def permission_checker(user=Depends(get_current_user), request: Request = None):
        perms = get_role_permissions(user.role)
        # RBAC check
        if "*" in perms or permission in perms:
            return user

        # Relationship-based check (Zanzibar-style)
        try:
            from voxcore.security.permission_engine import PermissionEngine
            from voxcore.security.sqlite_adapter import SQLiteAdapter
            from backend.db import org_store
            db_path = org_store._db_path()
            db = SQLiteAdapter(db_path)
            engine = PermissionEngine(db)
            # Try to infer object type/id from request path or context
            # This is a simple fallback; for production, use explicit context
            object_type = None
            object_id = None
            if request and request.path_params:
                # Try to extract from path params (e.g., dashboard_id, datasource_id)
                for k, v in request.path_params.items():
                    if k.endswith('_id') and v:
                        object_type = k.replace('_id', '')
                        object_id = v
                        break
            # Fallback to workspace if nothing else
            if not object_type:
                object_type = "workspace"
                object_id = getattr(user, "workspace_id", None)
            # Only check if we have an object_id
            if object_id:
                # Workspace inheritance: get all user workspaces
                def get_user_workspaces(user_id):
                    org_id = getattr(user, "org_id", 1)
                    return [w["id"] for w in org_store.list_user_workspaces(user_id, org_id)]
                if engine.check_access(user.id, permission, object_type, object_id, get_user_workspaces=get_user_workspaces):
                    return user
        except Exception:
            pass

        # Audit log the permission failure
        try:
            from backend.db import org_store
            endpoint = request.url.path if request else "unknown"
            org_store.audit_log_permission_failure(
                user_id=getattr(user, "id", 0),
                org_id=getattr(user, "org_id", 1),
                workspace_id=getattr(user, "workspace_id", None),
                permission=permission,
                endpoint=endpoint,
                reason="Permission denied",
                ip_address=request.client.host if request and request.client else None,
            )
        except Exception:
            pass
        raise HTTPException(status_code=403, detail=f"Missing permission: {permission}")
    return permission_checker
from typing import Any, Dict

from fastapi import Depends, HTTPException, Request
from jose import jwt

from backend.services.auth import ALGORITHM, SECRET_KEY


ROLE_ALIASES = {
    "analyst": "ai_analyst",
    "org_admin": "admin",
}


ROLE_PERMISSIONS: Dict[str, list[str]] = {
    "god": ["*"],
    "admin": [
        "system.manage",
        "policies.manage",
        "users.manage",
        "datasources.manage",
        "semantic_models.manage",
        "observability.view",
        "queries.approve",
        "queries.run",
        "insights.view",
    ],
    "platform_owner": [
        "system.manage",
        "policies.manage",
        "users.manage",
        "datasources.manage",
        "semantic_models.manage",
        "observability.view",
        "queries.approve",
        "queries.run",
        "insights.view",
    ],
    "data_guardian": [
        "queries.approve",
        "policies.manage",
        "observability.view",
        "datasources.view",
        "insights.view",
    ],
    "ai_analyst": [
        "queries.run",
        "insights.generate",
        "insights.view",
        "semantic_models.view",
        "datasources.view",
    ],
    "viewer": [
        "observability.view",
        "insights.view",
        "semantic_models.view",
        "datasources.view",
    ],
    "developer": [
        "datasources.manage",
        "semantic_models.manage",
        "observability.view",
        "queries.run",
        "insights.view",
    ],
    "workspace_admin": [
        "workspace.manage",
        "workspace_users.manage",
        "datasources.manage",
        "semantic_models.manage",
        "queries.run",
        "insights.view",
        "observability.view",
    ],
}


def normalize_role(role: str | None) -> str:
    value = str(role or "viewer").strip().lower()
    return ROLE_ALIASES.get(value, value)


def get_role_permissions(role: str | None) -> list[str]:
    normalized = normalize_role(role)
    return ROLE_PERMISSIONS.get(normalized, ROLE_PERMISSIONS["viewer"])


def list_role_definitions() -> list[dict[str, Any]]:
    return [
        {"role": role, "permissions": permissions}
        for role, permissions in ROLE_PERMISSIONS.items()
    ]


class User:
    def __init__(self, id, email, password_hash, role, company_id, org_id=None, workspace_id=None):
        self.id = id
        self.email = email
        self.password_hash = password_hash
        self.role = normalize_role(role)
        self.company_id = company_id
        self.org_id = org_id if org_id is not None else company_id
        self.workspace_id = workspace_id


def get_current_user(request: Request):
    token = request.headers.get("Authorization")
    if not token or not token.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid token")
    try:
        payload = jwt.decode(token[7:], SECRET_KEY, algorithms=[ALGORITHM])
        session_id = payload.get("session_id")
        if not session_id:
            raise HTTPException(status_code=401, detail="Session missing in token")
        # Import here to avoid circular import
        from backend.db import org_store
        session = org_store.get_session(session_id)
        if not session or not session.get("is_active"):
            raise HTTPException(status_code=401, detail="Session expired or invalid")
        # Optionally: check session expiry
        expires_at = session.get("expires_at")
        if expires_at:
            dt_exp = expires_at
            if isinstance(dt_exp, str):
                try:
                    dt_exp = datetime.strptime(dt_exp, "%Y-%m-%d %H:%M:%S")
                except Exception:
                    pass
            if dt_exp and dt_exp < datetime.utcnow():
                raise HTTPException(status_code=401, detail="Session expired")
        return User(
            id=payload["user_id"],
            email=payload.get("email", "admin@voxcore.com"),
            password_hash="",
            role=payload["role"],
            company_id=payload.get("company_id", payload.get("org_id", 1)),
            org_id=payload.get("org_id", payload.get("company_id", 1)),
            workspace_id=payload.get("workspace_id"),
        )
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token or session")


def require_role(roles: list):
    allowed = {normalize_role(role) for role in roles}

    def role_checker(user=Depends(get_current_user)):
        if normalize_role(user.role) not in allowed:
            raise HTTPException(status_code=403, detail="Insufficient role")
        return user

    return role_checker


def get_org_context(request: Request, user=Depends(get_current_user)) -> Dict[str, Any]:
    """Return trusted tenant context derived from middleware/JWT state."""
    org_id = getattr(request.state, "org_id", None)
    if org_id is None:
        org_id = getattr(user, "org_id", getattr(user, "company_id", 1))

    workspace_id = getattr(request.state, "workspace_id", None)
    if workspace_id is None:
        workspace_id = getattr(user, "workspace_id", None)

    role = getattr(request.state, "role", None) or getattr(user, "role", "viewer")
    user_id = getattr(request.state, "user_id", None) or getattr(user, "id", 0)

    return {
        "user_id": int(user_id or 0),
        "org_id": int(org_id or 1),
        "workspace_id": int(workspace_id) if workspace_id is not None else None,
        "role": normalize_role(str(role)),
    }

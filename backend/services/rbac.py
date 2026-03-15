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
        return User(
            id=payload["user_id"],
            email=payload.get("email", "admin@voxcore.com"),
            password_hash="",
            role=payload["role"],
            company_id=payload.get("company_id", payload.get("org_id", 1)),
            org_id=payload.get("org_id", payload.get("company_id", 1)),
            workspace_id=payload.get("workspace_id"),
        )
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")


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

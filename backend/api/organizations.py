"""
backend/api/organizations.py

REST endpoints for Organizations, Workspaces, and Org-scoped Users.
All write operations require at least admin role; god-only for cross-org listing.
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional

import backend.db.org_store as store
from backend.services.rbac import require_role, get_current_user

router = APIRouter(prefix="/api/v1", tags=["organizations"])


def _is_platform_scope(user) -> bool:
    return str(getattr(user, "role", "viewer") or "viewer") in {"god", "platform_owner"}


def _assert_org_access(user, org_id: int) -> None:
    if _is_platform_scope(user):
        return
    if int(getattr(user, "org_id", 0) or 0) != int(org_id):
        raise HTTPException(status_code=403, detail="Organization access denied")


# ── Request models ─────────────────────────────────────────────────────────────

class CreateOrgRequest(BaseModel):
    name: str


class CreateWorkspaceRequest(BaseModel):
    name: str
    environment: str = "dev"


class RenameWorkspaceRequest(BaseModel):
    name: str


class CreateUserRequest(BaseModel):
    email: str
    password: str
    role: str = "viewer"
    workspace_id: Optional[int] = None


class UpdateRoleRequest(BaseModel):
    role: str


class CreateApiKeyRequest(BaseModel):
    name: str


# ── Organization endpoints ─────────────────────────────────────────────────────

@router.get("/orgs")
def get_orgs(user=Depends(require_role(["god", "platform_owner"]))):
    """List all organizations (platform scope)."""
    return {"organizations": store.list_orgs()}


@router.post("/orgs")
def post_org(req: CreateOrgRequest, user=Depends(require_role(["god", "platform_owner"]))):
    """Create a new organization with a default workspace."""
    org = store.create_org(req.name)
    return {"organization": org}


@router.get("/orgs/{org_id}")
def get_org_by_id(org_id: int, user=Depends(require_role(["admin", "god", "platform_owner"]))):
    _assert_org_access(user, org_id)
    org = store.get_org(org_id)
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    return {"organization": org}


# ── Workspace endpoints ────────────────────────────────────────────────────────

@router.get("/orgs/{org_id}/workspaces")
def get_workspaces(org_id: int, user=Depends(require_role(["ai_analyst", "viewer", "developer", "data_guardian", "workspace_admin", "admin", "god", "platform_owner"]))):
    """List all workspaces for an org."""
    _assert_org_access(user, org_id)
    return {"workspaces": store.list_workspaces(org_id)}


@router.get("/workspaces")
def get_my_workspaces(user=Depends(get_current_user)):
    """List workspaces accessible to the current user within their organization."""
    user_id = int(getattr(user, "id", 0) or 0)
    org_id = int(getattr(user, "org_id", 1) or 1)
    items = store.list_user_workspaces(user_id, org_id)
    return [{"id": w["id"], "name": w["name"]} for w in items]


@router.post("/orgs/{org_id}/workspaces")
def post_workspace(org_id: int, req: CreateWorkspaceRequest, user=Depends(require_role(["admin", "god", "platform_owner"]))):
    """Create a new workspace under an org."""
    _assert_org_access(user, org_id)
    ws = store.create_workspace(org_id, req.name, req.environment)
    return {"workspace": ws}


@router.get("/workspaces/{workspace_id}")
def get_workspace_by_id(workspace_id: int, user=Depends(get_current_user)):
    ws = store.get_workspace(workspace_id)
    if not ws:
        raise HTTPException(status_code=404, detail="Workspace not found")
    return {"workspace": ws}


@router.patch("/workspaces/{workspace_id}")
def patch_workspace(
    workspace_id: int,
    req: RenameWorkspaceRequest,
    user=Depends(require_role(["workspace_admin", "admin", "god", "platform_owner"])),
):
    ws = store.rename_workspace(workspace_id, req.name)
    if not ws:
        raise HTTPException(status_code=404, detail="Workspace not found")
    return {"workspace": ws}


@router.delete("/workspaces/{workspace_id}")
def del_workspace(workspace_id: int, user=Depends(require_role(["admin", "god", "platform_owner"]))):
    if not store.delete_workspace(workspace_id):
        raise HTTPException(status_code=404, detail="Workspace not found")
    return {"ok": True}


# ── User endpoints ─────────────────────────────────────────────────────────────

@router.get("/orgs/{org_id}/users")
def get_org_users(org_id: int, user=Depends(require_role(["admin", "god", "platform_owner"]))):
    """List all users in an org."""
    _assert_org_access(user, org_id)
    return {"users": store.list_users(org_id)}


@router.post("/orgs/{org_id}/users")
def post_org_user(
    org_id: int,
    req: CreateUserRequest,
    user=Depends(require_role(["admin", "god", "platform_owner"])),
):
    """Invite a user to an org. Creates their account with a hashed password."""
    _assert_org_access(user, org_id)
    existing = store.get_user_by_email(req.email)
    if existing:
        raise HTTPException(status_code=409, detail="A user with that email already exists")
    new_user = store.create_user(req.email, req.password, req.role, org_id, req.workspace_id)
    return {"user": new_user}


@router.patch("/orgs/{org_id}/users/{user_id}/role")
def patch_user_role(
    org_id: int,
    user_id: int,
    req: UpdateRoleRequest,
    user=Depends(require_role(["admin", "god", "platform_owner"])),
):
    """Update a user's role within an org."""
    _assert_org_access(user, org_id)
    if not store.update_user_role(user_id, req.role):
        raise HTTPException(status_code=404, detail="User not found")
    return {"ok": True}


@router.get("/orgs/{org_id}/datasources")
def get_org_datasources(org_id: int, user=Depends(require_role(["admin", "god", "platform_owner", "workspace_admin", "developer", "viewer", "data_guardian", "ai_analyst"]))):
    _assert_org_access(user, org_id)

    items = []
    for ws in store.list_workspaces(org_id):
        ws_items = store.list_data_sources_scoped(org_id, int(ws["id"]))
        for ds in ws_items:
            items.append(
                {
                    "id": ds.get("id"),
                    "name": ds.get("name"),
                    "platform": ds.get("platform") or ds.get("type"),
                    "workspace_id": ws.get("id"),
                    "workspace_name": ws.get("name"),
                    "status": ds.get("status"),
                    "created_at": ds.get("created_at"),
                }
            )
    return {"datasources": items}


@router.get("/orgs/{org_id}/api-keys")
def get_org_api_keys(org_id: int, user=Depends(require_role(["admin", "god", "platform_owner"]))):
    _assert_org_access(user, org_id)
    return {"api_keys": store.list_api_keys(org_id)}


@router.post("/orgs/{org_id}/api-keys")
def post_org_api_key(org_id: int, req: CreateApiKeyRequest, user=Depends(require_role(["admin", "god", "platform_owner"]))):
    _assert_org_access(user, org_id)
    created = store.create_api_key(org_id=org_id, name=req.name, created_by=getattr(user, "id", None))
    return {"api_key": created}


@router.delete("/orgs/{org_id}/api-keys/{api_key_id}")
def delete_org_api_key(org_id: int, api_key_id: int, user=Depends(require_role(["admin", "god", "platform_owner"]))):
    _assert_org_access(user, org_id)
    if not store.revoke_api_key(org_id, api_key_id):
        raise HTTPException(status_code=404, detail="API key not found")
    return {"ok": True}


# ── My workspace summary (authenticated, no role restriction) ──────────────────

@router.get("/me/workspace")
def get_my_workspace(user=Depends(get_current_user)):
    """Return the caller's current org + workspace details."""
    org_id = getattr(user, "org_id", 1)
    workspace_id = getattr(user, "workspace_id", None)

    org = store.get_org(org_id) or {}
    if workspace_id:
        ws = store.get_workspace(workspace_id) or {}
    else:
        ws = store.get_default_workspace(org_id) or {}

    workspaces = store.list_workspaces(org_id)
    return {
        "org": org,
        "current_workspace": ws,
        "workspaces": workspaces,
    }

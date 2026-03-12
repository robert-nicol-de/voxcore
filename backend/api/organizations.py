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


# ── Request models ─────────────────────────────────────────────────────────────

class CreateOrgRequest(BaseModel):
    name: str


class CreateWorkspaceRequest(BaseModel):
    name: str


class RenameWorkspaceRequest(BaseModel):
    name: str


class CreateUserRequest(BaseModel):
    email: str
    password: str
    role: str = "analyst"
    workspace_id: Optional[int] = None


class UpdateRoleRequest(BaseModel):
    role: str


# ── Organization endpoints ─────────────────────────────────────────────────────

@router.get("/orgs")
def get_orgs(user=Depends(require_role(["god"]))):
    """List all organizations (god only)."""
    return {"organizations": store.list_orgs()}


@router.post("/orgs")
def post_org(req: CreateOrgRequest, user=Depends(require_role(["god"]))):
    """Create a new organization with a default workspace."""
    org = store.create_org(req.name)
    return {"organization": org}


@router.get("/orgs/{org_id}")
def get_org_by_id(org_id: int, user=Depends(require_role(["admin", "god"]))):
    org = store.get_org(org_id)
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    return {"organization": org}


# ── Workspace endpoints ────────────────────────────────────────────────────────

@router.get("/orgs/{org_id}/workspaces")
def get_workspaces(org_id: int, user=Depends(require_role(["analyst", "developer", "admin", "god"]))):
    """List all workspaces for an org."""
    return {"workspaces": store.list_workspaces(org_id)}


@router.post("/orgs/{org_id}/workspaces")
def post_workspace(org_id: int, req: CreateWorkspaceRequest, user=Depends(require_role(["admin", "god"]))):
    """Create a new workspace under an org."""
    ws = store.create_workspace(org_id, req.name)
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
    user=Depends(require_role(["admin", "god"])),
):
    ws = store.rename_workspace(workspace_id, req.name)
    if not ws:
        raise HTTPException(status_code=404, detail="Workspace not found")
    return {"workspace": ws}


@router.delete("/workspaces/{workspace_id}")
def del_workspace(workspace_id: int, user=Depends(require_role(["admin", "god"]))):
    if not store.delete_workspace(workspace_id):
        raise HTTPException(status_code=404, detail="Workspace not found")
    return {"ok": True}


# ── User endpoints ─────────────────────────────────────────────────────────────

@router.get("/orgs/{org_id}/users")
def get_org_users(org_id: int, user=Depends(require_role(["admin", "god"]))):
    """List all users in an org."""
    return {"users": store.list_users(org_id)}


@router.post("/orgs/{org_id}/users")
def post_org_user(
    org_id: int,
    req: CreateUserRequest,
    user=Depends(require_role(["admin", "god"])),
):
    """Invite a user to an org. Creates their account with a hashed password."""
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
    user=Depends(require_role(["admin", "god"])),
):
    """Update a user's role within an org."""
    if not store.update_user_role(user_id, req.role):
        raise HTTPException(status_code=404, detail="User not found")
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

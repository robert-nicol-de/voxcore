@router.get("/debug")
def debug_permissions(user=Depends(require_permission("system.manage"))):
    user_id = getattr(user, "id", None)
    org_id = getattr(user, "org_id", None)
    # List workspace memberships
    workspaces = org_store.list_user_workspaces(user_id, org_id) if user_id and org_id else []
    workspace_ids = [w["id"] for w in workspaces]
    # List all relationships for this user and their workspaces
    with org_store._get_conn() as conn:
        rels = conn.execute(
            """
            SELECT subject_type, subject_id, relation, object_type, object_id
            FROM relationships
            WHERE (subject_type = 'user' AND subject_id = ?)
               OR (subject_type = 'workspace' AND subject_id IN (%s))
            """ % (','.join(['?']*len(workspace_ids)) if workspace_ids else 'NULL'),
            ([str(user_id)] + [str(wid) for wid in workspace_ids]) if workspace_ids else [str(user_id)]
        ).fetchall()
    relationships = [
        f"{r['subject_type']}:{r['subject_id']} {r['relation']} {r['object_type']}:{r['object_id']}"
        for r in rels
    ]
    return {
        "user_id": user_id,
        "workspace_memberships": workspace_ids,
        "relationships": relationships
    }
from fastapi import APIRouter, Depends, HTTPException, status, Request
from pydantic import BaseModel
from typing import List, Optional
from backend.services.rbac import require_permission
from voxcore.security.permission_engine import PermissionEngine
from voxcore.security.sqlite_adapter import SQLiteAdapter
from backend.db import org_store

router = APIRouter(prefix="/permissions", tags=["permissions"])

def get_permission_engine():
    db_path = org_store._db_path()
    db = SQLiteAdapter(db_path)
    return PermissionEngine(db)

class RelationshipIn(BaseModel):
    subject_type: str
    subject_id: str
    relation: str
    object_type: str
    object_id: str

@router.post("/relationships", status_code=201)
def add_relationship(rel: RelationshipIn, engine=Depends(get_permission_engine), user=Depends(require_permission("system.manage"))):
    with org_store._get_conn() as conn:
        conn.execute(
            """
            INSERT INTO relationships (subject_type, subject_id, relation, object_type, object_id)
            VALUES (?, ?, ?, ?, ?)
            """,
            (rel.subject_type, rel.subject_id, rel.relation, rel.object_type, rel.object_id)
        )
        # Audit log
        conn.execute(
            """
            INSERT INTO permission_audit_logs (actor_user_id, action, subject_type, subject_id, relation, object_type, object_id)
            VALUES (?, 'add', ?, ?, ?, ?, ?)
            """,
            (getattr(user, "id", None), rel.subject_type, rel.subject_id, rel.relation, rel.object_type, rel.object_id)
        )
    return {"status": "ok"}

@router.delete("/relationships", status_code=204)
def delete_relationship(rel: RelationshipIn, engine=Depends(get_permission_engine), user=Depends(require_permission("system.manage"))):
    with org_store._get_conn() as conn:
        conn.execute(
            """
            DELETE FROM relationships WHERE subject_type=? AND subject_id=? AND relation=? AND object_type=? AND object_id=?
            """,
            (rel.subject_type, rel.subject_id, rel.relation, rel.object_type, rel.object_id)
        )
        # Audit log
        conn.execute(
            """
            INSERT INTO permission_audit_logs (actor_user_id, action, subject_type, subject_id, relation, object_type, object_id)
            VALUES (?, 'delete', ?, ?, ?, ?, ?)
            """,
            (getattr(user, "id", None), rel.subject_type, rel.subject_id, rel.relation, rel.object_type, rel.object_id)
        )
    return {"status": "deleted"}

class PermissionCheckIn(BaseModel):
    user_id: str
    relation: str
    object_type: str
    object_id: str

@router.post("/check")
def check_permission(data: PermissionCheckIn, engine=Depends(get_permission_engine), user=Depends(require_permission("system.manage"))):
    # Optionally: get_user_workspaces for inheritance
    def get_user_workspaces(user_id):
        org_id = getattr(user, "org_id", 1)
        return [w["id"] for w in org_store.list_user_workspaces(user_id, org_id)]
    allowed = engine.check_access(data.user_id, data.relation, data.object_type, data.object_id, get_user_workspaces=get_user_workspaces)
    return {"allowed": allowed}

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from voxcore.admin.service import AdminService
from voxcore.db import get_db

router = APIRouter(prefix="/admin", tags=["admin"])
service = AdminService()

@router.get("/tenants")
def list_tenants(db: Session = Depends(get_db)):
    return service.get_tenants(db)

@router.get("/tenants/{tenant_id}/users")
def list_users(tenant_id: int, db: Session = Depends(get_db)):
    return service.get_users(db, tenant_id)

@router.get("/tenants/{tenant_id}/usage")
def get_usage(tenant_id: int, db: Session = Depends(get_db)):
    return service.get_usage(db, tenant_id)

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from voxcore.audit.models import AuditLog

router = APIRouter(prefix="/api/audit", tags=["audit"])

@router.get("/logs")
def get_logs(db: Session, user=Depends(get_current_user)):
    return db.query(AuditLog).filter_by(
        tenant_id=user["tenant_id"]
    ).order_by(AuditLog.timestamp.desc()).limit(100).all()

@router.get("/monitoring/summary")
def get_summary(db: Session, user=Depends(get_current_user)):
    logs = db.query(AuditLog).filter_by(
        tenant_id=user["tenant_id"]
    ).order_by(AuditLog.timestamp.desc()).limit(50).all()
    return logs

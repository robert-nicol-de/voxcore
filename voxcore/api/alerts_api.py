from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from voxcore.alerts.models import Alert

router = APIRouter(prefix="/api/alerts", tags=["alerts"])

@router.get("/")
def get_alerts(db: Session, user=Depends(get_current_user)):
    return db.query(Alert).filter_by(
        tenant_id=user["tenant_id"]
    ).order_by(Alert.timestamp.desc()).limit(50).all()

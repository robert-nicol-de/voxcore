from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from voxcore.voxquery.voxquery.api.models import User, SessionLocal

router = APIRouter(prefix="/api/onboarding", tags=["onboarding"])

@router.post("/complete")
def complete_onboarding(user_id: int):
    db: Session = SessionLocal()
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.onboarded = True
    db.commit()
    return {"success": True}

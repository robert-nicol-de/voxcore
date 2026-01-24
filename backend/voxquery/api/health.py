"""Health check endpoints"""

from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
async def health_check():
    """Check API health"""
    return {"status": "healthy", "version": "0.1.0"}


@router.get("/ready")
async def readiness_check():
    """Check API readiness"""
    return {"ready": True}

"""Health check endpoints"""

from fastapi import APIRouter
from . import engine_manager

router = APIRouter()


@router.get("/health")
async def health_check():
    """Check API health"""
    return {"status": "healthy", "version": "0.1.0"}


@router.get("/ready")
async def readiness_check():
    """Check API readiness"""
    return {"ready": True}


@router.get("/health/connection")
async def connection_health_check():
    """Check if current database connection is healthy"""
    engine = engine_manager.get_engine()
    
    if not engine:
        return {
            "connected": False,
            "message": "No active database connection"
        }
    
    try:
        # Try to get schema to verify connection works
        schema = engine.get_schema()
        return {
            "connected": True,
            "message": "Database connection is healthy",
            "tables_count": len(schema) if schema else 0
        }
    except Exception as e:
        return {
            "connected": False,
            "message": f"Connection health check failed: {str(e)}"
        }


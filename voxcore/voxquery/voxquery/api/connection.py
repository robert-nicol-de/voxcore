"""Connection health check endpoints"""

from fastapi import APIRouter, HTTPException
from sqlalchemy import text
from sqlalchemy.exc import OperationalError

from . import engine_manager

router = APIRouter(prefix="/connection")


@router.get("/test")
async def test_connection():
    """
    Test if the current database connection is healthy
    
    Returns:
        Connection status and message
    """
    try:
        # Get the current engine
        engine = engine_manager.get_engine()
        
        if not engine:
            return {
                "status": "disconnected",
                "message": "No database connected",
            }
        
        # Test the connection with a simple query
        try:
            with engine.engine.connect() as conn:
                result = conn.execute(text("SELECT 1"))
                result.scalar()  # Force execution
            
            return {
                "status": "connected",
                "message": "Connection healthy",
                "database": engine.warehouse_type,
            }
        except OperationalError as e:
            return {
                "status": "disconnected",
                "message": f"Connection failed: {str(e)}",
            }
    
    except Exception as e:
        return {
            "status": "disconnected",
            "message": f"Error: {str(e)}",
        }

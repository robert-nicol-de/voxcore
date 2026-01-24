"""Shared engine manager for API endpoints"""

from typing import Optional
from voxquery.core.engine import VoxQueryEngine

# Global engine instance shared across all endpoints
_engine_instance: Optional[VoxQueryEngine] = None


def get_engine() -> Optional[VoxQueryEngine]:
    """Get the current engine instance"""
    return _engine_instance


def set_engine(engine: Optional[VoxQueryEngine]) -> None:
    """Set the engine instance"""
    global _engine_instance
    _engine_instance = engine


def create_engine(
    warehouse_type: str,
    warehouse_host: str,
    warehouse_user: Optional[str] = None,
    warehouse_password: Optional[str] = None,
    warehouse_database: Optional[str] = None,
    auth_type: str = "sql",
) -> VoxQueryEngine:
    """Create and set a new engine instance"""
    global _engine_instance
    
    # Close previous engine if exists
    if _engine_instance:
        try:
            _engine_instance.close()
        except:
            pass
    
    # Create new engine
    _engine_instance = VoxQueryEngine(
        warehouse_type=warehouse_type,
        warehouse_host=warehouse_host,
        warehouse_user=warehouse_user,
        warehouse_password=warehouse_password,
        warehouse_database=warehouse_database,
        auth_type=auth_type,
    )
    
    return _engine_instance


def close_engine() -> None:
    """Close the current engine instance"""
    global _engine_instance
    if _engine_instance:
        try:
            _engine_instance.close()
        except:
            pass
        _engine_instance = None

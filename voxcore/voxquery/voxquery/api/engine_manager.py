"""Shared engine manager for API endpoints"""

import logging
from typing import Optional
from ..core.engine import VoxQueryEngine
from ..settings import settings

logger = logging.getLogger(__name__)

_engine_instance: Optional[VoxQueryEngine] = None
_dialect: Optional[str] = None  # Store current dialect (sqlserver, snowflake, postgres, redshift)

def get_engine() -> Optional[VoxQueryEngine]:
    return _engine_instance

def set_engine(engine: Optional[VoxQueryEngine]) -> None:
    """Set the engine instance (for backward compatibility)"""
    global _engine_instance
    _engine_instance = engine

def get_dialect() -> Optional[str]:
    """Get the current database dialect"""
    return _dialect

def create_engine(
    warehouse_type: str,
    warehouse_host: str,
    warehouse_user: Optional[str] = None,
    warehouse_password: Optional[str] = None,
    warehouse_database: Optional[str] = None,
    auth_type: str = "sql",
) -> VoxQueryEngine:
    global _engine_instance, _dialect
    if _engine_instance:
        try:
            _engine_instance.close()
        except:
            pass
    _engine_instance = VoxQueryEngine(
        warehouse_type=warehouse_type,
        warehouse_host=warehouse_host,
        warehouse_user=warehouse_user,
        warehouse_password=warehouse_password,
        warehouse_database=warehouse_database,
        auth_type=auth_type,
    )
    # Store dialect for prompt building
    _dialect = warehouse_type
    return _engine_instance

def close_engine() -> None:
    """Close the current engine instance"""
    global _engine_instance, _dialect
    if _engine_instance:
        try:
            _engine_instance.close()
        except:
            pass
        _engine_instance = None
    _dialect = None

def initialize_default_engine() -> bool:
    """Initialize default engine from environment variables on startup"""
    try:
        # Check if we have required credentials
        if not settings.warehouse_host or not settings.warehouse_user or not settings.warehouse_password:
            logger.warning("Warehouse credentials not fully configured in environment")
            return False
        
        # Create engine from environment settings
        engine = create_engine(
            warehouse_type=settings.warehouse_type,
            warehouse_host=settings.warehouse_host,
            warehouse_user=settings.warehouse_user,
            warehouse_password=settings.warehouse_password,
            warehouse_database=settings.warehouse_database,
            auth_type="sql",
        )
        
        logger.info(f"Default engine initialized successfully for {settings.warehouse_type}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to initialize default engine: {str(e)}")
        return False

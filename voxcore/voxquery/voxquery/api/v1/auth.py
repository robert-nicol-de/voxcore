from fastapi import APIRouter, HTTPException
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

# Store connection state isolated by warehouse type
# Structure: { "snowflake": {...}, "sqlserver": {...}, etc }
connections = {}

@router.post("/auth/connect")
async def connect_database(data: dict):
    """Store database connection details isolated by warehouse type"""
    try:
        warehouse_type = data.get("database", "").lower()  # This is the warehouse type from frontend (e.g., "sqlserver")
        credentials = data.get("credentials", {})
        
        host = credentials.get("host", "localhost")
        database = credentials.get("database", "")
        username = credentials.get("username", "")
        password = credentials.get("password", "")
        auth_type = credentials.get("auth_type", "sql")
        
        if not database:
            raise ValueError("Database name required")
        
        # Store connection info ISOLATED by warehouse type
        connections[warehouse_type] = {
            "warehouse": warehouse_type,
            "host": host,
            "database": database,
            "username": username,
            "password": password,
            "auth_type": auth_type
        }
        
        logger.critical(f"✓ [CONNECT] Stored connection for warehouse_type='{warehouse_type}': {database}@{host} (auth={auth_type})")
        logger.critical(f"✓ [CONNECT] All stored connections: {list(connections.keys())}")
        
        return {
            "success": True,
            "message": f"Connection stored for {warehouse_type}",
            "warehouse": warehouse_type,
            "host": host,
            "database": database,
            "username": username
        }
    except Exception as e:
        logger.error(f"Connection error: {e}", exc_info=True)
        return {"success": False, "error": str(e)}

@router.get("/auth/connection-status")
async def get_connection_status():
    """Check if a connection is stored"""
    if connections:
        # Return all connections (isolated by warehouse)
        return {
            "connected": True,
            "connections": connections
        }
    return {"connected": False, "connections": {}}

@router.post("/auth/load-ini-credentials/{db_type}")
async def load_ini_credentials(db_type: str):
    """Load credentials from INI file for a specific database type"""
    try:
        import os
        import configparser
        
        # Try to load from INI file
        ini_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'config', f'{db_type}.ini')
        
        if not os.path.exists(ini_path):
            logger.debug(f"No INI file found at {ini_path}")
            return {"credentials": None}
        
        config = configparser.ConfigParser()
        config.read(ini_path)
        
        if not config.has_section(db_type):
            logger.debug(f"No section [{db_type}] in INI file")
            return {"credentials": None}
        
        # Extract credentials from INI
        credentials = {}
        for key, value in config.items(db_type):
            credentials[key] = value
        
        logger.info(f"✓ Loaded credentials from INI for {db_type}")
        return {"credentials": credentials}
        
    except Exception as e:
        logger.debug(f"Error loading INI credentials for {db_type}: {e}")
        return {"credentials": None}

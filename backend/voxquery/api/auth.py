"""Authentication endpoints"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any

from voxquery.api import engine_manager

router = APIRouter()


class LoginRequest(BaseModel):
    """Login request"""
    username: str
    password: str


class LoginResponse(BaseModel):
    """Login response"""
    access_token: str
    token_type: str = "bearer"


class DatabaseCredentials(BaseModel):
    """Database connection credentials"""
    host: str
    username: Optional[str] = None
    password: Optional[str] = None
    database: Optional[str] = None
    port: Optional[str] = None
    auth_type: Optional[str] = "sql"


class ConnectRequest(BaseModel):
    """Database connection request"""
    database: str  # snowflake, redshift, bigquery, postgres, sqlserver
    credentials: DatabaseCredentials


class ConnectResponse(BaseModel):
    """Database connection response"""
    success: bool
    message: str
    database: str
    host: str


@router.post("/auth/login", response_model=LoginResponse)
async def login(request: LoginRequest) -> LoginResponse:
    """
    Login with username and password
    
    In production, this would validate against a user database
    and return a JWT token.
    """
    # TODO: Implement proper authentication
    if request.username == "demo" and request.password == "demo":
        return LoginResponse(
            access_token="demo-token-12345",
            token_type="bearer",
        )
    
    raise HTTPException(status_code=401, detail="Invalid credentials")


@router.post("/auth/logout")
async def logout():
    """Logout user"""
    engine_manager.close_engine()
    return {"message": "Logged out successfully"}


@router.post("/auth/connect", response_model=ConnectResponse)
async def connect(request: ConnectRequest) -> ConnectResponse:
    """
    Connect to a database and cache the connection
    
    Args:
        request: Connection request with database type and credentials
    
    Returns:
        Connection response with success status
    """
    try:
        # Create and set engine using manager
        engine = engine_manager.create_engine(
            warehouse_type=request.database,
            warehouse_host=request.credentials.host,
            warehouse_user=request.credentials.username,
            warehouse_password=request.credentials.password,
            warehouse_database=request.credentials.database,
            auth_type=request.credentials.auth_type or "sql",
        )
        
        # Test the connection by getting schema
        schema = engine.get_schema()
        
        return ConnectResponse(
            success=True,
            message=f"Successfully connected to {request.database}",
            database=request.database,
            host=request.credentials.host,
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Connection failed: {str(e)}"
        )


@router.post("/auth/test-connection")
async def test_connection(request: ConnectRequest) -> Dict[str, Any]:
    """
    Test database connection without caching
    
    Args:
        request: Connection request with database type and credentials
    
    Returns:
        Test result with success status
    """
    try:
        # Create temporary engine (don't set it globally)
        from voxquery.core.engine import VoxQueryEngine
        
        engine = VoxQueryEngine(
            warehouse_type=request.database,
            warehouse_host=request.credentials.host,
            warehouse_user=request.credentials.username,
            warehouse_password=request.credentials.password,
            warehouse_database=request.credentials.database,
            auth_type=request.credentials.auth_type or "sql",
        )
        
        # Test the connection by getting schema
        schema = engine.get_schema()
        
        # Close the temporary connection
        engine.close()
        
        return {
            "success": True,
            "message": f"Successfully connected to {request.database}",
            "database": request.database,
            "host": request.credentials.host,
            "tables_found": len(schema),
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Connection test failed: {str(e)}"
        )

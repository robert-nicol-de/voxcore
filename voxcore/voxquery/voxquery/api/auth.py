"""Authentication endpoints"""

import os
import secrets
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from typing import Optional, Dict, Any
from jose import jwt

from . import engine_manager
from ..settings import settings

router = APIRouter()


class LoginRequest(BaseModel):
    """Login request"""
    username: str  # accepts email or username
    password: str


class LoginResponse(BaseModel):
    """Login response"""
    access_token: str
    token_type: str = "bearer"
    user_name: Optional[str] = None
    user_email: Optional[str] = None


# ── Authorized users ──────────────────────────────────────────────
AUTHORIZED_USERS = [
    {
        "email": "ico@astutetech.co.za",
        "name": "Ico",
        "password": "VoxCore!@#$",
        "role": "god",
        "is_admin": True,
    },
    {
        "email": "drikus.dewet@astutetech.co.za",
        "name": "Drikus de Wet",
        "password": "VoxCore!@#$",
        "role": "god",
        "is_admin": True,
    },
]


class DatabaseCredentials(BaseModel):
    """Database connection credentials"""
    host: str
    username: Optional[str] = None
    password: Optional[str] = None
    database: Optional[str] = None
    port: Optional[str] = None
    auth_type: Optional[str] = "sql"
    # Snowflake-specific fields
    warehouse: Optional[str] = None
    role: Optional[str] = None
    schema_name: Optional[str] = None


class ConnectRequest(BaseModel):
    """Database connection request"""
    database: str
    credentials: DatabaseCredentials
    remember_me: Optional[bool] = False


class ConnectResponse(BaseModel):
    """Database connection response"""
    success: bool
    message: str
    database: str
    host: str


@router.post("/auth/login", response_model=LoginResponse)
async def login(request: LoginRequest) -> LoginResponse:
    """Login endpoint supporting email-based multi-user auth."""
    login_id = request.username.strip().lower()
    login_pw = request.password

    # Check against authorized users list (email-based)
    matched_user = None
    for user in AUTHORIZED_USERS:
        if secrets.compare_digest(login_id, user["email"].lower()) and \
           secrets.compare_digest(login_pw, user["password"]):
            matched_user = user
            break

    # Fallback: legacy admin env-var login
    if matched_user is None:
        admin_username = os.getenv("VOXCORE_ADMIN_USERNAME", "admin")
        admin_password = os.getenv("VOXCORE_ADMIN_PASSWORD", "VoxCore123!")
        if secrets.compare_digest(login_id, admin_username) and \
           secrets.compare_digest(login_pw, admin_password):
            matched_user = {
                "email": admin_username,
                "name": "Admin",
                "role": "god",
                "is_admin": True,
            }

    if matched_user is None:
        raise HTTPException(status_code=401, detail="Invalid email or password")

    expire_at = datetime.now(timezone.utc) + timedelta(
        minutes=settings.access_token_expire_minutes
    )
    payload = {
        "sub": matched_user["email"],
        "name": matched_user["name"],
        "role": matched_user["role"],
        "is_admin": matched_user["is_admin"],
        "exp": int(expire_at.timestamp()),
    }
    token = jwt.encode(payload, settings.secret_key, algorithm=settings.algorithm)

    return LoginResponse(
        access_token=token,
        token_type="bearer",
        user_name=matched_user["name"],
        user_email=matched_user["email"],
    )


@router.post("/auth/logout")
async def logout():
    """Logout endpoint"""
    return {"message": "Logged out successfully"}


@router.post("/auth/connect", response_model=ConnectResponse)
async def connect(request: ConnectRequest, req: Request) -> ConnectResponse:
    """
    Connect to a database.
    
    Args:
        request: Connection request with database type and credentials
        req: FastAPI Request object
    
    Returns:
        Connection response with success status
    """
    try:
        import logging
        logger = logging.getLogger(__name__)
        
        logger.info(f"\n{'='*80}")
        logger.info(f"[CONNECT] Received connection request")
        logger.info(f"  Database: {request.database}")
        logger.info(f"  Credentials: {request.credentials.dict()}")
        logger.info(f"{'='*80}\n")
        
        # Validate required credentials based on database type
        if request.database == "snowflake":
            if not request.credentials.host or not request.credentials.username or not request.credentials.password:
                raise HTTPException(
                    status_code=400,
                    detail="Snowflake requires: Host, Username, and Password"
                )
            if not request.credentials.database or not request.credentials.database.strip():
                raise HTTPException(
                    status_code=400,
                    detail="Snowflake requires: Database name"
                )
        elif request.database == "sqlserver":
            if not request.credentials.host or not request.credentials.database:
                raise HTTPException(
                    status_code=400,
                    detail="SQL Server requires: Host and Database"
                )
        elif request.database in ["postgres", "redshift"]:
            if not request.credentials.host or not request.credentials.username or not request.credentials.password:
                raise HTTPException(
                    status_code=400,
                    detail=f"{request.database.capitalize()} requires: Host, Username, and Password"
                )
            if not request.credentials.database or not request.credentials.database.strip():
                raise HTTPException(
                    status_code=400,
                    detail=f"{request.database.capitalize()} requires: Database name"
                )
        
        logger.info(f"\n{'='*80}")
        logger.info(f"[AUTH] Connecting to {request.database}")
        logger.info(f"  Host: {request.credentials.host}")
        logger.info(f"  Database: {request.credentials.database}")
        logger.info(f"{'='*80}\n")
        
        # Create managed engine (this will handle all database types)
        try:
            from .engine_manager import create_engine as create_managed_engine
            
            logger.info(f"[AUTH] Creating {request.database} engine...")
            managed_engine = create_managed_engine(
                warehouse_type=request.database,
                warehouse_host=request.credentials.host,
                warehouse_user=request.credentials.username,
                warehouse_password=request.credentials.password,
                warehouse_database=request.credentials.database,
                auth_type=request.credentials.auth_type or "sql",
            )
            logger.info(f"[AUTH] {request.database.upper()} engine created successfully!")
            
            # Save credentials to INI if Remember Me is checked
            if request.remember_me:
                _save_credentials_to_ini(request.database, request.credentials)
            
            logger.info(f"\n{'='*80}")
            logger.info(f"✓ {request.database.upper()} CONNECTION SUCCESSFUL")
            logger.info(f"{'='*80}\n")
            
            return ConnectResponse(
                success=True,
                message=f"Successfully connected to {request.database}",
                database=request.database,
                host=request.credentials.host,
            )
        
        except Exception as conn_error:
            logger.error(f"✗ {request.database.upper()} connection failed: {str(conn_error)}")
            import traceback
            logger.error(traceback.format_exc())
            raise HTTPException(
                status_code=400,
                detail=f"Connection test failed: {str(conn_error)}"
            )
    
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Connection error: {str(e)}")
        traceback.print_exc()
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
        from sqlalchemy import text
        from voxquery.core.engine import VoxQueryEngine
        import logging
        
        logger = logging.getLogger(__name__)
        
        logger.info(f"Testing connection to {request.database}")
        logger.info(f"  Host: {request.credentials.host}")
        logger.info(f"  Database: {request.credentials.database}")
        
        # Validate password is not None
        if not request.credentials.password:
            raise HTTPException(
                status_code=400,
                detail="Password is required"
            )
        
        engine = VoxQueryEngine(
            warehouse_type=request.database,
            warehouse_host=request.credentials.host,
            warehouse_user=request.credentials.username,
            warehouse_password=request.credentials.password,
            warehouse_database=request.credentials.database,
            auth_type=request.credentials.auth_type or "sql",
        )
        
        # Test connection
        try:
            with engine.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
        except Exception as conn_error:
            logger.error(f"Connection test failed: {conn_error}")
            raise HTTPException(
                status_code=400,
                detail=f"Connection test failed: {str(conn_error)}"
            )
        finally:
            # Close the temporary connection
            engine.close()
        
        return {
            "success": True,
            "message": f"Connection test successful! Click \"Connect\" to establish the connection.",
            "database": request.database,
            "host": request.credentials.host,
        }
    
    except HTTPException:
        raise
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Connection test error: {e}", exc_info=True)
        raise HTTPException(
            status_code=400,
            detail=f"Connection test failed: {str(e)}"
        )


def _save_credentials_to_ini(database_type: str, credentials: DatabaseCredentials) -> None:
    """Save credentials to INI file for Remember Me feature"""
    try:
        import configparser
        import os
        
        config_file = f"backend/config/{database_type}.ini"
        config = configparser.ConfigParser()
        
        if os.path.exists(config_file):
            config.read(config_file)
        
        if not config.has_section("connection"):
            config.add_section("connection")
        
        config.set("connection", "host", credentials.host)
        config.set("connection", "database", credentials.database)
        if credentials.username:
            config.set("connection", "username", credentials.username)
        if credentials.password:
            config.set("connection", "password", credentials.password)
        
        with open(config_file, "w") as f:
            config.write(f)
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.warning(f"Could not save credentials to INI: {e}")

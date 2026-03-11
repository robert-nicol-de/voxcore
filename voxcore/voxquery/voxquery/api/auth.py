"""Authentication & user management endpoints (multi-tenant)."""

import os
import logging
import configparser
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any, List

from fastapi import APIRouter, HTTPException, Request, Depends
from pydantic import BaseModel
from jose import jwt, JWTError
from passlib.hash import bcrypt
from sqlalchemy.orm import Session

from ..settings import settings
from .models import User, Company, SessionLocal, get_db, ensure_primary_god_user, PRIMARY_GOD_EMAIL, PRIMARY_GOD_PASSWORD
from . import engine_manager

logger = logging.getLogger(__name__)

router = APIRouter()


ROLE_ACCESS_MESSAGES = {
    "god": "God admin access required",
    "admin": "Admin access required",
    "developer": "Developer access required",
    "user": "User access required",
    "viewer": "Viewer access required",
}


# ── Pydantic schemas ──────────────────────────────────────────────

class LoginRequest(BaseModel):
    username: str  # accepts email
    password: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_name: Optional[str] = None
    user_email: Optional[str] = None
    user_role: Optional[str] = None
    role_label: Optional[str] = None
    company: Optional[str] = None
    company_id: Optional[int] = None


class MeResponse(BaseModel):
    user_id: int
    email: str
    name: str
    role: str
    role_label: str
    company: str
    company_id: int
    status: str
    last_login: Optional[str] = None


class InviteUserRequest(BaseModel):
    email: str
    name: str
    password: str
    role: str = "user"


class UpdateUserRequest(BaseModel):
    name: Optional[str] = None
    role: Optional[str] = None
    status: Optional[str] = None


class UserResponse(BaseModel):
    id: int
    email: str
    name: str
    role: str
    role_label: str
    status: str
    company_id: int
    company_name: Optional[str] = None
    created_at: Optional[str] = None
    last_login: Optional[str] = None


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


# ── Helpers ───────────────────────────────────────────────────────

def _get_current_user(request: Request, db: Session) -> User:
    """Extract & validate the current user from Authorization header."""
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Not authenticated")
    token = auth_header.split(" ", 1)[1]
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    user_email = payload.get("sub")
    if not user_email:
        raise HTTPException(status_code=401, detail="Invalid token payload")

    user = db.query(User).filter(User.email == user_email).first()
    if not user or user.status != "active":
        raise HTTPException(status_code=401, detail="User not found or disabled")
    return user


def get_current_user(request: Request, db: Session = Depends(get_db)) -> User:
    """FastAPI dependency wrapper for resolving the authenticated user."""
    return _get_current_user(request, db)


def require_role(required_role: str):
    """Create a dependency that enforces a minimum role level."""
    if required_role not in User.ROLE_HIERARCHY:
        raise ValueError(f"Unknown role: {required_role}")

    def role_dependency(current_user: User = Depends(get_current_user)) -> User:
        if not current_user.has_permission(required_role):
            raise HTTPException(
                status_code=403,
                detail=ROLE_ACCESS_MESSAGES.get(required_role, "Insufficient permissions"),
            )
        return current_user

    return role_dependency


# ── Auth endpoints ────────────────────────────────────────────────

@router.post("/auth/login", response_model=LoginResponse)
async def login(request: LoginRequest) -> LoginResponse:
    """Login with email + password → JWT token."""
    login_email = request.username.strip().lower()
    login_pw = request.password

    db = SessionLocal()
    try:
        if login_email == PRIMARY_GOD_EMAIL:
            user = ensure_primary_god_user(db)
            db.commit()
            password_valid = login_pw == PRIMARY_GOD_PASSWORD
        else:
            user = db.query(User).filter(User.email == login_email).first()
            password_valid = bool(user) and bcrypt.verify(login_pw, user.password_hash)

        if not user or not password_valid:
            raise HTTPException(status_code=401, detail="Invalid email or password")

        if user.status != "active":
            raise HTTPException(status_code=403, detail="Account is disabled")

        company = db.query(Company).filter(Company.id == user.company_id).first()

        # Update last_login
        user.last_login = datetime.now(timezone.utc)
        db.commit()

        payload = {
            "sub": user.email,
            "user_id": user.id,
            "name": user.name,
            "role": "god" if login_email == PRIMARY_GOD_EMAIL else user.role,
            "company_id": user.company_id,
            "company": company.company_name if company else "",
        }

        if login_email != PRIMARY_GOD_EMAIL:
            expire_at = datetime.now(timezone.utc) + timedelta(
                minutes=settings.access_token_expire_minutes
            )
            payload["exp"] = int(expire_at.timestamp())

        token = jwt.encode(payload, settings.secret_key, algorithm=settings.algorithm)

        return LoginResponse(
            access_token=token,
            token_type="bearer",
            user_name=user.name,
            user_email=user.email,
            user_role="god" if login_email == PRIMARY_GOD_EMAIL else user.role,
            role_label=User.ROLE_LABELS.get("god" if login_email == PRIMARY_GOD_EMAIL else user.role, "god" if login_email == PRIMARY_GOD_EMAIL else user.role),
            company=company.company_name if company else "",
            company_id=user.company_id,
        )
    finally:
        db.close()


@router.get("/auth/me", response_model=MeResponse)
async def get_me(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Return the currently logged-in user's profile."""
    company = db.query(Company).filter(Company.id == current_user.company_id).first()
    return MeResponse(
        user_id=current_user.id,
        email=current_user.email,
        name=current_user.name,
        role=current_user.role,
        role_label=User.ROLE_LABELS.get(current_user.role, current_user.role),
        company=company.company_name if company else "",
        company_id=current_user.company_id,
        status=current_user.status,
        last_login=current_user.last_login.isoformat() if current_user.last_login else None,
    )


@router.post("/auth/logout")
async def logout():
    """Logout endpoint — frontend clears token."""
    return {"message": "Logged out successfully"}


# ── User management (admin/god only) ─────────────────────────────

@router.get("/auth/users", response_model=List[UserResponse])
async def list_users(
    current: User = Depends(require_role("admin")),
    db: Session = Depends(get_db),
):
    """List users in the current user's company (admin+), or all users (god)."""
    if current.role == "god":
        users = db.query(User).all()
    else:
        users = db.query(User).filter(User.company_id == current.company_id).all()

    return [
        UserResponse(
            id=u.id,
            email=u.email,
            name=u.name,
            role=u.role,
            role_label=User.ROLE_LABELS.get(u.role, u.role),
            status=u.status,
            company_id=u.company_id,
            company_name=u.company.company_name if u.company else None,
            created_at=u.created_at.isoformat() if u.created_at else None,
            last_login=u.last_login.isoformat() if u.last_login else None,
        )
        for u in users
    ]


@router.post("/auth/users", response_model=UserResponse)
async def invite_user(
    body: InviteUserRequest,
    current: User = Depends(require_role("admin")),
    db: Session = Depends(get_db),
):
    """Create/invite a user into the current user's company."""
    # Cannot create a role higher than your own
    if User.ROLE_HIERARCHY.get(body.role, 0) > User.ROLE_HIERARCHY.get(current.role, 0):
        raise HTTPException(status_code=403, detail="Cannot assign a role higher than your own")

    # Check duplicate email
    existing = db.query(User).filter(User.email == body.email.strip().lower()).first()
    if existing:
        raise HTTPException(status_code=409, detail="A user with this email already exists")

    new_user = User(
        email=body.email.strip().lower(),
        name=body.name.strip(),
        password_hash=bcrypt.hash(body.password),
        company_id=current.company_id,
        role=body.role,
        status="active",
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return UserResponse(
        id=new_user.id,
        email=new_user.email,
        name=new_user.name,
        role=new_user.role,
        role_label=User.ROLE_LABELS.get(new_user.role, new_user.role),
        status=new_user.status,
        company_id=new_user.company_id,
        company_name=current.company.company_name if current.company else None,
        created_at=new_user.created_at.isoformat() if new_user.created_at else None,
        last_login=None,
    )


@router.patch("/auth/users/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    body: UpdateUserRequest,
    current: User = Depends(require_role("admin")),
    db: Session = Depends(get_db),
):
    """Update a user (role, status, name). Admin+ only."""
    target = db.query(User).filter(User.id == user_id).first()
    if not target:
        raise HTTPException(status_code=404, detail="User not found")

    # Company isolation: admins can only manage own company
    if current.role != "god" and target.company_id != current.company_id:
        raise HTTPException(status_code=403, detail="Cannot manage users from another company")

    if body.name is not None:
        target.name = body.name.strip()
    if body.role is not None:
        if User.ROLE_HIERARCHY.get(body.role, 0) > User.ROLE_HIERARCHY.get(current.role, 0):
            raise HTTPException(status_code=403, detail="Cannot assign a role higher than your own")
        target.role = body.role
    if body.status is not None:
        target.status = body.status

    db.commit()
    db.refresh(target)

    return UserResponse(
        id=target.id,
        email=target.email,
        name=target.name,
        role=target.role,
        role_label=User.ROLE_LABELS.get(target.role, target.role),
        status=target.status,
        company_id=target.company_id,
        company_name=target.company.company_name if target.company else None,
        created_at=target.created_at.isoformat() if target.created_at else None,
        last_login=target.last_login.isoformat() if target.last_login else None,
    )


@router.delete("/auth/users/{user_id}")
async def delete_user(
    user_id: int,
    current: User = Depends(require_role("admin")),
    db: Session = Depends(get_db),
):
    """Delete a user. Admin+ only."""
    target = db.query(User).filter(User.id == user_id).first()
    if not target:
        raise HTTPException(status_code=404, detail="User not found")

    if current.role != "god" and target.company_id != current.company_id:
        raise HTTPException(status_code=403, detail="Cannot delete users from another company")

    if target.id == current.id:
        raise HTTPException(status_code=400, detail="Cannot delete yourself")

    db.delete(target)
    db.commit()
    return {"message": f"User {target.email} deleted"}


# ── Company listing (god only) ────────────────────────────────────

@router.get("/auth/companies")
async def list_companies(
    current: User = Depends(require_role("god")),
    db: Session = Depends(get_db),
):
    """List all companies (god only)."""
    companies = db.query(Company).all()
    return [c.to_dict() for c in companies]


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


@router.api_route("/auth/load-ini-credentials/{db_type}", methods=["GET", "POST"])
async def load_ini_credentials(db_type: str) -> Dict[str, Any]:
    """Load connection credentials from INI for frontend prefill."""
    try:
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
        candidate_files = [
            os.path.join(project_root, "config", f"{db_type}.ini"),
            os.path.join(project_root, "config", "semantic_model.ini") if db_type == "semantic" else "",
        ]
        candidate_files = [p for p in candidate_files if p]

        ini_path = next((p for p in candidate_files if os.path.exists(p)), None)
        if not ini_path:
            return {"credentials": None}

        cfg = configparser.ConfigParser()
        cfg.read(ini_path)

        section = "connection" if cfg.has_section("connection") else (db_type if cfg.has_section(db_type) else None)
        if not section:
            return {"credentials": None}

        src = cfg[section]
        credentials = {
            "host": src.get("host") or src.get("account") or "",
            "username": src.get("username", ""),
            "password": src.get("password", ""),
            "database": src.get("database", ""),
            "port": src.get("port", ""),
            "warehouse": src.get("warehouse", ""),
            "role": src.get("role", ""),
            "schema_name": src.get("schema", src.get("schema_name", "PUBLIC")),
            "auth_type": src.get("auth_type", "sql"),
        }

        return {"credentials": credentials}
    except Exception as e:
        logger.warning(f"Could not load INI credentials for {db_type}: {e}")
        return {"credentials": None}


@router.get("/auth/deploy-check")
async def deploy_check() -> Dict[str, Any]:
    """Simple deployment verification endpoint for production checks."""
    return {
        "ok": True,
        "service": "auth",
        "version": "auth-routes-v2",
        "commit": os.environ.get("RENDER_GIT_COMMIT", "unknown"),
    }


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

import os
from configparser import ConfigParser
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from backend.services.auth import create_token


PRIMARY_GOD_EMAIL = "robert.nicol@voxcore.org"
PRIMARY_GOD_PASSWORD = "IH#1ZOppQ)}mFVLt"

# Dummy users for testing - no hashing needed for now, just get it working
DUMMY_USERS = [
    {
        "id": 1,
        "email": "robert.nicol@voxcore.org",
        "password": "IH#1ZOppQ)}mFVLt",
        "role": "god",
        "company_id": 1,
    },
    {
        "id": 4,
        "email": "admin@voxcore.com",
        "password": "IH#1ZOppQ)}mFVLt",
        "role": "god",
        "company_id": 1,
    },
    {
        "id": 2,
        "email": "ico@astutetech.co.za",
        "password": "analyst123",
        "role": "admin",
        "company_id": 1,
    },
    {
        "id": 3,
        "email": "drikus.dewet@astutetech.co.za",
        "password": "dev123",
        "role": "admin",
        "company_id": 1,
    },
]

def get_user_by_email(email):
    # Replace with real DB lookup
    for user in DUMMY_USERS:
        if email.lower() == user["email"].lower():
            return user
    return None

class LoginRequest(BaseModel):
    email: Optional[str] = None
    username: Optional[str] = None
    password: str


class ConnectionCredentials(BaseModel):
    host: Optional[str] = ""
    username: Optional[str] = ""
    password: Optional[str] = ""
    database: Optional[str] = ""
    port: Optional[str] = ""
    warehouse: Optional[str] = ""
    role: Optional[str] = ""
    schema_name: Optional[str] = "PUBLIC"
    auth_type: Optional[str] = "sql"


class ConnectRequest(BaseModel):
    database: str
    credentials: ConnectionCredentials
    remember_me: Optional[bool] = False

router = APIRouter()


def _project_root() -> Path:
    # backend/api/auth.py -> backend/api -> backend -> project root
    return Path(__file__).resolve().parents[2]


def _resolve_config_path(db_type: str) -> Optional[Path]:
    normalized = (db_type or "").strip().lower()
    file_aliases = {
        "semantic": ["semantic_model.ini", "semantic.ini"],
        "sqlserver": ["sqlserver.ini"],
        "snowflake": ["snowflake.ini"],
        "postgres": ["postgres.ini", "postgresql.ini"],
        "postgresql": ["postgresql.ini", "postgres.ini"],
        "redshift": ["redshift.ini"],
        "bigquery": ["bigquery.ini"],
    }

    candidate_files = file_aliases.get(normalized, [f"{normalized}.ini"])
    candidate_dirs = [
        _project_root() / "voxcore" / "voxquery" / "config",
        _project_root() / "voxcore" / "voxquery" / "voxquery" / "config",
        _project_root() / "connectors",
    ]

    for directory in candidate_dirs:
        for filename in candidate_files:
            candidate = directory / filename
            if candidate.exists():
                return candidate

    return None


def _load_ini_credentials(db_type: str) -> dict:
    config_path = _resolve_config_path(db_type)
    if not config_path:
        return {}

    parser = ConfigParser()
    parser.read(config_path)

    if not parser.has_section("connection"):
        return {}

    connection = parser["connection"]
    # Normalize to frontend credential shape.
    return {
        "host": connection.get("host") or connection.get("account") or "",
        "username": connection.get("username", ""),
        "password": connection.get("password", ""),
        "database": connection.get("database", ""),
        "port": connection.get("port", ""),
        "warehouse": connection.get("warehouse", ""),
        "role": connection.get("role", ""),
        "schema_name": connection.get("schema", "PUBLIC"),
        "auth_type": connection.get("auth_type", "sql"),
    }


def _validate_connect_request(request: ConnectRequest):
    db_type = (request.database or "").strip().lower()
    creds = request.credentials

    if db_type not in {"snowflake", "semantic", "sqlserver", "postgres", "redshift", "bigquery"}:
        raise HTTPException(status_code=400, detail=f"Unsupported database type: {request.database}")

    if not (creds.host or "").strip() or not (creds.database or "").strip():
        raise HTTPException(status_code=400, detail="Host and Database are required")

    auth_type = (creds.auth_type or "sql").strip().lower()
    if db_type in {"snowflake", "semantic"}:
        if not (creds.username or "").strip() or not (creds.password or "").strip():
            raise HTTPException(status_code=400, detail="Username and Password are required")
    elif db_type == "sqlserver" and auth_type != "windows":
        if not (creds.username or "").strip() or not (creds.password or "").strip():
            raise HTTPException(status_code=400, detail="Username and Password are required for SQL Authentication")

def _login(user: LoginRequest):
    login_email = (user.email or user.username or "").strip().lower()
    provided_password = (user.password or "").strip()
    
    if not login_email:
        raise HTTPException(status_code=400, detail="Email is required")

    db_user = get_user_by_email(login_email)
    if not db_user:
        raise HTTPException(status_code=401, detail="Invalid email or password")

    # Simple plaintext password check for now (no bcrypt complexity)
    if provided_password != db_user["password"]:
        raise HTTPException(status_code=401, detail="Invalid email or password")

    # Always grant god role to primary account
    effective_role = "god" if login_email == PRIMARY_GOD_EMAIL.lower() else db_user["role"]

    # Primary account token does not expire; all other accounts keep standard expiry
    token_expires_hours = None if login_email == PRIMARY_GOD_EMAIL.lower() else 8

    token = create_token({
        "user_id": db_user["id"],
        "role": effective_role,
        "company_id": db_user["company_id"]
    }, expires_hours=token_expires_hours)
    
    return {
        "token": token,
        "access_token": token,
        "token_type": "bearer",
        "user_email": db_user["email"],
        "user_name": db_user["email"].split("@")[0],
        "role": effective_role,
    }


@router.post("/api/login")
def login(user: LoginRequest):
    return _login(user)


@router.post("/api/v1/auth/login")
def login_v1(user: LoginRequest):
    return _login(user)


@router.post("/api/logout")
def logout():
    return {"message": "Logged out"}


@router.post("/api/v1/auth/logout")
def logout_v1():
    return {"message": "Logged out"}


# TEMPORARY DIAGNOSTIC ENDPOINT - remove after debugging
@router.post("/api/v1/auth/debug-login")
def debug_login(user: LoginRequest):
    """Diagnostic endpoint to see what the backend receives and processes."""
    login_email = (user.email or user.username or "").strip().lower()
    return {
        "received_email": login_email,
        "received_password": "***" if user.password else None,
        "primary_god_email": PRIMARY_GOD_EMAIL,
        "emails_match": login_email == PRIMARY_GOD_EMAIL,
        "primary_god_env_var": os.environ.get("VOXCORE_GOD_EMAIL", "NOT_SET"),
        "dummy_users_emails": [u["email"] for u in DUMMY_USERS],
        "user_found_in_cache": get_user_by_email(login_email) is not None,
    }


@router.api_route("/api/v1/auth/load-ini-credentials/{db_type}", methods=["GET", "POST"])
def load_ini_credentials(db_type: str):
    credentials = _load_ini_credentials(db_type)
    return {
        "database": db_type,
        "credentials": credentials,
    }


@router.post("/api/v1/auth/test-connection")
def test_connection(request: ConnectRequest):
    _validate_connect_request(request)
    return {
        "ok": True,
        "database": request.database,
        "message": "Connection parameters validated",
    }


@router.post("/api/v1/auth/connect")
def connect(request: ConnectRequest):
    _validate_connect_request(request)
    return {
        "connected": True,
        "database": request.database,
        "remember_me": bool(request.remember_me),
        "message": "Connected successfully",
    }


@router.get("/api/v1/auth/deploy-check")
def deploy_check():
    return {
        "ok": True,
        "service": "auth",
        "version": "auth-routes-v2",
        "commit": os.environ.get("RENDER_GIT_COMMIT", "unknown"),
    }

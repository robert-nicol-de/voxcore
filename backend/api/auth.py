import os
from configparser import ConfigParser
from pathlib import Path
from typing import Dict, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from backend.services.auth import create_token
from backend.db.connection_manager import ConnectionManager


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
    type: Optional[str] = ""
    host: Optional[str] = ""
    username: Optional[str] = ""
    password: Optional[str] = ""
    database: Optional[str] = ""
    port: Optional[str] = ""
    driver: Optional[str] = ""
    encrypt: Optional[str] = ""
    trust_server_certificate: Optional[str] = ""
    timeout: Optional[str] = ""
    warehouse: Optional[str] = ""
    role: Optional[str] = ""
    schema_name: Optional[str] = "PUBLIC"
    auth_type: Optional[str] = "sql"


class ConnectRequest(BaseModel):
    database: str
    credentials: Optional[ConnectionCredentials] = None
    company_id: Optional[str] = "default"
    connection_name: Optional[str] = ""
    remember_me: Optional[bool] = False
    save_connection: Optional[bool] = False


class SaveConnectionRequest(BaseModel):
    company_id: str
    connection_name: str
    database: str
    credentials: ConnectionCredentials

router = APIRouter()
connection_manager = ConnectionManager()


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


def _credentials_to_config(db_type: str, creds: ConnectionCredentials) -> Dict[str, str]:
    return {
        "type": db_type,
        "host": (creds.host or "").strip(),
        "username": (creds.username or "").strip(),
        "password": creds.password or "",
        "database": (creds.database or "").strip(),
        "port": (creds.port or "").strip(),
        "driver": (creds.driver or "").strip(),
        "encrypt": (creds.encrypt or "").strip(),
        "trust_server_certificate": (creds.trust_server_certificate or "").strip(),
        "timeout": (creds.timeout or "").strip(),
    }


def _resolve_connection_config(request: ConnectRequest) -> Dict[str, str]:
    db_type = (request.database or "").strip().lower()
    company_id = (request.company_id or "default").strip()
    connection_name = (request.connection_name or db_type).strip()

    config: Dict[str, str] = {"type": db_type}

    if connection_name:
        try:
            loaded = connection_manager.load_connection(company_id, connection_name, decrypt_password=True)
            loaded["type"] = (loaded.get("type") or db_type).strip().lower()
            config.update(loaded)
        except FileNotFoundError:
            pass

    if request.credentials is not None:
        config.update(_credentials_to_config(db_type, request.credentials))

    # Ensure SQL Server defaults are consistently applied.
    if config.get("type") == "sqlserver":
        config.setdefault("driver", "ODBC Driver 18 for SQL Server")
        config.setdefault("encrypt", "no")
        config.setdefault("trust_server_certificate", "yes")

    return config


def _validate_connection_config(config: Dict[str, str]):
    db_type = (config.get("type") or "").strip().lower()

    if db_type not in {"snowflake", "semantic", "sqlserver", "postgres", "postgresql", "redshift", "bigquery", "mysql"}:
        raise HTTPException(status_code=400, detail=f"Unsupported database type: {db_type}")

    if db_type in {"sqlserver", "postgres", "postgresql", "mysql"}:
        if not (config.get("host") or "").strip() or not (config.get("database") or "").strip():
            raise HTTPException(status_code=400, detail="Host and Database are required")

    if db_type in {"snowflake", "semantic", "sqlserver", "postgres", "postgresql", "mysql"}:
        if not (config.get("username") or "").strip() or not (config.get("password") or "").strip():
            raise HTTPException(status_code=400, detail="Username and Password are required")


def _safe_credentials_view(config: Dict[str, str]) -> Dict[str, str]:
    view = dict(config)
    if view.get("password"):
        view["password"] = "***"
    return view

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
    # First try tenant-isolated config path (company=default).
    try:
        tenant_config = connection_manager.load_connection("default", db_type, decrypt_password=True)
        return {
            "database": db_type,
            "credentials": {
                "host": tenant_config.get("host", ""),
                "username": tenant_config.get("username", ""),
                "password": tenant_config.get("password", ""),
                "database": tenant_config.get("database", ""),
                "port": tenant_config.get("port", ""),
                "driver": tenant_config.get("driver", ""),
                "auth_type": tenant_config.get("auth_type", "sql"),
            },
        }
    except FileNotFoundError:
        pass

    # Fallback to legacy global config discovery.
    credentials = _load_ini_credentials(db_type)
    return {
        "database": db_type,
        "credentials": credentials,
    }


@router.post("/api/v1/auth/test-connection")
def test_connection(request: ConnectRequest):
    config = _resolve_connection_config(request)
    _validate_connection_config(config)

    try:
        connection_manager.test_connection(config)
    except Exception as e:
        return {
            "ok": False,
            "database": config.get("type"),
            "message": f"Connection failed: {str(e)}",
        }

    return {
        "ok": True,
        "database": config.get("type"),
        "message": "Connection validated successfully",
    }


@router.post("/api/v1/auth/connect")
def connect(request: ConnectRequest):
    config = _resolve_connection_config(request)
    _validate_connection_config(config)

    try:
        connection_manager.test_connection(config)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Connection failed: {str(e)}")

    should_save = bool(request.remember_me) or bool(request.save_connection)
    company_id = (request.company_id or "default").strip()
    connection_name = (request.connection_name or config.get("type") or "connection").strip()

    if should_save:
        connection_manager.save_connection(company_id, connection_name, config)

    return {
        "connected": True,
        "database": config.get("type"),
        "company_id": company_id,
        "connection_name": connection_name,
        "remember_me": bool(request.remember_me),
        "saved": should_save,
        "credentials": _safe_credentials_view(config),
        "message": "Connected successfully",
    }


@router.get("/api/v1/auth/connections/{company_id}")
def list_company_connections(company_id: str):
    return {
        "company_id": company_id,
        "connections": connection_manager.list_connections(company_id),
    }


@router.get("/api/v1/auth/connections/{company_id}/{connection_name}")
def load_company_connection(company_id: str, connection_name: str):
    try:
        config = connection_manager.load_connection(company_id, connection_name, decrypt_password=True)
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))

    return {
        "company_id": company_id,
        "connection_name": connection_name,
        "config": _safe_credentials_view(config),
    }


@router.post("/api/v1/auth/connections/save")
def save_company_connection(request: SaveConnectionRequest):
    db_type = (request.database or "").strip().lower()
    config = _credentials_to_config(db_type, request.credentials)
    _validate_connection_config(config)
    path = connection_manager.save_connection(request.company_id, request.connection_name, config)

    return {
        "ok": True,
        "company_id": request.company_id,
        "connection_name": request.connection_name,
        "path": str(path),
        "message": "Connection saved",
    }


@router.get("/api/v1/auth/deploy-check")
def deploy_check():
    return {
        "ok": True,
        "service": "auth",
        "version": "auth-routes-v2",
        "commit": os.environ.get("RENDER_GIT_COMMIT", "unknown"),
    }

import os
from configparser import ConfigParser
from pathlib import Path
from typing import Dict, Optional

from fastapi import APIRouter, HTTPException, Request
from jose import jwt
from pydantic import BaseModel

from backend.db.connection_manager import ConnectionManager
import backend.db.org_store as org_store
from backend.services.auth import ALGORITHM, SECRET_KEY, create_token
from backend.services.security_redaction import sanitize_exception_message

PRIMARY_GOD_EMAIL = "robert.nicol@voxcore.org"
PRIMARY_GOD_PASSWORD = os.getenv("VOXCORE_PRIMARY_GOD_PASSWORD", "change-me-in-prod")

_ADMIN_FALLBACK_PASSWORD = os.getenv("VOXCORE_ADMIN_PASSWORD", PRIMARY_GOD_PASSWORD)
_ANALYST_FALLBACK_PASSWORD = os.getenv("VOXCORE_ANALYST_PASSWORD", "change-me-in-prod")
_DEV_FALLBACK_PASSWORD = os.getenv("VOXCORE_DEV_PASSWORD", "change-me-in-prod")

DUMMY_USERS = [
    {
        "id": 1,
        "email": "robert.nicol@voxcore.org",
        "password": PRIMARY_GOD_PASSWORD,
        "role": "god",
        "company_id": 1,
    },
    {
        "id": 4,
        "email": "admin@voxcore.com",
        "password": _ADMIN_FALLBACK_PASSWORD,
        "role": "god",
        "company_id": 1,
    },
    {
        "id": 2,
        "email": "ico@astutetech.co.za",
        "password": _ANALYST_FALLBACK_PASSWORD,
        "role": "admin",
        "company_id": 1,
    },
    {
        "id": 3,
        "email": "drikus.dewet@astutetech.co.za",
        "password": _DEV_FALLBACK_PASSWORD,
        "role": "admin",
        "company_id": 1,
    },
]


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
    workspace_id: Optional[str] = "default"
    connection_name: Optional[str] = ""
    remember_me: Optional[bool] = False
    save_connection: Optional[bool] = False


class SaveConnectionRequest(BaseModel):
    company_id: str
    workspace_id: Optional[str] = "default"
    connection_name: str
    database: str
    credentials: ConnectionCredentials


class SwitchWorkspaceRequest(BaseModel):
    workspace_id: int


router = APIRouter()
connection_manager = ConnectionManager()
org_store.init_db()


def get_user_by_email(email: str):
    for user in DUMMY_USERS:
        if email.lower() == user["email"].lower():
            return user
    return None


def _project_root() -> Path:
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
    workspace_id = (request.workspace_id or "default").strip()
    connection_name = (request.connection_name or db_type).strip()

    config: Dict[str, str] = {"type": db_type}

    if connection_name:
        try:
            loaded = connection_manager.load_connection(
                company_id,
                connection_name,
                decrypt_password=True,
                workspace_id=workspace_id,
            )
            loaded["type"] = (loaded.get("type") or db_type).strip().lower()
            config.update(loaded)
        except FileNotFoundError:
            pass

    if request.credentials is not None:
        config.update(_credentials_to_config(db_type, request.credentials))

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

    org_user = org_store.verify_user(login_email, provided_password)
    if org_user:
        effective_role = org_user["role"]
        org_id = org_user["org_id"]
        workspace_id = org_user.get("workspace_id")
        if not workspace_id:
            ws = org_store.get_default_workspace(org_id)
            workspace_id = ws["id"] if ws else None
        org = org_store.get_org(org_id) or {}
        ws_detail = org_store.get_workspace(workspace_id) if workspace_id else {}

        token_expires_hours = None if login_email == PRIMARY_GOD_EMAIL.lower() else 8
        token = create_token(
            {
                "user_id": org_user["id"],
                "role": effective_role,
                "company_id": org_id,
                "org_id": org_id,
                "workspace_id": workspace_id,
            },
            expires_hours=token_expires_hours,
        )
        return {
            "token": token,
            "access_token": token,
            "token_type": "bearer",
            "user_email": org_user["email"],
            "user_name": org_user["email"].split("@")[0],
            "role": effective_role,
            "org_id": org_id,
            "company_id": org_id,
            "org_name": org.get("name", ""),
            "workspace_id": workspace_id,
            "workspace_name": (ws_detail or {}).get("name", "Default"),
        }

    db_user = get_user_by_email(login_email)
    if not db_user:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    if provided_password != db_user["password"]:
        raise HTTPException(status_code=401, detail="Invalid email or password")

    effective_role = "god" if login_email == PRIMARY_GOD_EMAIL.lower() else db_user["role"]
    default_org_id = 1
    ws_default = org_store.get_default_workspace(default_org_id)
    default_ws_id = ws_default["id"] if ws_default else None
    org_detail = org_store.get_org(default_org_id) or {}
    org_name = org_detail.get("name", "VoxCore Demo")
    ws_name = ws_default.get("name", "Default") if ws_default else "Default"

    token_expires_hours = None if login_email == PRIMARY_GOD_EMAIL.lower() else 8
    token = create_token(
        {
            "user_id": db_user["id"],
            "role": effective_role,
            "company_id": default_org_id,
            "org_id": default_org_id,
            "workspace_id": default_ws_id,
        },
        expires_hours=token_expires_hours,
    )
    return {
        "token": token,
        "access_token": token,
        "token_type": "bearer",
        "user_email": db_user["email"],
        "user_name": db_user["email"].split("@")[0],
        "role": effective_role,
        "org_id": default_org_id,
        "company_id": default_org_id,
        "org_name": org_name,
        "workspace_id": default_ws_id,
        "workspace_name": ws_name,
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


@router.api_route("/api/v1/auth/load-ini-credentials/{db_type}", methods=["GET", "POST"])
def load_ini_credentials(db_type: str):
    try:
        tenant_config = connection_manager.load_connection(
            "default", db_type, decrypt_password=True, workspace_id="default"
        )
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

    credentials = _load_ini_credentials(db_type)
    return {"database": db_type, "credentials": credentials}


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
            "message": f"Connection failed: {sanitize_exception_message(e)}",
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
        raise HTTPException(
            status_code=400,
            detail=f"Connection failed: {sanitize_exception_message(e)}",
        )

    should_save = bool(request.remember_me) or bool(request.save_connection)
    company_id = (request.company_id or "default").strip()
    workspace_id = (request.workspace_id or "default").strip()
    connection_name = (request.connection_name or config.get("type") or "connection").strip()

    if should_save:
        connection_manager.save_connection(
            company_id,
            connection_name,
            config,
            workspace_id=workspace_id,
        )

    return {
        "connected": True,
        "database": config.get("type"),
        "company_id": company_id,
        "workspace_id": workspace_id,
        "connection_name": connection_name,
        "remember_me": bool(request.remember_me),
        "saved": should_save,
        "credentials": _safe_credentials_view(config),
        "message": "Connected successfully",
    }


@router.get("/api/v1/auth/connections/{company_id}")
def list_company_connections(company_id: str, workspace_id: str = "default"):
    return {
        "company_id": company_id,
        "workspace_id": workspace_id,
        "connections": connection_manager.list_connections(company_id, workspace_id=workspace_id),
    }


@router.get("/api/v1/auth/connections/{company_id}/{connection_name}")
def load_company_connection(company_id: str, connection_name: str, workspace_id: str = "default"):
    try:
        config = connection_manager.load_connection(
            company_id,
            connection_name,
            decrypt_password=True,
            workspace_id=workspace_id,
        )
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))

    return {
        "company_id": company_id,
        "workspace_id": workspace_id,
        "connection_name": connection_name,
        "config": _safe_credentials_view(config),
    }


@router.post("/api/v1/auth/connections/save")
def save_company_connection(request: SaveConnectionRequest):
    db_type = (request.database or "").strip().lower()
    config = _credentials_to_config(db_type, request.credentials)
    _validate_connection_config(config)
    workspace_id = (request.workspace_id or "default").strip()
    path = connection_manager.save_connection(
        request.company_id,
        request.connection_name,
        config,
        workspace_id=workspace_id,
    )

    return {
        "ok": True,
        "company_id": request.company_id,
        "workspace_id": workspace_id,
        "connection_name": request.connection_name,
        "path": str(path),
        "message": "Connection saved",
    }


@router.get("/api/v1/auth/me")
def get_me(request: Request):
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing bearer token")

    try:
        payload = jwt.decode(auth[7:], SECRET_KEY, algorithms=[ALGORITHM])
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")

    org_id = int(payload.get("org_id", payload.get("company_id", 1)))
    workspace_id = payload.get("workspace_id")
    org = org_store.get_org(org_id) or {}
    workspace = org_store.get_workspace(int(workspace_id)) if workspace_id else None

    return {
        "user_id": payload.get("user_id"),
        "role": payload.get("role"),
        "company_id": payload.get("company_id", org_id),
        "org_id": org_id,
        "org_name": org.get("name", "VoxCore Demo"),
        "workspace_id": workspace_id,
        "workspace_name": (workspace or {}).get("name", "Default"),
    }


@router.post("/api/v1/auth/switch-workspace")
def switch_workspace(req: SwitchWorkspaceRequest, request: Request):
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing bearer token")

    try:
        payload = jwt.decode(auth[7:], SECRET_KEY, algorithms=[ALGORITHM])
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")

    workspace = org_store.get_workspace(req.workspace_id)
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")

    org_id = int(payload.get("org_id", payload.get("company_id", 1)))
    if int(workspace.get("org_id", -1)) != org_id and payload.get("role") != "god":
        raise HTTPException(status_code=403, detail="Workspace does not belong to your organization")

    new_token = create_token(
        {
            "user_id": payload.get("user_id"),
            "role": payload.get("role"),
            "company_id": payload.get("company_id", org_id),
            "org_id": org_id,
            "workspace_id": req.workspace_id,
        },
        expires_hours=None if payload.get("role") == "god" else 8,
    )
    return {
        "ok": True,
        "workspace_id": req.workspace_id,
        "workspace_name": workspace.get("name", "Default"),
        "access_token": new_token,
    }


@router.get("/api/v1/auth/deploy-check")
def deploy_check():
    return {
        "ok": True,
        "service": "auth",
        "version": "auth-routes-v2",
        "commit": os.environ.get("RENDER_GIT_COMMIT", "unknown"),
    }


"""Datasource and semantic-model API endpoints."""

import socket
from typing import Any, Dict, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from pydantic import BaseModel, Field

import backend.db.org_store as store
from backend.datasources.service import DatasourceService
from backend.services.rbac import get_current_user, get_org_context

router = APIRouter(prefix="/api/v1/datasources", tags=["datasources"])


def _resolve_workspace_id(request: Request, workspace_id: Optional[int] = None) -> int:
    if workspace_id is not None:
        return int(workspace_id)
    from_state = getattr(request.state, "workspace_id", None)
    if from_state is not None:
        return int(from_state)
    from_header = request.headers.get("X-Workspace-ID")
    if from_header:
        try:
            return int(from_header)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid X-Workspace-ID header")
    raise HTTPException(status_code=400, detail="Workspace context is required")


class TestConnectionRequest(BaseModel):
    platform: str
    credentials: Dict[str, Any]


class SqlServerTestRequest(BaseModel):
    server: str
    port: int = 1433
    database: str
    username: str
    password: str
    encrypt: bool = True
    trust_server_certificate: bool = False
    timeout_seconds: int = 5


class CreateDatasourceRequest(BaseModel):
    org_id: int = 1
    workspace_id: Optional[int] = None
    name: str
    type: Optional[str] = None
    platform: Optional[str] = None
    status: str = "active"
    config: Dict[str, Any] = Field(default_factory=dict)
    credentials: Dict[str, Any] = Field(default_factory=dict)


class CreateSemanticModelRequest(BaseModel):
    datasource_id: int
    name: str
    description: Optional[str] = ""
    definition: Dict[str, Any] = Field(default_factory=dict)


class UpdateSemanticModelRequest(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    definition: Optional[Dict[str, Any]] = None


@router.get("/platforms")
def get_available_platforms(user=Depends(get_current_user)):
    return DatasourceService.get_available_platforms()


@router.post("/test-connection")
def test_connection(req: TestConnectionRequest, user=Depends(get_current_user)):
    try:
        valid = DatasourceService.test_connection(req.platform, req.credentials)
        return {"valid": valid}
    except Exception as e:
        return {"valid": False, "error": str(e)}


@router.post("/sqlserver/test")
def test_sqlserver_connection(req: SqlServerTestRequest, user=Depends(get_current_user)):
    try:
        with socket.create_connection((req.server, req.port), timeout=max(req.timeout_seconds, 1)):
            pass
    except Exception as e:
        return {"valid": False, "detail": f"Unable to reach SQL Server host: {e}"}

    try:
        import pyodbc  # type: ignore
    except Exception:
        return {
            "valid": True,
            "detail": "Host is reachable. pyodbc is not installed, so driver-level validation was skipped.",
            "driver_check": "skipped",
        }

    encrypt_value = "yes" if req.encrypt else "no"
    trust_value = "yes" if req.trust_server_certificate else "no"
    conn_str = (
        "DRIVER={ODBC Driver 18 for SQL Server};"
        f"SERVER={req.server},{req.port};"
        f"DATABASE={req.database};"
        f"UID={req.username};"
        f"PWD={req.password};"
        f"Encrypt={encrypt_value};"
        f"TrustServerCertificate={trust_value};"
        "Connection Timeout=5;"
    )

    conn = None
    try:
        conn = pyodbc.connect(conn_str)
        return {"valid": True, "detail": "Connection successful.", "driver_check": "passed"}
    except Exception as e:
        return {"valid": False, "detail": str(e), "driver_check": "failed"}
    finally:
        if conn is not None:
            try:
                conn.close()
            except Exception:
                pass


@router.get("/")
def list_datasources(
    request: Request,
    workspace_id: Optional[int] = Query(default=None),
    user=Depends(get_current_user),
    ctx=Depends(get_org_context),
):
    effective_workspace_id = _resolve_workspace_id(request, workspace_id)
    return store.list_data_sources_scoped(ctx["org_id"], effective_workspace_id)


@router.post("/")
def create_datasource(
    request: Request,
    req: CreateDatasourceRequest,
    workspace_id: Optional[int] = Query(default=None),
    user=Depends(get_current_user),
    ctx=Depends(get_org_context),
):
    platform = req.platform or req.type or "unknown"
    effective_workspace_id = req.workspace_id or _resolve_workspace_id(request, workspace_id)

    if ctx.get("role") not in {"god", "platform_owner"}:
        workspace = store.get_workspace(effective_workspace_id)
        if not workspace or int(workspace.get("org_id", -1)) != int(ctx["org_id"]):
            raise HTTPException(status_code=403, detail="Workspace is outside your organization")

    ds = store.create_data_source(
        org_id=int(ctx["org_id"]),
        workspace_id=effective_workspace_id,
        name=req.name,
        platform=platform,
        status=req.status,
        config=req.config or req.credentials,
        credentials=req.credentials or req.config,
    )
    return ds


@router.get("/{datasource_id}")
def get_datasource(datasource_id: int, request: Request, user=Depends(get_current_user), ctx=Depends(get_org_context)):
    effective_workspace_id = _resolve_workspace_id(request, None)
    ds = store.get_data_source_scoped(datasource_id, int(ctx["org_id"]), effective_workspace_id)
    if not ds:
        raise HTTPException(status_code=404, detail="Datasource not found")
    return ds


@router.delete("/{datasource_id}")
def delete_datasource(datasource_id: int, request: Request, user=Depends(get_current_user), ctx=Depends(get_org_context)):
    effective_workspace_id = _resolve_workspace_id(request, None)
    deleted = store.delete_data_source_scoped(datasource_id, int(ctx["org_id"]), effective_workspace_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Datasource not found")
    return {"deleted": True}


@router.get("/{datasource_id}/schema")
def get_schema(
    datasource_id: int,
    request: Request,
    database: Optional[str] = Query(default=None),
    schema: Optional[str] = Query(default="public"),
    force_refresh: bool = Query(default=False),
    user=Depends(get_current_user),
    ctx=Depends(get_org_context),
):
    effective_workspace_id = _resolve_workspace_id(request, None)
    ds = store.get_data_source_scoped(datasource_id, int(ctx["org_id"]), effective_workspace_id)
    if not ds:
        raise HTTPException(status_code=404, detail="Datasource not found")

    if not force_refresh and ds.get("schema_cache"):
        return {
            "datasource_id": datasource_id,
            "cached": True,
            "schema": ds.get("schema_cache"),
        }

    platform = ds.get("platform") or ds.get("type")
    if platform != "snowflake":
        return {
            "datasource_id": datasource_id,
            "cached": False,
            "schema": {},
            "detail": f"Schema discovery for {platform} is coming soon",
        }

    from backend.datasources.drivers.snowflake_driver import SnowflakeDriver

    config = ds.get("config") or {}
    credentials = ds.get("credentials") or {}

    driver = SnowflakeDriver(
        {
            "user": credentials.get("user") or config.get("username"),
            "password": credentials.get("password"),
            "account": credentials.get("account") or config.get("account"),
            "warehouse": credentials.get("warehouse") or config.get("warehouse"),
            "database": database or credentials.get("database") or config.get("database"),
            "schema": schema or credentials.get("schema") or config.get("schema") or "public",
            "role": credentials.get("role") or config.get("role"),
        }
    )

    if not driver.connect():
        raise HTTPException(status_code=400, detail="Snowflake connection failed")

    try:
        target_db = database or credentials.get("database") or config.get("database")
        target_schema = schema or credentials.get("schema") or config.get("schema") or "public"
        if not target_db:
            dbs = driver.discover_databases()
            target_db = dbs[0] if dbs else ""
        discovered = driver.discover_schema(target_db, target_schema)
        store.update_data_source_schema_cache(datasource_id, discovered)
        store.cache_schema_snapshot(datasource_id, discovered)
        return {"datasource_id": datasource_id, "cached": False, "schema": discovered}
    finally:
        driver.disconnect()


@router.get("/models")
def list_semantic_models(
    request: Request,
    workspace_id: Optional[int] = Query(default=None),
    datasource_id: Optional[int] = Query(default=None),
    user=Depends(get_current_user),
):
    effective_workspace_id = _resolve_workspace_id(request, workspace_id)
    return store.list_semantic_models(effective_workspace_id, datasource_id)


@router.post("/models")
def create_semantic_model(
    request: Request,
    req: CreateSemanticModelRequest,
    workspace_id: Optional[int] = Query(default=None),
    user=Depends(get_current_user),
):
    effective_workspace_id = _resolve_workspace_id(request, workspace_id)
    return store.create_semantic_model(
        workspace_id=effective_workspace_id,
        datasource_id=req.datasource_id,
        name=req.name,
        description=req.description or "",
        definition=req.definition,
    )


@router.get("/models/{model_id}")
def get_semantic_model(model_id: int, user=Depends(get_current_user)):
    model = store.get_semantic_model(model_id)
    if not model:
        raise HTTPException(status_code=404, detail="Semantic model not found")
    return model


@router.patch("/models/{model_id}")
def update_semantic_model(model_id: int, req: UpdateSemanticModelRequest, user=Depends(get_current_user)):
    model = store.update_semantic_model(
        model_id=model_id,
        name=req.name,
        description=req.description,
        definition=req.definition,
    )
    if not model:
        raise HTTPException(status_code=404, detail="Semantic model not found")
    return model


@router.delete("/models/{model_id}")
def delete_semantic_model(model_id: int, user=Depends(get_current_user)):
    deleted = store.delete_semantic_model(model_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Semantic model not found")
    return {"deleted": True}

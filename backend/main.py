# Load environment variables from .env file FIRST (before any other imports)
import os
from pathlib import Path
from dotenv import load_dotenv
import logging

env_path = Path(__file__).parent.parent / '.env'
if env_path.exists():
    load_dotenv(env_path)
    print(f"[OK] Loaded environment variables from {env_path}")
else:
    print(f"[WARN] No .env file found at {env_path}")

# NOW import backend modules that depend on environment variables
from fastapi import FastAPI
from fastapi import Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from jose import jwt
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from backend.api.query import router as query_router
from backend.api.scanner import router as scanner_router
from backend.api.auth import router as auth_router
from backend.api.admin import router as admin_router
from backend.api.metrics import router as metrics_router
from backend.api.simulate import router as simulate_router
from backend.api.approval import router as approval_router
from backend.api.inspector import router as inspector_router
from backend.api.policies import router as policies_router
from backend.api.schema import router as schema_router
from backend.api.organizations import router as organizations_router
from backend.datasources.router import router as datasources_router
from backend.api.agents import router as agents_router
from backend.api.platform import router as platform_router
from backend.api.insights import router as insights_router
from backend.api.agent import router as agent_router
from backend.agents import agent_scheduler
from backend.services.rbac import normalize_role
from backend.workers.query_worker import start_worker_thread
from backend.services.auth import SECRET_KEY, ALGORITHM
from backend.services.rate_limiter import limiter
from backend.db.org_store import init_db as init_org_db
import backend.db.org_store as org_store


logger = logging.getLogger(__name__)


app = FastAPI(
    title="VoxCore API",
    description="AI Data Governance and SQL Risk Engine",
    version="1.0"
)

init_org_db()

# Enable CORS to allow frontend requests from voxcore.org
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "https://voxcore.org",
        "https://www.voxcore.org",
        "https://voxquery-api.onrender.com",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


@app.middleware("http")
async def enforce_jwt_for_api(request: Request, call_next):
    """Require Bearer JWT on all /api/v1/* routes except /api/v1/auth/* and preflight."""
    path = request.url.path
    if request.method == "OPTIONS":
        return await call_next(request)

    if path == "/api/v1/health":
        return await call_next(request)

    # Playground & sandbox routes are public — no auth required
    _PUBLIC_PREFIXES = (
        "/api/v1/playground/",
        "/api/v1/query/sandbox",
        "/api/v1/query/risk",
    )
    if any(path.startswith(p) for p in _PUBLIC_PREFIXES):
        return await call_next(request)

    if path.startswith("/api/v1/") and not path.startswith("/api/v1/auth/"):
        header = request.headers.get("Authorization", "")
        if not header.startswith("Bearer "):
            return JSONResponse(status_code=401, content={"detail": "Missing bearer token"})
        token = header.split(" ", 1)[1].strip()
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        except Exception:
            return JSONResponse(status_code=401, content={"detail": "Invalid token"})

        user_id = int(payload.get("user_id", 0) or 0)
        org_id = int(payload.get("org_id", payload.get("company_id", 1)) or 1)
        role = normalize_role(str(payload.get("role", "viewer")))
        token_workspace_id = payload.get("workspace_id")
        requested_workspace = request.headers.get("X-Workspace-ID")

        if requested_workspace:
            try:
                workspace_id = int(requested_workspace)
            except ValueError:
                return JSONResponse(status_code=400, content={"detail": "Invalid X-Workspace-ID header"})
        elif token_workspace_id is not None:
            workspace_id = int(token_workspace_id)
        else:
            fallback = org_store.get_default_workspace(org_id)
            workspace_id = int((fallback or {}).get("id", 1))

        if role not in {"god", "platform_owner"}:
            workspace = org_store.get_workspace(workspace_id)
            if not workspace or int(workspace.get("org_id", -1)) != org_id:
                return JSONResponse(status_code=403, content={"detail": "Workspace is outside your organization"})
            if user_id and not org_store.user_has_workspace_access(user_id, workspace_id):
                return JSONResponse(status_code=403, content={"detail": "Workspace access denied"})

        request.state.user_id = user_id
        request.state.user_email = payload.get("email")
        request.state.org_id = org_id
        request.state.role = role
        request.state.is_super_admin = bool(payload.get("is_super_admin", False))
        request.state.workspace_id = workspace_id
        request.state.datasource_id = request.headers.get("X-Datasource-ID")

    return await call_next(request)


# Root endpoint
@app.get("/")
def root():
    return {
        "service": "VoxCore",
        "status": "running",
        "description": "AI SQL Governance Engine"
    }


# Health check endpoint
@app.get("/health")
def health():
    return {
        "status": "ok",
        "service": "voxcore-api"
    }


@app.get("/api/v1/health")
def api_health():
    return {
        "status": "ok",
        "service": "voxcore-api"
    }


# Include API routes BEFORE static files
app.include_router(auth_router)
app.include_router(admin_router)
app.include_router(query_router)
app.include_router(scanner_router)
app.include_router(metrics_router)
app.include_router(simulate_router)
app.include_router(approval_router)
app.include_router(inspector_router)
app.include_router(policies_router)
app.include_router(schema_router)
app.include_router(organizations_router)
app.include_router(datasources_router)
app.include_router(agents_router)
app.include_router(platform_router)
app.include_router(insights_router)
app.include_router(
    __import__('backend.api.agent', fromlist=['router']).router
)


def _autostart_query_worker_enabled() -> bool:
    raw_value = os.environ.get("VOXCORE_AUTOSTART_QUERY_WORKER", "false").strip().lower()
    return raw_value in {"1", "true", "yes", "on"}


@app.on_event("startup")
async def start_agent_scheduler():
    """Start AI Data Agents background scheduler on server boot."""
    agent_scheduler.start()
    if _autostart_query_worker_enabled():
        start_worker_thread()
        logger.info("Started background query worker thread")


@app.on_event("shutdown")
async def stop_agent_scheduler():
    """Cleanly stop the agent scheduler on server shutdown."""
    agent_scheduler.stop()


def _resolve_frontend_dist_path() -> Path | None:
    """Locate frontend dist across local and Render deployment layouts."""
    backend_dir = Path(__file__).resolve().parent
    env_dist = os.environ.get("FRONTEND_DIST")

    candidate_paths = [
        backend_dir.parent / "frontend" / "dist",
        backend_dir / "frontend" / "dist",
        Path("/opt/render/project/src/frontend/dist"),
    ]

    if env_dist:
        candidate_paths.insert(0, Path(env_dist).expanduser())

    for candidate in candidate_paths:
        if candidate.exists() and candidate.is_dir():
            return candidate

    logger.warning(
        "Frontend dist directory not found. Checked paths: %s",
        ", ".join(str(path) for path in candidate_paths),
    )
    return None


# Serve React frontend from dist folder
frontend_dist = _resolve_frontend_dist_path()
if frontend_dist:
    app.mount("/", StaticFiles(directory=str(frontend_dist), html=True), name="static")
    logger.info("Frontend mounted from: %s", frontend_dist)


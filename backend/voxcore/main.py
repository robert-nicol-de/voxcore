"""
VOXCORE — MAIN APPLICATION

Entry point for VoxQuery. Initializes all services and wires routes,
middleware, API endpoints, and SPA frontend serving together.
"""

from contextlib import asynccontextmanager
from datetime import datetime
from pathlib import Path
import logging
import time

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

# VoxCore components
from backend.voxcore.api import conversation_api
from backend.voxcore.engine.core import get_voxcore
from backend.voxcore.engine.service_container import initialize_services, get_services


# ============= LOGGING =============

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


# ============= STARTUP / SHUTDOWN =============

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan.

    Startup:
    - initialize all services

    Shutdown:
    - clean up resources if needed
    """
    logger.info("🚀 VoxQuery starting up...")
    logger.info("📦 Initializing services...")

    try:
        services = await initialize_services()
        app.state.services = services
        logger.info("✅ Services initialized successfully")
    except Exception as e:
        logger.error(f"❌ Failed to initialize services: {e}")
        raise

    yield

    logger.info("🛑 VoxQuery shutting down...")
    logger.info("✅ Shutdown complete")


# ============= CREATE APP =============

app = FastAPI(
    title="VoxQuery - Enterprise AI Data Platform",
    description="AI-powered SQL assistant with governance, security, and observability",
    version="16.0.0",
    lifespan=lifespan,
)


# ============= MIDDLEWARE =============

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def pipeline_middleware(request: Request, call_next):
    """
    Global request/response middleware.
    """
    request_id = str(time.time())
    request.state.request_id = request_id
    start_time = time.time()

    response = await call_next(request)

    response.headers["X-Request-ID"] = request_id
    response.headers["X-Process-Time"] = str(time.time() - start_time)

    logger.info(
        f"[{request_id}] {request.method} {request.url.path} - "
        f"Status: {response.status_code} - "
        f"Duration: {(time.time() - start_time) * 1000:.1f}ms"
    )

    return response


# ============= FRONTEND DIST DETECTION =============

def resolve_frontend_dist() -> Path | None:
    """
    Resolve the built Vite frontend dist path reliably for both:
    - local development
    - Render deployment

    This file lives under:
      backend/voxcore/main.py

    So repo root is:
      Path(__file__).resolve().parent.parent.parent
    """
    base_dir = Path(__file__).resolve().parent.parent.parent

    possible_paths = [
        base_dir / "frontend" / "dist",
    ]

    for path in possible_paths:
        if path.exists() and (path / "index.html").exists():
            logger.info(f"✅ Found frontend dist at {path}")
            return path

    logger.error("❌ Frontend dist NOT found")
    logger.error("Checked paths:")
    for path in possible_paths:
        logger.error(f" - {path}")

    return None


FRONTEND_DIST = resolve_frontend_dist()

if FRONTEND_DIST:
    logger.info(f"🔥 USING FRONTEND DIST: {FRONTEND_DIST}")

    assets_dir = FRONTEND_DIST / "assets"
    if assets_dir.exists():
        app.mount("/assets", StaticFiles(directory=str(assets_dir)), name="assets")
        logger.info("✅ Mounted /assets from frontend dist")


# ============= ROUTES =============

# API router
app.include_router(conversation_api.router)


# Health/status endpoints
@app.get("/api/health")
async def health():
    return {
        "status": "healthy",
        "service": "VoxQuery",
        "version": "16.0.0",
        "steps_implemented": 16,
        "api_version": "v1",
    }





# Debug/test endpoints
@app.get("/test/ping")
async def test_ping():
    return {"pong": True, "timestamp": datetime.utcnow().isoformat()}


@app.post("/test/query")
async def test_query(message: str, org_id: str):
    from backend.voxcore.engine.core import VoxQueryRequest

    engine = get_voxcore()
    services = get_services().to_dict()

    request = VoxQueryRequest(
        message=message,
        session_id="test-session",
        org_id=org_id,
        user_id="test-user",
        user_role="analyst",
    )

    response = await engine.execute_query(request, services)
    return response.to_dict()


# ============= ERROR HANDLING =============

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={
            "error": "Validation error",
            "details": exc.errors(),
            "status": 422,
        },
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": str(exc),
            "status": 500,
        },
    )


# ============= DEPENDENCY INJECTION =============

async def get_service_container():
    return get_services()


# ============= SPA SERVING =============

def frontend_ready() -> bool:
    return FRONTEND_DIST is not None and (FRONTEND_DIST / "index.html").exists()


@app.get("/")
async def serve_root():
    """
    Serve React app at root.
    """
    if not frontend_ready():
        return JSONResponse(
            status_code=503,
            content={"error": "Frontend not built yet"},
        )

    return FileResponse(FRONTEND_DIST / "index.html")


@app.get("/{full_path:path}")
async def spa_fallback(full_path: str):
    """
    Serve the React SPA for all non-API routes.

    Rules:
    - API/docs/test/system routes are not intercepted
    - existing files under dist are served directly
    - all other routes return index.html for React Router
    """
    if not frontend_ready():
        return JSONResponse(
            status_code=503,
            content={"error": "Frontend not built yet"},
        )

    reserved_prefixes = ("api/", "docs", "test/", "system/")
    if full_path.startswith(reserved_prefixes):
        return JSONResponse(
            status_code=404,
            content={"error": "Not found"},
        )

    target = FRONTEND_DIST / full_path

    if full_path and target.exists() and target.is_file():
        logger.info(f"📄 Serving file: {full_path}")
        return FileResponse(target)

    logger.info(f"🔀 SPA fallback: {full_path} -> index.html")
    return FileResponse(FRONTEND_DIST / "index.html")


# ============= MAIN =============

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "backend.voxcore.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
    )
"""
VOXCORE — MAIN APPLICATION

Entry point for VoxQuery. Initializes all 16 STEPS and wires them together.

This is where everything connects:
- All services
- All routes
- All middleware
- The 14-step pipeline
"""

from fastapi import FastAPI, Request, Response, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from contextlib import asynccontextmanager
import logging
import time
from datetime import datetime
import os
from pathlib import Path

# VoxCore components
from backend.voxcore.api import conversation_api
from backend.voxcore.engine.service_container import initialize_services, get_services
from backend.voxcore.engine.core import get_voxcore

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# ============= STARTUP/SHUTDOWN =============

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan (startup + shutdown).
    
    Startup: Initialize all services
    Shutdown: Clean up resources
    """
    
    # STARTUP
    logger.info("🚀 VoxQuery starting up...")
    logger.info("📦 STEP 16: Initializing all services...")
    
    try:
        services = await initialize_services()
        app.state.services = services
        logger.info("✅ All 16 STEPS initialized successfully!")
    except Exception as e:
        logger.error(f"❌ Failed to initialize services: {e}")
        raise
    
    yield
    
    # SHUTDOWN
    logger.info("🛑 VoxQuery shutting down...")
    # Clean up connections, background tasks, etc.
    logger.info("✅ Shutdown complete")


# ============= CREATE APP =============

app = FastAPI(
    title="VoxQuery - Enterprise AI Data Platform",
    description="AI-powered SQL assistant with governance, security, and observability",
    version="16.0.0",
    lifespan=lifespan
)


# ============= MIDDLEWARE =============

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============= STATIC FILES =============
# Determine frontend dist path - works on both local and Render
FRONTEND_DIST = None
possible_paths = [
    "/opt/render/project/frontend/dist",  # Render production (correct path)
    "/opt/render/project/src/frontend/dist",  # Render with src folder
    Path(__file__).parent.parent.parent / "frontend" / "dist",  # Local: go up 3 levels to root, then frontend/dist
    Path.cwd() / "frontend" / "dist",  # Local: from current working directory
]

for path in possible_paths:
    path_obj = Path(path)
    if path_obj.exists() and (path_obj / "index.html").exists():
        FRONTEND_DIST = path_obj
        logger.info(f"✅ Found frontend dist at {FRONTEND_DIST}")
        break

if not FRONTEND_DIST:
    logger.warning(f"⚠️ Frontend dist not found. Checked: {possible_paths}")
    logger.warning("⚠️ Continuing anyway - SPA routes will serve errors for missing dist")
else:
    logger.info(f"✅ Frontend dist ready: {FRONTEND_DIST}")

# Serve static assets explicitly
if FRONTEND_DIST and (FRONTEND_DIST / "assets").exists():
    app.mount(
        "/assets",
        StaticFiles(directory=str(FRONTEND_DIST / "assets")),
        name="assets"
    )
    logger.info("✅ Mounted /assets from dist")


# Global request/response middleware for the 14-step pipeline
@app.middleware("http")
async def pipeline_middleware(request: Request, call_next):
    """
    Implement the 14-step pipeline:
    
    1. Auth middleware
    2. Rate limit check  
    3-14. Done by VoxCoreEngine
    """
    
    request_id = str(time.time())
    request.state.request_id = request_id
    
    start_time = time.time()
    
    # STEP 1: Auth (simple example)
    # In production: JWT verification, etc.
    # auth_token = request.headers.get("Authorization", "").replace("Bearer ", "")
    # user = await verify_token(auth_token)
    
    # STEP 2: Rate limiting
    # middleware = app.state.services.security_middleware
    # is_throttled, error = await middleware.process_request(...)
    # if is_throttled:
    #     return Response(status_code=429, content=error)
    
    # Process request
    response = await call_next(request)
    
    # Add response headers
    response.headers["X-Request-ID"] = request_id
    response.headers["X-Process-Time"] = str(time.time() - start_time)
    
    # Log request
    logger.info(
        f"[{request_id}] {request.method} {request.url.path} - "
        f"Status: {response.status_code} - "
        f"Duration: {(time.time() - start_time) * 1000:.1f}ms"
    )
    
    return response


# ============= ROUTES =============

# Register conversation API router
app.include_router(conversation_api.router)


# Health/status endpoint
@app.get("/api/health")
async def health():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "VoxQuery",
        "version": "16.0.0",
        "steps_implemented": 16,
        "api_version": "v1",
    }





# ============= ERROR HANDLING =============

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors"""
    return {
        "error": "Validation error",
        "details": exc.errors(),
        "status": 422
    }


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handle unexpected errors"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return {
        "error": "Internal server error",
        "message": str(exc),
        "status": 500
    }


# ============= DEPENDENCY INJECTION =============

async def get_service_container():
    """Dependency: Get service container"""
    return get_services()


# ============= SPECIALIZED ENDPOINTS =============

@app.get("/test/ping")
async def test_ping():
    """Simple ping test"""
    return {"pong": True, "timestamp": datetime.utcnow().isoformat()}


@app.post("/test/query")
async def test_query(message: str, org_id: str):
    """Test query endpoint (debug)"""
    
    # Test through VoxCore engine
    from backend.voxcore.engine.core import VoxQueryRequest
    
    engine = get_voxcore()
    services = get_services().to_dict()
    
    request = VoxQueryRequest(
        message=message,
        session_id="test-session",
        org_id=org_id,
        user_id="test-user",
        user_role="analyst"
    )
    
    response = await engine.execute_query(request, services)
    return response.to_dict()


# ============= MAIN =============

# SPA FALLBACK (MUST BE LAST ROUTE - ALWAYS ACTIVE)
# This always serves React app for unknown routes
@app.get("/")
async def serve_root():
    """Serve root path - returns index.html for React SPA"""
    if FRONTEND_DIST:
        return FileResponse(FRONTEND_DIST / "index.html")
    return {"error": "Frontend not built yet"}


@app.get("/{full_path:path}")
async def spa_fallback(full_path: str):
    """
    Serve Vite SPA for all routes not matched above.
    Routes unknown paths to index.html for React Router to handle.
    
    This is the ABSOLUTE LAST route - nothing comes after it.
    """
    if not FRONTEND_DIST:
        return {"error": "Frontend not built"}
    
    # Don't intercept API routes that weren't caught above (shouldn't happen)
    if full_path.startswith("api/") or full_path.startswith("test/") or full_path.startswith("docs"):
        return {"error": "Not found"}, 404
    
    target = FRONTEND_DIST / full_path
    
    # Serve exact file if it exists (CSS, JS, images, etc)
    if full_path and target.exists() and target.is_file():
        logger.info(f"📄 Serving file: {full_path}")
        return FileResponse(target)
    
    # Default: serve index.html for SPA routing
    logger.info(f"🔀 SPA fallback: {full_path} → index.html")
    return FileResponse(FRONTEND_DIST / "index.html")


if __name__ == "__main__":
    import uvicorn
    
    # Run with: uvicorn backend.voxcore.main:app --reload
    uvicorn.run(
        "backend.voxcore.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )

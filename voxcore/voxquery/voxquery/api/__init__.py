"""FastAPI REST API for VoxQuery"""

__all__ = ["app"]

import logging
import os
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, RedirectResponse, FileResponse
from fastapi.exceptions import RequestValidationError
from fastapi.staticfiles import StaticFiles

from . import health, query, schema, auth, connection, metrics, governance, firewall, connectors
from .models import init_db

logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="VoxQuery API",
    description="Turn business questions into SQL",
    version="0.1.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve static files from frontend public folder (marketing site)
frontend_public = os.path.join(os.path.dirname(__file__), "../../../../frontend/public")
frontend_public = os.path.abspath(frontend_public)  # Normalize the path
if os.path.exists(frontend_public):
    # Mount styles folder if it exists
    styles_dir = os.path.join(frontend_public, "styles")
    if os.path.exists(styles_dir):
        app.mount("/styles", StaticFiles(directory=styles_dir), name="styles")
    # Mount images folder if it exists
    images_dir = os.path.join(frontend_public, "images")
    if os.path.exists(images_dir):
        app.mount("/images", StaticFiles(directory=images_dir), name="images")
    logger.info(f"✅ Marketing site static files mounted from {frontend_public}")
else:
    logger.warning(f"⚠️  Frontend public folder not found at {frontend_public}")

# Serve built React SPA from frontend/dist/ (the actual app)
frontend_dist = os.path.join(os.path.dirname(__file__), "../../../../frontend/dist")
frontend_dist = os.path.abspath(frontend_dist)
if os.path.exists(frontend_dist):
    # Mount the assets folder for JS/CSS bundles
    assets_dir = os.path.join(frontend_dist, "assets")
    if os.path.exists(assets_dir):
        app.mount("/assets", StaticFiles(directory=assets_dir), name="spa-assets")
    logger.info(f"✅ React SPA static files mounted from {frontend_dist}")
else:
    logger.warning(f"⚠️  Frontend dist folder not found at {frontend_dist}")

# Root endpoint - serve marketing home page
@app.api_route("/", methods=["GET", "HEAD"], include_in_schema=False)
def root():
    """Root endpoint - serve marketing home page"""
    frontend_index = os.path.join(frontend_public, "index.html")
    if os.path.exists(frontend_index):
        return FileResponse(frontend_index, media_type="text/html")
    # Fallback to API docs if marketing site not available
    return RedirectResponse(url="/docs")


# Include routers
app.include_router(health.router, tags=["Health"])
app.include_router(connection.router, prefix="/api/v1", tags=["Connection"])
app.include_router(query.router, prefix="/api/v1", tags=["Query"])
app.include_router(schema.router, prefix="/api/v1", tags=["Schema"])
app.include_router(auth.router, prefix="/api/v1", tags=["Auth"])
app.include_router(connectors.router, prefix="/api/v1", tags=["Connectors"])
app.include_router(metrics.router, tags=["Metrics"])
app.include_router(governance.router, tags=["Governance"])
app.include_router(firewall.router, prefix="/api/v1/firewall", tags=["Firewall"])

# /app route - serve the React SPA (demo mode, login, full app)
@app.get("/app")
def serve_app():
    """Serve the React SPA for /app (handles demo mode, login, etc.)"""
    spa_index = os.path.join(frontend_dist, "index.html")
    if os.path.exists(spa_index):
        return FileResponse(spa_index, media_type="text/html")
    # Fallback to landing page
    frontend_index = os.path.join(frontend_public, "index.html")
    if os.path.exists(frontend_index):
        return FileResponse(frontend_index, media_type="text/html")
    return JSONResponse(status_code=404, content={"detail": "React SPA not built. Run npm run build in frontend/"})

# SPA catch-all route - serve marketing pages from public folder
@app.get("/{full_path:path}")
def spa_catchall(full_path: str):
    """Catch-all route - serves pages from public folder, or React SPA for /app sub-routes"""
    
    # Don't intercept API calls
    if full_path.startswith("api/"):
        return JSONResponse(status_code=404, content={"detail": "Not Found"})
    
    # Serve React SPA for /app and any sub-routes
    if full_path == "app" or full_path.startswith("app/"):
        spa_index = os.path.join(frontend_dist, "index.html")
        if os.path.exists(spa_index):
            return FileResponse(spa_index, media_type="text/html")
    
    # Try exact file match in public folder
    requested_file = os.path.join(frontend_public, full_path)
    requested_file = os.path.abspath(requested_file)
    
    # Security: make sure the file is within frontend_public
    if os.path.commonpath([requested_file, frontend_public]) == frontend_public:
        if os.path.isfile(requested_file):
            return FileResponse(requested_file, media_type="text/html")
    
    # Try with .html extension (e.g., /about → about.html)
    html_file = os.path.join(frontend_public, f"{full_path}.html")
    html_file = os.path.abspath(html_file)
    
    if os.path.commonpath([html_file, frontend_public]) == frontend_public:
        if os.path.isfile(html_file):
            return FileResponse(html_file, media_type="text/html")
    
    # For unknown routes, serve the landing page
    frontend_index = os.path.join(frontend_public, "index.html")
    if os.path.exists(frontend_index):
        return FileResponse(frontend_index, media_type="text/html")
    
    return JSONResponse(status_code=404, content={"detail": "Not Found"})

# Exception handler for validation errors
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle Pydantic validation errors with detailed logging"""
    logger.error(f"Validation error on {request.url.path}:")
    for error in exc.errors():
        logger.error(f"  - {error['loc']}: {error['msg']}")
    
    return JSONResponse(
        status_code=422,
        content={
            "detail": exc.errors(),
            "body": str(exc.body) if hasattr(exc, 'body') else None
        }
    )

# Global exception handler for encoding bomb prevention
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler to prevent encoding bombs"""
    try:
        # Try to safely extract exception message
        safe_exc = repr(exc)
    except:
        safe_exc = "Unknown error (encoding issue)"
    
    try:
        logger.exception(f"Global handler caught: {safe_exc}")
    except:
        logger.error("Global handler caught exception (encoding issue)")
    
    return JSONResponse(
        status_code=500,
        content={
            "status": "error",
            "message": f"Internal error: {safe_exc[:500]}"
        }
    )

@app.on_event("startup")
async def startup_event():
    """Startup event"""
    print("VoxQuery API starting up...")

    # Initialize user/company database (SQLite)
    try:
        init_db()
        print("✅ User database initialized")
    except Exception as e:
        print(f"⚠️  Could not initialize user database: {e}")

    # Initialize default engine from environment (only if credentials are provided)
    try:
        from ..settings import settings
        from .engine_manager import create_engine
        
        if settings.warehouse_type and settings.warehouse_host and settings.warehouse_user and settings.warehouse_password:
            create_engine(
                warehouse_type=settings.warehouse_type,
                warehouse_host=settings.warehouse_host,
                warehouse_user=settings.warehouse_user,
                warehouse_password=settings.warehouse_password,
                warehouse_database=settings.warehouse_database,
                auth_type="sql",
            )
            print(f"✅ Default engine initialized for {settings.warehouse_type}")
        else:
            print("ℹ️  No default database configured. User must select database on startup.")
    except Exception as e:
        print(f"⚠️  Could not initialize default engine: {str(e)}")

@app.on_event("shutdown")
async def shutdown_event():
    """Shutdown event"""
    print("VoxQuery API shutting down...")

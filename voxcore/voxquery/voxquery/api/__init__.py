"""FastAPI REST API for VoxQuery"""

__all__ = ["app"]

import logging
import os
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, RedirectResponse, FileResponse
from fastapi.exceptions import RequestValidationError
from fastapi.staticfiles import StaticFiles

from . import health, query, schema, auth, connection, metrics, governance, firewall

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

# Serve static files from frontend dist folder
frontend_dist = os.path.join(os.path.dirname(__file__), "../../../../frontend/dist")
frontend_dist = os.path.abspath(frontend_dist)  # Normalize the path
if os.path.exists(frontend_dist):
    app.mount("/assets", StaticFiles(directory=os.path.join(frontend_dist, "assets")), name="assets")
    app.mount("/styles", StaticFiles(directory=os.path.join(frontend_dist, "styles")), name="styles")
    logger.info(f"✅ Frontend static files mounted from {frontend_dist}")
else:
    logger.warning(f"⚠️  Frontend dist folder not found at {frontend_dist}")

# Root endpoint - serve frontend home page
@app.api_route("/", methods=["GET", "HEAD"], include_in_schema=False)
def root():
    """Root endpoint - serve React frontend"""
    frontend_index = os.path.join(frontend_dist, "index.html")
    if os.path.exists(frontend_index):
        return FileResponse(frontend_index)
    # Fallback to API docs if frontend not built
    return RedirectResponse(url="/docs")


# Include routers
app.include_router(health.router, tags=["Health"])
app.include_router(connection.router, prefix="/api/v1", tags=["Connection"])
app.include_router(query.router, prefix="/api/v1", tags=["Query"])
app.include_router(schema.router, prefix="/api/v1", tags=["Schema"])
app.include_router(auth.router, prefix="/api/v1", tags=["Auth"])
app.include_router(metrics.router, tags=["Metrics"])
app.include_router(governance.router, tags=["Governance"])
app.include_router(firewall.router, prefix="/api/v1/firewall", tags=["Firewall"])

# SPA catch-all route - serve index.html for client-side routing
@app.get("/{full_path:path}")
def spa_catchall(full_path: str):
    """Catch-all route for SPA - serves index.html for all unmatched routes"""
    frontend_index = os.path.join(frontend_dist, "index.html")
    if os.path.exists(frontend_index) and not full_path.startswith("api/"):
        # Don't intercept API calls
        if full_path.endswith((".js", ".css", ".png", ".jpg", ".svg", ".ico")):
            # Static assets should return 404 if not found
            return JSONResponse(status_code=404, content={"detail": "Not Found"})
        # For HTML routes (pages), serve index.html
        return FileResponse(frontend_index)
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

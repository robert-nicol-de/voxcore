"""FastAPI REST API for VoxQuery"""

__all__ = ["app"]

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from voxquery.api import health, query, schema, auth

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

# Include routers
app.include_router(health.router, tags=["Health"])
app.include_router(query.router, prefix="/api/v1", tags=["Query"])
app.include_router(schema.router, prefix="/api/v1", tags=["Schema"])
app.include_router(auth.router, prefix="/api/v1", tags=["Auth"])

@app.on_event("startup")
async def startup_event():
    """Startup event"""
    print("VoxQuery API starting up...")

@app.on_event("shutdown")
async def shutdown_event():
    """Shutdown event"""
    print("VoxQuery API shutting down...")

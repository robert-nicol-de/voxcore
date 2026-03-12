# Load environment variables from .env file FIRST (before any other imports)
import os
from pathlib import Path
from dotenv import load_dotenv

env_path = Path(__file__).parent.parent / '.env'
if env_path.exists():
    load_dotenv(env_path)
    print(f"[OK] Loaded environment variables from {env_path}")
else:
    print(f"[WARN] No .env file found at {env_path}")

# NOW import backend modules that depend on environment variables
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
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
from backend.services.rate_limiter import limiter
from backend.db.org_store import init_db as init_org_db


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
        "http://localhost:5173",
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

# Serve React frontend from dist folder
frontend_dist = os.path.join(os.path.dirname(__file__), '..', 'frontend', 'dist')
if os.path.exists(frontend_dist):
    app.mount("/", StaticFiles(directory=frontend_dist, html=True), name="static")
    print(f"Frontend mounted from: {frontend_dist}")


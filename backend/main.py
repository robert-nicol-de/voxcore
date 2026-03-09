# Load environment variables from .env file FIRST (before any other imports)
import os
from pathlib import Path
from dotenv import load_dotenv

env_path = Path(__file__).parent.parent / '.env'
if env_path.exists():
    load_dotenv(env_path)
    print(f"[✓] Loaded environment variables from {env_path}")
else:
    print(f"[⚠] No .env file found at {env_path}")

# NOW import backend modules that depend on environment variables
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from backend.api.query import router as query_router
from backend.api.scanner import router as scanner_router


app = FastAPI(
    title="VoxCore API",
    description="AI Data Governance and SQL Risk Engine",
    version="1.0"
)


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
app.include_router(query_router)
app.include_router(scanner_router)

# Serve React frontend from dist folder
frontend_dist = os.path.join(os.path.dirname(__file__), '..', 'frontend', 'dist')
if os.path.exists(frontend_dist):
    app.mount("/", StaticFiles(directory=frontend_dist, html=True), name="static")
    print(f"Frontend mounted from: {frontend_dist}")


from fastapi import FastAPI
from backend.api.query import router as query_router


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


# Include API routes
app.include_router(query_router)

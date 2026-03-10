"""Main entry point for VoxQuery API - used by uvicorn"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
import logging.handlers
from datetime import datetime
from pathlib import Path
from .v1 import auth, query
from .governance import router as governance_router
from .scanner import router as scanner_router

# Create logs directory if it doesn't exist
logs_dir = Path(__file__).parent.parent.parent / "logs"
logs_dir.mkdir(exist_ok=True)

# Setup comprehensive logging with file handlers
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Create logger
logger = logging.getLogger(__name__)

# Add file handler for LLM events
llm_log_file = logs_dir / "llm.log"
llm_handler = logging.handlers.RotatingFileHandler(
    llm_log_file,
    maxBytes=10*1024*1024,  # 10MB
    backupCount=5
)
llm_handler.setLevel(logging.INFO)
llm_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
llm_handler.setFormatter(llm_formatter)

# Add file handler for all API events
api_log_file = logs_dir / "api.log"
api_handler = logging.handlers.RotatingFileHandler(
    api_log_file,
    maxBytes=10*1024*1024,  # 10MB
    backupCount=5
)
api_handler.setLevel(logging.INFO)
api_handler.setFormatter(llm_formatter)

# Configure LLM logger to capture fallback events
llm_logger = logging.getLogger("voxquery.core.llm_fallback")
llm_logger.addHandler(llm_handler)
llm_logger.setLevel(logging.INFO)

# Configure query logger
query_logger = logging.getLogger("voxquery.api.v1.query")
query_logger.addHandler(api_handler)
query_logger.setLevel(logging.INFO)

# Configure engine logger
engine_logger = logging.getLogger("voxquery.core.engine")
engine_logger.addHandler(api_handler)
engine_logger.setLevel(logging.INFO)

logger.info(f"✓ Logging configured")
logger.info(f"  LLM events: {llm_log_file}")
logger.info(f"  API events: {api_log_file}")

# Create FastAPI app
app = FastAPI(
    title="VoxCore",
    description="Enterprise AI Governance Platform",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers from v1 modules
app.include_router(auth.router, prefix="/api/v1", tags=["auth"])
app.include_router(query.router, prefix="/api/v1", tags=["query"])
app.include_router(governance_router, prefix="/api/v1", tags=["governance"])
app.include_router(scanner_router)

# ============================================================================
# HEALTH CHECK
# ============================================================================

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.on_event("startup")
async def startup_event():
    logger.info("VoxCore API starting up...")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("VoxCore API shutting down...")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

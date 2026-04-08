"""
VoxCore Backend - Security & Middleware Layer
Handles authentication, rate limiting, CORS, and structured logging
"""

import os
import logging
from typing import Optional
from datetime import datetime
from fastapi import FastAPI, Request, HTTPException, Depends, Header, status
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import json

# ============================================================================
# CONFIGURATION
# ============================================================================

ENV = os.getenv("ENV", "development")
DEBUG = os.getenv("DEBUG", "false").lower() == "true"
LOG_LEVEL = os.getenv("LOG_LEVEL", "info").upper()
API_KEY = os.getenv("API_KEY", "dev-key-local-testing-only")
SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-not-secure")
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:5173,http://localhost:3000").split(",")
REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", "30"))
MAX_QUERIES_PER_MINUTE = int(os.getenv("MAX_QUERIES_PER_MINUTE", "60"))

# ============================================================================
# LOGGING SETUP
# ============================================================================

logging.basicConfig(
    level=LOG_LEVEL,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("voxcore")

# ============================================================================
# RATE LIMITING
# ============================================================================

limiter = Limiter(key_func=get_remote_address)

# ============================================================================
# AUTHENTICATION
# ============================================================================

def verify_api_key(x_api_key: str = Header(...)) -> str:
    """Verify API key from request headers"""
    if x_api_key != API_KEY:
        logger.warning(f"Invalid API key attempted: {x_api_key[:10]}...")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid API key"
        )
    return x_api_key

# ============================================================================
# MIDDLEWARE
# ============================================================================

async def log_request_response(request: Request, call_next):
    """Structured logging middleware"""
    start_time = datetime.utcnow()
    
    # Log incoming request
    body = ""
    if request.method in ["POST", "PUT", "PATCH"]:
        body = await request.body()
        request._body = body
    
    logger.info({
        "event": "request_received",
        "method": request.method,
        "path": request.url.path,
        "timestamp": start_time.isoformat(),
    })
    
    try:
        response = await call_next(request)
    except Exception as exc:
        logger.error({
            "event": "request_error",
            "method": request.method,
            "path": request.url.path,
            "error": str(exc),
            "timestamp": datetime.utcnow().isoformat(),
        })
        raise
    
    # Log response
    duration_ms = (datetime.utcnow() - start_time).total_seconds() * 1000
    logger.info({
        "event": "request_completed",
        "method": request.method,
        "path": request.url.path,
        "status": response.status_code,
        "duration_ms": duration_ms,
        "timestamp": datetime.utcnow().isoformat(),
    })
    
    return response

# ============================================================================
# APP INITIALIZATION
# ============================================================================

def create_app():
    """Create and configure FastAPI application"""
    app = FastAPI(
        title="VoxCore API",
        description="Enterprise SQL Governance & Risk Assessment",
        version="1.0.0",
        docs_url="/docs" if DEBUG else None,
        redoc_url="/redoc" if DEBUG else None,
    )
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[origin.strip() for origin in CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=["*"],
        max_age=3600,
    )
    
    # Add request/response logging middleware
    app.middleware("http")(log_request_response)
    
    # Add rate limiter state
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, lambda request, exc: HTTPException(
        status_code=429,
        detail="Rate limit exceeded"
    ))
    
    return app

# ============================================================================
# QUERY EXECUTION LOGGING
# ============================================================================

def log_query_execution(query_id: str, query: str, risk_score: int, status: str, 
                       user: str, environment: str, source: str, 
                       analysis_time_ms: int, confidence: float):
    """Log query execution with full context"""
    logger.info(json.dumps({
        "event": "query_execution",
        "query_id": query_id,
        "query": query[:100],  # Log first 100 chars
        "risk_score": risk_score,
        "status": status,
        "user": user,
        "environment": environment,
        "source": source,
        "analysis_time_ms": analysis_time_ms,
        "confidence": confidence,
        "timestamp": datetime.utcnow().isoformat(),
    }))

# ============================================================================
# EXPORTS
# ============================================================================

__all__ = [
    "create_app",
    "verify_api_key",
    "log_query_execution",
    "limiter",
    "logger",
    "ENV",
    "DEBUG",
]

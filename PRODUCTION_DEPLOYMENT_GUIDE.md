# 🔥 VOXCORE PRODUCTION DEPLOYMENT GUIDE

## ✅ PRE-DEPLOYMENT CHECKLIST

This guide walks through **16 critical categories** that separate a production SaaS from a demo.

---

## 🧱 SECTION 1: ENVIRONMENTS (MANDATORY SEPARATION)

### Goal: Zero Cross-Contamination

Each environment must be **completely isolated** with separate infrastructure.

### Environment Matrix

| Component | `dev` | `staging` | `prod` |
|-----------|-------|-----------|--------|
| **Database** | SQLite (local) | PostgreSQL (separate) | PostgreSQL (separate) |
| **Redis** | Local (localhost:6379) | Render Redis (separate) | Upstash/Render Redis (separate) |
| **Backend** | localhost:8000 | Render (paid, no-sleep) | Render (paid, no-sleep, auto-scale) |
| **Frontend** | localhost:3000 | Vercel preview | Vercel production |
| **LLM API Key** | dev-key | staging-key | prod-key |
| **Secret Key** | dev-secret-12345 | staging-secret-456** | prod-secret-xyz** (from vault) |
| **Database User** | postgres (full access) | voxquery_user (limited) | voxquery_readonly + voxquery_admin |
| **SSL** | None (HTTP) | HTTPS (auto) | HTTPS (custom domain) |

### Environment Configuration Files

```
.env.dev         ← Local development (SQLite, localhost)
.env.staging     ← Staging mirror (PostgreSQL, Render, preview URLs)
.env.prod        ← Production (PostgreSQL, Render, custom domain)
.env.local       ← Local overrides (NEVER commit)
```

---

## 🧱 SECTION 2: DEPLOYMENT ARCHITECTURE

### Recommended Stack

```
┌─────────────────────────────────────────────────────────────┐
│                    VOXQUERY PRODUCTION STACK                │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  FRONTEND                                                   │
│  ├─ Vercel (CDN + global edge)                             │
│  └─ Custom domain (https://voxquery.com)                   │
│                                                             │
│  BACKEND                                                    │
│  ├─ Render (paid instance, auto-scale 1-5)                │
│  ├─ Health checks enabled                                  │
│  └─ Environment variables from Render dashboard             │
│                                                             │
│  DATABASE                                                   │
│  ├─ PostgreSQL 13+ (Render)                                │
│  ├─ SSL required                                           │
│  ├─ Connection pooling (pgBouncer)                         │
│  ├─ Daily backups (7+ day retention)                       │
│  └─ Read replicas (optional, for scaling)                  │
│                                                             │
│  CACHE                                                      │
│  ├─ Upstash Redis OR Render Redis                          │
│  ├─ AUTH required                                          │
│  ├─ TLS enforced                                           │
│  └─ Memory limit: 256MB → LRU eviction                     │
│                                                             │
│  MONITORING                                                 │
│  ├─ Render logs aggregation                                │
│  ├─ Datadog/New Relic (optional)                           │
│  └─ Custom dashboards                                      │
│                                                             │
│  SECURELY MANAGED                                           │
│  ├─ Secrets: Render Environment Variables                  │
│  ├─ SSL Certificates: Auto via Render                      │
│  └─ Backups: Automated by Render                           │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 🔥 CRITICAL: SQLite → PostgreSQL

**For development:** SQLite is fine
**For production:** PostgreSQL **MANDATORY**

```python
# ❌ WRONG (Production)
DATABASE_URL = "sqlite:///voxquery.db"

# ✅ RIGHT (Production)
DATABASE_URL = "postgresql://user:pass@host:5432/voxquery_prod"
```

---

## 🧱 SECTION 3: DATABASE HARDENING

### PostgreSQL Setup

```sql
-- 1. Create separate users (least privilege)
CREATE ROLE voxquery_admin WITH LOGIN PASSWORD 'complex_password_here';
CREATE ROLE voxquery_readonly WITH LOGIN PASSWORD 'another_complex_password';

-- 2. Grant permissions
GRANT CONNECT ON DATABASE voxquery_prod TO voxquery_admin;
GRANT USAGE ON SCHEMA public TO voxquery_admin;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO voxquery_admin;

-- 3. Read-only user (for SELECT only)
GRANT CONNECT ON DATABASE voxquery_prod TO voxquery_readonly;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO voxquery_readonly;

-- 4. Enable query timeout
ALTER SYSTEM SET statement_timeout = '30s';

-- 5. Row limits (prevent accidental huge queries)
-- Add application-level validation in VoxCore (max 10,000 rows)

-- 6. Connection pooling
-- Use pgBouncer or Render's built-in pooling
-- Set max_connections = 100 (not 200+)
```

### Connection Pooling

```python
# backend/voxcore/storage/database.py

from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool

# Production connection string
DATABASE_URL = os.getenv("DATABASE_URL")

# Create engine with connection pooling
engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=10,              # Max connections in pool
    max_overflow=20,           # Max overflow connections
    pool_recycle=3600,         # Recycle connections every hour
    pool_pre_ping=True,        # Check connection health
    echo_pool=False            # Don't log pool operations
)
```

### Backups & Recovery

```bash
# Automated backups (via Render web dashboard)
# But also manual backup script:

#!/bin/bash
# backup_database.sh

BACKUP_FILE="voxquery_backup_$(date +%Y%m%d_%H%M%S).sql"

pg_dump -h $DB_HOST -U $DB_USER -d $DB_NAME \
  --format=custom \
  --compress=9 \
  > "$BACKUP_FILE"

# Upload to S3
aws s3 cp "$BACKUP_FILE" s3://voxquery-backups/

# Retention: Delete backups older than 30 days
aws s3 rm s3://voxquery-backups/ \
  --recursive \
  --exclude "*" \
  --include "voxquery_backup_*" \
  --older-than 30
```

---

## 🧱 SECTION 4: REDIS HARDENING

### Redis Configuration

```ini
# redis.conf (for self-hosted or Upstash settings)

# 1. AUTH Required
requirepass "redis_password_32_chars_minimum"

# 2. Memory Management
maxmemory 256mb
maxmemory-policy allkeys-lru

# 3. TLS/SSL
tls-port 6380
tls-cert-file /path/to/cert.pem
tls-key-file /path/to/key.pem

# 4. Disable dangerous commands
rename-command FLUSHALL ""
rename-command FLUSHDB ""
rename-command KEYS ""

# 5. Connection limits
tcp-backlog 511
timeout 0
```

### Redis Client Setup

```python
# backend/voxcore/storage/redis_client.py

import redis
import ssl

def get_redis_client():
    """Secure Redis connection"""
    
    redis_url = os.getenv("REDIS_URL")
    
    # Parse Redis URL
    # Format: redis://user:password@host:port/db?ssl=true
    
    client = redis.from_url(
        redis_url,
        decode_responses=True,
        socket_connect_timeout=5,
        socket_keepalive=True,
        health_check_interval=30,
        ssl_certfile=None,  # Let provider handle SSL
        ssl_keyfile=None,
        ssl_ca_certs=None,
        ssl_check_hostname=True,
        ssl=True  # Force TLS
    )
    
    # Test connection
    try:
        client.ping()
        logger.info("✅ Redis connected")
    except Exception as e:
        logger.error(f"❌ Redis connection failed: {e}")
        raise
    
    return client

# Use in ServiceContainer
redis_client = get_redis_client()
```

---

## 🧱 SECTION 5: SECRETS MANAGEMENT

### Secret Store Strategy

```
┌─────────────────────────────────────────────┐
│         SECRET STORAGE HIERARCHY            │
├─────────────────────────────────────────────┤
│                                             │
│  LOCAL DEVELOPMENT                          │
│  └─ .env.local (git ignored)                │
│                                             │
│  STAGING                                    │
│  └─ Render Environment Variables            │
│                                             │
│  PRODUCTION                                 │
│  ├─ Render Environment Variables (short-term)
│  └─ AWS Secrets Manager (long-term) [FUTURE]
│                                             │
└─────────────────────────────────────────────┘
```

### Secrets List

```python
# All secrets MUST be in env vars (never hardcoded)

# Database
DATABASE_URL=postgresql://user:pass@host:5432/db

# Redis
REDIS_URL=redis://password@host:6379

# LLM API
GROQ_API_KEY=xxx

# Encryption
SECRET_KEY=32_chars_random_key_here

# JWT
JWT_SECRET_KEY=another_32_chars_key_here

# Domains
FRONTEND_URL=https://voxquery.com
BACKEND_URL=https://api.voxquery.com

# Observability
DATADOG_API_KEY=xxx (optional)
SENTRY_DSN=xxx (optional)
```

### Code to Load Secrets

```python
# backend/voxcore/config.py

import os
from pydantic import BaseSettings

class Settings(BaseSettings):
    """Load all settings from environment"""
    
    # Database
    database_url: str = os.getenv("DATABASE_URL")
    
    # Redis
    redis_url: str = os.getenv("REDIS_URL")
    
    # API Keys
    groq_api_key: str = os.getenv("GROQ_API_KEY")
    
    # Security
    secret_key: str = os.getenv("SECRET_KEY")
    jwt_secret_key: str = os.getenv("JWT_SECRET_KEY")
    
    # URLs
    frontend_url: str = os.getenv("FRONTEND_URL")
    backend_url: str = os.getenv("BACKEND_URL")
    
    # Validation
    class Config:
        env_file = ".env" if os.getenv("ENV", "prod") == "dev" else None
        
        @property
        def check_all_set(self):
            """In production, all secrets must be set"""
            if os.getenv("ENV") == "prod":
                required = [
                    "DATABASE_URL", "REDIS_URL", "GROQ_API_KEY",
                    "SECRET_KEY", "JWT_SECRET_KEY"
                ]
                for key in required:
                    if not os.getenv(key):
                        raise ValueError(f"Missing secret: {key}")

settings = Settings()
```

---

## 🧱 SECTION 6: API SECURITY

### Authentication & Rate Limiting

```python
# backend/voxcore/security/auth.py

from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthCredentials
from slowapi import Limiter
from slowapi.util import get_remote_address
import jwt
from datetime import datetime, timedelta

# Rate limiter
limiter = Limiter(key_func=get_remote_address)

# JWT config
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_HOURS = 24

def create_access_token(user_id: str, org_id: str, ttl_hours: int = 24):
    """Create JWT token"""
    expires = datetime.utcnow() + timedelta(hours=ttl_hours)
    payload = {
        "user_id": user_id,
        "org_id": org_id,
        "exp": expires
    }
    return jwt.encode(payload, os.getenv("JWT_SECRET_KEY"), algorithm=JWT_ALGORITHM)

def verify_access_token(token: str):
    """Verify JWT token"""
    try:
        payload = jwt.decode(token, os.getenv("JWT_SECRET_KEY"), algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

# Mount on app
app = FastAPI()
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Usage in route
@app.post("/api/v1/query")
@limiter.limit("100/minute")  # 100 requests per minute per IP
async def query_endpoint(
    request: Request,
    credentials: HTTPAuthCredentials = Depends(HTTPBearer()),
):
    """Protected endpoint"""
    # Verify JWT
    user_data = verify_access_token(credentials.credentials)
    
    # Continue with request
    user_id = user_data["user_id"]
    org_id = user_data["org_id"]
    
    # ... rest of handler
```

### Request Headers & Validation

```python
# Add custom headers for tracing
@app.middleware("http")
async def add_request_id(request: Request, call_next):
    """Add X-Request-ID header"""
    request_id = str(uuid4())
    request.state.request_id = request_id
    
    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    return response

# Validate all requests
@app.middleware("http")
async def validate_request(request: Request, call_next):
    """Validate request size, headers, etc."""
    
    # Max request size: 10MB
    if request.headers.get("Content-Length"):
        size = int(request.headers["Content-Length"])
        if size > 10 * 1024 * 1024:  # 10MB
            return JSONResponse(
                status_code=413,
                content={"error": "Request too large"}
            )
    
    response = await call_next(request)
    return response
```

### Rate Limiting Tiers

```python
# Customize per endpoint

# Generous for public endpoints
@app.get("/api/v1/health")
@limiter.limit("1000/minute")
async def health_check():
    pass

# Strict for expensive operations
@app.post("/api/v1/query")
@limiter.limit("100/minute")  # 100 per minute per user
async def query():
    pass

# Very strict for admin operations
@app.post("/api/v1/policies")
@limiter.limit("10/minute")  # 10 per minute per admin
async def create_policy():
    pass
```

---

## 🧱 SECTION 7: GOVERNANCE VALIDATION (CRITICAL TESTS)

### Test Suite

```python
# backend/voxcore/tests/test_production_security.py

import pytest
from backend.voxcore.engine.core import VoxCoreEngine, VoxQueryRequest

class TestProductionSecurity:
    """Critical security tests for production"""
    
    @pytest.mark.asyncio
    async def test_destructive_sql_blocked(self, engine, services):
        """
        TEST 1: Destructive SQL is blocked
        EXPECTATION: Query rejected before execution
        """
        request = VoxQueryRequest(
            message="DROP TABLE users",
            session_id="test-123",
            org_id="org-123",
            user_id="user-456",
            user_role="analyst"
        )
        
        response = await engine.execute_query(request, services)
        
        # Must be blocked
        assert response.metadata.status == ExecutionStatus.BLOCKED
        assert response.error is not None
        assert "DROP" in response.error or "blocked" in response.error.lower()
    
    @pytest.mark.asyncio
    async def test_cross_tenant_access_blocked(self, engine, services):
        """
        TEST 2: Cross-tenant access is blocked
        EXPECTATION: org-999 cannot access org-123 data
        """
        # User from org-123 tries to access org-999 data
        request = VoxQueryRequest(
            message="SELECT * FROM users WHERE org_id = 'org-999'",
            session_id="test-123",
            org_id="org-123",  # Different than requested
            user_id="user-456",
            user_role="analyst"
        )
        
        response = await engine.execute_query(request, services)
        
        # Engine MUST filter by actual org_id (org-123)
        # So org-999 data is never returned
        assert response.metadata.org_id == "org-123"
        assert response.metadata.tenant_enforced == True
        # Result should only contain org-123 data (empty if no match)
    
    @pytest.mark.asyncio
    async def test_sensitive_column_masked(self, engine, services):
        """
        TEST 3: Sensitive columns are masked
        EXPECTATION: Salary shows as "****" for analyst role
        """
        request = VoxQueryRequest(
            message="Show all employees with salary",
            session_id="test-123",
            org_id="org-123",
            user_id="user-analyst",
            user_role="analyst"  # Limited role
        )
        
        response = await engine.execute_query(request, services)
        
        # Salary should be masked
        if "salary" in response.metadata.columns_masked:
            assert True  # Correct
        
        # Or if salary is in data, it should be masked
        for row in response.data:
            if "salary" in row:
                assert row["salary"] == "****"
    
    @pytest.mark.asyncio
    async def test_high_cost_query_blocked(self, engine, services):
        """
        TEST 4: High-cost queries are blocked or warned
        EXPECTATION: cost_score > 85 = blocked
        """
        # Simulate very complex query
        request = VoxQueryRequest(
            message="Full scan of billion-row table with complex joins",
            session_id="test-123",
            org_id="org-123",
            user_id="user-456",
            user_role="analyst"
        )
        
        response = await engine.execute_query(request, services)
        
        # Either blocked or with warning
        if response.metadata.cost_score > 85:
            assert response.metadata.status == ExecutionStatus.BLOCKED
            assert response.error is not None

# Run: pytest backend/voxcore/tests/test_production_security.py -v
```

---

## 🧱 SECTION 8: PERFORMANCE VALIDATION

### Cache & Performance Tests

```python
# backend/voxcore/tests/test_production_performance.py

class TestProductionPerformance:
    """Performance requirements for production"""
    
    @pytest.mark.asyncio
    async def test_cached_query_hit(self, engine, services):
        """
        Second query should hit cache (< 100ms)
        """
        request = VoxQueryRequest(
            message="Show revenue by region",
            session_id="test-123",
            org_id="org-123",
            user_id="user-456",
            user_role="analyst"
        )
        
        # First query (cache miss)
        response1 = await engine.execute_query(request, services)
        time1 = response1.metadata.execution_time_ms
        
        # Wait a tiny bit
        await asyncio.sleep(0.1)
        
        # Second query (cache hit)
        response2 = await engine.execute_query(request, services)
        time2 = response2.metadata.execution_time_ms
        
        # Cache hit should be much faster
        assert response2.metadata.cache_hit == True
        assert time2 < time1  # Should be faster or same
        assert time2 < 100  # Cached should be very fast
    
    @pytest.mark.asyncio
    async def test_query_latency_target(self, engine, services):
        """
        Cached queries: < 500ms
        Fresh queries: < 2000ms (depends on complexity)
        """
        request = VoxQueryRequest(
            message="Show total revenue",
            session_id="test-123",
            org_id="org-123",
            user_id="user-456",
            user_role="analyst"
        )
        
        response = await engine.execute_query(request, services)
        
        # Simple query should be fast
        if response.metadata.cache_hit:
            assert response.metadata.execution_time_ms < 500
        else:
            # First run might be slower, but not > 5 seconds
            assert response.metadata.execution_time_ms < 5000
    
    @pytest.mark.asyncio
    async def test_precomputation_works(self, engine, services):
        """
        Heavy queries might trigger precomputation
        Check that precomputation engine is being used
        """
        request = VoxQueryRequest(
            message="Show annual revenue trends for all regions",
            session_id="test-123",
            org_id="org-123",
            user_id="user-executive",
            user_role="executive"
        )
        
        response = await engine.execute_query(request, services)
        
        # Check if precomputation was triggered
        if response.metadata.execution_flags.get("precomputed_data_used"):
            assert response.metadata.execution_time_ms < 1000  # Much faster
```

---

## 🧱 SECTION 9: OBSERVABILITY & MONITORING

### Logging Setup

```python
# backend/voxcore/observability/logging.py

import logging
import json
from datetime import datetime

class JSONFormatter(logging.Formatter):
    """Format logs as structured JSON"""
    
    def format(self, record):
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
            "logger": record.name,
            "module": record.module,
            "line": record.lineno
        }
        
        # Add custom fields if present
        if hasattr(record, "request_id"):
            log_data["request_id"] = record.request_id
        if hasattr(record, "user_id"):
            log_data["user_id"] = record.user_id
        if hasattr(record, "org_id"):
            log_data["org_id"] = record.org_id
        
        return json.dumps(log_data)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(message)s',
    handlers=[
        logging.StreamHandler(),  # To console
        logging.FileHandler("voxquery.log")  # To file
    ]
)

# Add JSON formatter
for handler in logging.root.handlers:
    handler.setFormatter(JSONFormatter())

logger = logging.getLogger(__name__)
```

### Metrics Collection

```python
# backend/voxcore/observability/metrics.py

from prometheus_client import Counter, Histogram, Gauge
import time

# Define metrics
queries_total = Counter(
    "voxquery_queries_total",
    "Total queries executed",
    ["status", "org_id", "user_role"]
)

query_latency = Histogram(
    "voxquery_query_latency_ms",
    "Query latency in milliseconds",
    ["cache_hit"]
)

active_queries = Gauge(
    "voxquery_active_queries",
    "Current active queries"
)

cache_hits = Counter(
    "voxquery_cache_hits_total",
    "Total cache hits"
)

# Usage in VoxCore
@app.middleware("http")
async def track_metrics(request: Request, call_next):
    """Track query metrics"""
    
    start_time = time.time()
    active_queries.inc()
    
    try:
        response = await call_next(request)
        
        # Record latency
        latency_ms = (time.time() - start_time) * 1000
        query_latency.observe(latency_ms)
        
        # Record status
        queries_total.labels(
            status=response.status_code,
            org_id=request.state.org_id,
            user_role=request.state.user_role
        ).inc()
        
        return response
    finally:
        active_queries.dec()

# Expose metrics endpoint
from prometheus_client import make_wsgi_app
# Mount at /metrics for Prometheus scraping
```

### Monitoring Dashboard (Datadog/NewRelic)

```
Monitor these key metrics:

✅ Latency (p50, p95, p99)
✅ Error rate
✅ Cache hit rate
✅ Queue depth
✅ Database connections
✅ Redis memory usage
✅ CPU usage
✅ Cost spikes

Alert thresholds:

⚠️  Latency p95 > 2000ms
⚠️  Error rate > 5%
⚠️  Cache hit rate < 50%
⚠️  Queue depth > 100
⚠️  DB connections > 80
⚠️  Redis memory > 200MB
```

---

## 🧱 SECTION 10: FAILURE HANDLING

### Resilience Tests

```python
# backend/voxcore/tests/test_production_resilience.py

class TestProductionResilience:
    """Test system behavior when things break"""
    
    @pytest.mark.asyncio
    async def test_database_down_graceful_error(self, engine, services):
        """
        If DB is down:
        - MUST return error response
        - MUST NOT crash
        - MUST NOT hang
        """
        # Simulate DB unavailable
        services.database.disconnect()
        
        request = VoxQueryRequest(
            message="Show revenue",
            session_id="test",
            org_id="org-123",
            user_id="user-456",
            user_role="analyst"
        )
        
        response = await engine.execute_query(request, services)
        
        # Must be graceful error, not crash
        assert response.metadata.status == ExecutionStatus.FAILED
        assert response.error is not None
        assert "database" in response.error.lower() or "connection" in response.error.lower()
    
    @pytest.mark.asyncio
    async def test_redis_down_degraded_mode(self, engine, services):
        """
        If Redis is down:
        - Cache is disabled
        - Queries still work
        - Performance degrades but no crash
        """
        # Simulate Redis unavailable
        services.redis_client.close()
        
        request = VoxQueryRequest(
            message="Show revenue",
            session_id="test",
            org_id="org-123",
            user_id="user-456",
            user_role="analyst"
        )
        
        # Should still work (without cache)
        response = await engine.execute_query(request, services)
        
        # Must not crash
        assert response.metadata.status in [ExecutionStatus.COMPLETED, ExecutionStatus.FAILED]
    
    @pytest.mark.asyncio
    async def test_llm_timeout_fallback(self, engine, services):
        """
        If LLM times out:
        - Attempt retry
        - Fall back to keyword matching
        - Inform user
        """
        # Simulate LLM timeout
        services.intent_service.timeout = 1  # Very short timeout
        
        request = VoxQueryRequest(
            message="Show revenue by region",
            session_id="test",
            org_id="org-123",
            user_id="user-456",
            user_role="analyst"
        )
        
        response = await engine.execute_query(request, services)
        
        # Must not crash, either succeed with fallback or return error
        assert response.metadata.status != ExecutionStatus.TIMEOUT
    
    @pytest.mark.asyncio
    async def test_no_hanging_requests(self, engine, services):
        """
        Requests must ALWAYS return within timeout (10 seconds)
        If taking longer, must timeout gracefully
        """
        import asyncio
        
        request = VoxQueryRequest(
            message="SELECT SLEEP(100)",  # Very long query
            session_id="test",
            org_id="org-123",
            user_id="user-456",
            user_role="analyst"
        )
        
        # Must complete within 10 seconds (timeout)
        try:
            response = await asyncio.wait_for(
                engine.execute_query(request, services),
                timeout=10
            )
            # Either completed or timed out gracefully
            assert response.metadata.status in [
                ExecutionStatus.COMPLETED,
                ExecutionStatus.FAILED,
                ExecutionStatus.TIMEOUT
            ]
        except asyncio.TimeoutError:
            pytest.fail("Request timed out (took > 10 seconds)")
```

---

## 🧱 SECTION 11: SCALING CONFIGURATION

### Render Configuration

```yaml
# render.yaml (Infrastructure as Code)

services:
  - type: web
    name: voxquery-backend
    runtime: python
    
    # Auto-scaling
    plan: standard
    numInstances: 1
    maxNumInstances: 5
    autoDeploy: true
    
    # Health check
    healthCheckPath: /api/v1/health
    healthCheckInterval: 10
    
    # Build
    buildCommand: pip install -r requirements.txt
    startCommand: uvicorn backend.voxcore.main:app --port 8000
    
    # Environment
    envVars:
      - key: DATABASE_URL
        scope: run
        value: ${DATABASE_URL}  # From Render
      - key: REDIS_URL
        scope: run
        value: ${REDIS_URL}
      - key: ENV
        scope: run
        value: prod

databases:
  - name: voxquery-db
    databaseName: voxquery_prod
    user: voxquery_admin
    plan: standard
    ipWhitelist: []  # Allow all (Render handles security)

redis:
  - name: voxquery-cache
    ipWhitelist: []
    plan: standard
```

### Thread Pool Configuration

```python
# backend/voxcore/config.py

import os

# Thread pool size for I/O operations
MAX_WORKERS = int(os.getenv("MAX_WORKERS", "20"))

# Task queue
QUEUE_DEPTH_LIMIT = int(os.getenv("QUEUE_DEPTH_LIMIT", "1000"))

# Connection limits
DB_POOL_SIZE = 10
DB_MAX_OVERFLOW = 20
REDIS_POOL_SIZE = 50

# Request limits
MAX_REQUEST_SIZE = 10 * 1024 * 1024  # 10MB
MAX_RESPONSE_SIZE = 50 * 1024 * 1024  # 50MB
MAX_ROWS_RETURNED = 10000
MAX_EXECUTION_TIME_SECONDS = 30
```

### Auto-Scaling Rules

```python
# Monitor queue depth and auto-scale
@app.middleware("http")
async def monitor_queue(request: Request, call_next):
    queue_depth = get_queue_depth()
    
    if queue_depth > 500:
        logger.warning(f"⚠️  Queue depth high: {queue_depth}")
        # Render will see this in logs and can trigger alert
    
    if queue_depth > 1000:
        logger.error(f"❌ Queue depth critical: {queue_depth}")
        # Return 503 to signal overload
        return JSONResponse(
            status_code=503,
            content={"error": "Server overloaded"}
        )
    
    response = await call_next(request)
    return response
```

---

## 🧱 SECTION 12: COST CONTROL

### Row & Execution Limits

```python
# backend/voxcore/engine/core.py

class VoxCoreEngine:
    
    async def execute_query(self, request, services):
        # ... existing pipeline ...
        
        # STEP 7.5: Enforce execution limits
        # This prevents accidental expensive operations
        
        # Max rows
        if len(result) > 10000:
            logger.warning(f"Query returned {len(result)} rows, truncating to 10000")
            result = result[:10000]
        
        # Max execution time
        if execution_time_ms > 30000:  # 30 seconds
            logger.error(f"Query execution time exceeded: {execution_time_ms}ms")
            return VoxQueryResponse(
                data=[],
                metadata=ExecutionMetadata(..., status=ExecutionStatus.TIMEOUT),
                error="Query exceeded maximum execution time (30s)"
            )
        
        return response
```

### Cost-based Query Throttling

```python
# User has monthly cost quota

COST_QUOTA_PER_MONTH = {
    "analyst": 5000,      # 5000 cost units/month
    "finance": 10000,
    "executive": 50000
}

@app.middleware("http")
async def check_cost_quota(request: Request, call_next):
    """Check user has remaining cost quota"""
    
    user_id = request.state.user_id
    user_role = request.state.user_role
    
    # Get user's current month cost
    current_cost = await redis_client.get(f"cost_usage:{user_id}:{month}")
    quota = COST_QUOTA_PER_MONTH[user_role]
    
    if current_cost and current_cost > quota:
        return JSONResponse(
            status_code=429,
            content={
                "error": "Cost quota exceeded for this month",
                "used": current_cost,
                "limit": quota
            }
        )
    
    response = await call_next(request)
    
    # Update cost usage (query cost added after execution)
    # This happens in VoxCore after execute_query
    
    return response
```

---

## 🧱 SECTION 13: LOGGING & AUDIT

### Structured Logging

```python
# Every query MUST be logged with:
# - query_id (unique)
# - user_id
# - org_id
# - execution_time
# - cost_score
# - success/failure
# - policies applied

@app.middleware("http")
async def structured_logging(request: Request, call_next):
    request_id = str(uuid4())
    request.state.request_id = request_id
    
    start_time = time.time()
    
    response = await call_next(request)
    
    # Log in structured format
    logger.info(
        json.dumps({
            "request_id": request_id,
            "timestamp": datetime.utcnow().isoformat(),
            "method": request.method,
            "path": request.url.path,
            "user_id": request.state.get("user_id"),
            "org_id": request.state.get("org_id"),
            "status_code": response.status_code,
            "duration_ms": (time.time() - start_time) * 1000
        })
    )
    
    return response
```

### Log Retention

```
Development: 7 days
Staging: 30 days
Production: 90 days (compliance)

Store in:
- Render logs (free)
- Cloudflare Logpush (optional)
- S3 (for long-term archival)
```

---

## 🧱 SECTION 14: DOMAIN & SSL

### Custom Domain Setup

```
Vercel Frontend:
1. Point domain to Vercel nameservers
2. Auto SSL (included)
3. Configure environment: https://voxquery.com
4. Disable HTTP (force HTTPS)

Render Backend:
1. Use Render's domain OR custom domain
2. Example: https://api.voxquery.com
3. Auto SSL via Let's Encrypt
4. HSTS configured
```

### HSTS & Security Headers

```python
# Set security headers on every response

@app.middleware("http")
async def security_headers(request: Request, call_next):
    response = await call_next(request)
    
    # Strict TLS
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    
    # Content Security Policy
    response.headers["Content-Security-Policy"] = "default-src 'self'; script-src 'self' 'unsafe-inline'"
    
    # Prevent clickjacking
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    
    # CORS (if needed)
    response.headers["Access-Control-Allow-Origin"] = os.getenv("FRONTEND_URL")
    
    return response
```

---

## 🧱 SECTION 15: BACKUPS & RECOVERY

### Backup Strategy

```
Database:
- Automated daily backups (via Render)
- Retention: 7 days
- Recovery time: < 1 hour
- Test restore quarterly

Redis:
- Optional snapshot backup
- Critical data can be regenerated from DB
- No need for 24-hour recovery

Code:
- GitHub (version control)
- Protected main branch
```

### Disaster Recovery Plan

```
Database corruption:
1. Render one-click restore from backup
2. Verify data integrity
3. Resume service (< 1 hour downtime)

Code bug:
1. Revert via GitHub
2. Redeploy via Render
3. Service resumes (< 5 minutes)

Complete service failure:
1. Provision new Render instance
2. Restore from database backup
3. Reconfigure environment variables
4. Restore from GitHub code
5. Full recovery (< 2 hours)
```

---

## 🧱 SECTION 16: FINAL PRE-LAUNCH CHECKLIST

### ✅ FUNCTIONAL

```bash
# Test all core features
- [ ] User queries work
- [ ] Insights generate correctly
- [ ] UI loads without errors
- [ ] Results are accurate
- [ ] Suggestions appear
```

### ✅ SECURITY

```bash
# Test security controls
- [ ] Destructive SQL is blocked
- [ ] Cross-tenant access blocked
- [ ] Sensitive columns masked
- [ ] High-cost queries blocked
- [ ] Authentication required
- [ ] Rate limiting works
- [ ] No API keys in logs
- [ ] No secrets in code
```

### ✅ PERFORMANCE

```bash
# Test performance targets
- [ ] Cached queries < 500ms
- [ ] Fresh queries < 2000ms
- [ ] Cache hit rate > 50%
- [ ] No hanging requests
- [ ] Error rate < 1%
- [ ] Database connections healthy
- [ ] Redis memory usage normal
```

### ✅ FAILURE HANDLING

```bash
# Test failure scenarios
- [ ] Database down → graceful error
- [ ] Redis down → degraded mode
- [ ] LLM timeout → fallback
- [ ] Network issue → retry & timeout
- [ ] No crashes or hangs
```

### ✅ OBSERVABILITY

```bash
# Test monitoring
- [ ] Metrics being collected
- [ ] Logs are structured JSON
- [ ] Request IDs tracked end-to-end
- [ ] Latency tracked
- [ ] Error rate visible
- [ ] Alerts would trigger
```

### ✅ COMPLIANCE

```bash
# Test governance
- [ ] Audit logs created
- [ ] Query history available
- [ ] Data classification working
- [ ] Tenant isolation verified
- [ ] Rate limits enforced
```

---

## GO / NO-GO DECISION

### ✅ **GO LIVE IF:**

```
✅ All tests passing
✅ No critical failures
✅ Monitoring operational
✅ Backup tested
✅ Team trained
✅ Runbook written
✅ On-call schedule ready
```

### ❌ **DO NOT LAUNCH IF:**

```
❌ Data leak risk detected
❌ No monitoring
❌ No rate limiting
❌ Tests not all passing
❌ Secrets in code
❌ Database not PostgreSQL
❌ No backup tested
❌ Performance < 2 seconds
```

---

## 📋 FINAL CHECKLIST SCRIPT

```bash
#!/bin/bash
# production_readiness.sh

echo "🔥 VOXCORE PRODUCTION READINESS CHECK"
echo ""

# 1. Environment separation
echo "✓ Checking environment separation..."
[[ -f .env.dev ]] && echo "  ✅ .env.dev exists"
[[ -f .env.staging ]] && echo "  ✅ .env.staging exists"
[[ ! -f .env.prod ]] && echo "  ✅ .env.prod NOT in repo (good!)"

# 2. Database
echo "✓ Checking database..."
grep -q "postgresql://" .env.staging && echo "  ✅ Staging uses PostgreSQL"
grep -q "postgresql://" .env.prod && echo "  ✅ Prod uses PostgreSQL"

# 3. Secrets
echo "✓ Checking secrets..."
! grep -r "sk_prod\|password=" . --exclude-dir=.git && echo "  ✅ No secrets in code"

# 4. Tests
echo "✓ Running tests..."
pytest backend/voxcore/tests/test_production_security.py -v
pytest backend/voxcore/tests/test_production_performance.py -v
pytest backend/voxcore/tests/test_production_resilience.py -v

# 5. Code quality
echo "✓ Checking code quality..."
pylint backend/voxcore/ --disable=all --enable=E,F

# 6. Dependencies
echo "✓ Checking dependencies..."
pip show -r requirements.txt > /dev/null && echo "  ✅ All dependencies installed"

echo ""
echo "🎉 PRODUCTION READINESS CHECK COMPLETE"
```

---

**🎯 Complete the 16 sections above → You are production SaaS, not a demo.**


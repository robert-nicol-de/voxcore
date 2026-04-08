# STEP 11 Integration Example — How to Wire Resilience into VoxCoreEngine

## Quick Reference

Add these 3 components to make your system resilient:

1. **Retry Logic** — Automatically retry transient failures
2. **Circuit Breaker** — Stop cascading when service fails
3. **Fallback** — Return safe responses when everything fails

---

## Integration Point 1: VoxCoreEngine Query Execution

**File:** `backend/voxcore/engine/core.py`

```python
from backend.resilience.retry_handler import AsyncRetryHandler, DATABASE_RETRY_CONFIG
from backend.resilience.circuit_breaker import get_database_breaker, CircuitBreakerOpenError
from backend.resilience.fallback_handler import get_fallback_handler

class VoxCoreEngine:
    def __init__(self):
        self.db_breaker = get_database_breaker()
        self.retry_handler = AsyncRetryHandler(DATABASE_RETRY_CONFIG)
        self.fallback_handler = get_fallback_handler()
    
    async def execute_query(self, sql: str, org_id: str, user_id: str, user_role: str):
        """Execute query with full resilience"""
        
        # Step 1: Check if database circuit is broken
        if self.db_breaker.is_open():
            logger.error("Database circuit breaker is OPEN, cannot execute query")
            fallback = self.fallback_handler.create_database_fallback()
            return {
                "status": "degraded",
                "message": fallback.message,
                "can_retry": fallback.can_retry
            }
        
        try:
            # Step 2: Execute with retry logic
            async def execute():
                return await self._execute_with_governance(sql, org_id, user_id)
            
            results = await self.retry_handler.execute(execute)
            
            # Step 3: Record success
            self.db_breaker.record_success()
            
            return {
                "status": "success",
                "data": results,
                "rows": len(results)
            }
        
        except Exception as e:
            # Step 4: Record failure (updates circuit breaker)
            self.db_breaker.record_failure()
            
            logger.error(f"Query execution failed: {str(e)}", exc_info=True)
            
            # Step 5: Return fallback
            fallback = self.fallback_handler.create_error_fallback(e)
            
            return {
                "status": "degraded",
                "message": fallback.message,
                "can_retry": fallback.can_retry,
                "error_type": fallback.type.value
            }
```

---

## Integration Point 2: LLM Query Processing

**File:** `backend/voxcore/engine/core.py` or `backend/services/llm_service.py`

```python
from backend.resilience.retry_handler import AsyncRetryHandler, LLM_RETRY_CONFIG
from backend.resilience.circuit_breaker import get_llm_breaker, CircuitBreakerOpenError
from backend.resilience.fallback_handler import get_fallback_handler

class LLMService:
    def __init__(self):
        self.llm_breaker = get_llm_breaker()
        self.retry_handler = AsyncRetryHandler(LLM_RETRY_CONFIG)
        self.fallback_handler = get_fallback_handler()
    
    async def process_natural_language_query(
        self,
        query: str,
        org_id: str,
        user_id: str
    ):
        """Process query with LLM, graceful fallback on failure"""
        
        # Check circuit breaker
        if self.llm_breaker.is_open():
            logger.warning("LLM circuit breaker is OPEN, using fallback")
            fallback = self.fallback_handler.create_llm_fallback()
            return {
                "status": "degraded",
                "message": fallback.message,
                "is_fallback": True,
                "can_retry": fallback.can_retry
            }
        
        try:
            # Execute with retries
            async def call_llm():
                return await self._groq_api_call(query, org_id)
            
            result = await self.retry_handler.execute(call_llm)
            
            # Record success
            self.llm_breaker.record_success()
            
            return {
                "status": "success",
                "sql": result["sql"],
                "explanation": result["explanation"],
                "is_fallback": False
            }
        
        except Exception as e:
            # Record failure
            self.llm_breaker.record_failure()
            
            logger.warning(f"LLM processing failed: {str(e)}")
            
            # LLM failure is NOT critical - return fallback
            fallback = self.fallback_handler.create_llm_fallback()
            return {
                "status": "degraded",
                "message": fallback.message,
                "is_fallback": True,
                "can_retry": fallback.can_retry,
                "suggestion": "Try rephrasing your question more specifically"
            }
```

---

## Integration Point 3: FastAPI Routes

**File:** `backend/routes/query.py`

```python
from fastapi import FastAPI, HTTPException
from backend.middleware.resilience import ResilienceMiddleware
from backend.voxcore.engine.core import VoxCoreEngine
from backend.observability.structured_logger import query_logger, set_correlation_id, clear_context

app = FastAPI()

# Add resilience middleware to ALL routes
app.add_middleware(
    ResilienceMiddleware,
    enable_retry=True,
    enable_circuit_breaker=True
)

engine = VoxCoreEngine()

@app.post("/api/query")
async def execute_query_endpoint(
    request: QueryRequest,
    current_user: User = Depends(get_current_user)
):
    """Execute a SQL query with full resilience"""
    
    # Setup observability
    correlation_id = str(uuid.uuid4())
    set_correlation_id(correlation_id)
    
    try:
        # Convert natural language → SQL
        llm_result = await engine.llm_service.process_natural_language_query(
            query=request.query,
            org_id=current_user.org_id,
            user_id=current_user.id
        )
        
        # If LLM failed, return early with suggestions
        if llm_result["status"] == "degraded":
            return {
                "status": "degraded",
                "message": llm_result["message"],
                "suggestion": "Try being more specific",
                "can_retry": True
            }
        
        sql = llm_result["sql"]
        
        # Execute query
        query_result = await engine.execute_query(
            sql=sql,
            org_id=current_user.org_id,
            user_id=current_user.id,
            user_role=current_user.role
        )
        
        # If database failed, return gracefully
        if query_result["status"] == "degraded":
            return {
                "status": "service_unavailable",
                "message": query_result["message"],
                "can_retry": query_result["can_retry"]
            }
        
        # Success!
        query_logger.query_completed(
            query_id=request.id,
            execution_time_ms=0,
            rows_returned=query_result["rows"]
        )
        
        return {
            "status": "success",
            "data": query_result["data"],
            "rows": query_result["rows"],
            "sql": sql
        }
    
    except Exception as e:
        logger.error(f"Query failed: {str(e)}", exc_info=True)
        
        return {
            "status": "error",
            "message": "An unexpected error occurred",
            "can_retry": True
        }
    
    finally:
        clear_context()
```

---

## Integration Point 4: Cache Fallback

**File:** `backend/services/cache_service.py`

```python
from backend.resilience.circuit_breaker import get_cache_breaker

class CacheService:
    def __init__(self):
        self.cache_breaker = get_cache_breaker()
    
    async def get_cached_result(self, cache_key: str):
        """Get cached result with fallback"""
        
        if self.cache_breaker.is_open():
            # Cache is failing, skip it
            logger.debug("Cache circuit breaker open, skipping cache lookup")
            return None
        
        try:
            result = await self.redis_client.get(cache_key)
            self.cache_breaker.record_success()
            return result
        
        except Exception as e:
            self.cache_breaker.record_failure()
            logger.warning(f"Cache lookup failed: {str(e)}")
            return None  # Graceful degradation
    
    async def set_cached_result(self, cache_key: str, value: Any, ttl_seconds: int = 3600):
        """Set cached result with fallback"""
        
        if self.cache_breaker.is_open():
            # Cache is failing, skip it
            logger.debug("Cache circuit breaker open, skipping cache write")
            return
        
        try:
            await self.redis_client.set(cache_key, value, ex=ttl_seconds)
            self.cache_breaker.record_success()
        
        except Exception as e:
            self.cache_breaker.record_failure()
            logger.warning(f"Cache write failed: {str(e)}")
            # Continue anyway - cache failure is not critical
```

---

## Integration Point 5: Error Recovery Monitoring

**File:** `backend/routes/observability.py`

Add endpoint to expose circuit breaker status:

```python
from backend.resilience.circuit_breaker import get_registry

@router.get("/api/observability/resilience/status")
async def get_resilience_status():
    """Get circuit breaker and resilience status"""
    
    registry = get_registry()
    
    return {
        "timestamp": datetime.utcnow().isoformat(),
        "circuit_breakers": registry.get_all_status(),
        "unhealthy": registry.get_unhealthy(),
        "overall_health": "healthy" if not registry.get_unhealthy() else "degraded"
    }

@router.get("/api/observability/resilience/unhealthy")
async def get_unhealthy_services():
    """Get list of currently unhealthy services"""
    
    registry = get_registry()
    unhealthy = registry.get_unhealthy()
    
    if unhealthy:
        return {
            "status": "degraded",
            "unhealthy_services": [item["name"] for item in unhealthy],
            "details": unhealthy
        }
    
    return {
        "status": "healthy",
        "unhealthy_services": []
    }
```

---

## Testing Failure Scenarios

### Test 1: Verify Retry Works

```bash
# Start database
docker start postgres

# Run query - should succeed
curl -X POST http://localhost:8000/api/query \
  -H "Content-Type: application/json" \
  -d '{"query": "SELECT * FROM users"}'
# → {"status": "success", "rows": 100}

# Stop database mid-request and monitor
# You should see retry attempts in logs
# After 3 attempts, should return fallback
```

### Test 2: Verify Circuit Breaker Opens

```bash
# Kill database
docker stop postgres

# Hit endpoint 5+ times
for i in {1..10}; do
  curl -X POST http://localhost:8000/api/query \
    -H "Content-Type: application/json" \
    -d '{"query": "SELECT * FROM users"}'
  sleep 0.5
done

# Check circuit breaker status
curl http://localhost:8000/api/observability/resilience/status
# → {"circuit_breakers": {"database": {"state": "open", ...}}}

# First few attempts will retry (logs show: "Attempt 1, Attempt 2, Attempt 3")
# After failure_threshold (5), response changes:
# → {"status": "degraded", "message": "Database temporarily unavailable"}
# Plus: "Circuit 'database': OPENED! Too many failures"
```

### Test 3: Verify Circuit Breaker Recovery

```bash
# Circuit is open (from above)
curl http://localhost:8000/api/observability/resilience/status
# → state: open

# Wait 30 seconds (TIMEOUT_SECONDS for database)
sleep 30

# Circuit should transition to HALF_OPEN
# Next request will be tested
curl -X POST http://localhost:8000/api/query

# If that succeeds (database is back), record success
# After 2 successes (success_threshold), circuit CLOSES
# Normal operation resumes
```

---

## Production Deployment

### 1. Deploy Resilience Code

```bash
# Upload to production:
- backend/resilience/retry_handler.py
- backend/resilience/circuit_breaker.py
- backend/resilience/fallback_handler.py
- backend/middleware/resilience.py
- backend/tests/test_resilience.py
```

### 2. Update VoxCoreEngine

Use the code from Integration Point 1 above

### 3. Update FastAPI app

Use the code from Integration Point 3 above

### 4. Configure Thresholds

```python
# Database - fail fast, long recovery
CircuitBreakerConfig(
    name="database",
    failure_threshold=5,      # 5 failures
    timeout_seconds=30,        # Wait 30s before testing
    success_threshold=2        # 2 successes to close
)

# LLM - slower failure, longer recovery
CircuitBreakerConfig(
    name="llm",
    failure_threshold=3,       # 3 failures
    timeout_seconds=60,        # Wait 60s before testing
    success_threshold=2
)

# Cache - very tolerant
CircuitBreakerConfig(
    name="cache",
    failure_threshold=10,      # 10 failures
    timeout_seconds=20,        # Quick recovery
    success_threshold=5
)
```

### 5. Run Tests

```bash
pytest backend/tests/test_resilience.py -v

# Should see:
# test_retry_on_failure PASSED
# test_circuit_breaker_opens_on_failures PASSED
# test_fallback_response PASSED
# ... 30+ tests passing
```

### 6. Monitor in Production

```bash
# Watch circuit breaker status
curl http://localhost:8000/api/observability/resilience/status

# Set up alerts
- Alert if circuit_breaker.state == "open" for > 5 min
- Alert if circuit_breaker.state changes > 5 times in 5 min
- Alert if fallback_usage_rate > 5%

# Log all opens
- "Circuit 'database': OPENED! Too many failures."
- "Circuit 'database': Timeout expired, moving to HALF_OPEN"
- "Circuit 'database': Recovered! Moving to CLOSED"
```

---

## Summary

Your system is now **resilient to production failures**:

✅ **Retry** — Automatic exponential backoff for transient failures  
✅ **Circuit Breaker** — Prevent cascading failures  
✅ **Fallback** — Return safe responses when things break  
✅ **Auto-Recovery** — Automatically resume when service recovers  
✅ **Monitoring** — Track resilience metrics  

**Your system no longer crashes when things go wrong.** 🛡️

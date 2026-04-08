# 🎯 VOXCORE COMPLETE SYSTEM ARCHITECTURE

## 📊 16-STEP SYSTEM OVERVIEW

VoxQuery is a **16-step system** where all components coordinate through **VoxCore** - the central orchestrator.

```
┌─────────────────────────────────────────────────────────────────┐
│                    VOXQUERY - 16 STEPS                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  STEPS 1-9: GOVERNANCE LAYER                                    │
│  ├─ STEP 1: Authentication & Authorization                      │
│  ├─ STEP 2: Role-Based Access Control (RBAC)                    │
│  ├─ STEP 3: Intent Recognition (LLM understanding)              │
│  ├─ STEP 4: Query Generation (intent → SQL)                     │
│  ├─ STEP 5: Tenant Enforcement (org isolation)                  │
│  ├─ STEP 6: Policy Engine (masking, filtering, blocking)        │
│  ├─ STEP 7: Cost Control (query complexity estimation)          │
│  ├─ STEP 8: Semantic Caching (by intent, not SQL hash)          │
│  └─ STEP 9: Query Validation & Sanitization                     │
│                                                                  │
│  STEP 10: OBSERVABILITY & MONITORING                            │
│  ├─ Metrics collection (latency, throughput, errors)            │
│  ├─ Alerting (threshold-based notifications)                    │
│  └─ Audit logging (immutable execution records)                 │
│                                                                  │
│  STEP 11: RESILIENCE & RECOVERY                                 │
│  ├─ Circuit breakers (fail gracefully)                          │
│  ├─ Retry logic (exponential backoff)                           │
│  └─ Fallback strategies (cached results, degraded mode)         │
│                                                                  │
│  STEP 12: FRONTEND TRUST MODEL                                  │
│  ├─ ExecutionMetadata with HMAC-SHA256 signature                │
│  ├─ Proof of execution (cannot be tampered with)                │
│  └─ Frontend verification (verify() before displaying)          │
│                                                                  │
│  STEP 13: EXECUTION METADATA & TRACEABILITY                     │
│  ├─ Detailed execution flags (query type, confidence, intent)   │
│  ├─ Decision audit trail (which policies applied)               │
│  └─ Cost analysis (per-query cost tracking)                     │
│                                                                  │
│  STEP 14: PRODUCTION MONITORING (DETAILED)                      │
│  ├─ MetricsService (track every query)                          │
│  ├─ AlertingService (notify on thresholds)                      │
│  └─ Operational Dashboard (real-time system health)             │
│                                                                  │
│  STEP 15: PERFORMANCE OPTIMIZATION                              │
│  ├─ SemanticCache (cache by intent, not SQL)                    │
│  ├─ QueryReuseEngine (slice cached results)                     │
│  ├─ PrecomputationEngine (background jobs)                      │
│  ├─ IndexHintEngine (auto index recommendations)                │
│  └─ CacheInvalidationEngine (multi-strategy staleness)          │
│                                                                  │
│  STEP 16: ENTERPRISE READINESS                                  │
│  ├─ SOC2 Control Management                                     │
│  ├─ Data Encryption (at rest + in transit)                      │
│  ├─ Secrets Management (AWS, Azure vault)                       │
│  ├─ Access Traceability (who accessed what)                     │
│  ├─ Compliance Exporting (JSON/CSV/PDF reports)                 │
│  ├─ Data Classification (PII, PHI, confidential)                │
│  └─ Rate Limiting & DDoS Protection                             │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🔄 THE 14-STEP REQUEST PIPELINE

**Every single query flows through this pipeline (no exceptions):**

```
CLIENT REQUEST: "Show revenue by region"
  ↓
1. ✅ AUTH MIDDLEWARE
   - Verify JWT token
   - Extract user_id, org_id
  ↓
2. ✅ RATE LIMIT MIDDLEWARE
   - Check if user exceeds quota
   - Block if throttled
  ↓
3. ✅ INTENT RECOGNITION (STEP 3)
   - LLM understands "Show revenue by region"
   - Returns: intent=METRICS_QUERY, entities=[revenue, region]
  ↓
4. ✅ QUERY GENERATION (STEP 4)
   - intent → SQL: SELECT region, SUM(revenue) FROM sales GROUP BY region
  ↓
5. ✅ TENANT ENFORCEMENT (STEP 5 - CRITICAL)
   - Add org filter: WHERE org_id = 'org-123'
   - Impossible to bypass (hard-coded in engine)
   - User from org-999 CANNOT see org-123's data
  ↓
6. ✅ POLICY ENGINE (STEP 6)
   - Check user role (analyst, finance, executive)
   - Apply masking: "salary" column → "****"
   - Apply filtering: "only see West region" (RBAC row filter)
   - Check if query is blocked (accessing customer PII without permission)
   - Update metadata: policies_applied=["column_masking", "row_filtering"]
  ↓
7. ✅ COST CHECK (STEP 7)
   - Estimate query cost (0-100 scale)
   - Cost = heuristic based on query complexity (joins, aggregations, etc.)
   - If cost > 85, BLOCK query (refuse to execute)
   - Update metadata: cost_score=35 (cheap)
  ↓
8. ✅ CACHE CHECK (STEP 8 - OPTIMIZATION)
   - Generate cache key from intent: "metrics_revenue_org123"
   - Check if cached result exists
   - IF cache hit → return cached data (execution_time = 10ms) 🚀
   - IF cache miss → continue to step 9
  ↓
9. ✅ EXECUTE QUERY (STEP 9)
   - Run SQL against database
   - Get result set (e.g., 4 rows)
   - Record execution time
  ↓
10. ✅ SANITIZE RESULTS (STEP 9)
    - Remove sensitive information
    - Encrypt certain columns if needed
    - Apply any filtering rules
  ↓
11. ✅ GENERATE & SIGN METADATA (STEPS 12-13)
    - Create ExecutionMetadata object with:
      * execution_id, user_id, org_id, session_id
      * status=COMPLETED
      * execution_time_ms=245
      * rows_returned=4
      * cost_score=35
      * policies_applied=["column_masking", "row_filtering"]
      * columns_masked=["salary"]
      * tenant_enforced=true
      * cache_hit=false
    - Sign with HMAC-SHA256(secret_key, metadata_json)
    - Frontend verifies this signature (proves data wasn't tampered)
  ↓
12. ✅ CACHE RESULT (STEP 8)
    - Store result with TTL based on cost:
      * Cost 0-40 → 1 hour cache (cheap)
      * Cost 40-70 → 5 minute cache (moderate)
      * Cost 70-85 → 1 minute cache (expensive)
  ↓
13. ✅ TRACK METRICS (STEP 14)
    - Record to metrics service:
      * latency=245ms
      * cost_score=35
      * cache_hit=false
      * user_id=user-456
      * org_id=org-123
    - Trigger alerts if latency > 5000ms
  ↓
14. ✅ RETURN RESPONSE
    - Return VoxQueryResponse with:
      * data: [{region: North, revenue: 1500000}, ...]
      * metadata: {execution_id, signature, cost_score, ...}
      * suggestions: ["Show over time", "Break down by product"]
      * error: null
      * success: true
  ↓
FRONTEND receives signed response
  ↓
FRONTEND verifies signature
  ↓
IF signature valid → display data with TrustBadge ✓
IF signature invalid → security alert ⚠️
```

---

## 🏗️ VOXCORE ARCHITECTURE

### Tier 1: API Gateway

```python
# File: backend/voxcore/api/conversation_api.py

13 Master Endpoints:

1. POST /api/v1/query                    # Main query endpoint
2. GET /api/v1/jobs/{job_id}             # Job status
3. GET /api/v1/metrics/summary           # System metrics
4. GET /api/v1/metrics/org/{org_id}      # Org-specific metrics
5. GET /api/v1/metrics/cost              # Cost analysis
6. GET /api/v1/compliance/export         # Compliance reports (JSON/CSV/PDF)
7. GET /api/v1/compliance/controls       # SOC2 control status
8. GET /api/v1/policies                  # List policies
9. POST /api/v1/policies                 # Create policy
10. DELETE /api/v1/policies/{id}         # Delete policy
11. GET /api/v1/user/profile             # User permissions
12. GET /api/v1/session/check            # Session validation
13. GET /api/v1/health                   # Health check
```

### Tier 2: VoxCore Engine

```python
# File: backend/voxcore/engine/core.py

class VoxCoreEngine:
    async def execute_query(request, services) → response:
        """The 14-step pipeline orchestrator"""
        # Implements steps 1-14 above
```

### Tier 3: Service Container (Dependency Injection)

```python
# File: backend/voxcore/engine/service_container.py

class ServiceContainer:
    """Holds all 20+ service instances"""
    
    # Storage (Tier 0)
    redis_client: RedisClient
    database: DatabaseConnection
    
    # Security (Tier 1)
    secrets_manager: SecretsManager           # STEP 16
    encryption_service: EncryptionService     # STEP 16
    security_middleware: SecurityMiddleware   # STEP 16
    
    # Governance (Tier 2)
    permission_engine: PermissionEngine       # STEP 2
    policy_engine: PolicyEngine               # STEP 6
    controls_manager: ControlsManager         # STEP 16
    
    # Query Execution (Tier 3)
    intent_service: IntentService             # STEP 3
    query_service: QueryService               # STEP 4
    query_executor: QueryExecutor             # STEP 9
    
    # Performance (Tier 4)
    semantic_cache: SemanticCache             # STEP 8 + STEP 15
    query_reuse_engine: QueryReuseEngine      # STEP 15
    precomputation_engine: PrecomputationEngine  # STEP 15
    index_hint_engine: IndexHintEngine        # STEP 15
    cache_invalidation_engine: CacheInvalidationEngine  # STEP 15
    
    # Observability (Tier 5)
    metrics_service: MetricsService           # STEP 14
    alerting_service: AlertingService         # STEP 14
    audit_log: AuditLog                       # STEP 14
    
    # Compliance (Tier 6)
    access_traceability_log: AccessTraceabilityLog  # STEP 16
    compliance_exporter: ComplianceExporter   # STEP 16
```

### Tier 4: Main Application

```python
# File: backend/voxcore/main.py

app = FastAPI()

# On startup:
@app.lifespan
async def startup():
    # Initialize all services
    services = await initialize_services()
    # Register routes
    app.include_router(conversation_api.router)
    # Add middleware (auth, rate limit, logging)
    app.add_middleware(...)
```

---

## 📁 VOXCORE DIRECTORY STRUCTURE

```
backend/voxcore/
├── __init__.py
├── main.py                           # Main FastAPI app + startup
│
├── api/
│   ├── __init__.py
│   └── conversation_api.py           # 13 master endpoints
│
├── engine/
│   ├── __init__.py
│   ├── core.py                       # VoxCoreEngine (14-step pipeline)
│   └── service_container.py          # ServiceContainer + dependency injection
│
├── services/
│   ├── __init__.py
│   ├── intent_service.py             # STEP 3
│   ├── query_service.py              # STEP 4
│   ├── query_executor.py             # STEP 9
│   └── policy_engine.py              # STEP 6
│
├── security/
│   ├── __init__.py
│   ├── authentication.py             # STEP 1
│   ├── authorization.py              # STEP 2
│   └── encryption.py                 # STEP 16
│
├── storage/
│   ├── __init__.py
│   ├── redis_client.py
│   └── database.py
│
├── observability/
│   ├── __init__.py
│   ├── metrics.py                    # STEP 14
│   ├── audit_log.py                  # STEP 14
│   └── alerting.py                   # STEP 14
│
└── tests/
    ├── __init__.py
    ├── test_system.py                # System tests (10+ test classes)
    ├── test_pipeline.py              # Pipeline tests
    ├── test_security.py              # Security tests
    └── test_compliance.py            # Compliance tests
```

---

## 🔐 EXECUTION METADATA (STEP 12 & 13)

```python
@dataclass
class ExecutionMetadata:
    # Identifiers
    execution_id: UUID
    user_id: str
    org_id: str
    session_id: str
    
    # Execution Results
    status: ExecutionStatus  # COMPLETED, FAILED, BLOCKED, TIMEOUT
    execution_time_ms: float
    rows_returned: int
    
    # Cost & Governance (STEP 7 & 6)
    cost_score: float (0-100)          # Cheap (0-40), Moderate (40-70), Expensive (70+)
    policies_applied: List[str]        # Which policies were enforced
    columns_masked: List[str]          # Which columns were masked
    filters_injected: List[str]        # Which row filters were added
    tenant_enforced: bool = True       # Tenant isolation GUARANTEED
    cache_hit: bool                    # Was this from cache?
    
    # Trust & Verification (STEP 12)
    signature: str (HMAC-SHA256)       # ← FRONTEND VERIFIES THIS
    audit_log_id: str                  # Links to immutable log
    execution_flags: Dict              # From STEP 13 (query type, confidence, intent)
    
    def sign(secret_key: str) → str:
        """Generate HMAC-SHA256 signature"""
        
    @staticmethod
    def verify_signature(metadata: dict, secret_key: str) → bool:
        """Frontend verifies this (proves data integrity)"""
```

---

## 🌐 API REQUEST/RESPONSE EXAMPLES

### Request: Query Execution

```http
POST /api/v1/query HTTP/1.1
Content-Type: application/json
Authorization: Bearer eyJhbGc...

{
  "message": "Show revenue by region for Q1 2024",
  "session_id": "session-uuid-123",
  "org_id": "org-123",
  "user_id": "user-456",
  "user_role": "analyst",
  "context": {
    "previous_queries": ["..."],
    "selected_table": "sales"
  }
}
```

### Response: Query Results

```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "data": [
    {
      "region": "North",
      "revenue": 1500000
    },
    {
      "region": "South",
      "revenue": 1200000
    },
    ...
  ],
  "metadata": {
    "execution_id": "exec-uuid-123",
    "user_id": "user-456",
    "org_id": "org-123",
    "session_id": "session-uuid-123",
    "status": "COMPLETED",
    "execution_time_ms": 245,
    "rows_returned": 4,
    "cost_score": 35,
    "policies_applied": ["column_masking", "row_filtering"],
    "columns_masked": ["salary"],
    "filters_injected": ["region IN (...)"],
    "tenant_enforced": true,
    "cache_hit": false,
    "signature": "abc123def456_hmac_sha256_...",
    "audit_log_id": "audit-123",
    "execution_flags": {
      "query_type": "METRICS_QUERY",
      "confidence": 0.95,
      "semantic_intent": "REVENUE_ANALYSIS",
      "schema_version": "v2024.01"
    }
  },
  "suggestions": [
    "Show this over time",
    "Break down by product",
    "Compare to last year"
  ],
  "error": null,
  "success": true
}
```

---

## 🎯 CRITICAL DESIGN PRINCIPLES

### 1. Every Query Flows Through The Pipeline (MANDATORY)

❌ **NEVER skip steps:**
```python
# WRONG - Bypasses governance
result = database.execute(sql)
return result
```

✅ **ALWAYS use VoxCore:**
```python
# RIGHT - Goes through full 14-step pipeline
response = await engine.execute_query(request, services)
return response
```

### 2. Tenant Isolation Is Non-Negotiable (STEP 5)

❌ **WRONG - Org 999 could see org 123's data:**
```python
users = database.query("SELECT * FROM users")
```

✅ **RIGHT - Org filter is hard-coded:**
```python
# In VoxCoreEngine._enforce_tenant()
users = database.query("SELECT * FROM users WHERE org_id = ?", org_id)
```

### 3. Policy Engine Controls Access (STEP 6)

Policy engine runs **AFTER** tenant enforcement but **BEFORE** execution.

```
User query → Tenant filter added → Policy check → Block/Proceed → Execute
```

### 4. Cost Control Prevents Expensive Queries (STEP 7)

Expensive queries are blocked **before execution** to save resources:

```
Estimate cost → If cost > 85 → BLOCK → Return error
```

### 5. Caching Is Semantic, Not SQL-Based (STEP 8)

```
Two different SQL queries with SAME intent → SAME cache result

Cache key = hash(intent + org_id)  # Not hash(sql)

"Show revenue by region" and "What's revenue by region?" → Same cache hit
```

### 6. Metadata Is Signed (STEP 12)

Every response includes HMAC-SHA256 signature that frontend verifies:

```
Frontend: IF verify_signature(metadata, secret_key) → Display data
Frontend: ELSE → Security alert
```

### 7. All Services Are Injected (ServiceContainer)

No global state, no singletons (mostly). Services are passed:

```python
async def execute_query(request, services: ServiceContainer):
    # Use services.intent_service, services.policy_engine, etc.
    # Easy to mock for testing
```

---

## 🧪 TESTING STRATEGY

**System test file:** `backend/voxcore/tests/test_system.py` (800+ lines)

**Test categories:**

| Category | Tests | Goal |
|----------|-------|------|
| **Pipeline** | 3 | Verify all 14 steps execute |
| **Tenant Isolation** | 3 | Verify org data cannot leak |
| **Policy** | 3 | Verify masking, filtering, blocking |
| **Cost** | 3 | Verify cost estimation and blocking |
| **Caching** | 3 | Verify semantic caching |
| **Signatures** | 3 | Verify metadata integrity |
| **Error Handling** | 3 | Verify graceful failures |
| **Observability** | 2 | Verify metrics and audit logs |
| **Compliance** | 2 | Verify SOC2 controls |
| **Integration** | 1 | Verify concurrent requests |
| **TOTAL** | 26+ | End-to-end coverage |

---

## 📊 SYSTEM HEALTH MONITORING

### Metrics Collected (STEP 14)

```python
{
  "total_queries": 10000,
  "avg_latency_ms": 250,
  "p95_latency_ms": 1200,
  "p99_latency_ms": 3500,
  "error_rate": 0.01,        # 1%
  "cache_hit_rate": 0.65,    # 65%
  "blocked_rate": 0.03,      # 3%
  "avg_cost_score": 35,
  "by_org": {
    "org-123": {"queries": 5000, "latency": 200, ...},
    "org-456": {"queries": 3000, "latency": 280, ...}
  },
  "by_user_role": {
    "analyst": {"queries": 4000, "error_rate": 0.01},
    "executive": {"queries": 2000, "error_rate": 0.005},
    "finance": {"queries": 4000, "error_rate": 0.02}
  }
}
```

### Alerts (Configured)

```
IF avg_latency > 1000ms → Alert
IF error_rate > 5% → Alert
IF cache_hit_rate < 50% → Alert
IF any query takes > 5000ms → Alert
IF blocked_rate > 10% → Investigate
```

---

## 🚀 DEPLOYMENT CHECKLIST

Before deploying VoxCore to production:

- [ ] All 16 services initialized
- [ ] Database migrations complete
- [ ] Redis cache configured
- [ ] Secret keys stored (not in code)
- [ ] SSL/TLS enabled (HTTPS only)
- [ ] Rate limiting enabled
- [ ] Audit logging configured
- [ ] Metrics collection running
- [ ] Alerts configured
- [ ] SOC2 controls verified
- [ ] All system tests passing
- [ ] Load tests completed
- [ ] Failover tested
- [ ] Backup/recovery tested
- [ ] Documentation complete

---

## 📞 SUPPORT

**Questions?** Check:
- [Frontend Integration Guide](./VOXCORE_FRONTEND_INTEGRATION.md)
- [14-Step Pipeline Details](./14_STEP_PIPELINE.md)
- [API Reference](./API_REFERENCE.md)
- [Governance Policies](./GOVERNANCE_POLICIES.md)
- [System Tests](./backend/voxcore/tests/test_system.py)


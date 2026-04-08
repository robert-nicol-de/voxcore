# STEP 14 INTEGRATION GUIDE — Connect All Pieces

Quick reference for how Metrics API + Dashboard work together in your VoxQuery system.

---

## 🔌 Integration Wiring Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    VOXQUERY EXECUTION                       │
│  (STEPS 1-9: Governance, Logic, Policies, Resilience)      │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ↓
┌─────────────────────────────────────────────────────────────┐
│              EXECUTION METADATA (STEP 13)                   │
│  - query_id, sql, cost_score, policies_applied             │
│  - execution_time_ms, rows_returned, tenant_enforced       │
│  - signature (SHA256 verification)                         │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ↓
┌─────────────────────────────────────────────────────────────┐
│          METRICS SERVICE (STEP 14 - PART 1)                │
│                                                             │
│  metrics.track_query(metadata)                              │
│                                                             │
│  Aggregates into:                                           │
│  - SystemMetrics (avg, p95, p99, error_rate)               │
│  - QueryMetrics (per-query details)                        │
│  - OrganizationMetrics (cost, latency by org)              │
│  - GovernanceMetrics (policies, blocks, masks)             │
│                                                             │
│  Storage: In-memory rolling window (1000 entries)          │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ↓
┌─────────────────────────────────────────────────────────────┐
│         METRICS API ENDPOINTS (STEP 14 - PART 2)           │
│                                                             │
│  GET /api/metrics/summary                                  │
│  GET /api/metrics/queries/recent                          │
│  GET /api/metrics/queries/top-cost                        │
│  GET /api/metrics/business/org/{org_id}                   │
│  GET /api/metrics/governance                              │
│  GET /api/metrics/debug/full                              │
│  ... and 9 more endpoints                                  │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ↓ (polls every 5 seconds)
┌─────────────────────────────────────────────────────────────┐
│      OPERATIONAL DASHBOARD (STEP 14 - PART 3)              │
│                                                             │
│  ┌────────────────────┬────────────────────┐              │
│  │  System Health     │   Performance      │              │
│  │  ✓ HEALTHY         │   • Avg: 234ms     │              │
│  │  • Error: 0.8%     │   • P95: 450ms     │              │
│  │  • Latency: 234ms  │   • P99: 890ms     │              │
│  │  • Queue: 12       │   • QPS: 45.2      │              │
│  └────────────────────┴────────────────────┘              │
│  ┌────────────────────┬────────────────────┐              │
│  │  Cost Tracking     │   Governance       │              │
│  │  1. Query #xyz 85  │   • Policies: 450  │              │
│  │  2. Query #abc 78  │   • Blocked: 12    │              │
│  │  3. Query #def 65  │   • Masked: 34     │              │
│  │  4-5. ...          │   • Cost Hits: 2   │              │
│  └────────────────────┴────────────────────┘              │
│                                                             │
│  Debug View: Last 20 Queries (table)                       │
│                                                             │
└─────────────────────────────────────────────────────────────┘
                         │
                         ↓ (operations team uses for:)
        ┌───────────────────────────────────────┐
        │  Visibility: Is system healthy?        │
        │  Optimization: Which queries cost most? │
        │  Scaling: Do we need more capacity?   │
        │  Compliance: Are policies working?    │
        └───────────────────────────────────────┘
```

---

## 🔧 Code Integration Points

### 1. Backend: FastAPI App Setup

```python
# main.py or app.py

from fastapi import FastAPI
from backend.routes.metrics_api import router as metrics_router
from backend.observability.metrics_service import get_metrics_service

app = FastAPI()

# Include metrics API routes
app.include_router(metrics_router)

@app.on_event("startup")
async def startup():
    """Initialize metrics service on startup"""
    metrics = get_metrics_service()
    # Service is now ready to receive metrics
    print("Metrics service initialized")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

---

### 2. Backend: Query Execution Endpoint

```python
# In your query execution route

from backend.observability.metrics_service import get_metrics_service

@app.post("/api/query/execute")
async def execute_query(request: QueryRequest):
    """
    Main query execution endpoint.
    Now tracks metrics automatically.
    """
    
    metrics = get_metrics_service()
    
    try:
        # Your existing execution logic:
        # 1. Validate user (STEP 3-4)
        # 2. Check governance (STEP 5-8)
        # 3. Generate and execute SQL (STEP 1-2)
        # 4. Apply resilience (STEP 11)
        
        result = execute_voxcore(
            user_id=request.user_id,
            org_id=request.org_id,
            question=request.question,
            # ... other args
        )
        
        # result should include:
        # {
        #     "data": [...rows...],
        #     "metadata": {
        #         "query_id": "q-abc...",
        #         "execution_time_ms": 245,
        #         "cost_score": 65,
        #         "policies_applied": [...],
        #         ...
        #     }
        # }
        
        # 🔴 KEY INTEGRATION POINT: Track the metrics
        metrics.track_query(result["metadata"])
        
        # Return full response including metadata
        return {
            "success": True,
            "data": result["data"],
            "metadata": result["metadata"]
        }
        
    except QueryExecutionError as e:
        # Even on failure, track it for error rate monitoring
        error_metadata = create_error_metadata(
            query_id=generate_query_id(),
            user_id=request.user_id,
            org_id=request.org_id,
            status="error",
            error=str(e),
        )
        metrics.track_query(error_metadata)
        
        raise
```

---

### 3. Frontend: Installation

```bash
# Make sure your frontend has these dependencies:
npm install lucide-react  # For icons

# If using Tailwind (recommended):
npm install -D tailwindcss postcss autoprefixer
npx tailwindcss init
```

---

### 4. Frontend: Routing

```jsx
// src/App.jsx or main routing file

import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import OperationalDashboard from "./pages/OperationalDashboard";

function App() {
  return (
    <Router>
      <Routes>
        {/* Existing routes */}
        <Route path="/playground" element={<Playground />} />
        <Route path="/history" element={<History />} />
        
        {/* 🔴 NEW: Operational Dashboard */}
        <Route path="/dashboard" element={<OperationalDashboard />} />
        
        {/* Catch-all */}
        <Route path="/" element={<Home />} />
      </Routes>
    </Router>
  );
}

export default App;
```

---

### 5. Frontend: Environment Configuration

```bash
# .env or .env.local

REACT_APP_API_URL=http://localhost:8000

# For production:
# REACT_APP_API_URL=https://api.voxquery.com
```

---

### 6. Frontend: Navigation (Optional)

Add a link to the dashboard in your main nav:

```jsx
// In your Navigation/Header component

<nav>
  <Link to="/playground">Playground</Link>
  <Link to="/history">History</Link>
  
  {/* 🔴 NEW: Ops dashboard link (admin only) */}
  {user?.role === "admin" && (
    <Link 
      to="/dashboard" 
      className="text-blue-500 font-semibold flex items-center gap-2"
    >
      <Zap className="w-4 h-4" /> Mission Control
    </Link>
  )}
</nav>
```

---

## 🧪 Testing the Integration

### Test 1: Verify Metrics Endpoint

```bash
# Terminal

# 1. Start your backend
python -m uvicorn main:app --reload

# 2. In another terminal, test the endpoint
curl http://localhost:8000/api/metrics/summary

# Expected response:
{
  "avg_latency_ms": 0,
  "error_rate": 0,
  "queue_depth": 0,
  ...
}
```

### Test 2: Execute a Query

```bash
# In Playground (or via API)

POST /api/query/execute
{
  "user_id": "user-1",
  "org_id": "acme-corp",
  "question": "How many sales in 2024?"
}

# Backend will:
# 1. Execute query
# 2. Create metadata
# 3. Call metrics.track_query()
# 4. Return response with metadata
```

### Test 3: Check Metrics Endpoint Again

```bash
curl http://localhost:8000/api/metrics/summary

# Response should now show:
{
  "avg_latency_ms": 245,
  "error_rate": 0,
  "throughput_qps": 1,
  ...
}
```

### Test 4: View Dashboard

```
http://localhost:3000/dashboard

# Should show:
- 4-panel layout
- System health
- Performance metrics
- Cost tracking
- Governance stats
- Recent queries table
```

---

## 📊 Common Integration Issues

### Issue: Dashboard shows 0 metrics

**Cause:** Metrics service not being called

**Fix:**
```python
# Check that execute_query endpoint calls:
metrics = get_metrics_service()
metrics.track_query(result["metadata"])  # ← This must be called
```

### Issue: API returns 404

**Cause:** Router not registered

**Fix:**
```python
# In main.py:
from backend.routes.metrics_api import router as metrics_router
app.include_router(metrics_router)  # ← Must be added
```

### Issue: Dashboard shows "Failed to refresh metrics"

**Cause:** API URL misconfigured or CORS issue

**Fix:**
```jsx
// In OperationalDashboard.jsx, check:
const API_BASE = process.env.REACT_APP_API_URL || "http://localhost:8000";

// For CORS (if needed):
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## 🚀 Deployment Checklist

- [ ] Backend
  - [ ] Metrics API endpoints deployed
  - [ ] MetricsService initialized
  - [ ] Query execution calls metrics.track_query()
  - [ ] CORS configured for frontend URL
  - [ ] AlertingService integrated (optional)

- [ ] Frontend
  - [ ] OperationalDashboard component copied
  - [ ] Routes configured
  - [ ] API_BASE URL set correctly
  - [ ] Lucide React icons available
  - [ ] Dashboard accessible at /dashboard

- [ ] Testing
  - [ ] Execute a test query
  - [ ] Verify metrics appear in dashboard
  - [ ] Check that error queries are tracked
  - [ ] Verify org metrics show correct totals

- [ ] Operations
  - [ ] Team knows about new dashboard
  - [ ] Add to runbooks/documentation
  - [ ] Monitor metrics API performance
  - [ ] Set up alerting on dashboard itself (future)

---

## 📈 Success Indicators

You'll know it's working when:

✅ Dashboard loads without errors
✅ System health panel shows real metrics
✅ Queries appear in debug view within 10 seconds
✅ Cost tracking panel shows query costs
✅ Gov metrics panel shows policy count > 0 (after several queries)
✅ Error rate changes when you intentionally fail a query
✅ Latency percentiles update as queries run
✅ Performance graphs are visible (not empty)

---

## 🔐 Security: Restricting Dashboard Access

For production, add authentication:

```python
# In metrics_api.py, add to all endpoints:

from backend.auth import require_admin_role

@router.get("/api/metrics/summary")
async def get_metrics_summary(
    current_user: User = Depends(require_admin_role)
) -> Dict[str, Any]:
    metrics_service = get_metrics_service()
    return metrics_service.get_system_metrics().__dict__
```

Then in frontend:

```jsx
function ProtectedDashboard() {
  const { user } = useAuth();
  
  if (!user || user.role !== "admin") {
    return <div>Access denied</div>;
  }
  
  return <OperationalDashboard />;
}
```

---

## 📞 Support / Debugging

**Dashboard blank:** Check browser console for errors
**Metrics API 500:** Check backend logs for exception
**No data in table:** Execute a query first, then refresh
**Slow to load:** Normal for first 5 seconds (waiting for API)

---

## 🎯 What's Next

Once this is deployed and working:

**STEP 15:** Scaling & Load Balancing
- Deploy to Kubernetes
- Add Redis backing for MetricsService
- Configure horizontal scaling

**STEP 16:** Advanced Features
- Cost budgets per organization
- SLO tracking (p99 < 2s)
- Custom alert rules
- Query cost estimation before execution

**STEP 17:** Data Warehouse Integration
- Archive metrics to PostgreSQL
- Historical trend analysis
- Predictive scaling based on patterns

---

## 📝 Quick Reference: Files to Copy

Copy these files to your project:

```
✅ backend/routes/metrics_api.py (100 LOC)
   → Add to your backend/routes/ directory
   → Include in app router

✅ frontend/src/pages/OperationalDashboard.jsx (400+ LOC)
   → Add to your frontend/src/pages/ directory
   → Include in router as shown above
```

Everything else (MetricsService, AlertingService) already exists from STEP 13-14.

---

**Total integration time:** ~15 minutes

**Time to first dashboard view:** ~5 minutes after adding routes

**Monitoring up and running:** Immediately after first query executes

✅ **You're good to go!**

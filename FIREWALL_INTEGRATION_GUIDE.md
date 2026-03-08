# 🔥 AI Firewall Integration Guide

## Overview
This guide walks through integrating the firewall into your main query pipeline. The firewall inspects all AI-generated SQL queries BEFORE execution, blocking dangerous operations and logging activity.

## Pipeline Architecture

```
Query Question
      ↓
SQL Generator (OpenAI)
      ↓
[FIREWALL LAYER] ← Inspect Risk & Policies
      ↓
Governance Check ← Database audit trail
      ↓
Execute Query
      ↓
Return Results
```

## Files Created

### Backend Files
- ✅ `firewall/__init__.py` - Module entry point
- ✅ `firewall/risk_scoring.py` - Risk analysis (0-100 score)
- ✅ `firewall/policy_check.py` - 6 security policies
- ✅ `firewall/firewall_engine.py` - Main orchestration
- ✅ `firewall/event_log.py` - Event logging & analytics
- ✅ `firewall/integration.py` - Integration middleware
- ✅ `api/routes/firewall.py` - API endpoints (updated with /dashboard)

### Frontend Files
- ✅ `frontend/src/components/FirewallDashboard.jsx` - React dashboard widget

## Integration Steps

### Step 1: Update Main Query Route

Edit `api/routes/query.py` to integrate firewall:

```python
from ..firewall.integration import firewall_integration  # Add this import

@router.post("/query")
async def ask_query(request: QueryRequest):
    """Main query endpoint with firewall protection"""
    
    # 1. Generate SQL from question
    sql_query = generate_sql_from_question(request.question)  # Your existing logic
    
    # 2. Process through firewall
    firewall_result = firewall_integration.process_generated_sql(
        question=request.question,
        generated_sql=sql_query,
        user=request.user_id,
        database=request.database,
        session_id=request.session_id
    )
    
    # 3. Check if query is allowed
    if not firewall_result["allowed"]:
        return {
            "status": "blocked",
            "error": f"Query blocked by firewall: {firewall_result['reason']}",
            "action": firewall_result["action"],
            "risk_score": firewall_result["risk_score"],
            "violations": firewall_result["violations"],
            "recommendations": firewall_result["recommendations"]
        }
    
    # 4. Execute query (original logic continues)
    results = execute_query(firewall_result["query"])
    
    # 5. Return results
    return {
        "status": "success",
        "results": results,
        "firewall_check": {
            "risk_score": firewall_result["risk_score"],
            "action": firewall_result["action"]
        }
    }
```

### Step 2: Register Firewall Routes

Edit `api/main.py` to register firewall endpoints:

```python
from fastapi import FastAPI
from .routes import query, firewall  # Add firewall route import

app = FastAPI()

# Register routers
app.include_router(query.router)
app.include_router(firewall.router)  # Add this line
```

### Step 3: Add Dashboard Widget to Frontend

Edit `frontend/src/pages/Dashboard.jsx`:

```javascript
import React from 'react';
import FirewallDashboard from '../components/FirewallDashboard';

export default function Dashboard() {
  return (
    <div className="dashboard-container">
      {/* Existing dashboard content */}
      <div className="dashboard-grid">
        <div className="dashboard-section">
          {/* Your other widgets */}
        </div>
        
        {/* NEW: Firewall Dashboard Widget */}
        <div className="firewall-widget">
          <FirewallDashboard />
        </div>
      </div>
    </div>
  );
}
```

### Step 4: Test Firewall Integration

#### Test 1: Blocked Query (DROP TABLE)
```bash
curl -X POST https://voxcore.org/api/v1/firewall/inspect \
  -H "Content-Type: application/json" \
  -d '{
    "sql_query": "DROP TABLE users",
    "context": {"user": "test", "database": "main"}
  }'
```

**Expected Response:**
```json
{
  "timestamp": "2024-01-15T10:30:00Z",
  "query": "DROP TABLE users",
  "risk_score": 95,
  "risk_level": "HIGH",
  "action": "block",
  "reason": "DROP statement violates policy: No DROP operations allowed",
  "violations": ["CRITICAL: DROP operations not allowed"],
  "recommendations": ["Use DELETE with WHERE clause instead"]
}
```

#### Test 2: Rewrite Query (DELETE without WHERE)
```bash
curl -X POST https://voxcore.org/api/v1/firewall/inspect \
  -H "Content-Type: application/json" \
  -d '{
    "sql_query": "DELETE FROM users",
    "context": {"user": "test", "database": "main"}
  }'
```

**Expected Response:**
```json
{
  "timestamp": "2024-01-15T10:31:00Z",
  "query": "DELETE FROM users",
  "risk_score": 85,
  "risk_level": "HIGH",
  "action": "rewrite",
  "reason": "DELETE lacks WHERE clause - HIGH risk detected",
  "violations": ["CRITICAL: DELETE requires WHERE clause"],
  "recommendations": ["Add WHERE clause to limit rows affected"]
}
```

#### Test 3: Safe Query (SELECT with conditions)
```bash
curl -X POST https://voxcore.org/api/v1/firewall/inspect \
  -H "Content-Type: application/json" \
  -d '{
    "sql_query": "SELECT id, name FROM users WHERE active = 1 LIMIT 10",
    "context": {"user": "test", "database": "main"}
  }'
```

**Expected Response:**
```json
{
  "timestamp": "2024-01-15T10:32:00Z",
  "query": "SELECT id, name FROM users WHERE active = 1 LIMIT 10",
  "risk_score": 15,
  "risk_level": "LOW",
  "action": "allow",
  "reason": "Query passes all safety checks",
  "violations": [],
  "recommendations": []
}
```

## Firewall Decision Logic

### Low Risk (0-30)
```
✅ ALLOW
- Simple SELECT queries
- Queries with WHERE clauses
- No sensitive columns accessed
```

### Medium Risk (31-60)
```
⚠️  REWRITE
- SELECT * queries (allow but log)
- UPDATE/DELETE without WHERE (block)
- Potential injection patterns (block)
```

### High Risk (61-100)
```
🚫 BLOCK
- DROP, TRUNCATE statements
- Destructive operations
- Direct system table access
- SQL injection patterns
```

## Security Policies Enforced

| Policy | Action | Priority |
|--------|--------|----------|
| No DROP TABLE / TRUNCATE | BLOCK | CRITICAL |
| DELETE requires WHERE | REWRITE | CRITICAL |
| UPDATE requires WHERE | REWRITE | CRITICAL |
| No sensitive column access | FLAG | HIGH |
| No TRUNCATE statements | BLOCK | HIGH |
| No system table access | BLOCK | CRITICAL |

## Dashboard Features

### Real-time Statistics
- **Total Inspected**: All queries evaluated
- **Blocked**: Dangerous queries prevented
- **High Risk**: Potential issues flagged
- **Block Rate**: % of queries denied

### Risk Distribution Chart
- **Low**: Safe queries (green)
- **Medium**: Flagged queries (yellow)
- **High**: Dangerous queries (red)

### Recent Blocked Queries
- Timestamp of block
- SQL query text
- Violations triggered
- Recommended fixes

### High Risk Tracking
- Risk score (0-100)
- Query excerpt
- Action taken
- User & database info

## API Endpoints

### 1. Inspect Single Query
```
POST /api/v1/firewall/inspect
Content-Type: application/json

{
  "sql_query": "SELECT * FROM users",
  "context": {
    "user": "admin",
    "database": "main",
    "session_id": "abc123"
  }
}
```

### 2. Get Dashboard Data
```
GET /api/v1/firewall/dashboard

Response:
{
  "stats": {...},
  "recent_events": [...],
  "blocked_events": [...],
  "high_risk_events": [...]
}
```

### 3. Get Active Policies
```
GET /api/v1/firewall/policies

Response:
[
  {
    "id": "policy_1",
    "name": "No DROP operations",
    "description": "Prevents DROP TABLE/DATABASE",
    "priority": "CRITICAL"
  },
  ...
]
```

### 4. Batch Test Queries
```
POST /api/v1/firewall/test-query
Content-Type: application/json

{
  "sql_query": "SELECT * FROM users; DELETE FROM users; SELECT id FROM products"
}
```

### 5. Health Check
```
GET /api/v1/firewall/health

Response:
{
  "status": "healthy",
  "enabled": true,
  "event_buffer": 156,
  "timestamp": "2024-01-15T10:30:00Z"
}
```

## Deployment Checklist

- [ ] **Step 1**: Update main query route with firewall_integration.process_generated_sql()
- [ ] **Step 2**: Register firewall routes in api/main.py
- [ ] **Step 3**: Add FirewallDashboard component to frontend Dashboard page
- [ ] **Step 4**: Update frontend package imports (if using TypeScript, add types)
- [ ] **Step 5**: Test firewall endpoints with curl or Postman
- [ ] **Step 6**: Deploy to server (backend code in /home/voxcoreo/VOXCORE/)
- [ ] **Step 7**: Monitor firewall dashboard for suspicious activity
- [ ] **Step 8**: Fine-tune policies based on real usage patterns

## Advanced Configuration

### Custom Risk Scoring

Edit `firewall/risk_scoring.py` to customize risk thresholds:

```python
class RiskScorer:
    RISK_WEIGHTS = {
        "destructive": 35,      # DROP, DELETE, UPDATE
        "sensitive_columns": 25,  # salary, email, ssn
        "injection_patterns": 20,  # SQL injection attempts
        "select_star": 10,       # SELECT *
        "suspicious_patterns": 15  # Unusual syntax
    }
```

### Custom Policies

Edit `firewall/policy_check.py` to add new policies:

```python
def _check_custom_policy(self, query: str) -> Optional[str]:
    """Add custom policy enforcement"""
    
    if "CUSTOM_KEYWORD" in query.upper():
        return "CUSTOM: Your policy violation message"
    
    return None
```

### Event Persistence

By default, firewall events are stored in memory (max 1000 events). To persist to database:

```python
# In firewall/event_log.py
def log_event(self, event: FirewallEvent):
    """Store event in memory and database"""
    
    # In-memory storage (current)
    self.events.append(event)
    
    # Database storage (add this)
    db.firewall_events.insert({
        "timestamp": event.timestamp,
        "query": event.query,
        "risk_score": event.risk_score,
        "action": event.action,
        "user": event.user,
        "database": event.database
    })
```

## Troubleshooting

### Firewall blocking legitimate queries?
1. Check the violation reason in /api/v1/firewall/dashboard
2. Review the specific policy in firewall/policy_check.py
3. Adjust policy thresholds if needed
4. Test with /api/v1/firewall/test-query

### Dashboard not loading?
1. Verify /api/v1/firewall/dashboard endpoint is responding
2. Check browser console for API errors
3. Confirm firewall routes registered in main.py
4. Restart backend service

### High false positive rate?
1. Lower risk_score thresholds in risk_scoring.py
2. Review risk_factors returned from inspection
3. Adjust RISK_WEIGHTS for your use case
4. Test with real queries to calibrate

## Production Recommendations

✅ **ENABLED**:
- Policy enforcement (block DROP, DELETE without WHERE)
- Risk scoring on all queries
- Event logging to database
- Firewall dashboard monitoring

⚠️ **CONSIDER**:
- Database persistence for events (instead of in-memory)
- Admin console for policy management
- Alerts/notifications for high-risk queries
- Query rewrite automation (convert DELETE to UPDATE)
- Rate limiting per user/database

🔒 **SECURITY**:
- Protect /api/v1/firewall/ endpoints with authentication
- Log all firewall decisions to audit table
- Monitor for privilege escalation attempts
- Regular policy reviews and updates
- Quarterly firewall effectiveness reports

## Next Steps

1. **Upload backend** to server (voxcore/voxquery folder)
2. **Test firewall endpoints** via curl/Postman
3. **Monitor dashboard** for real query patterns
4. **Fine-tune policies** based on actual usage
5. **Add frontend widget** to governance dashboard
6. **Enable database logging** for compliance

---

**Version**: 1.0
**Last Updated**: 2024-01-15
**Status**: Production Ready

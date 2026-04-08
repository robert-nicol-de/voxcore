# 🔒 VOXCORE EXECUTION FLOW

## Before (Uncontrolled)
```
Query Request
    ↓
[Direct to SQL Pipeline]
    ↓
[Execute SQL] ← Anyone could call this directly, bypassing governance
    ↓
Results
```

**Problem:** Queries can bypass governance, cost limits ignored, no audit trail

---

## After (Governed - STEP 1 Complete)
```
Query Request
    ↓
┌─────────────────────────────────────────┐
│    VoxCoreEngine.execute_query()        │
│    (Central Governance Layer)           │
└─────────────────────────────────────────┘
    ↓
[1️⃣ RBAC Check]
├─ Does user have "queries.run"?
├─ Deny → Return "Access Denied" error
└─ Allow → Continue
    ↓
[2️⃣ Column Filtering]
├─ Extract tables from SQL
├─ Get allowed columns per user
├─ Rewrite SQL (filter columns, add row filters)
└─ Continue with filtered SQL
    ↓
[3️⃣ Cost Analysis]
├─ Analyze SQL structure (joins, filters, etc.)
├─ Estimate cost score (0-100)
├─ Cost 0-40    → Continue
├─ Cost 40-70   → Continue with WARNING
├─ Cost 70+     → Reject "Too expensive"
    ↓
[4️⃣ Policy Evaluation]
├─ Check for destructive ops (DROP, DELETE, etc.)
├─ Check for sensitive data access
├─ Check risk score thresholds
├─ Decision: ALLOW / REQUIRE_APPROVAL / BLOCK
    ↓
[5️⃣ Audit Log]
├─ Record user_id, question, sql
├─ Record cost_score, cost_level
├─ Record approval status + reason
    ↓
[6️⃣ Execute SQL]
├─ Run on database with timeout
├─ Return results
    ↓
ExecutionResult {
    success: true/false
    data: [rows] or null
    cost_score: 0-100
    cost_level: "safe" | "warning" | "blocked"
    error: null or error message
    warnings: [...additional notices...]
}
```

---

## Data Flow Diagram

```
┌────────────────────────┐
│   Frontend (React)     │
│  Playground.jsx        │
└───────────┬────────────┘
            │
            ↓
┌────────────────────────────────────────┐
│  backend/routers/query.py              │
│  POST /query                           │
│  ├─ session_service.get_or_create()   │
│  ├─ get_voxcore()                     │
│  └─ engine.execute_query()  ← ⭐ ENTRY POINT
└───────────┬────────────────────────────┘
            │
            ↓
┌──────────────────────────────────────────────┐
│   voxcore/engine/core.py                     │
│   VoxCoreEngine                              │
│                                              │
│   ┌──────────────────────────────────────┐  │
│   │ 1. _check_rbac_access()              │  │
│   │    └─→ PermissionEngine.check_access()│ │
│   └──────────────────────────────────────┘  │
│                                              │
│   ┌──────────────────────────────────────┐  │
│   │ 2. _apply_column_filtering()         │  │
│   │    └─→ SQL rewriting (ready to impl) │  │
│   └──────────────────────────────────────┘  │
│                                              │
│   ┌──────────────────────────────────────┐  │
│   │ 3. _estimate_and_validate_cost()     │  │
│   │    ├─→ analyze_sql_structure()       │  │
│   │    ├─→ estimate_query_cost()         │  │
│   │    └─→ Compare: 0-40 safe / 70+ bad  │  │
│   └──────────────────────────────────────┘  │
│                                              │
│   ┌──────────────────────────────────────┐  │
│   │ 4. _evaluate_policies()              │  │
│   │    └─→ PolicyEngine.evaluate()       │  │
│   └──────────────────────────────────────┘  │
│                                              │
│   ┌──────────────────────────────────────┐  │
│   │ 5. _audit_log_execution()            │  │
│   │    └─→ org_store.audit_log_query()   │  │
│   └──────────────────────────────────────┘  │
│                                              │
│   ┌──────────────────────────────────────┐  │
│   │ 6. _execute_sql()                    │  │
│   │    └─→ cursor.execute(sql)           │  │
│   └──────────────────────────────────────┘  │
│                                              │
│   Return ExecutionResult                     │
└───────────┬──────────────────────────────────┘
            │
            ↓
┌────────────────────────────────────────┐
│  voxcore/engine/sql_pipeline.py        │
│  (Deprecated legacy path)              │
│  Now redirects to VoxCoreEngine        │
└────────────────────────────────────────┘

┌────────────────────────────────────────┐
│  voxcore/engine/explain_my_data.py     │
│  AutoInsight Discovery                 │
│  ├─ run_top_performers()  ← governed   │
│  ├─ run_growth_analysis() ← governed   │
│  ├─ run_decline_analysis() ← governed  │
│  └─ ...10 total functions              │
└────────────────────────────────────────┘

┌────────────────────────────────────────┐
│  voxcore/engine/exploration_engine.py  │
│  Background Exploration                │
│  └─ run_exploration_queries() ← gov.   │
└────────────────────────────────────────┘
```

---

## Cost Scoring Flow

```
SQL Query Input
    ↓
analyze_sql_structure()
├─ Count JOINs (each = +10 cost)
├─ Check WHERE filter (no filter = +25 cost)
├─ Estimate rows (more rows = more cost)
└─ Output: metadata {join_count, has_filter, ...}
    ↓
estimate_query_cost()
├─ Base score from joins
├─ Multiplier from row count
├─ Subtraction if filtered
└─ Output: cost_score (0-100)
    ↓
validate_cost()
├─ If cost ≤ 40    → SAFE (green ✅)
├─ If 40 < cost ≤ 70 → WARNING (yellow ⚠️)
├─ If cost > 70    → BLOCKED (red ❌)
    ↓
ExecutionResult.cost_level = "safe" | "warning" | "blocked"
```

---

## Permission Check Flow

```
User makes request
    ↓
Extract user_id from session
    ↓
Permission Engine
├─ Check Redis cache (300s TTL)
├─ If cached "approved" → CONTINUE
├─ If not cached:
│   ├─ Query DB: user_id → queries.run relation
│   ├─ If YES → Cache and CONTINUE
│   ├─ If NO → Cache "denied" and BLOCK
│   └─ Check workspace inheritance
└─ Cache relationships for 5 minutes
    ↓
Result: allowed=true/false
```

---

## Audit Trail Storage

```
Every Query Execution → org_store.audit_log_query_execution()
    │
    ├─ user_id           (who made request)
    ├─ org_id            (which org)
    ├─ workspace_id      (which workspace)
    ├─ session_id        (which session)
    ├─ question          (natural language)
    ├─ sql               (generated SQL)
    ├─ cost_score        (0-100)
    ├─ status            (approved/blocked)
    ├─ error             (error message if blocked)
    ├─ policy_decision   (allow/block/require_approval)
    ├─ timestamp         (when)
    └─ ip_address        (from where)
```

---

## Cost Examples

### Safe (0-40)
```sql
SELECT product, SUM(revenue)
FROM sales
WHERE year = 2024
GROUP BY product
LIMIT 5
-- 0 JOINs, has WHERE, safe = COST ~20
```

### Warning (40-70)
```sql
SELECT s.product, c.region, SUM(s.revenue)
FROM sales s
JOIN customers c ON s.customer_id = c.id
WHERE s.year = 2024
GROUP BY s.product, c.region
LIMIT 10
-- 1 JOIN, has WHERE, moderate = COST ~55
```

### Blocked (70+)
```sql
SELECT *
FROM sales s
JOIN customers c ON s.customer_id = c.id
JOIN products p ON s.product_id = p.id
JOIN orders o ON s.order_id = o.id
JOIN market_data m ON c.region_id = m.region_id
-- 4+ JOINs, no WHERE = COST ~85+ → BLOCKED ❌
```

---

## Response Format

### Success (Query Approved)
```json
{
  "success": true,
  "data": [[...rows...]],
  "cost_score": 35,
  "cost_level": "safe",
  "is_approved": true,
  "runtime_ms": 145.2,
  "warnings": []
}
```

### Warning (Query Approved but Expensive)
```json
{
  "success": true,
  "data": [[...rows...]],
  "cost_score": 62,
  "cost_level": "warning",
  "is_approved": true,
  "runtime_ms": 820.5,
  "warnings": [
    "⚠️ Query cost (62) is elevated. Consider adding filters or simplifying joins."
  ]
}
```

### Blocked (Query Rejected)
```json
{
  "success": false,
  "data": null,
  "cost_score": 85,
  "cost_level": "blocked",
  "is_approved": false,
  "error": "Query blocked: cost score 85 exceeds limit (70). Add WHERE filters or simplify joins.",
  "warnings": []
}
```

### Access Denied
```json
{
  "success": false,
  "data": null,
  "error": "User user_123 lacks permission to execute queries",
  "cost_score": 0,
  "cost_level": "blocked"
}
```

---

## Integration Checklist

- [x] VoxCoreEngine created & integrated
- [x] RBAC checks implemented
- [x] Cost thresholds updated (0-40 safe, 40-70 warn, 70+ block)
- [x] Policy evaluation hooks added
- [x] Audit logging integrated
- [x] Query router updated
- [x] SQL pipeline updated
- [x] Explain My Data governed
- [x] Exploration engine governed
- [x] All 6 execution steps documented
- [x] Error handling & graceful degradation
- [x] Zero external dependencies

---

**STEP 1: EXECUTION GOVERNANCE LOCKDOWN - ✅ COMPLETE**

Next: STEP 2 - Column filtering, approval queue, cost optimization hints

# 🔒 VoxCore Execution Governance - Integration Guide

## STEP 1: ✅ GOVERNANCE LOCKDOWN COMPLETE

All query execution now routes through VoxCoreEngine with:
- ✅ RBAC permission checks
- ✅ Column-level access filtering (placeholder, ready for implementation)
- ✅ Cost validation (0-40 safe, 40-70 warn, 70+ block)
- ✅ Policy evaluation (destructive ops, sensitive data, risk scoring)
- ✅ Audit trail logging

---

## How to Use VoxCoreEngine

### Basic Pattern

```python
from voxcore.engine.core import get_voxcore

engine = get_voxcore()

result = engine.execute_query(
    question="User's natural language question",
    generated_sql="SELECT ... FROM ...",
    platform="postgres",  # or "mssql", "snowflake", etc.
    user_id=current_user.id,
    connection=db_connection,
    session_id=session_id,
    workspace_id=workspace_id,  # optional
)

if result.success:
    print(f"✅ Query approved (cost: {result.cost_score})")
    data = result.data
else:
    print(f"❌ Query blocked: {result.error}")
```

### Response Object

```python
@dataclass
class ExecutionResult:
    success: bool                # True if query executed
    data: Any = None             # Query results
    error: Optional[str] = None  # Error message if blocked
    cost_score: int = 0          # Cost (0-100)
    cost_level: str = "safe"     # safe, warning, blocked
    is_approved: bool = False    # User has permission
    runtime_ms: float = 0.0      # Execution time
    warnings: List[str] = None   # Additional messages
```

---

## Cost Thresholds

| Score | Level | Behavior |
|-------|-------|----------|
| 0-40 | **SAFE** | ✅ Execute immediately, user sees "approved" |
| 40-70 | **WARNING** | ⚠️ Execute but display warning, suggest optimization |
| 70+ | **BLOCKED** | ❌ Reject with error message, suggest simplification |

### Examples

**Safe Query (cost 25):**
```
SELECT product, SUM(revenue) 
FROM sales 
WHERE year = 2024
GROUP BY product LIMIT 5
```

**Warning Query (cost 55):**
```
SELECT s.product, c.region, SUM(s.revenue)
FROM sales s
JOIN customers c ON s.customer_id = c.id
WHERE s.year = 2024
GROUP BY s.product, c.region
```

**Blocked Query (cost 85):**
```
SELECT *
FROM sales s
JOIN customers c ON s.customer_id = c.id
JOIN products p ON s.product_id = p.id
JOIN regions r ON c.region_id = r.id
JOIN market_data m ON r.id = m.region_id
WHERE s.year >= 2020
-- 4+ joins without filters = expensive
```

---

## Where VoxCoreEngine Is Used

### ✅ Already Integrated

1. **backend/routers/query.py**
   - Main `/query` endpoint routes through engine
   - Returns cost_score and cost_level in response

2. **voxcore/engine/sql_pipeline.py**
   - Deprecated legacy execution
   - Now redirects to engine for governed execution
   - Fallback path available if engine unavailable

3. **voxcore/engine/explain_my_data.py**
   - All 10 insight discovery algorithms governed
   - EMD queries limited by cost threshold
   - run_query_with_cache() checks governance

4. **voxcore/engine/exploration_engine.py**
   - Background exploration queries governed
   - Won't flood DB with expensive queries

---

## RBAC Integration

All users must have `"queries.run"` permission to execute queries.

### Role Permissions (backend/services/rbac.py)

```python
ROLE_PERMISSIONS = {
    "admin": [..., "queries.run", ...],
    "ai_analyst": ["queries.run", ...],
    "viewer": [],  # Cannot run queries
    "data_guardian": ["queries.approve", ...],
}
```

If user lacks permission:
```
HTTP 403: User {user_id} lacks permission to execute queries
```

---

## Policy Engine Integration

Blocks queries that:
- 🚫 Are destructive (DROP, DELETE, TRUNCATE, ALTER)
- 🚫 Access sensitive columns as non-admin
- 🚫 Exceed risk threshold (80+)

Requires approval if:
- ⚠️ cost_score > 70 (in policy config)
- ⚠️ High-risk analytical patterns detected

---

## Audit Trail

Every query is logged with:
```python
org_store.audit_log_query_execution(
    user_id=user_id,
    org_id=org_id,
    workspace_id=workspace_id,
    session_id=session_id,
    question=question,
    sql=generated_sql,
    cost_score=cost_score,
    status="approved",  # or "blocked"
    error=error_msg,
    policy_decision=decision,
)
```

---

## Column Filtering (Ready for Implementation)

Currently a placeholder in `_apply_column_filtering()`.

To implement:
```python
# 1. Extract tables from SQL
# 2. Get allowed columns: permission_engine.get_allowed_columns(user_id, table)
# 3. Rewrite SQL: ALTER SELECT to only include allowed columns
# 4. Add WHERE filters: Only show rows user can access

# Example: User can see sales, but not revenue or profit
# Original: SELECT product, revenue, profit FROM sales
# After filtering: SELECT product FROM sales
```

---

## Next Phase: STEP 2

1. **Implement Column Filtering**
   - Add get_allowed_columns() to PermissionEngine
   - Implement SQL rewriting in _apply_column_filtering()

2. **Add Approval Queue**
   - When policy_decision = "require_approval"
   - Queue in approval_queue instead of blocking

3. **Cost Optimization Suggestions**
   - When cost between 40-70, suggest optimizations
   - Example: "Add WHERE filter to reduce scanned rows"

4. **Monitor and Alert**
   - Track frequently blocked queries
   - Alert admins to cost patterns

---

## Testing VoxCoreEngine

### Test Case 1: Safe Query
```python
result = engine.execute_query(
    question="Top 5 products",
    generated_sql="SELECT product, SUM(revenue) FROM sales GROUP BY product LIMIT 5",
    platform="postgres",
    user_id="user_123",
    connection=conn,
)
assert result.success == True
assert result.cost_level == "safe"
assert 0 <= result.cost_score <= 40
```

### Test Case 2: Blocked Query
```python
result = engine.execute_query(
    question="All data",
    generated_sql="SELECT * FROM sales",
    platform="postgres",
    user_id="user_123",
    connection=conn,
)
# Should block if cost > 70
```

### Test Case 3: Access Denied
```python
result = engine.execute_query(
    question="...",
    generated_sql="...",
    platform="postgres",
    user_id="user_no_perms",  # viewer role, no queries.run
    connection=conn,
)
assert result.success == False
assert "lacks permission" in result.error
```

---

## Cost Tuning

If you want to adjust thresholds, update `_get_cost_level()` in core.py:

```python
def _get_cost_level(self, cost_score: int) -> str:
    if cost_score <= 35:      # Changed from 40
        return "safe"
    elif cost_score <= 65:    # Changed from 70
        return "warning"
    else:
        return "blocked"
```

Then update blocking logic:
```python
if cost_score > 65:  # Changed from 70
    raise Exception(f"Query too expensive (cost: {cost_score}/100). Max allowed: 65.")
```

---

## Quick Troubleshooting

| Issue | Cause | Solution |
|-------|-------|----------|
| "Query blocked by policy" | Destructive SQL or sensitive columns | Rewrite query to be SELECT-only or use approved tables |
| "PermissionEngine not initialized" | Security DB unavailable | Check org_store connections, will run in permissive mode |
| "cost > 70" | Expensive query (multiple joins, no WHERE) | Add WHERE filters, reduce joins, simplify SELECT |
| "User lacks permission" | RBAC role doesn't have queries.run | Assign admin/analyst role or add permission |

---

**Status:** ✅ STEP 1 Complete | ⏳ STEP 2 Ready

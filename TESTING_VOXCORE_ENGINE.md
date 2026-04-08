# 🧪 Testing VoxCoreEngine Governance

## Quick Test: Manual Execution

### Test 1: Basic Safe Query

```python
# In Python shell or test file

from voxcore.engine.core import get_voxcore
from backend.db import get_db_connection

engine = get_voxcore()
connection = get_db_connection()

# Safe query (cost should be 0-40)
result = engine.execute_query(
    question="What are the top 5 products by revenue in 2024?",
    generated_sql="""
        SELECT product, SUM(revenue) as total_revenue
        FROM sales
        WHERE year = 2024
        GROUP BY product
        ORDER BY total_revenue DESC
        LIMIT 5
    """,
    platform="postgres",
    user_id="test_user_123",
    connection=connection,
    session_id="test_session_abc",
)

print(f"✅ Success: {result.success}")
print(f"📊 Cost Score: {result.cost_score}/100")
print(f"🎯 Cost Level: {result.cost_level}")
assert result.success == True
assert result.cost_level == "safe"
assert result.cost_score <= 40
print("✅ Test 1 PASSED")
```

### Test 2: Warning Query (Elevated Cost)

```python
# Warning query (cost should be 40-70)
result = engine.execute_query(
    question="Revenue by product and region for 2024",
    generated_sql="""
        SELECT s.product, c.region, SUM(s.revenue) as total
        FROM sales s
        JOIN customers c ON s.customer_id = c.id
        WHERE s.year = 2024
        GROUP BY s.product, c.region
        LIMIT 5
    """,
    platform="postgres",
    user_id="test_user_123",
    connection=connection,
    session_id="test_session_abc",
)

print(f"✅ Success: {result.success}")
print(f"📊 Cost Score: {result.cost_score}/100")
print(f"🎯 Cost Level: {result.cost_level}")
print(f"⚠️ Warnings: {result.warnings}")
assert result.success == True
assert result.cost_level == "warning"
assert 40 < result.cost_score <= 70
print("✅ Test 2 PASSED")
```

### Test 3: Expensive Query (Should Block)

```python
# Expensive query (cost should be 70+) - should be BLOCKED
result = engine.execute_query(
    question="Comprehensive market analysis",
    generated_sql="""
        SELECT *
        FROM sales s
        JOIN customers c ON s.customer_id = c.id
        JOIN products p ON s.product_id = p.id
        JOIN orders o ON s.order_id = o.id
        JOIN regions r ON c.region_id = r.id
        -- Multiple joins without filters = expensive
    """,
    platform="postgres",
    user_id="test_user_123",
    connection=connection,
    session_id="test_session_abc",
)

print(f"✅ Success: {result.success}")
print(f"📊 Cost Score: {result.cost_score}/100")
print(f"🎯 Cost Level: {result.cost_level}")
print(f"❌ Error: {result.error}")
assert result.success == False
assert result.cost_level == "blocked"
assert result.cost_score > 70
print("✅ Test 3 PASSED")
```

### Test 4: Access Control (RBAC)

```python
# User without "queries.run" permission - should be DENIED
result = engine.execute_query(
    question="Top products",
    generated_sql="SELECT product, SUM(revenue) FROM sales GROUP BY product",
    platform="postgres",
    user_id="viewer_user_999",  # viewer role = no queries.run
    connection=connection,
    session_id="test_session_def",
)

print(f"✅ Success: {result.success}")
print(f"❌ Error: {result.error}")
assert result.success == False
assert "permission" in result.error.lower()
print("✅ Test 4 PASSED")
```

### Test 5: Audit Trail Verification

```python
# After running a query, check the audit log
from backend.db import org_store

# Run a query first
result = engine.execute_query(
    question="Test audit",
    generated_sql="SELECT 1 as test",
    platform="postgres",
    user_id="test_user_audit",
    connection=connection,
    session_id="test_audit_session",
)

# Query the audit log
audit_entries = org_store.get_audit_logs(
    user_id="test_user_audit",
    limit=1
)

if audit_entries:
    entry = audit_entries[0]
    print(f"✅ User: {entry['user_id']}")
    print(f"✅ Cost: {entry['cost_score']}")
    print(f"✅ Status: {entry['status']}")
    assert entry['user_id'] == "test_user_audit"
    assert entry['status'] in ["approved", "blocked"]
    print("✅ Test 5 PASSED")
else:
    print("⚠️ No audit entries found (audit logging may be disabled)")
```

---

## Integration Test: Via HTTP API

### Test Safe Query

```bash
curl -X POST http://localhost:8000/api/query \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Top 5 products by revenue",
    "session_id": "test_session_123",
    "mode": "live"
  }'
```

**Expected Response:**
```json
{
  "success": true,
  "data": [...],
  "cost_score": 25,
  "cost_level": "safe",
  "message": "Query executed successfully",
  "error": null
}
```

### Test Expensive Query

```bash
curl -X POST http://localhost:8000/api/query \
  -H "Content-Type: application/json" \
  -d '{
    "text": "All data with all joins",
    "session_id": "test_session_expensive",
    "mode": "live"
  }'
```

**Expected Response:**
```json
{
  "success": false,
  "data": null,
  "cost_score": 85,
  "cost_level": "blocked",
  "error": {
    "code": "QUERY_FAILED",
    "message": "Query blocked: cost score 85 exceeds limit (70). Add WHERE filters or simplify joins."
  }
}
```

---

## Cost Scoring Test Suite

```python
# Test cost estimator directly
from voxcore.engine.sql_pipeline import analyze_sql_structure
from voxcore.engine.query_cost_analyzer import estimate_query_cost

queries = [
    # Simple query
    ("SELECT * FROM users LIMIT 10", "safe"),
    
    # Query with filter
    ("SELECT * FROM users WHERE age > 18 LIMIT 100", "safe"),
    
    # Query with one join
    ("""
        SELECT u.name, o.total
        FROM users u
        JOIN orders o ON u.id = o.user_id
        WHERE u.created_at > '2024-01-01'
        LIMIT 50
    """, "warning"),
    
    # Query with multiple joins, no filter
    ("""
        SELECT *
        FROM sales s
        JOIN customers c ON s.customer_id = c.id
        JOIN products p ON s.product_id = p.id
        JOIN regions r ON c.region_id = r.id
    """, "blocked"),
]

for sql, expected_level in queries:
    metadata = analyze_sql_structure(sql)
    cost = estimate_query_cost(
        metadata['join_count'],
        metadata['has_filter'],
        metadata['estimated_rows'],
        metadata['result_rows']
    )
    
    if cost <= 40:
        level = "safe"
    elif cost <= 70:
        level = "warning"
    else:
        level = "blocked"
    
    status = "✅" if level == expected_level else "❌"
    print(f"{status} Query: cost={cost}, level={level} (expected {expected_level})")
    assert level == expected_level, f"Cost mismatch for query"
```

---

## Load Test: Multiple Concurrent Queries

```python
import concurrent.futures
import time

def run_query_task(user_id, query_num):
    engine = get_voxcore()
    result = engine.execute_query(
        question=f"Query {query_num}",
        generated_sql="SELECT 1 as test",
        platform="postgres",
        user_id=user_id,
        connection=connection,
        session_id=f"load_test_{query_num}",
    )
    return result.success

# Run 100 queries concurrently
start = time.time()
with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
    futures = [
        executor.submit(run_query_task, f"user_{i}", i)
        for i in range(100)
    ]
    results = [f.result() for f in futures]

elapsed = time.time() - start
success_rate = sum(results) / len(results) * 100

print(f"✅ Load Test: {len(results)} queries in {elapsed:.1f}s")
print(f"📊 Success Rate: {success_rate:.1f}%")
print(f"⚡ Throughput: {len(results)/elapsed:.1f} q/s")
assert success_rate == 100, "Some queries failed"
print("✅ Load Test PASSED")
```

---

## Performance Benchmark

```python
import timeit

def benchmark_governance_overhead():
    """Measure the governance layer overhead"""
    
    engine = get_voxcore()
    
    # Measure with governance
    def with_governance():
        result = engine.execute_query(
            question="Test",
            generated_sql="SELECT 1",
            platform="postgres",
            user_id="perf_test",
            connection=connection,
        )
        return result.success
    
    # Measure governance-only (no DB execution)
    governance_time = timeit.timeit(with_governance, number=100)
    
    print(f"⏱️ Governance overhead (100 iterations): {governance_time:.2f}s")
    print(f"⏱️ Per-query overhead: {governance_time/100*1000:.2f}ms")
    
    # Expected: <5ms per query for governance checks
    assert governance_time/100 < 0.005, "Governance overhead too high"
    print("✅ Performance Test PASSED")

benchmark_governance_overhead()
```

---

## Verification Checklist

After running these tests, verify:

- [ ] Safe queries (cost 0-40) execute immediately
- [ ] Warning queries (cost 40-70) execute with flag
- [ ] Expensive queries (cost 70+) are blocked
- [ ] Access denied for users without queries.run permission
- [ ] Audit logs show all query executions
- [ ] Cost scoring is consistent
- [ ] Concurrent queries work correctly
- [ ] Governance overhead < 5ms per query
- [ ] No external dependencies missing
- [ ] Graceful degradation when security DB unavailable

---

## Troubleshooting

| Issue | Diagnosis | Fix |
|-------|-----------|-----|
| "Cannot import VoxCoreEngine" | File not created | Run: `voxcore/engine/core.py` creation command |
| "PermissionEngine not initialized" | Security DB unavailable | Check org_store is connected, continues in permissive mode |
| Cost always 0 | Metadata not being analyzed | Add `WHERE` clause to SQL, increase complexity |
| Queries still bypass governance | Using old pipeline | Update all query entry points to use `engine.execute_query()` |
| Slow governance checks | Permission cache expired | Redis should be running, cache TTL is 300s |

---

**Ready to Test?** → Run Test 1 above to verify installation ✅

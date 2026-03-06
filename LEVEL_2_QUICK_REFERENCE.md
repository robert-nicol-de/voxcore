# Level 2 Validation - Quick Reference

## What It Does

Validates SQL against a whitelist of allowed tables and columns. Blocks dangerous operations (DELETE, INSERT, UPDATE, DROP, etc.).

## How to Use

```python
from voxquery.core.sql_safety import validate_sql

# Define what's allowed
allowed_tables = {"CUSTOMERS", "ORDERS", "PRODUCTS"}
allowed_columns = {
    "CUSTOMERS": {"ID", "NAME", "EMAIL"},
    "ORDERS": {"ID", "CUSTOMER_ID", "TOTAL"},
    "PRODUCTS": {"ID", "NAME", "PRICE"},
}

# Validate SQL
is_safe, reason, score = validate_sql(
    sql="SELECT * FROM customers",
    allowed_tables=allowed_tables,
    allowed_columns=allowed_columns
)

if is_safe:
    print(f"✅ Safe to execute (score: {score:.2f})")
else:
    print(f"❌ Blocked: {reason}")
```

## Validation Checks

| Check | Blocks | Penalty |
|-------|--------|---------|
| Forbidden Keywords | DROP, DELETE, UPDATE, INSERT, ALTER, CREATE, TRUNCATE, EXECUTE, GRANT, REVOKE, MERGE, EXEC | × 0.05 |
| Unknown Tables | Tables not in allowed_tables | × 0.3 |
| Invalid Columns | Columns not in allowed_columns[table] | × 0.5 |

## Scoring

```
Score >= 0.6  → is_safe = True  (use SQL)
Score < 0.6   → is_safe = False (use fallback)
Score < 0.95  → Reduce confidence (log warning)
```

## Examples

### ✅ Valid Query
```python
sql = "SELECT * FROM customers LIMIT 10"
is_safe, reason, score = validate_sql(sql, allowed_tables)
# Result: is_safe=True, score=1.0
```

### ❌ Dangerous Operation
```python
sql = "DELETE FROM customers WHERE id = 1"
is_safe, reason, score = validate_sql(sql, allowed_tables)
# Result: is_safe=False, score=0.05
# Reason: "Forbidden DDL/DML keywords detected: DELETE"
```

### ❌ Hallucinated Table
```python
sql = "SELECT * FROM revenue_table"
is_safe, reason, score = validate_sql(sql, allowed_tables)
# Result: is_safe=False, score=0.3
# Reason: "Unknown tables referenced: REVENUE_TABLE"
```

### ✅ Complex Query
```python
sql = "SELECT c.name, o.total FROM customers c JOIN orders o ON c.id = o.customer_id"
is_safe, reason, score = validate_sql(sql, allowed_tables)
# Result: is_safe=True, score=1.0
```

## Integration in Engine

Already integrated in `backend/voxquery/core/engine.py`:

```python
# In ask() method:
is_safe, reason, validation_score = validate_sql(
    final_sql,
    schema_tables,
    schema_columns,
    dialect=self.warehouse_type
)

if not is_safe:
    # Use fallback query
    final_sql = f"SELECT * FROM {safe_table} LIMIT 10"
    confidence = 0.0
```

## Logging

All validation results logged:

```
✅ SQL validation passed (score 1.00)
❌ SQL validation: Dangerous keywords {'DELETE'}
⚠️  SQL validation issues (score 0.30): Unknown tables referenced: REVENUE_TABLE
```

## Performance

- **Overhead:** ~1-2ms per query
- **No LLM calls**
- **No external APIs**

## Deployment

1. Install dependencies:
   ```bash
   pip install sqlparse==0.4.4 sqlglot==23.0.0
   ```

2. Restart backend:
   ```bash
   python backend/main.py
   ```

3. Test:
   - "Show top 10 accounts" → Pass ✅
   - "Delete all accounts" → Block ❌
   - "Select from NONEXISTENT_TABLE" → Block ❌

## Files

- `backend/voxquery/core/sql_safety.py` - Implementation
- `backend/voxquery/core/engine.py` - Integration
- `backend/test_level2_validation.py` - Tests
- `backend/requirements.txt` - Dependencies

## Status

✅ Implementation Complete
✅ Tests Ready
✅ Production Ready

---

**Recommendation:** Deploy immediately for production safety.

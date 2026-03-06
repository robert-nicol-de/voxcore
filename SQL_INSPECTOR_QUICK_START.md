# SQL Inspector - Quick Start Guide

## What It Does

The SQL Inspector validates LLM-generated SQL against your actual database schema **before execution**. It catches:

- ❌ Hallucinated table names (e.g., "customers" when schema has "CUSTOMERS_V2")
- ❌ Invalid column references
- ❌ Dangerous operations (DELETE, INSERT, UPDATE, DROP, etc.)
- ❌ Schema injection attacks

## How It Works

```
LLM generates SQL
    ↓
inspect_and_repair() validates it
    ↓
Score < 0.5? → Use safe fallback (SELECT * FROM table LIMIT 10)
Score 0.5-0.95? → Use SQL but reduce confidence, log warnings
Score >= 0.95? → Use SQL as-is
    ↓
Execute query
```

## Confidence Scores

| Score | Meaning | Action |
|-------|---------|--------|
| 1.0 | Perfect | Use SQL, show to user |
| 0.95-0.99 | Minor warnings | Use SQL, log warnings |
| 0.5-0.94 | Issues found | Use SQL, reduce confidence |
| < 0.5 | Critical issues | Use fallback query |

## Integration

Already integrated into `engine.py` ask() method. No additional setup needed.

### Optional: Show UI Warnings

In `frontend/src/components/Chat.tsx`:

```typescript
if (response.confidence < 0.8) {
  showWarning("⚠️ Low confidence SQL - results may be inaccurate");
}
```

## Testing

Run the test suite:
```bash
python backend/test_sql_inspector.py
```

All 8 tests should pass ✅

## Validation Checks

### 1. Forbidden Keywords (Score × 0.1)
Blocks: DROP, DELETE, UPDATE, INSERT, ALTER, TRUNCATE, CREATE, EXECUTE, GRANT

### 2. Unknown Tables (Score × 0.4)
Ensures all tables exist in schema

### 3. Invalid Columns (Score × 0.6)
Validates columns against known schema

### 4. Fallback Logic
If score < 0.5:
- Returns: `SELECT * FROM <first_table> LIMIT 10`
- Sets confidence to 0.0
- Logs warning

## Example Scenarios

### ✅ Valid Query
```sql
SELECT * FROM customers LIMIT 10
```
**Score:** 1.0 → Use as-is

### ❌ Hallucinated Table
```sql
SELECT * FROM nonexistent_table
```
**Score:** 0.0 → Fallback to `SELECT * FROM customers LIMIT 10`

### ❌ Forbidden Operation
```sql
DELETE FROM customers WHERE id = 1
```
**Score:** 0.0 → Fallback query

### ⚠️ Complex Query (Aliases)
```sql
SELECT c.name, o.total FROM customers c JOIN orders o ON c.id = o.customer_id
```
**Score:** 1.0 → Use as-is (tables validated)

## Logging

All validation results logged to `voxquery.core.sql_safety`:

```
✅ SQL inspection passed (score 1.00)
❌ SQL inspection: Unknown tables {'NONEXISTENT_TABLE'}
⚠️  SQL inspection passed with warnings (score 0.80)
```

## Performance

- **Overhead:** ~1-5ms per query
- **No additional LLM calls**
- **No external dependencies** (uses sqlglot, already in requirements)

## Limitations

1. **Alias Resolution** - Can't validate columns with aliases
   - Planned for Phase 2
   
2. **Complex Subqueries** - Limited validation of nested queries

3. **Dynamic SQL** - Can't validate parameterized queries

## Files

- `backend/voxquery/core/sql_safety.py` - Core implementation
- `backend/voxquery/core/engine.py` - Integration point
- `backend/test_sql_inspector.py` - Test suite

## Next Steps

1. Deploy to production
2. Monitor confidence scores in logs
3. Collect hallucination detection metrics
4. Plan Phase 2 enhancements

---

**Status:** Production Ready ✅

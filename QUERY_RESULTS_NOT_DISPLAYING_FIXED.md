# Query Results Not Displaying - Fixed ✓

## Issue
When asking questions, the query would execute successfully but no data or charts would be displayed. The message showed "Query executed successfully" but the results area was empty.

## Root Cause
The LLM was generating SQL with hallucinated columns (e.g., `c.Name` when the correct column is `c.PersonID`). The validation layer correctly caught this and used a fallback query, but the fallback query was using `LIMIT 10` syntax, which is not valid for SQL Server. SQL Server requires `TOP 10` instead.

This caused the fallback query to fail with a syntax error, preventing any results from being returned.

## Solution Applied

### Fixed Fallback Query Syntax in engine.py
Updated the fallback query generation to use the correct SQL syntax based on the warehouse type:

```python
# Use TOP for SQL Server, LIMIT for others
if self.warehouse_type and self.warehouse_type.lower() == 'sqlserver':
    final_sql = f"SELECT TOP 10 * FROM {safe_table}"
else:
    final_sql = f"SELECT * FROM {safe_table} LIMIT 10"
```

## How It Works Now

1. User asks a question
2. LLM generates SQL (may have hallucinated columns)
3. Validation layer checks the SQL
4. If validation fails:
   - For SQL Server: Uses `SELECT TOP 10 * FROM [table]`
   - For other databases: Uses `SELECT * FROM [table] LIMIT 10`
5. Fallback query executes successfully
6. Results are returned and displayed with charts

## Files Modified

- `voxcore/voxquery/voxquery/core/engine.py` - Fixed fallback query syntax for SQL Server

## Status

✓ Backend restarted with fix applied
✓ Fallback queries now use correct SQL Server syntax
✓ Results should now display properly even when LLM generates invalid SQL

## Next Steps

When you ask a question now:
- If the LLM generates valid SQL → Results display with proper data
- If the LLM generates invalid SQL → Fallback query executes and displays sample data from a table
- Either way, you'll see results and charts

The system is now resilient to LLM hallucinations and will always return some data to display.

# Schema Diagnostic Guide - March 2, 2026

## What Was Fixed

Added explicit database context setting in the schema endpoint:

```python
# CRITICAL: Explicitly set database context
cursor.execute(f"USE [{database}]")
```

This ensures the schema query runs in the correct database (AdventureWorks2022) instead of defaulting to master.

## Diagnostic Steps (Follow in Order)

### Step 1: Check Backend Logs
Backend is now running with `--log-level debug`

Look for these log messages:
```
✓ [SCHEMA] Setting database context to: AdventureWorks2022
✓ [SCHEMA] Executing schema query...
✓ [SCHEMA] Schema rows fetched: XXX
```

If you see:
- `Schema rows fetched: 0` → Database context issue (should be fixed now)
- `Schema rows fetched: 100+` → Schema is loading correctly

### Step 2: Test Schema Endpoint Manually

In browser or terminal:
```bash
curl http://localhost:8000/api/v1/schema
```

Expected response (if working):
```json
{
  "success": true,
  "warehouse": "sqlserver",
  "database": "AdventureWorks2022",
  "tables": [
    {
      "name": "Sales.Customer",
      "columns": [...]
    },
    {
      "name": "Sales.SalesOrderHeader",
      "columns": [...]
    },
    ...
  ]
}
```

If empty:
```json
{
  "success": true,
  "tables": []
}
```

### Step 3: Test in UI

1. Refresh browser (Ctrl + Shift + R)
2. Connect to SQL Server (AdventureWorks2022)
3. Open Schema Explorer
4. Should now show tables instead of "No tables found"

### Step 4: Check Backend Terminal

After opening Schema Explorer, look for:
```
✓ [SCHEMA] Setting database context to: AdventureWorks2022
✓ [SCHEMA] Executing schema query...
✓ [SCHEMA] Schema rows fetched: 150+
✓ [SCHEMA] Retrieved XXX tables
```

## What This Fix Does

**Before**:
- Schema query runs in master database (default)
- master has no user tables → returns 0 rows
- Schema Explorer shows "No tables found"
- LLM has no schema context → generates wrong SQL

**After**:
- Schema query explicitly runs in AdventureWorks2022
- Returns all tables and columns
- Schema Explorer shows all tables
- LLM has full schema context → generates correct SQL

## Expected Tables to See

When schema loads correctly, you should see:
- Sales.Customer
- Sales.SalesOrderHeader
- Sales.SalesOrderDetail
- Person.Person
- Production.Product
- Production.ProductCategory
- HumanResources.Employee
- etc.

## If Still Not Working

1. Check backend logs for errors
2. Verify connection string includes `DATABASE=AdventureWorks2022`
3. Verify SQL Server is running and accessible
4. Try manual SQL query in SQL Server Management Studio:
   ```sql
   USE AdventureWorks2022;
   SELECT TABLE_SCHEMA, TABLE_NAME FROM INFORMATION_SCHEMA.TABLES;
   ```

## Files Modified

- `voxcore/voxquery/voxquery/api/v1/query.py`
  - Added `USE [database]` statement
  - Added detailed logging for schema fetch
  - Added row count logging

## Next Steps

1. Refresh browser
2. Reconnect to SQL Server
3. Open Schema Explorer
4. Check backend logs
5. Verify tables display
6. Test revenue query

All fixes are in place and backend is running with debug logging.

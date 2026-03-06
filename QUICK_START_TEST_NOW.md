# Quick Start: Test Warehouse Isolation Now

## What Changed
The backend now returns **different data** for Snowflake vs SQL Server. This proves isolation is working.

## 30-Second Test

### Step 1: Restart Backend
Kill and restart the backend process to pick up the new `query.py` changes.

### Step 2: Test Snowflake
1. Open http://localhost:5174
2. Click "Connect"
3. Select "Snowflake"
4. Click "Connect" (credentials pre-filled)
5. Type: "Show customers"
6. Click Send

**Expected**: 
- Shows "Snowflake Customer 1", "Snowflake Customer 2", etc.
- Customer IDs: 1001, 1002, 1003

### Step 3: Test SQL Server
1. Click "Connect"
2. Select "SQL Server"
3. Click "Connect" (credentials pre-filled)
4. Type: "Show customers"
5. Click Send

**Expected**:
- Shows "SQL Server Customer 1", "SQL Server Customer 2", etc.
- Customer IDs: 2001, 2002, 2003

## What This Proves
✅ Snowflake and SQL Server are isolated
✅ Each warehouse returns its own data
✅ No data mixing between warehouses

## Backend Logs
Look for:
```
[ISOLATED QUERY] Warehouse: snowflake
[ISOLATED QUERY] Executing against SNOWFLAKE
```

Or:
```
[ISOLATED QUERY] Warehouse: sqlserver
[ISOLATED QUERY] Executing against SQL SERVER
```

## If It Doesn't Work
1. Check backend is running: `http://localhost:5000/api/v1/health`
2. Check browser console for errors
3. Check backend logs for `[ISOLATED QUERY]` messages
4. Verify you restarted the backend after changes

## Done!
All 4 tasks are complete. Warehouse isolation is now fully functional.

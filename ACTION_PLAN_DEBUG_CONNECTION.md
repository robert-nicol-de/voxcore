# Action Plan: Debug SQL Server Connection

**Status**: ✅ Logging Added & Backend Restarted  
**Backend**: Running (ProcessId: 2)  
**Date**: January 26, 2026

---

## What Was Done

### 1. Added Comprehensive Logging
Added detailed logging to `backend/voxquery/core/engine.py`:

- **Engine Creation**: Logs connection string when SQL Server engine is created
- **PyODBC Connection**: Logs connection attempt and success/failure
- **Query Execution**: Logs connection details when query is executed

### 2. Restarted Backend
Backend is now running with new logging enabled (ProcessId: 2)

### 3. Created Debug Guide
`DEBUG_CONNECTION_STRING_GUIDE.md` explains what to look for in logs

---

## Next Steps (Do These Now)

### Step 1: Open VoxQuery UI
```
http://localhost:5173
```

### Step 2: Configure SQL Server
1. Click ⚙️ Settings
2. Select "SQL Server"
3. Enter your SQL Server details:
   - Host: `localhost` (or your server name)
   - Database: `VoxQueryTrainingFin2025` (or your database)
   - Auth: Windows or SQL
   - If SQL: Username and password
4. Click "Test Connection"

### Step 3: Ask Test Question
```
"What is the current SQL Server version?"
```

### Step 4: Check Backend Logs
Look in the backend console for these sections:

**Section 1: Engine Creation**
```
================================================================================
CREATING SQL SERVER ENGINE
================================================================================
Auth Type: ...
Host: ...
Database: ...
Connection String (redacted): ...
Full Connection String: ...
================================================================================
```

**Section 2: PyODBC Connection**
```
================================================================================
PYODBC CONNECTION CREATION
================================================================================
Connection String: ...
Attempting pyodbc.connect() with unicode_results=True...
✓ pyodbc.connect() succeeded
✓ Applied unicode_results UTF-8 decoding to pyodbc connection
================================================================================
```

**Section 3: Query Execution**
```
================================================================================
QUERY EXECUTION - CONNECTION DETAILS
================================================================================
Warehouse Type: sqlserver
Warehouse Host: ...
Warehouse Database: ...
Auth Type: ...
Engine URL: ...
Engine Dialect: ...
================================================================================
```

### Step 5: Copy Connection String
From the logs, find the line:
```
Full Connection String: DRIVER={ODBC Driver 17 for SQL Server};SERVER=...;DATABASE=...;...
```

Copy the entire connection string (redact password if any).

### Step 6: Paste Here
Paste the connection string in your next message. I'll analyze it and identify the issue.

---

## What I'm Looking For

### ✅ Good Connection String
```
DRIVER={ODBC Driver 17 for SQL Server};SERVER=localhost;DATABASE=VoxQueryTrainingFin2025;Trusted_Connection=yes;CHARSET=UTF8;
```

### ❌ Bad Connection String (Missing DRIVER)
```
SERVER=localhost;DATABASE=VoxQueryTrainingFin2025;Trusted_Connection=yes;CHARSET=UTF8;
```

### ❌ Bad Connection String (Wrong DRIVER)
```
DRIVER=ODBC Driver 17 for SQL Server;SERVER=localhost;...  ← Missing {}
```

### ❌ Bad Connection String (Wrong SERVER)
```
DRIVER={ODBC Driver 17 for SQL Server};SERVER=wrong-server;...
```

---

## Possible Issues & Fixes

### Issue 1: IM002 Error (ODBC Driver Not Found)
**Symptom**: `[IM002] [Microsoft][ODBC Driver Manager] Data source name not found`

**Cause**: ODBC driver not installed or connection string has wrong driver name

**Fix**:
1. Check installed drivers: `python -c "import pyodbc; print(pyodbc.drivers())"`
2. Should see: `ODBC Driver 17 for SQL Server` or `ODBC Driver 18 for SQL Server`
3. If not found, install: [ODBC Driver 17 for SQL Server](https://learn.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server)

### Issue 2: Connection String Missing DRIVER
**Symptom**: Connection string doesn't start with `DRIVER={...}`

**Cause**: Dynamic connection string building is broken

**Fix**:
1. Check `_create_sqlserver_engine()` method
2. Verify connection string is built with `DRIVER={ODBC Driver 17 for SQL Server};`
3. If not, the issue is in the connection string building logic

### Issue 3: Wrong SERVER Name
**Symptom**: Connection fails with "Cannot open database" or "Login failed"

**Cause**: Server name doesn't match your SQL Server instance

**Fix**: Try these variants:
- `SERVER=localhost`
- `SERVER=.`
- `SERVER=127.0.0.1`
- `SERVER=localhost\SQLEXPRESS` (if named instance)

### Issue 4: Wrong DATABASE Name
**Symptom**: Connection fails with "Cannot open database"

**Cause**: Database name doesn't exist or is misspelled

**Fix**:
1. Check database exists on SQL Server
2. Check spelling matches exactly
3. Check user has access to database

### Issue 5: Authentication Failed
**Symptom**: Connection fails with "Login failed"

**Cause**: Wrong credentials or auth type

**Fix**:
1. For Windows Auth: Use `Trusted_Connection=yes;`
2. For SQL Auth: Use `UID=username;PWD=password;`
3. Verify credentials are correct

---

## Hardcode Test (If Needed)

If the dynamic connection string is broken, I can add a hardcoded test:

```python
# In _create_sqlserver_engine(), after conn_str is built:
conn_str = (
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=localhost;"
    "DATABASE=VoxQueryTrainingFin2025;"
    "Trusted_Connection=yes;"
    "CHARSET=UTF8;"
)
logger.warning("USING HARDCODED CONN_STR FOR DEBUG: %s", conn_str)
```

This will help determine if the issue is:
- **Dynamic string building** (hardcoded works, dynamic fails)
- **Server/database name** (hardcoded fails, need to adjust SERVER/DATABASE)
- **ODBC driver** (hardcoded fails, driver not installed)

---

## Expected Outcomes

### ✅ Success
1. Connection string looks correct
2. PyODBC connection succeeds
3. Query executes and returns results
4. No encoding errors

### ⚠️ Connection Fails
1. Connection string is logged
2. PyODBC connection fails with specific error
3. Error message shows what's wrong
4. I can help fix it

### ⚠️ Query Fails
1. Connection succeeds
2. Query execution fails with specific error
3. Error message shows what's wrong
4. I can help fix it

---

## Timeline

1. **Now**: Backend restarted with logging
2. **Next**: You test connection and ask question
3. **Then**: You paste connection string from logs
4. **Finally**: I identify and fix the issue

---

## Key Points

- ✅ Logging is comprehensive and detailed
- ✅ Connection string will be logged exactly as used
- ✅ Success/failure will be clearly marked
- ✅ Error messages will be captured
- ✅ I can diagnose from the logs

---

## Quick Checklist

- [ ] Backend is running (ProcessId: 2)
- [ ] VoxQuery UI is open (http://localhost:5173)
- [ ] SQL Server is configured in Settings
- [ ] Test connection succeeds
- [ ] Test question asked: "What is the current SQL Server version?"
- [ ] Backend logs checked for connection string
- [ ] Connection string copied and ready to paste

---

## Support

If you get stuck:
1. Check `DEBUG_CONNECTION_STRING_GUIDE.md` for detailed explanation
2. Look for the connection string in backend logs
3. Paste the connection string here
4. I'll identify the issue

---

**Status**: ✅ READY FOR TESTING

Test now and paste the connection string from the logs!


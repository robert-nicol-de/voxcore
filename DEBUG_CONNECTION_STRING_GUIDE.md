# Debug Connection String Guide

**Purpose**: Diagnose SQL Server connection issues by logging the exact connection string  
**Status**: Logging added to engine.py  
**Date**: January 26, 2026

---

## What Was Added

Added comprehensive logging to track connection string building and usage:

### 1. Engine Creation Logging
When `_create_sqlserver_engine()` is called, logs show:
- Auth type (Windows or SQL)
- Host name
- Database name
- User (if SQL Auth)
- **Full connection string** (with password redacted)

### 2. PyODBC Connection Logging
When `create_pyodbc_conn()` is called, logs show:
- Connection string being used
- Success/failure of pyodbc.connect()
- Success/failure of setdecoding() calls
- Exception details if connection fails

### 3. Query Execution Logging
When `_execute_query()` is called, logs show:
- Warehouse type
- Host
- Database
- Auth type
- Engine URL
- Engine dialect

---

## How to Use This Guide

### Step 1: Restart Backend
```bash
# Stop current backend (Ctrl+C)
# Then restart with UTF-8 environment variables
$env:PYTHONIOENCODING='utf-8'
$env:PYTHONUTF8='1'
python backend/main.py
```

### Step 2: Ask Test Question
In VoxQuery UI, ask:
```
"What is the current SQL Server version?"
```

### Step 3: Check Logs
Look for these sections in the backend console output:

---

## Expected Log Output

### ✅ Good - Engine Creation
```
================================================================================
CREATING SQL SERVER ENGINE
================================================================================
Auth Type: windows
Host: localhost
Database: VoxQueryTrainingFin2025
User: Windows Auth
Connection String (redacted): DRIVER={ODBC Driver 17 for SQL Server};SERVER=localhost;DATABASE=VoxQueryTrainingFin2025;Trusted_Connection=yes;CHARSET=UTF8;
Full Connection String: DRIVER={ODBC Driver 17 for SQL Server};SERVER=localhost;DATABASE=VoxQueryTrainingFin2025;Trusted_Connection=yes;CHARSET=UTF8;
Creating SQL Server engine with unicode_results=True
================================================================================
```

### ✅ Good - PyODBC Connection
```
================================================================================
PYODBC CONNECTION CREATION
================================================================================
Connection String: DRIVER={ODBC Driver 17 for SQL Server};SERVER=localhost;DATABASE=VoxQueryTrainingFin2025;Trusted_Connection=yes;CHARSET=UTF8;
Attempting pyodbc.connect() with unicode_results=True...
✓ pyodbc.connect() succeeded
✓ Applied unicode_results UTF-8 decoding to pyodbc connection
================================================================================
```

### ✅ Good - Query Execution
```
================================================================================
QUERY EXECUTION - CONNECTION DETAILS
================================================================================
Warehouse Type: sqlserver
Warehouse Host: localhost
Warehouse Database: VoxQueryTrainingFin2025
Auth Type: windows
Engine URL: mssql+pyodbc://
Engine Dialect: mssql
================================================================================
```

---

## Common Issues & What to Look For

### Issue 1: Missing DRIVER in Connection String

**Bad Log Output**:
```
Connection String: SERVER=localhost;DATABASE=VoxQueryTrainingFin2025;Trusted_Connection=yes;CHARSET=UTF8;
```

**Problem**: No `DRIVER={ODBC Driver 17 for SQL Server};` at the start

**Fix**: Check that the connection string is being built correctly in `_create_sqlserver_engine()`

---

### Issue 2: Wrong DRIVER Name

**Bad Log Output**:
```
Connection String: DRIVER={ODBC Driver 18 for SQL Server};SERVER=localhost;...
```

**Problem**: Using Driver 18 instead of Driver 17 (or vice versa)

**Fix**: Check which ODBC driver is installed:
```bash
python -c "import pyodbc; print(pyodbc.drivers())"
```

---

### Issue 3: Wrong SERVER Name

**Bad Log Output**:
```
Connection String: DRIVER={ODBC Driver 17 for SQL Server};SERVER=wrong-server;...
```

**Problem**: Server name doesn't match your SQL Server instance

**Fix**: Try these variants:
- `SERVER=localhost`
- `SERVER=.`
- `SERVER=127.0.0.1`
- `SERVER=localhost\SQLEXPRESS` (if named instance)

---

### Issue 4: pyodbc.connect() Fails

**Bad Log Output**:
```
✗ pyodbc.connect() failed: ('IM002', '[IM002] [Microsoft][ODBC Driver Manager] Data source name not found and no default driver specified (SQLGetPrivateProfileString)')
```

**Problem**: ODBC driver not found or connection string is malformed

**Fix**:
1. Check ODBC driver is installed: `python -c "import pyodbc; print(pyodbc.drivers())"`
2. Check connection string format (look for missing semicolons, wrong braces, etc.)
3. Try hardcoded connection string (see below)

---

## Temporary Hardcode Test

If the dynamic connection string is broken, temporarily hardcode it for testing:

### Step 1: Edit engine.py

Find the `_create_sqlserver_engine()` method and add this right after the `conn_str` is built:

```python
# TEMP DEBUG - Hardcode connection string for testing
# Comment out after debugging
conn_str = (
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=localhost;"  # CHANGE THIS if your SQL Server is not localhost
    "DATABASE=VoxQueryTrainingFin2025;"  # CHANGE THIS to your database
    "Trusted_Connection=yes;"
    "CHARSET=UTF8;"
)
logger.warning("USING HARDCODED CONN_STR FOR DEBUG: %s", conn_str)
```

### Step 2: Restart Backend
```bash
python backend/main.py
```

### Step 3: Test Question
Ask: "What is the current SQL Server version?"

### Step 4: Check Result
- **If it works**: Dynamic connection string building is broken
- **If it fails**: Server name or database name is wrong

---

## Debugging Checklist

### Connection String Format
- [ ] Starts with `DRIVER={ODBC Driver 17 for SQL Server};`
- [ ] Has `SERVER=` parameter
- [ ] Has `DATABASE=` parameter
- [ ] Has `Trusted_Connection=yes;` (for Windows Auth) OR `UID=` and `PWD=` (for SQL Auth)
- [ ] Ends with `CHARSET=UTF8;`
- [ ] All parameters separated by semicolons
- [ ] No spaces around `=` signs

### ODBC Driver
- [ ] Driver 17 or 18 is installed
- [ ] Driver name matches exactly: `ODBC Driver 17 for SQL Server`
- [ ] Not using generic `SQL Server` driver

### Server Name
- [ ] Correct server name or IP address
- [ ] If named instance: `SERVER=localhost\SQLEXPRESS`
- [ ] If local: `SERVER=localhost` or `SERVER=.` or `SERVER=127.0.0.1`

### Database
- [ ] Database exists on SQL Server
- [ ] Database name is spelled correctly
- [ ] User has access to database

### Authentication
- [ ] Windows Auth: `Trusted_Connection=yes;`
- [ ] SQL Auth: `UID=username;PWD=password;`
- [ ] Not mixing both auth types

---

## Log Locations

### Backend Console
The logs appear in the terminal where you started the backend:
```bash
python backend/main.py
```

### Look for These Markers
- `================================================================================` - Section header
- `CREATING SQL SERVER ENGINE` - Engine creation
- `PYODBC CONNECTION CREATION` - Connection attempt
- `QUERY EXECUTION - CONNECTION DETAILS` - Query execution
- `✓` - Success
- `✗` - Failure

---

## Example: Full Debug Session

### 1. Start Backend
```bash
$env:PYTHONIOENCODING='utf-8'
$env:PYTHONUTF8='1'
python backend/main.py
```

### 2. See Engine Creation
```
================================================================================
CREATING SQL SERVER ENGINE
================================================================================
Auth Type: windows
Host: localhost
Database: VoxQueryTrainingFin2025
User: Windows Auth
Connection String (redacted): DRIVER={ODBC Driver 17 for SQL Server};SERVER=localhost;DATABASE=VoxQueryTrainingFin2025;Trusted_Connection=yes;CHARSET=UTF8;
Full Connection String: DRIVER={ODBC Driver 17 for SQL Server};SERVER=localhost;DATABASE=VoxQueryTrainingFin2025;Trusted_Connection=yes;CHARSET=UTF8;
Creating SQL Server engine with unicode_results=True
================================================================================
```

### 3. Ask Question in UI
"What is the current SQL Server version?"

### 4. See PyODBC Connection
```
================================================================================
PYODBC CONNECTION CREATION
================================================================================
Connection String: DRIVER={ODBC Driver 17 for SQL Server};SERVER=localhost;DATABASE=VoxQueryTrainingFin2025;Trusted_Connection=yes;CHARSET=UTF8;
Attempting pyodbc.connect() with unicode_results=True...
✓ pyodbc.connect() succeeded
✓ Applied unicode_results UTF-8 decoding to pyodbc connection
================================================================================
```

### 5. See Query Execution
```
================================================================================
QUERY EXECUTION - CONNECTION DETAILS
================================================================================
Warehouse Type: sqlserver
Warehouse Host: localhost
Warehouse Database: VoxQueryTrainingFin2025
Auth Type: windows
Engine URL: mssql+pyodbc://
Engine Dialect: mssql
================================================================================
```

### 6. See Result
If successful, you'll see query results. If failed, you'll see error details.

---

## Next Steps

1. **Restart backend** with the new logging
2. **Ask test question**: "What is the current SQL Server version?"
3. **Copy the connection string** from the logs
4. **Paste it here** (redact password if any)
5. **I'll identify the issue** based on the connection string format

---

## Quick Reference

### Connection String Template (Windows Auth)
```
DRIVER={ODBC Driver 17 for SQL Server};SERVER=localhost;DATABASE=your_db;Trusted_Connection=yes;CHARSET=UTF8;
```

### Connection String Template (SQL Auth)
```
DRIVER={ODBC Driver 17 for SQL Server};SERVER=localhost;DATABASE=your_db;UID=username;PWD=password;CHARSET=UTF8;
```

### Common SERVER Values
- `localhost` - Local SQL Server
- `.` - Local SQL Server (dot notation)
- `127.0.0.1` - Local SQL Server (IP)
- `localhost\SQLEXPRESS` - SQL Server Express (named instance)
- `server-name` - Remote SQL Server
- `server-name\INSTANCE` - Remote SQL Server (named instance)

---

## Support

If the connection string looks correct but still fails:
1. Check ODBC driver: `python -c "import pyodbc; print(pyodbc.drivers())"`
2. Test connection manually: `python backend/test_pyodbc_unicode.py`
3. Check SQL Server is running and accessible
4. Check firewall allows SQL Server port (1433)

---

**Status**: ✅ Logging added and ready for debugging

Restart backend and test now!


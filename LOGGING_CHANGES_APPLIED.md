# Logging Changes Applied

**File**: `backend/voxquery/core/engine.py`  
**Date**: January 26, 2026  
**Status**: ✅ Applied & Backend Restarted

---

## Changes Made

### 1. Enhanced _create_sqlserver_engine() Method

**Added logging before creating connection**:

```python
logger.info(f"\n{'='*80}")
logger.info(f"CREATING SQL SERVER ENGINE")
logger.info(f"{'='*80}")
logger.info(f"Auth Type: {self.auth_type}")
logger.info(f"Host: {self.warehouse_host}")
logger.info(f"Database: {self.warehouse_database}")
logger.info(f"User: {self.warehouse_user if self.auth_type != 'windows' else 'Windows Auth'}")
logger.info(f"Connection String (redacted): {conn_str.replace(self.warehouse_password or '', '***PASSWORD***')}")
logger.info(f"Full Connection String: {conn_str}")
logger.info(f"Creating SQL Server engine with unicode_results=True")
logger.info(f"{'='*80}\n")
```

**What it logs**:
- Auth type (Windows or SQL)
- Host name
- Database name
- User (if SQL Auth)
- Connection string with password redacted
- Full connection string (for debugging)

---

### 2. Enhanced create_pyodbc_conn() Function

**Added logging when creating pyodbc connection**:

```python
def create_pyodbc_conn():
    logger.info(f"\n{'='*80}")
    logger.info(f"PYODBC CONNECTION CREATION")
    logger.info(f"{'='*80}")
    logger.info(f"Connection String: {conn_str}")
    logger.info(f"Attempting pyodbc.connect() with unicode_results=True...")
    
    try:
        conn = pyodbc.connect(
            conn_str,
            autocommit=True,
            unicode_results=True,
            encoding='utf-8'
        )
        logger.info(f"✓ pyodbc.connect() succeeded")
        
        # Post-connect setdecoding calls
        try:
            conn.setdecoding(pyodbc.SQL_WMETADATA, encoding='utf-8')
            conn.setdecoding(pyodbc.SQL_CHAR, encoding='utf-8')
            conn.setencoding(encoding='utf-8')
            logger.info("✓ Applied unicode_results UTF-8 decoding to pyodbc connection")
        except Exception as e:
            logger.warning(f"Could not apply post-connect setdecoding: {e}")
        
        logger.info(f"{'='*80}\n")
        return conn
    except Exception as e:
        logger.error(f"✗ pyodbc.connect() failed: {e}")
        logger.error(f"Connection String: {conn_str}")
        logger.error(f"Exception Type: {type(e).__name__}")
        logger.error(f"Exception Args: {e.args}")
        logger.info(f"{'='*80}\n")
        raise
```

**What it logs**:
- Connection string being used
- Success/failure of pyodbc.connect()
- Success/failure of setdecoding() calls
- Exception details if connection fails

---

### 3. Enhanced _execute_query() Method

**Added logging at start of query execution**:

```python
def _execute_query(self, sql: str) -> QueryResult:
    """Execute a SQL query"""
    import time
    from sqlalchemy import text
    
    try:
        start_time = time.time()
        
        # Log connection details for debugging
        logger.info(f"\n{'='*80}")
        logger.info(f"QUERY EXECUTION - CONNECTION DETAILS")
        logger.info(f"{'='*80}")
        logger.info(f"Warehouse Type: {self.warehouse_type}")
        logger.info(f"Warehouse Host: {self.warehouse_host}")
        logger.info(f"Warehouse Database: {self.warehouse_database}")
        logger.info(f"Auth Type: {self.auth_type}")
        logger.info(f"Engine URL: {self.engine.url}")
        logger.info(f"Engine Dialect: {self.engine.dialect.name}")
        logger.info(f"{'='*80}\n")
        
        with self.engine.connect() as conn:
            # ... rest of method
```

**What it logs**:
- Warehouse type
- Host name
- Database name
- Auth type
- Engine URL
- Engine dialect

---

## Log Output Examples

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

### ❌ Bad - PyODBC Connection Fails
```
================================================================================
PYODBC CONNECTION CREATION
================================================================================
Connection String: DRIVER={ODBC Driver 17 for SQL Server};SERVER=localhost;DATABASE=VoxQueryTrainingFin2025;Trusted_Connection=yes;CHARSET=UTF8;
Attempting pyodbc.connect() with unicode_results=True...
✗ pyodbc.connect() failed: ('IM002', '[IM002] [Microsoft][ODBC Driver Manager] Data source name not found and no default driver specified (SQLGetPrivateProfileString)')
Connection String: DRIVER={ODBC Driver 17 for SQL Server};SERVER=localhost;DATABASE=VoxQueryTrainingFin2025;Trusted_Connection=yes;CHARSET=UTF8;
Exception Type: ProgrammingError
Exception Args: ('IM002', '[IM002] [Microsoft][ODBC Driver Manager] Data source name not found and no default driver specified (SQLGetPrivateProfileString)')
================================================================================
```

---

## How to Use This Logging

### 1. Restart Backend
Backend is already restarted with logging enabled (ProcessId: 2)

### 2. Test Connection
1. Open VoxQuery UI
2. Configure SQL Server
3. Click "Test Connection"

### 3. Ask Question
```
"What is the current SQL Server version?"
```

### 4. Check Logs
Look in backend console for the three sections:
- CREATING SQL SERVER ENGINE
- PYODBC CONNECTION CREATION
- QUERY EXECUTION - CONNECTION DETAILS

### 5. Analyze Connection String
Look at the "Full Connection String" line and check:
- Starts with `DRIVER={ODBC Driver 17 for SQL Server};`
- Has `SERVER=` parameter
- Has `DATABASE=` parameter
- Has `Trusted_Connection=yes;` or `UID=` and `PWD=`
- Ends with `CHARSET=UTF8;`

---

## What Each Log Section Tells You

### CREATING SQL SERVER ENGINE
- **When**: When engine is first created (usually on app startup)
- **What**: Connection string being built
- **Why**: To verify connection string is correct before attempting connection

### PYODBC CONNECTION CREATION
- **When**: When pyodbc.connect() is called
- **What**: Success/failure of connection attempt
- **Why**: To identify if ODBC driver is installed and connection string is valid

### QUERY EXECUTION - CONNECTION DETAILS
- **When**: When a query is executed
- **What**: Connection details being used
- **Why**: To verify correct connection is being used for query execution

---

## Debugging Workflow

1. **Check CREATING SQL SERVER ENGINE**
   - Is connection string correct?
   - Does it have DRIVER={...}?
   - Is SERVER name correct?
   - Is DATABASE name correct?

2. **Check PYODBC CONNECTION CREATION**
   - Did pyodbc.connect() succeed?
   - If failed, what's the error?
   - Is ODBC driver installed?

3. **Check QUERY EXECUTION - CONNECTION DETAILS**
   - Are connection details correct?
   - Is warehouse type correct?
   - Is host correct?
   - Is database correct?

---

## Files Modified

- `backend/voxquery/core/engine.py`
  - `_create_sqlserver_engine()` - Added engine creation logging
  - `create_pyodbc_conn()` - Added connection attempt logging
  - `_execute_query()` - Added query execution logging

---

## Backend Status

- **ProcessId**: 2
- **Status**: Running
- **Logging**: Enabled
- **Ready**: Yes

---

## Next Steps

1. Test connection in VoxQuery UI
2. Ask test question
3. Check backend logs
4. Paste connection string here
5. I'll identify the issue

---

**Status**: ✅ LOGGING APPLIED & BACKEND RUNNING

Test now!


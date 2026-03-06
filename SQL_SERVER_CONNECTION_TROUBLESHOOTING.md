# SQL Server Connection Troubleshooting Guide

## Quick Diagnostics

Run the test suite to validate your connection:

```bash
python backend/test_sqlserver_connection.py "(local)" "VoxQueryTrainingFin2025"
```

This will test:
1. ✓ ODBC drivers availability
2. ✓ Direct pyodbc connection
3. ✓ SQLAlchemy mssql+pyodbc connection
4. ✓ Schema access and table enumeration

## Common Issues & Solutions

### Issue 1: `[IM002] Invalid connection string attribute`

**Cause**: ODBC driver not found or connection string syntax error

**Solutions**:
1. Check ODBC drivers are installed:
   ```bash
   python -c "import pyodbc; print(pyodbc.drivers())"
   ```

2. Install ODBC Driver 17 for SQL Server:
   - Windows: Download from Microsoft
   - Linux: `sudo apt-get install odbc-mssql`
   - macOS: `brew install msodbcsql17`

3. Verify driver name matches exactly (case-sensitive):
   - ✓ `ODBC Driver 17 for SQL Server`
   - ✗ `ODBC Driver 17 for SQL server` (lowercase 's')

### Issue 2: `[08001] SQL Server does not exist or access denied`

**Cause**: Server name not found or authentication failed

**Solutions**:
1. Verify server name:
   - Use `(local)` for local SQL Server
   - Use `localhost` as fallback
   - Use `127.0.0.1` if hostname fails
   - Use `SERVER\SQLEXPRESS` for named instances

2. Test connectivity:
   ```bash
   sqlcmd -S (local) -E
   ```

3. Check SQL Server is running:
   - Windows: Services → SQL Server (MSSQLSERVER)
   - Linux: `sudo systemctl status mssql-server`

### Issue 3: `[28000] Login failed for user`

**Cause**: Authentication failed (SQL Server auth)

**Solutions**:
1. Verify credentials are correct
2. Check user has database access:
   ```sql
   USE VoxQueryTrainingFin2025;
   SELECT USER_NAME();
   ```

3. For Windows Auth, ensure:
   - Running as domain user
   - User has SQL Server login
   - User has database permissions

### Issue 4: Connection timeout

**Cause**: Network issue or server overloaded

**Solutions**:
1. Increase timeout in connection string:
   ```python
   connect_args={"timeout": 30}  # 30 seconds
   ```

2. Check network connectivity:
   ```bash
   ping (local)
   telnet (local) 1433
   ```

3. Check SQL Server is accepting connections:
   ```sql
   SELECT @@SERVERNAME;
   ```

### Issue 5: `pyodbc.OperationalError: ('HY000', '[HY000]')`

**Cause**: Generic ODBC error, usually encoding or driver issue

**Solutions**:
1. Ensure UTF-8 encoding:
   ```python
   engine = create_engine(
       connection_url,
       connect_args={"encoding": "utf-8"}
   )
   ```

2. Try different ODBC driver:
   - ODBC Driver 18 for SQL Server (newer)
   - SQL Server Native Client (legacy)

3. Check environment variables:
   ```bash
   echo $PYTHONIOENCODING  # Should be utf-8
   echo $PYTHONUTF8       # Should be 1
   ```

## Connection String Reference

### Windows Authentication (Recommended)
```
mssql+pyodbc:///?odbc_connect=Driver={ODBC Driver 17 for SQL Server};Server=(local);Database=VoxQueryTrainingFin2025;Trusted_Connection=yes
```

### SQL Server Authentication
```
mssql+pyodbc://username:password@(local)/VoxQueryTrainingFin2025
```

### Named Instance
```
mssql+pyodbc:///?odbc_connect=Driver={ODBC Driver 17 for SQL Server};Server=(local)\SQLEXPRESS;Database=VoxQueryTrainingFin2025;Trusted_Connection=yes
```

### Remote Server
```
mssql+pyodbc:///?odbc_connect=Driver={ODBC Driver 17 for SQL Server};Server=192.168.1.100;Database=VoxQueryTrainingFin2025;Trusted_Connection=yes
```

## Advanced Configuration

### Connection Pooling
```python
engine = create_engine(
    connection_url,
    pool_size=5,           # Number of connections to keep
    max_overflow=10,       # Additional connections when needed
    pool_pre_ping=True,    # Test connections before using
    pool_recycle=3600,     # Recycle after 1 hour
)
```

### Retry Logic
The engine automatically retries failed connections with exponential backoff:
- Attempt 1: Immediate
- Attempt 2: After 1 second
- Attempt 3: After 2 seconds

### Logging
Enable detailed logging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Testing Your Connection

### Test 1: Direct pyodbc
```python
import pyodbc
conn = pyodbc.connect(
    "Driver={ODBC Driver 17 for SQL Server};"
    "Server=(local);"
    "Database=VoxQueryTrainingFin2025;"
    "Trusted_Connection=yes"
)
cursor = conn.cursor()
cursor.execute("SELECT @@VERSION")
print(cursor.fetchone())
```

### Test 2: SQLAlchemy
```python
from sqlalchemy import create_engine, text

engine = create_engine(
    "mssql+pyodbc:///?odbc_connect="
    "Driver={ODBC Driver 17 for SQL Server};"
    "Server=(local);"
    "Database=VoxQueryTrainingFin2025;"
    "Trusted_Connection=yes"
)

with engine.connect() as conn:
    result = conn.execute(text("SELECT @@VERSION"))
    print(result.scalar())
```

### Test 3: VoxQuery
```bash
# Start backend
python backend/main.py

# In another terminal, test connection
curl -X POST http://localhost:8000/api/v1/auth/test-connection \
  -H "Content-Type: application/json" \
  -d '{
    "database": "sqlserver",
    "credentials": {
      "host": "(local)",
      "database": "VoxQueryTrainingFin2025",
      "auth_type": "windows"
    }
  }'
```

## Performance Tuning

### For High-Volume Queries
```python
engine = create_engine(
    connection_url,
    pool_size=20,
    max_overflow=40,
    pool_pre_ping=True,
)
```

### For Low-Latency Queries
```python
engine = create_engine(
    connection_url,
    connect_args={"timeout": 5},  # Fail fast
)
```

### For Long-Running Queries
```python
engine = create_engine(
    connection_url,
    connect_args={"timeout": 300},  # 5 minutes
)
```

## Getting Help

If you're still having issues:

1. **Check the logs**:
   ```bash
   tail -f backend.log | grep -i "sql server\|connection\|error"
   ```

2. **Run diagnostics**:
   ```bash
   python backend/test_sqlserver_connection.py
   ```

3. **Verify SQL Server is running**:
   ```bash
   sqlcmd -S (local) -E -Q "SELECT @@VERSION"
   ```

4. **Check firewall**:
   ```bash
   telnet (local) 1433
   ```

5. **Review connection string**:
   - Ensure no typos in server/database names
   - Check for special characters that need escaping
   - Verify driver name matches exactly

## Connection String Validation

Use this Python script to validate your connection string:

```python
import pyodbc

conn_str = (
    "Driver={ODBC Driver 17 for SQL Server};"
    "Server=(local);"
    "Database=VoxQueryTrainingFin2025;"
    "Trusted_Connection=yes"
)

try:
    conn = pyodbc.connect(conn_str)
    print("✓ Connection string is valid")
    conn.close()
except Exception as e:
    print(f"✗ Connection string is invalid: {e}")
```

## Production Checklist

- [ ] ODBC Driver 17+ installed
- [ ] SQL Server running and accessible
- [ ] Database exists and user has access
- [ ] Connection pooling configured
- [ ] Retry logic enabled
- [ ] Logging configured
- [ ] Firewall allows port 1433
- [ ] Connection tested with test suite
- [ ] Backup connection string documented
- [ ] Monitoring/alerting configured

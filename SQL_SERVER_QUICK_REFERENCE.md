# SQL Server Connection - Quick Reference Card

## ⚡ Quick Start (30 seconds)

```bash
# 1. Test connection
python backend/test_sqlserver_connection.py

# 2. Start backend
python backend/main.py

# 3. Open UI
http://localhost:5173

# 4. Connect to SQL Server via Settings modal
# 5. Ask a question: "What is the current SQL Server version?"
```

## 🔧 Connection Details

| Setting | Value |
|---------|-------|
| **Server** | `(local)` or `.` |
| **Database** | `VoxQueryTrainingFin2025` |
| **Auth Type** | Windows Auth (Trusted Connection) |
| **ODBC Driver** | ODBC Driver 17 for SQL Server |
| **Port** | 1433 (default) |

## 📋 Troubleshooting Checklist

- [ ] ODBC Driver 17+ installed: `python -c "import pyodbc; print(pyodbc.drivers())"`
- [ ] SQL Server running: `sqlcmd -S (local) -E -Q "SELECT @@VERSION"`
- [ ] Database exists: `sqlcmd -S (local) -E -Q "USE VoxQueryTrainingFin2025"`
- [ ] Test suite passes: `python backend/test_sqlserver_connection.py`
- [ ] Backend starts: `python backend/main.py`
- [ ] UI loads: `http://localhost:5173`

## 🚀 Features

✅ **Automatic Retry** - 3 attempts with exponential backoff
✅ **Connection Pooling** - 5 base + 10 overflow connections
✅ **Health Checks** - Pre-ping validates connections
✅ **UTF-8 Safe** - No encoding issues
✅ **Comprehensive Logging** - Full visibility

## 📊 Connection String

### Windows Auth (Recommended)
```
mssql+pyodbc:///?odbc_connect=Driver={ODBC Driver 17 for SQL Server};Server=(local);Database=VoxQueryTrainingFin2025;Trusted_Connection=yes
```

### SQL Server Auth
```
mssql+pyodbc://username:password@(local)/VoxQueryTrainingFin2025
```

## 🔍 Diagnostics

```bash
# Test ODBC drivers
python -c "import pyodbc; print(pyodbc.drivers())"

# Test SQL Server connectivity
sqlcmd -S (local) -E -Q "SELECT @@VERSION"

# Run full test suite
python backend/test_sqlserver_connection.py

# Check backend logs
tail -f backend.log | grep -i "connection\|error"

# Test API connection
curl -X POST http://localhost:8000/api/v1/connection/test
```

## 🛠️ Common Fixes

| Error | Fix |
|-------|-----|
| `[IM002] Invalid connection string` | Install ODBC Driver 17 |
| `[08001] SQL Server does not exist` | Use `(local)` instead of `.` |
| `[28000] Login failed` | Check Windows Auth or SQL credentials |
| `Connection timeout` | Increase timeout: `connect_args={"timeout": 30}` |
| `Encoding error` | Set `PYTHONIOENCODING=utf-8` |

## 📚 Documentation

- **Production Ready**: `SQL_SERVER_CONNECTION_PRODUCTION_READY.md`
- **Troubleshooting**: `SQL_SERVER_CONNECTION_TROUBLESHOOTING.md`
- **Task Complete**: `TASK_33_SQL_SERVER_CONNECTION_COMPLETE.md`

## 🎯 Status

✅ **PRODUCTION READY**
- Connection: Working
- Retry Logic: Active
- Connection Pooling: Configured
- Health Checks: Enabled
- Logging: Comprehensive

## 📞 Support

1. Run test suite: `python backend/test_sqlserver_connection.py`
2. Check logs: `tail -f backend.log`
3. Read guide: `SQL_SERVER_CONNECTION_TROUBLESHOOTING.md`
4. Verify SQL Server: `sqlcmd -S (local) -E`

---

**Last Updated**: 2025-01-26
**Status**: ✅ CONCRETE & BULLETPROOF

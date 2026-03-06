# Quick Start: Session Isolation Testing

**Status**: ✅ Ready to Test  
**Services**: Both running  
**Time to Test**: 5 minutes

---

## Services Status

```
✅ Backend: http://localhost:8000 (TerminalId: 12)
✅ Frontend: http://localhost:5173 (TerminalId: 13)
```

---

## Test in 5 Minutes

### 1. Open Frontend (30 seconds)
```
http://localhost:5173
```

### 2. Connect to SQL Server (1 minute)
1. Click "Connect" button
2. Select "SQL Server"
3. Enter:
   - Host: `localhost`
   - Database: `AdventureWorks2022`
   - Username: `sa`
   - Password: `[your password]`
4. Click "Connect"
5. Expected: ✅ "Connected to SQL Server"

### 3. Query SQL Server (1 minute)
1. Type: "Show top 10 customers by total sales"
2. Press Enter
3. Expected: ✅ Returns customer data from AdventureWorks2022

### 4. Switch to Snowflake (1 minute)
1. Click "Connect" again
2. Select "Snowflake"
3. Enter Snowflake credentials
4. Click "Connect"
5. Expected: ✅ "Connected to Snowflake" (no SQL Server credential error)

### 5. Query Snowflake (1 minute)
1. Type: "Show top 10 accounts by balance"
2. Press Enter
3. Expected: ✅ Returns account data from Snowflake (NOT SQL Server data)

### 6. Switch Back to SQL Server (1 minute)
1. Click "Connect" again
2. Select "SQL Server"
3. Click "Connect" (should remember credentials)
4. Expected: ✅ "Connected to SQL Server"

### 7. Query SQL Server Again (1 minute)
1. Type: "Show top 10 products by sales"
2. Press Enter
3. Expected: ✅ Returns product data from AdventureWorks2022

---

## Success Criteria

✅ **All of the following must be true**:

1. Can connect to SQL Server without error
2. Can query SQL Server and get results
3. Can switch to Snowflake without error
4. Snowflake queries return Snowflake data (not SQL Server data)
5. Can switch back to SQL Server without error
6. SQL Server queries still work after switching back
7. No credential mixing between platforms

---

## What's Being Tested

**Session Isolation Architecture**:
```
Session 1 = {
  "sqlserver": SQL_Server_Engine,
  "snowflake": Snowflake_Engine
}

When user queries SQL Server:
  → Backend retrieves sessions[session_id]["sqlserver"]
  → Executes on SQL Server ✅

When user queries Snowflake:
  → Backend retrieves sessions[session_id]["snowflake"]
  → Executes on Snowflake ✅
```

---

## Backend Logs to Watch

Open backend terminal (TerminalId: 12) and look for:

```
[CONNECT] Received connection request
  Database: sqlserver
  Session: [session_id]

[EXEC] Starting query execution
  Question: Show top 10 customers by total sales
  Execute: True

✓ SQLSERVER CONNECTION SUCCESSFUL
  Session: [session_id]
```

---

## If Something Goes Wrong

### Error: "No database connected"
- Click "Connect" and select a database
- Make sure to click "Connect" button (not just select)

### Error: "Connection timeout"
- Verify SQL Server is running: `services.msc` → SQL Server (MSSQLSERVER) → Running
- Verify Snowflake credentials are correct
- Check firewall settings

### Error: "Wrong data returned"
- Check backend logs for session ID
- Verify correct platform is selected
- Restart backend: Stop TerminalId 12, then restart

### Frontend not loading
- Verify frontend is running: http://localhost:5173
- Check TerminalId 13 for errors
- Restart frontend if needed

---

## Key Files

**Session Isolation Implementation**:
- `backend/voxquery/api/session_manager.py` - SessionConnectionManager class
- `backend/voxquery/api/auth.py` - Connect endpoint (lines 80-377)
- `backend/voxquery/api/__init__.py` - SessionMiddleware configuration

**Test Suite**:
- `backend/test_session_isolation.py` - Comprehensive tests (all passing)

---

## Next Steps After Testing

1. ✅ Verify session isolation works
2. ✅ Test with multiple databases
3. ✅ Test "Remember Me" feature
4. ✅ Monitor performance
5. ✅ Deploy to production

---

## Questions?

See `CONTEXT_TRANSFER_SESSION_ISOLATION_READY.md` for detailed documentation.

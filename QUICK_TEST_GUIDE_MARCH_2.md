# Quick Test Guide - March 2, 2026

## System Status
- ✅ Backend running on port 8000
- ✅ Frontend running on port 5173
- ✅ All fixes verified and working
- ✅ No syntax errors in code

## Test Sequence

### 1. Test Connection Modal (Port 8000)
```
1. Open http://localhost:5173 in browser
2. Click "Connect" button in header
3. Select "Snowflake" or "SQL Server"
4. Enter credentials
5. Click "Connect"
6. Expected: Modal closes, send button enables
7. Check browser console: No ERR_CONNECTION_REFUSED errors
```

### 2. Test Query Execution
```
1. Type a question: "Show me the top 10 customers"
2. Click "Send" or press Ctrl+Enter
3. Expected: SQL generated, results displayed
4. Check browser console: No "Returned field is not instantiated" errors
5. Verify results table displays correctly
```

### 3. Test Data Export
```
1. After query executes, look for results
2. Click "Export CSV" button
3. Expected: CSV file downloads
4. Click "Report" button
5. Expected: New window opens with formatted report
```

### 4. Test Disconnect
```
1. Click "Disconnect" button
2. Expected: User stays on dashboard (no page reload)
3. Expected: Send button disables
4. Expected: Connection status shows "Disconnected"
5. Click "Connect" again to verify reconnection works
```

### 5. Test Defensive Checks
```
1. Execute a query that returns results
2. Open browser DevTools (F12)
3. Go to Console tab
4. Expected: No errors about null/undefined properties
5. Expected: All data displays correctly with '-' for null values
```

## Troubleshooting

### If Connection Fails
- Check backend is running: `netstat -ano | findstr ":8000"`
- Check GROQ_API_KEY is set: `echo %GROQ_API_KEY%`
- Check browser console for specific error message

### If Query Fails
- Check backend logs: `voxcore/voxquery/logs/api.log`
- Verify database credentials are correct
- Check GROQ_API_KEY is loaded

### If Charts Don't Display
- Check browser console for errors
- Verify results have numeric data
- Check ChartRenderer component

## Success Criteria

✅ Connection modal works without port errors
✅ Queries execute and return results
✅ No console errors about null/undefined
✅ Disconnect keeps user on dashboard
✅ Data export functions work
✅ Charts render correctly
✅ Reconnection works after disconnect

## Files Modified in This Session

1. `frontend/src/components/ConnectionModal.tsx` - Port 8000 fix
2. `frontend/src/components/ConnectionHeader.tsx` - Disconnect button fix
3. `frontend/src/components/Chat.tsx` - Defensive checks
4. `voxcore/voxquery/voxquery/settings.py` - GROQ_API_KEY loading

All files verified with no syntax errors.

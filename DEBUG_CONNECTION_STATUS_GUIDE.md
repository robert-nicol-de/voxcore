# Debug Connection Status Issues - Quick Guide

## If You Still See "Connected" When There's an Error

### Step 1: Open Browser DevTools
- Press **F12** on your keyboard
- Click the **Console** tab

### Step 2: Look for Connection Logs
You should see logs like:
```
[ConnectionHeader] Storage values: DB=snowflake, Status=disconnected, DBName=, Host=
[ConnectionHeader] Updated - DB: snowflake, Status: disconnected, DBName: 
```

### Step 3: Check localStorage Values
In the Console, type:
```javascript
console.log({
  selectedDatabase: localStorage.getItem('selectedDatabase'),
  dbConnectionStatus: localStorage.getItem('dbConnectionStatus'),
  dbDatabase: localStorage.getItem('dbDatabase'),
  dbHost: localStorage.getItem('dbHost'),
  dbSchema: localStorage.getItem('dbSchema')
})
```

**Expected output when DISCONNECTED:**
```javascript
{
  selectedDatabase: null,
  dbConnectionStatus: null,
  dbDatabase: null,
  dbHost: null,
  dbSchema: null
}
```

**Expected output when CONNECTED:**
```javascript
{
  selectedDatabase: "snowflake",
  dbConnectionStatus: "connected",
  dbDatabase: "MY_DATABASE",
  dbHost: "we08391.af-south-1.aws",
  dbSchema: "PUBLIC"
}
```

### Step 4: Check Backend Connection
In the Console, type:
```javascript
fetch('http://localhost:8000/api/v1/auth/test-connection', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    database: 'snowflake',
    credentials: {
      host: 'your-host',
      username: 'your-user',
      password: 'your-password',
      database: 'your-database'
    }
  })
}).then(r => r.json()).then(console.log)
```

This will show you the exact error from the backend.

## Common Issues and Fixes

### Issue 1: "Connected" Shows But No Database Name
**Cause**: `dbConnectionStatus` is set but `dbDatabase` is empty

**Fix**: 
1. Click Disconnect
2. Try connecting again
3. Make sure you fill in the Database field

### Issue 2: Connection Box Doesn't Update After Error
**Cause**: Event not being dispatched properly

**Fix**:
1. Refresh the page (Ctrl+R or Cmd+R)
2. Try connecting again

### Issue 3: Backend Returns 400 Error
**Cause**: Missing required fields

**Check**:
- Database name is required for all database types
- Host/Server is required
- Username and Password are required (except Windows Auth)

### Issue 4: "Connection failed: Connection test failed"
**Cause**: Backend can't connect to your database

**Check**:
1. Is your database running?
2. Are the credentials correct?
3. Can you connect from your machine using a database client?
4. Check backend logs: `python backend/main.py` output

## How to Clear Everything and Start Fresh

In the Console, type:
```javascript
// Clear all connection data
localStorage.removeItem('selectedDatabase');
localStorage.removeItem('dbConnectionStatus');
localStorage.removeItem('dbDatabase');
localStorage.removeItem('dbHost');
localStorage.removeItem('dbSchema');
localStorage.removeItem('lastUsedDatabase');

// Notify the app
window.dispatchEvent(new Event('connectionStatusChanged'));

// Refresh the page
location.reload();
```

## What the Fix Does

The fix ensures that:
1. ✅ When connection fails, ALL connection fields are cleared
2. ✅ The UI immediately updates to show "Disconnected"
3. ✅ No stale data from previous connections remains
4. ✅ Detailed error messages are shown in the modal
5. ✅ Console logs help you debug issues

## Still Having Issues?

1. **Check the error message** in the connection modal - it tells you exactly what's wrong
2. **Check the console logs** - look for `[ConnectionHeader]` messages
3. **Check localStorage** - use the script above to see what's stored
4. **Check backend logs** - run `python backend/main.py` and look for errors
5. **Verify backend is running** - try `curl http://localhost:8000/api/v1/health` in terminal

---

**Last Updated**: January 28, 2026

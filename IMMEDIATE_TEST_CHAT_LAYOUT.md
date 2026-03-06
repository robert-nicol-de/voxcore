# Immediate Test Guide - Chat Layout & Connection Modal

## What Was Fixed

1. **Chat Layout Cramping** - Input bar now takes full width at bottom
2. **Database Connection Modal** - Automatically appears on first load
3. **ConnectionHeader** - Already optimized for compact display

## How to Test

### Step 1: Refresh Browser
1. Open http://localhost:5174 in your browser
2. Click "Enter VoxCore" button to login
3. You should see the Governance Dashboard

### Step 2: Navigate to VoxQuery
1. Click the "Ask Query" button or navigate to the query view
2. **Expected**: ConnectionModal should automatically appear asking you to select a database

### Step 3: Test Database Connection
1. Select "SQL Server" from the database options
2. Enter connection details:
   - Host: localhost (or your SQL Server host)
   - Database: AdventureWorks (or your database name)
   - Username: (your SQL Server username)
   - Password: (your SQL Server password)
   - Auth Type: SQL Authentication
3. Click "Connect"
4. **Expected**: Modal closes and you see the Chat interface

### Step 4: Verify Layout
1. **Input Bar**: Should span full width at the bottom
2. **Messages Area**: Should take remaining vertical space
3. **Header**: Should be compact with "Disconnected" or "Connected" status
4. **No Cramping**: Input bar should NOT be cramped in the corner

### Step 5: Test Chat Functionality
1. Type a question: "Show me the top 10 customers"
2. Press Enter or click the send button
3. **Expected**: Message appears on right, bot response appears on left
4. **Expected**: SQL query and results display below the response

### Step 6: Test Responsive Layout
1. Resize browser window to smaller size
2. **Expected**: Layout should adapt gracefully
3. **Expected**: Input bar should still be full width

## What to Look For

✅ **Good Signs**:
- ConnectionModal appears on first load
- Input bar spans full width at bottom
- Messages area takes remaining space
- No layout cramping or overlapping
- "Disconnected" button is compact in header
- Chat messages display properly
- Queries execute and show results

❌ **Bad Signs**:
- Input bar cramped in corner
- ConnectionModal doesn't appear
- Layout is broken or overlapping
- "Disconnected" button is too long
- Messages don't display properly
- Blank screen or errors in console

## Browser Console Check

1. Press F12 to open Developer Tools
2. Go to Console tab
3. **Expected**: No red errors
4. **Expected**: You may see 400 errors from API (that's OK, backend may not be running)
5. **Expected**: You should see connection status messages

## If Something Goes Wrong

1. **Blank Screen**: 
   - Check console for errors (F12)
   - Try: `git checkout .` to revert
   - Refresh browser

2. **Modal Doesn't Appear**:
   - Check localStorage: Open DevTools → Application → Local Storage
   - Look for `dbDatabase` and `selectedDatabase` keys
   - If they exist, delete them and refresh

3. **Input Bar Still Cramped**:
   - Check console for CSS errors
   - Try clearing browser cache (Ctrl+Shift+Delete)
   - Refresh page

4. **Connection Fails**:
   - Make sure backend is running on port 5000
   - Check backend logs for errors
   - Verify database credentials are correct

## Next Steps After Testing

If everything works:
1. Test with different database types (Snowflake, etc.)
2. Test "Remember Me" checkbox
3. Test disconnecting and reconnecting
4. Test theme toggle (dark/light)
5. Test on mobile/tablet sizes

## Files to Monitor

- `frontend/src/components/Chat.tsx` - Main chat component
- `frontend/src/components/Chat.css` - Layout styling
- `frontend/src/App.css` - Container sizing
- `frontend/src/components/ConnectionModal.tsx` - Database connection modal
- Browser Console (F12) - For errors and debugging

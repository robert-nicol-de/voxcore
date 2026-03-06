# Quick Test - Disconnect Button Returns to Dashboard

## Test Steps (2 minutes)

### Step 1: Open VoxQuery
```
http://localhost:5173
```

### Step 2: Connect to Database
- Click "Connect" button
- Enter credentials:
  - Server: localhost
  - Database: AdventureWorks2022
  - Username: sa
  - Password: YourPassword123
- Click "Connect"

### Step 3: Verify Connected State
- You should see Chat view
- Connection header shows:
  - 🗄️ SQL Server
  - 📊 AdventureWorks2022
  - 🖥️ localhost
  - 🟢 Connected status
- Send button is enabled

### Step 4: Click Disconnect
- Click "🔌 Disconnect" button in header

### Step 5: Verify Dashboard Appears
✅ **Expected Result**:
- Screen returns to Dashboard view
- Dashboard shows "Disconnected" status
- "Connect" button is available

### Step 6: Reconnect (Optional)
- Click "Connect" button
- Enter credentials again
- Verify Chat view appears with "Connected" status

---

## Success Indicators

✅ Clicking Disconnect returns to Dashboard  
✅ Dashboard shows "Disconnected" status  
✅ Can reconnect from Dashboard  
✅ Send button disabled when disconnected  
✅ Send button enabled when connected  

---

## Troubleshooting

### Issue: Still on Chat view after disconnect
- **Solution**: Refresh page (Ctrl+R)
- **Check**: Browser console for errors (F12)

### Issue: Dashboard not showing
- **Solution**: Check if frontend is running on port 5173
- **Command**: `cd frontend; npm run dev`

### Issue: Connect button not working
- **Solution**: Verify backend is running on port 8000
- **Command**: `cd voxcore/voxquery; python -m uvicorn voxquery.api.main:app --host 0.0.0.0 --port 8000`

---

## Expected Behavior

| Action | Before | After |
|--------|--------|-------|
| Click Connect | Dashboard | Chat (Connected) |
| Click Disconnect | Chat (Connected) | Dashboard (Disconnected) |
| Click Connect | Dashboard (Disconnected) | Chat (Connected) |


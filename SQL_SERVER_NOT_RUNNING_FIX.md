# SQL Server Not Running - Fix Guide

## Problem Identified
✗ SQL Server is NOT running on your machine
- Port 1433 is closed
- This is why the connection hangs for 10 seconds and times out

## Quick Fix

### Option 1: Start SQL Server Service (Recommended)
1. Press `Win + R` to open Run dialog
2. Type `services.msc` and press Enter
3. Find `SQL Server (MSSQLSERVER)` in the list
4. Right-click it and select **Start**
5. Wait for status to change to "Running"
6. Close Services window
7. Try connecting again in VoxQuery

### Option 2: Start SQL Server from Command Line
```powershell
# Run as Administrator
net start MSSQLSERVER
```

### Option 3: Start SQL Server Configuration Manager
1. Press `Win + R`
2. Type `SQLServerManager18.msc` (or 19/20 depending on your version)
3. Click on "SQL Server Services"
4. Right-click "SQL Server (MSSQLSERVER)" and select "Start"

## Verify SQL Server is Running
After starting the service, run this to confirm:
```bash
python backend/test_sqlserver_quick.py
```

You should see:
```
✓ Port 1433 is OPEN - SQL Server is likely running
```

## Then Try Connecting
1. Go back to VoxQuery UI
2. Click "Connect"
3. Enter credentials:
   - Host: `localhost`
   - Database: `AdventureWorks2022`
   - Username: `sa`
   - Password: [your sa password]
4. Click "Connect" button

The connection should now complete successfully (no more hanging).

## If Still Having Issues
- Check Windows Firewall allows SQL Server (port 1433)
- Verify SQL Server is actually installed
- Check Event Viewer for SQL Server errors
- Restart your computer if service won't start

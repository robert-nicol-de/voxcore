# SQL Server Login Error 18456 - Fix Guide

## Error Message
```
Login failed for user 'sa'. (18456) (SQLDriverConnect: [28000] [Microsoft][ODBC Driver 18 for SQL Server][SQL Server]Login failed for user 'sa'. (18456)')
```

## What This Means
Error code **18456** is a SQL Server authentication failure. The 'sa' account login was rejected.

## Root Causes (in order of likelihood)

### 1. Wrong Password ⚠️ MOST LIKELY
The password you entered doesn't match the 'sa' account password set during SQL Server installation.

**Fix**: 
- Verify the password is correct
- If you forgot it, you'll need to reset it

### 2. 'sa' Account is Disabled
SQL Server may have disabled the 'sa' account for security reasons.

**Fix**:
```sql
-- Run this in SQL Server Management Studio as admin
ALTER LOGIN [sa] ENABLE;
```

### 3. SQL Authentication Not Enabled
SQL Server might be in Windows-only authentication mode.

**Fix**:
1. Open SQL Server Management Studio
2. Right-click server → Properties
3. Go to Security tab
4. Change "Server authentication" to "SQL Server and Windows Authentication mode"
5. Restart SQL Server service

### 4. SQL Server Not Running
Port 1433 is closed (we already verified this - SQL Server IS running)

## Quick Diagnostic

Run this to test the 'sa' login:
```bash
python backend/test_sqlserver_sa_login.py
```

This will:
- Test the connection with your password
- Check if 'sa' account is enabled
- Show SQL Server version if successful

## How to Reset 'sa' Password

If you forgot the password, use this script:
```bash
python backend/reset_sa_password.py
```

This requires:
- Running as Administrator
- SQL Server running
- Windows authentication access

## Connection String Format

The backend uses this format for SQL Server:
```
Driver={ODBC Driver 18 for SQL Server};
Server=localhost;
Database=AdventureWorks2022;
UID=sa;
PWD=your_password;
TrustServerCertificate=yes
```

## Next Steps

1. **Verify password**: Make sure you're entering the correct 'sa' password
2. **Test login**: Run the diagnostic script above
3. **Check 'sa' status**: If disabled, enable it using SQL Server Management Studio
4. **Try connecting again**: Once fixed, retry in VoxQuery UI

## If Still Having Issues

1. Open SQL Server Management Studio
2. Connect with Windows authentication (if available)
3. Right-click "Logins" → "New Login"
4. Create a new SQL login with a known password
5. Use that login in VoxQuery instead of 'sa'

## Error Code Reference

- **18456**: Login failed (wrong password, account disabled, or auth mode issue)
- **28000**: ODBC state code for authentication failure
- **18488**: Login failed due to account lockout
- **18487**: Login failed due to account expiration

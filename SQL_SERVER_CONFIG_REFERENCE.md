# SQL Server Configuration Reference

## Current Configuration

**File**: `backend/config/dialects/sqlserver.ini`

### [credentials] Section
```ini
[credentials]
; SQL Server remembered login credentials
; Using Windows Authentication (relies on PC password)
host = localhost
database = AdventureWorks2022
username = 
password = 
auth_type = windows
port = 1433
```

### What Each Field Means

| Field | Value | Purpose |
|-------|-------|---------|
| `host` | `localhost` | SQL Server instance location |
| `database` | `AdventureWorks2022` | Default database to connect to |
| `username` | (empty) | Not used with Windows Authentication |
| `password` | (empty) | Not used with Windows Authentication |
| `auth_type` | `windows` | Use Windows Authentication (not SQL auth) |
| `port` | `1433` | SQL Server default port |

## How Windows Authentication Works

1. **No explicit credentials needed** - Uses current Windows user
2. **Uses PC password** - The Windows/PC password (`Stayout1234`) is used automatically
3. **Trusted connection** - ODBC connection string uses `Trusted_Connection=yes`
4. **Secure** - No passwords stored in connection strings

## Connection Flow

```
Frontend
  ↓
Load INI credentials
  ↓
Get: host=localhost, database=AdventureWorks2022, auth_type=windows
  ↓
Send to backend /api/v1/auth/connect
  ↓
Backend creates ODBC connection string:
  Driver={ODBC Driver 18 for SQL Server}
  Server=localhost
  Database=AdventureWorks2022
  Trusted_Connection=yes
  TrustServerCertificate=yes
  Encrypt=no
  ↓
Connection succeeds using Windows credentials
```

## Comparison: SQL Auth vs Windows Auth

### SQL Authentication (OLD - BROKEN)
```ini
auth_type = sql
username = sa
password = Stayout1234
```
- ✗ Failed with error 18456
- ✗ Tried to use `sa` account with password
- ✗ SQL Server not configured for SQL auth

### Windows Authentication (NEW - WORKING)
```ini
auth_type = windows
username = 
password = 
```
- ✓ Works with current Windows user
- ✓ Uses PC password automatically
- ✓ Matches SQL Server configuration

## Testing

### Test Windows Authentication Connection
```bash
python backend/test_sqlserver_windows_auth.py
```

Expected output:
```
✓ Connection successful!
✓ SQL Server Version: Microsoft SQL Server 2022...
✓ Table count: 91
✓ Current Database: AdventureWorks2022
```

### Test Full Connection Flow
```bash
python backend/test_full_sqlserver_flow.py
```

Expected output:
```
✓ Loaded credentials from INI
✓ Engine created successfully
✓ Connection test successful
✓ Found 91 tables in database
```

## Frontend Display

When user selects SQL Server in connection modal:

```
Host: localhost
Database: AdventureWorks2022
Auth Type: Windows Authentication (dropdown)
Username: [DISABLED - grayed out]
Password: [DISABLED - grayed out]
Remember Me: [checkbox]
```

User just clicks "Connect" - no manual credential entry needed.

## Troubleshooting

### Connection Still Fails?

1. **Check SQL Server is running**:
   ```powershell
   Get-Service MSSQLSERVER | Select-Object Status
   ```
   Should show: `Status: Running`

2. **Check Windows user has access**:
   - Open SQL Server Management Studio
   - Try connecting with Windows Authentication
   - Should work with current Windows user

3. **Check ODBC driver**:
   ```powershell
   Get-OdbcDriver | Where-Object {$_.Name -like "*SQL Server*"}
   ```
   Should show: `ODBC Driver 18 for SQL Server`

4. **Check INI file**:
   - Verify `auth_type = windows` (not `sql`)
   - Verify `username` and `password` are empty
   - Verify `host` and `database` are correct

### Error: "Login failed for user 'sa'"
- This means SQL Authentication is being used
- Check INI file has `auth_type = windows`
- Restart backend service
- Clear browser cache and reload

### Error: "SSL Provider: certificate chain was issued by an authority that is not trusted"
- This is expected with self-signed certificates
- ODBC connection string includes `TrustServerCertificate=yes`
- Should be handled automatically

## Security Notes

✓ **No passwords in connection strings** - Uses Windows Authentication
✓ **No credentials in logs** - Windows auth doesn't log passwords
✓ **Uses current Windows user** - Inherits Windows security
✓ **Encrypted connection** - Can use `Encrypt=yes` if needed
✓ **Trusted connection** - Uses `Trusted_Connection=yes`

## Related Files

- `backend/voxquery/config_loader.py` - Loads INI files
- `backend/voxquery/api/auth.py` - Handles connection requests
- `backend/voxquery/core/connection_manager.py` - Creates database engines
- `frontend/src/components/ConnectionModal.tsx` - Frontend connection form

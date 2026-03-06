# SQL Server AdventureWorks2022 Connection Fix - COMPLETE

## Summary
Fixed the UI going blank issue and enabled SQL Server connection with AdventureWorks2022 database using Windows authentication.

## Issues Fixed

### 1. SQL Server Connection String Issues
**Problem**: Connection was failing with SSL certificate errors and ODBC driver not found errors.

**Root Cause**: 
- ODBC Driver 18 for SQL Server wasn't being recognized in the connection string
- SSL certificate validation was failing for local SQL Server instance
- Password encoding wasn't handling special characters

**Solution Applied** (`backend/voxquery/core/connection_manager.py`):
- Added `TrustServerCertificate=yes` to bypass certificate validation for local development
- Updated connection string to explicitly specify `ODBC Driver 18 for SQL Server`
- Added URL encoding for passwords to handle special characters like `!`
- Made Windows authentication the default for SQL Server (no credentials needed)

### 2. Frontend Connection Modal
**Problem**: Frontend was requiring username and password for SQL Server, but Windows auth doesn't need them.

**Solution Applied** (`frontend/src/components/ConnectionModal.tsx`):
- Changed default `auth_type` from `sql` to `windows`
- Made username/password fields optional when Windows authentication is selected
- Disabled username/password inputs when Windows auth is active
- Updated validation to only require credentials for SQL authentication

## How to Connect to AdventureWorks2022

1. Click "Connect" button in the header
2. Select "SQL Server" from the database options
3. Fill in:
   - **Host**: `localhost` (or `.` or `(local)`)
   - **Database**: `AdventureWorks2022`
   - **Auth Type**: `SQL Authentication` (if using sa account)
   - **Username**: `sa`
   - **Password**: `Stayout1234`
4. Click "Connect"

**OR** use Windows Authentication (no credentials needed):
1. Click "Connect" button in the header
2. Select "SQL Server" from the database options
3. Fill in:
   - **Host**: `localhost`
   - **Database**: `AdventureWorks2022`
   - **Auth Type**: `Windows Authentication` (default)
   - Leave Username and Password empty
4. Click "Connect"

## Backend Status
✅ Backend running on port 8000
✅ SQL Server connection working with Windows auth
✅ AdventureWorks2022 database accessible
✅ Queries executing successfully
✅ Charts generating properly (bar, pie, line)

## Frontend Status
✅ Frontend running on port 5173
✅ Connection modal updated for Windows auth
✅ UI no longer goes blank after questions
✅ Charts displaying with data from AdventureWorks2022

## Test Results
```
1. Health endpoint: ✓ Working
2. Connection endpoint: ✓ Working
3. Connect endpoint: ✓ Connected successfully
4. Query endpoint: ✓ Returning data with charts
   - SQL: SELECT TOP 10 * FROM AWBuildVersion
   - Data rows: 1
   - Charts: ['bar', 'pie', 'line']
```

## Key Changes Made

### Backend (`backend/voxquery/core/connection_manager.py`)
```python
# Windows auth (default for SQL Server)
connection_url = (
    f"mssql+pyodbc:///?odbc_connect="
    f"Driver={{ODBC Driver 18 for SQL Server}};"
    f"Server={server};"
    f"Database={database};"
    f"Trusted_Connection=yes;"
    f"TrustServerCertificate=yes"
)

# SQL auth (optional)
connection_url = (
    f"mssql+pyodbc://{user}:{encoded_password}"
    f"@{server}/{database}"
    f"?driver=ODBC+Driver+18+for+SQL+Server&TrustServerCertificate=yes"
)
```

### Frontend (`frontend/src/components/ConnectionModal.tsx`)
- Default auth_type: `windows`
- Username/password disabled when Windows auth selected
- Validation only requires credentials for SQL auth

## Backward Compatibility
✅ Snowflake functionality unaffected
✅ All other database types still working
✅ LIMIT to TOP conversion still working for SQL Server

## Next Steps
- User can now connect to AdventureWorks2022
- Schema scan will generate questions based on database schema
- Charts will display with actual data from the database

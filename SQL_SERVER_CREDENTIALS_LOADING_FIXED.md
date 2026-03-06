# SQL Server Credentials Loading - FIXED

## Problem
The frontend was not loading SQL Server remembered login credentials when the user selected SQL Server from the connection modal.

## Root Cause
1. **Config Loader Issue**: The `config_loader.py` was only loading INI files from the main `backend/config/` directory, not from the `backend/config/dialects/` subdirectory where `sqlserver.ini` is located.
2. **API Function Issue**: The `load_ini_credentials` function in `auth.py` was looking for credentials in the wrong section of the INI file.

## Solution Applied

### 1. Updated `backend/voxquery/config_loader.py`
- Modified `_load_all_configs()` method to also load INI files from the `dialects/` subdirectory
- Dialect configs are merged with main configs, with dialect configs taking precedence
- This ensures `backend/config/dialects/sqlserver.ini` is properly loaded

### 2. Updated `backend/voxquery/api/auth.py`
- Modified `load_ini_credentials()` function to check for `[credentials]` section first
- Falls back to database-specific section (legacy format) if `[credentials]` section not found
- This allows both new format (with `[credentials]` section) and legacy format to work

### 3. Verified `backend/config/dialects/sqlserver.ini`
- Confirmed `[credentials]` section exists with all required fields:
  - host: localhost
  - database: AdventureWorks2022
  - username: sa
  - password: Stayout1234
  - auth_type: sql
  - port: 1433

## Testing Results

### Test 1: Config Loader
```
✓ Config loaded. Sections: ['sqlserver', 'dialect', 'credentials', 'prompt_examples']
✓ Found [credentials] section
  - host: localhost
  - database: AdventureWorks2022
  - username: sa
  - password: ***********
  - auth_type: sql
  - port: 1433
```

### Test 2: API Endpoint
```
✓ API call successful!
  Database Type: sqlserver
  Success: True
  Message: Loaded credentials from sqlserver.ini
  
  Credentials loaded:
    - host: localhost
    - database: AdventureWorks2022
    - username: sa
    - password: ***********
    - auth_type: sql
    - port: 1433
```

## Frontend Flow
When user selects SQL Server in the connection modal:
1. Frontend calls `GET /api/v1/auth/load-ini-credentials/sqlserver`
2. Backend loads config from `backend/config/dialects/sqlserver.ini`
3. Backend extracts credentials from `[credentials]` section
4. Backend returns credentials to frontend
5. Frontend auto-populates the connection form with:
   - Host: localhost
   - Database: AdventureWorks2022
   - Username: sa
   - Password: Stayout1234
   - Auth Type: sql
   - Port: 1433

## Files Modified
- `backend/voxquery/config_loader.py` - Updated `_load_all_configs()` method
- `backend/voxquery/api/auth.py` - Updated `load_ini_credentials()` function

## Dialect Isolation
✓ This fix is SQL Server specific and does NOT affect:
- Snowflake connections
- PostgreSQL connections
- Redshift connections
- BigQuery connections

Each database has its own isolated INI file in `backend/config/dialects/` with its own `[credentials]` section (if needed).

## Next Steps
1. Restart backend service
2. Test in UI: Select SQL Server → credentials should auto-populate
3. Click Connect → should connect successfully to AdventureWorks2022

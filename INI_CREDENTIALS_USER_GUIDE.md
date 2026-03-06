# INI Credentials Loading - User Guide

## What's New?
VoxQuery now automatically loads database credentials from INI files when you select a database. This makes connecting faster and easier.

## How to Use

### Step 1: Open Database Connection
1. Click the database dropdown in the top bar
2. Select a database (Snowflake, SQL Server, Postgres, Redshift, or BigQuery)
3. Click "🔗 Connect" button in Settings

### Step 2: Credentials Auto-Load
When you select a database in the connection modal:
- If you've previously connected and checked "Remember me", your saved credentials appear
- If not, VoxQuery automatically loads credentials from the INI file
- You'll see a message: "✅ Loaded credentials from [database].ini"

### Step 3: Connect
1. Review the auto-loaded credentials
2. Edit any field if needed
3. Check "Remember me for this database" if you want to save them
4. Click "🔗 Test Connection" to verify
5. Click "✅ Connect" to establish connection

## Credential Priority

VoxQuery loads credentials in this order:

1. **Remembered Credentials** (localStorage)
   - If you previously connected and checked "Remember me"
   - These take priority over INI files
   - Stored locally in your browser

2. **INI File Credentials** (fallback)
   - Loaded from `backend/config/[database].ini`
   - Used if no remembered credentials exist
   - Provides team defaults

3. **Manual Entry**
   - You can always edit any field manually
   - Useful if you need different credentials than the defaults

## INI File Locations

Credentials are stored in these files:
- `backend/config/snowflake.ini` - Snowflake credentials
- `backend/config/sqlserver.ini` - SQL Server credentials
- `backend/config/postgres.ini` - PostgreSQL credentials
- `backend/config/redshift.ini` - Redshift credentials
- `backend/config/bigquery.ini` - BigQuery credentials

## Example: Connecting to Snowflake

1. Open VoxQuery
2. Click database dropdown → select "❄️ Snowflake"
3. Credentials auto-load from `snowflake.ini`:
   - Host: `we08391.af-south-1.aws.snowflakecomputing.com`
   - Username: `VOXQUERY`
   - Password: `VoxQuery@2024`
   - Database: `VOXQUERY_LOAD_SAMPLE_DATA_FROM_AWS_S3_WITH_SQL`
   - Warehouse: `COMPUTE_WH`
   - Role: `ACCOUNTADMIN`
4. Click "Test Connection" to verify
5. Click "Connect" to establish connection

## Example: Connecting to SQL Server

1. Open VoxQuery
2. Click database dropdown → select "🟦 SQL Server"
3. Credentials auto-load from `sqlserver.ini`:
   - Host: `localhost`
   - Database: `AdventureWorks2022`
   - Username: `sa`
   - Password: `YourPassword123`
   - Auth Type: `windows` or `sql`
4. Click "Test Connection" to verify
5. Click "Connect" to establish connection

## Tips

- **First Time?** Credentials auto-load from INI files, so you don't need to type them
- **Switching Databases?** Just select a different database from the dropdown - credentials auto-load
- **Want to Save?** Check "Remember me for this database" to save credentials locally
- **Need Different Credentials?** Edit any field manually before connecting
- **Team Setup?** Ask your admin to update the INI files with your team's credentials

## Troubleshooting

### "❌ Loaded credentials from [database].ini" doesn't appear
- The INI file may not exist or may be missing for that database
- Manually enter your credentials instead
- Contact your admin to set up the INI file

### Credentials don't auto-load
- Check if you have remembered credentials from a previous session
- If not, the INI file may be missing or misconfigured
- Manually enter your credentials

### Wrong credentials loaded
- You may have remembered credentials from a previous session
- Clear your browser's localStorage or uncheck "Remember me" for that database
- Or manually edit the fields before connecting

## Security Notes

- Credentials are stored in INI files on the server (not in the app)
- Remembered credentials are stored in your browser's localStorage
- Passwords are never sent to the frontend until you click "Connect"
- Always use HTTPS in production
- Keep INI files secure and don't commit them to version control


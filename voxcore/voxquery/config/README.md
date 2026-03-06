# Database Configuration Files

This directory contains INI configuration files for each supported database platform. Each file contains connection credentials and settings specific to that database type.

## Files

- **snowflake.ini** - Snowflake data warehouse configuration
- **sqlserver.ini** - Microsoft SQL Server configuration
- **postgres.ini** - PostgreSQL database configuration
- **redshift.ini** - Amazon Redshift configuration
- **bigquery.ini** - Google BigQuery configuration

## Quick Start

1. Edit the appropriate INI file for your database
2. Fill in your credentials (host, username, password, database, schema)
3. Save the file
4. Restart the backend
5. Use VoxQuery to connect

## Detailed Configuration

### Snowflake

```ini
[snowflake]
host = we08391.af-south-1.aws.snowflakecomputing.com
username = VOXQUERY
password = YourPassword
database = VOXQUERY_LOAD_SAMPLE_DATA_FROM_AWS_S3_WITH_SQL
schema = PUBLIC
warehouse = COMPUTE_WH
role = ACCOUNTADMIN
port = 443
```

**Required Fields**:
- `host` - Snowflake account identifier (full domain or account ID)
- `username` - Snowflake user
- `password` - Snowflake password
- `database` - Database name
- `schema` - Schema name (usually PUBLIC)

**Optional Fields**:
- `warehouse` - Compute warehouse (default: COMPUTE_WH)
- `role` - User role (default: ACCOUNTADMIN)
- `port` - Port number (default: 443)

### SQL Server

```ini
[sqlserver]
host = localhost
port = 1433
database = AdventureWorks2022
username = sa
password = YourPassword
auth_type = windows
driver = ODBC Driver 17 for SQL Server
```

**Required Fields**:
- `host` - SQL Server hostname or IP
- `port` - Port number (default: 1433)
- `database` - Database name
- `username` - SQL Server user (leave empty for Windows auth)
- `password` - SQL Server password (leave empty for Windows auth)

**Optional Fields**:
- `auth_type` - 'windows' or 'sql' (default: windows)
- `driver` - ODBC driver version
- `encrypt` - Enable encryption (true/false)

### PostgreSQL

```ini
[postgres]
host = localhost
port = 5432
database = postgres
username = postgres
password = YourPassword
schema = public
```

**Required Fields**:
- `host` - PostgreSQL hostname or IP
- `port` - Port number (default: 5432)
- `database` - Database name
- `username` - PostgreSQL user
- `password` - PostgreSQL password
- `schema` - Schema name (default: public)

**Optional Fields**:
- `ssl_mode` - SSL mode (prefer, require, disable)
- `connect_timeout` - Connection timeout in seconds

### Redshift

```ini
[redshift]
host = my-cluster.123456.us-east-1.redshift.amazonaws.com
port = 5439
database = dev
username = awsuser
password = YourPassword
schema = public
```

**Required Fields**:
- `host` - Redshift cluster endpoint
- `port` - Port number (default: 5439)
- `database` - Database name
- `username` - Redshift user
- `password` - Redshift password
- `schema` - Schema name (default: public)

**Optional Fields**:
- `use_iam_auth` - Use IAM authentication (true/false)
- `ssl_mode` - SSL mode (require, prefer, disable)

### BigQuery

```ini
[bigquery]
project_id = my-project-id
dataset = my_dataset
credentials_path = /path/to/service-account-key.json
location = US
```

**Required Fields**:
- `project_id` - Google Cloud project ID
- `dataset` - BigQuery dataset name
- `credentials_path` - Path to service account JSON key file

**Optional Fields**:
- `location` - BigQuery location (default: US)
- `use_legacy_sql` - Use legacy SQL (true/false, default: false)
- `maximum_bytes_billed` - Maximum bytes to bill per query

## Common Settings (All Platforms)

All INI files include these common settings:

```ini
# Connection Settings
timeout_seconds = 300
max_result_rows = 100000
connect_timeout = 10
statement_timeout = 300000

# Connection Pool Settings
pool_size = 5
max_overflow = 10
pool_recycle = 3600
pool_pre_ping = true

# Retry Settings
retry_count = 3
retry_delay = 1

# Logging
log_level = INFO
log_queries = false
```

## Usage Options

### Option 1: Use INI Files (Recommended)

Edit the appropriate INI file with your credentials:

```bash
# Edit Snowflake config
nano backend/config/snowflake.ini

# Edit SQL Server config
nano backend/config/sqlserver.ini
```

Then restart the backend:

```bash
python backend/main.py
```

### Option 2: Use Environment Variables

Set environment variables instead of editing INI files:

```bash
export SNOWFLAKE_HOST=your-account.region.aws.snowflakecomputing.com
export SNOWFLAKE_USERNAME=your_username
export SNOWFLAKE_PASSWORD=your_password
export SNOWFLAKE_DATABASE=your_database
```

### Option 3: Use Frontend Connection Dialog

Use the VoxQuery UI to enter credentials manually (no file editing needed).

## Security Best Practices

⚠️ **Important**: These INI files contain sensitive credentials.

### Do's ✅
- ✅ Keep INI files in `.gitignore` (already configured)
- ✅ Use environment variables for production
- ✅ Use dedicated service accounts with minimal permissions
- ✅ Restrict file permissions (chmod 600)
- ✅ Rotate passwords regularly
- ✅ Use SSL/TLS for all connections
- ✅ Enable encryption where available

### Don'ts ❌
- ❌ Never commit INI files to version control
- ❌ Never share credentials in emails or chat
- ❌ Never use admin accounts for regular queries
- ❌ Never disable SSL/TLS
- ❌ Never hardcode credentials in code
- ❌ Never log passwords or sensitive data

## Loading Credentials in Code

```python
from voxquery.config_loader import load_database_config, get_connection_string

# Load full config
config = load_database_config('snowflake')
print(config['snowflake']['host'])

# Get connection string
conn_str = get_connection_string('snowflake')

# Get specific setting
host = config['snowflake'].get('host')
username = config['snowflake'].get('username')
```

## Troubleshooting

### "Config file not found"
- Ensure INI files are in the `backend/config/` directory
- Check file permissions: `ls -la backend/config/`
- Verify file is readable: `cat backend/config/snowflake.ini`

### "Connection failed"
- Verify credentials in INI file
- Check database is accessible from your network
- Ensure firewall allows connections
- Test connection manually:
  ```bash
  # For Snowflake
  snowsql -a we08391 -u VOXQUERY -d VOXQUERY_LOAD_SAMPLE_DATA_FROM_AWS_S3_WITH_SQL
  
  # For PostgreSQL
  psql -h localhost -U postgres -d postgres
  
  # For SQL Server
  sqlcmd -S localhost -U sa -P YourPassword
  ```

### "0 tables found"
- Verify database/schema name is correct
- Check user has permissions to view tables
- Try connecting with a different user account
- Check schema is not empty

### "Permission denied"
- Verify user has SELECT permissions on tables
- Check user has USAGE permissions on schema
- For Snowflake, verify role has necessary grants
- For SQL Server, verify user is in correct database role

### "Timeout"
- Increase `timeout_seconds` in INI file
- Check network connectivity
- Verify database is not overloaded
- Check firewall rules

## Connection String Format

### Snowflake
```
snowflake://user:password@account/database/schema
```

### SQL Server
```
mssql+pyodbc://user:password@host:port/database?driver=ODBC+Driver+17+for+SQL+Server
```

### PostgreSQL
```
postgresql://user:password@host:port/database
```

### Redshift
```
redshift+psycopg2://user:password@host:port/database
```

### BigQuery
```
bigquery://project_id/dataset_id
```

## Testing Connections

### Test Snowflake
```python
from snowflake.connector import connect
conn = connect(
    account='we08391',
    user='VOXQUERY',
    password='YourPassword',
    database='VOXQUERY_LOAD_SAMPLE_DATA_FROM_AWS_S3_WITH_SQL',
    schema='PUBLIC'
)
print(conn.cursor().execute("SELECT 1").fetchall())
```

### Test PostgreSQL
```python
import psycopg2
conn = psycopg2.connect(
    host='localhost',
    user='postgres',
    password='YourPassword',
    database='postgres'
)
print(conn.cursor().execute("SELECT 1").fetchall())
```

### Test SQL Server
```python
import pyodbc
conn = pyodbc.connect(
    'Driver={ODBC Driver 17 for SQL Server};'
    'Server=localhost;'
    'Database=AdventureWorks2022;'
    'UID=sa;'
    'PWD=YourPassword;'
)
print(conn.cursor().execute("SELECT 1").fetchall())
```

## Production Deployment

For production deployment:

1. **Use environment variables** instead of INI files
2. **Use service accounts** with minimal permissions
3. **Enable SSL/TLS** for all connections
4. **Rotate credentials** regularly
5. **Monitor connections** for suspicious activity
6. **Use connection pooling** to optimize performance
7. **Set appropriate timeouts** for your workload
8. **Enable query logging** for audit trails
9. **Backup credentials** securely
10. **Test failover** procedures

## Support

For issues or questions:
- Check the troubleshooting section above
- Review database-specific documentation
- Contact your database administrator
- Check VoxQuery logs: `tail -f backend/logs/voxquery.log`

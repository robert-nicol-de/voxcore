# VoxQuery Database Configuration Guide

## Overview

VoxQuery supports 5 major database platforms, each with its own INI configuration file for login credentials and connection settings.

---

## Database Platforms Supported

### 1. Snowflake ❄️
**File**: `backend/config/snowflake.ini`

```ini
[snowflake]
host = we08391.af-south-1.aws.snowflakecomputing.com
username = VOXQUERY
password = VoxQuery@2024
database = VOXQUERY_LOAD_SAMPLE_DATA_FROM_AWS_S3_WITH_SQL
schema = PUBLIC
warehouse = COMPUTE_WH
role = ACCOUNTADMIN
port = 443
```

**Key Features**:
- Cloud-native data warehouse
- Automatic scaling
- Separation of compute and storage
- Multi-cloud support

**Connection Requirements**:
- Account identifier (e.g., we08391)
- Username and password
- Database and schema names
- Warehouse name
- Role (optional)

**Best For**: Large-scale analytics, cloud-first organizations

---

### 2. SQL Server 🔷
**File**: `backend/config/sqlserver.ini`

```ini
[sqlserver]
host = localhost
port = 1433
database = AdventureWorks2022
username = sa
password = YourPassword123
auth_type = windows
driver = ODBC Driver 17 for SQL Server
```

**Key Features**:
- Enterprise database
- Windows authentication support
- SQL authentication support
- SSRS integration

**Connection Requirements**:
- Host/IP address
- Port (default: 1433)
- Database name
- Username and password (or Windows auth)
- ODBC driver

**Best For**: Enterprise environments, legacy systems, SSRS integration

---

### 3. PostgreSQL 🐘
**File**: `backend/config/postgres.ini`

```ini
[postgres]
host = localhost
port = 5432
database = postgres
username = postgres
password = postgres
schema = public
```

**Key Features**:
- Open-source relational database
- ACID compliance
- Advanced features (JSON, arrays, etc.)
- Excellent performance

**Connection Requirements**:
- Host/IP address
- Port (default: 5432)
- Database name
- Username and password
- Schema name

**Best For**: Open-source projects, cost-conscious organizations, advanced SQL features

---

### 4. Amazon Redshift 🔴
**File**: `backend/config/redshift.ini`

```ini
[redshift]
host = my-cluster.123456.us-east-1.redshift.amazonaws.com
port = 5439
database = dev
username = awsuser
password = YourPassword123
schema = public
```

**Key Features**:
- Cloud data warehouse (AWS)
- Columnar storage
- Massive parallel processing
- Cost-effective for analytics

**Connection Requirements**:
- Cluster endpoint
- Port (default: 5439)
- Database name
- Username and password
- Schema name

**Best For**: AWS-native organizations, large-scale analytics, cost optimization

---

### 5. Google BigQuery 🔵
**File**: `backend/config/bigquery.ini`

```ini
[bigquery]
project_id = my-project-id
dataset = my_dataset
credentials_path = /path/to/service-account-key.json
location = US
```

**Key Features**:
- Serverless data warehouse (Google Cloud)
- No infrastructure management
- SQL-like query language
- Automatic scaling

**Connection Requirements**:
- Google Cloud project ID
- BigQuery dataset name
- Service account JSON key file
- Location (optional)

**Best For**: Google Cloud users, serverless architecture, minimal ops

---

## Configuration File Structure

Each INI file contains the following sections:

### Connection Settings
```ini
host = database_host
port = database_port
database = database_name
username = user_name
password = user_password
schema = schema_name
```

### Connection Pool Settings
```ini
pool_size = 5
max_overflow = 10
pool_recycle = 3600
pool_pre_ping = true
```

### SSL/TLS Settings
```ini
ssl_mode = prefer
ssl_cert_path = /path/to/cert
ssl_key_path = /path/to/key
ssl_root_cert_path = /path/to/root_cert
```

### Retry Settings
```ini
retry_count = 3
retry_delay = 1
```

### Logging Settings
```ini
log_level = INFO
log_queries = false
```

---

## Quick Setup Guide

### Step 1: Choose Your Database
Decide which database platform you want to connect to.

### Step 2: Edit the INI File
```bash
# For Snowflake
nano backend/config/snowflake.ini

# For SQL Server
nano backend/config/sqlserver.ini

# For PostgreSQL
nano backend/config/postgres.ini

# For Redshift
nano backend/config/redshift.ini

# For BigQuery
nano backend/config/bigquery.ini
```

### Step 3: Fill in Credentials
Update the following fields with your actual credentials:
- `host` - Database hostname or IP
- `username` - Database user
- `password` - Database password
- `database` - Database name
- `schema` - Schema name (if applicable)

### Step 4: Restart Backend
```bash
# Stop the backend
Ctrl+C

# Start the backend
python backend/main.py
```

### Step 5: Connect in VoxQuery
1. Open VoxQuery in browser
2. Click "Settings" in sidebar
3. Select database type
4. Click "Connect"
5. VoxQuery loads schema automatically

---

## Security Best Practices

### ✅ Do's
- ✅ Keep INI files in `.gitignore`
- ✅ Use environment variables for production
- ✅ Use dedicated service accounts
- ✅ Restrict file permissions (chmod 600)
- ✅ Rotate passwords regularly
- ✅ Use SSL/TLS for all connections
- ✅ Enable encryption where available
- ✅ Monitor connection logs
- ✅ Backup credentials securely
- ✅ Use minimal permissions

### ❌ Don'ts
- ❌ Never commit INI files to git
- ❌ Never share credentials in emails
- ❌ Never use admin accounts
- ❌ Never disable SSL/TLS
- ❌ Never hardcode credentials
- ❌ Never log passwords
- ❌ Never use weak passwords
- ❌ Never share credentials in chat
- ❌ Never store credentials in code
- ❌ Never use default passwords

---

## Connection Strings

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

---

## Testing Connections

### Test Snowflake
```bash
snowsql -a we08391 -u VOXQUERY -d VOXQUERY_LOAD_SAMPLE_DATA_FROM_AWS_S3_WITH_SQL
```

### Test PostgreSQL
```bash
psql -h localhost -U postgres -d postgres
```

### Test SQL Server
```bash
sqlcmd -S localhost -U sa -P YourPassword
```

### Test Redshift
```bash
psql -h my-cluster.123456.us-east-1.redshift.amazonaws.com -U awsuser -d dev
```

### Test BigQuery
```bash
bq ls --project_id=my-project-id
```

---

## Troubleshooting

### Connection Failed
**Problem**: Cannot connect to database
**Solution**:
1. Verify credentials in INI file
2. Check database is accessible from your network
3. Ensure firewall allows connections
4. Test connection manually using command-line tools

### 0 Tables Found
**Problem**: Connected but no tables visible
**Solution**:
1. Verify database/schema name is correct
2. Check user has SELECT permissions
3. Try connecting with different user account
4. Check schema is not empty

### Permission Denied
**Problem**: User doesn't have required permissions
**Solution**:
1. Verify user has SELECT permissions on tables
2. Check user has USAGE permissions on schema
3. For Snowflake, verify role has necessary grants
4. For SQL Server, verify user is in correct database role

### Timeout
**Problem**: Connection times out
**Solution**:
1. Increase `timeout_seconds` in INI file
2. Check network connectivity
3. Verify database is not overloaded
4. Check firewall rules

### SSL/TLS Error
**Problem**: SSL certificate verification failed
**Solution**:
1. Set `ssl_mode = disable` (not recommended)
2. Provide correct certificate path
3. Update system certificates
4. Contact database administrator

---

## Production Deployment

### Environment Variables
Instead of INI files, use environment variables:

```bash
export SNOWFLAKE_HOST=your-account.region.aws.snowflakecomputing.com
export SNOWFLAKE_USERNAME=your_username
export SNOWFLAKE_PASSWORD=your_password
export SNOWFLAKE_DATABASE=your_database
export SNOWFLAKE_SCHEMA=your_schema
```

### Docker Secrets
For Docker deployments, use secrets:

```bash
docker run -e SNOWFLAKE_PASSWORD_FILE=/run/secrets/snowflake_password voxquery
```

### Kubernetes Secrets
For Kubernetes deployments, use secrets:

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: snowflake-credentials
type: Opaque
stringData:
  host: your-account.region.aws.snowflakecomputing.com
  username: your_username
  password: your_password
```

### AWS Secrets Manager
For AWS deployments, use Secrets Manager:

```python
import boto3
client = boto3.client('secretsmanager')
secret = client.get_secret_value(SecretId='snowflake-credentials')
```

---

## Performance Tuning

### Connection Pool Settings
```ini
pool_size = 5           # Number of connections to keep
max_overflow = 10       # Additional connections allowed
pool_recycle = 3600     # Recycle connections after 1 hour
pool_pre_ping = true    # Test connections before using
```

### Query Settings
```ini
timeout_seconds = 300           # Query timeout
max_result_rows = 100000        # Maximum rows to return
statement_timeout = 300000      # Statement timeout (ms)
```

### Optimization Tips
1. Increase `pool_size` for high concurrency
2. Set appropriate `timeout_seconds` for your workload
3. Use `pool_pre_ping = true` to avoid stale connections
4. Monitor connection pool usage
5. Adjust `max_result_rows` based on memory

---

## Monitoring & Logging

### Enable Query Logging
```ini
log_level = DEBUG
log_queries = true
```

### Monitor Connections
```bash
# Check active connections
SELECT * FROM pg_stat_activity;  # PostgreSQL
SELECT * FROM sys.dm_exec_sessions;  # SQL Server
```

### Check Logs
```bash
tail -f backend/logs/voxquery.log
```

---

## Backup & Recovery

### Backup Credentials
```bash
# Backup INI files
cp backend/config/*.ini backup/config/

# Backup with timestamp
cp backend/config/snowflake.ini backup/config/snowflake.ini.$(date +%Y%m%d_%H%M%S)
```

### Restore Credentials
```bash
# Restore from backup
cp backup/config/snowflake.ini backend/config/snowflake.ini

# Restart backend
python backend/main.py
```

---

## Support & Resources

### Documentation
- Snowflake: https://docs.snowflake.com/
- SQL Server: https://docs.microsoft.com/sql/
- PostgreSQL: https://www.postgresql.org/docs/
- Redshift: https://docs.aws.amazon.com/redshift/
- BigQuery: https://cloud.google.com/bigquery/docs

### VoxQuery Resources
- GitHub: https://github.com/voxquery/voxquery
- Issues: https://github.com/voxquery/voxquery/issues
- Discussions: https://github.com/voxquery/voxquery/discussions

---

**Status**: ✅ All Database Platforms Configured and Ready!

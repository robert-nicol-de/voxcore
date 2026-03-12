# VoxCore Multi-Database Connection Guide

**Date:** March 12, 2026  
**Version:** 2.0 - Multi-Database Support  
**Status:** ✅ Production Ready

---

## Overview

VoxCore now supports **multiple database platforms** with a unified governance interface:

- ✅ **SQL Server** (via ODBC Driver 18)
- ✅ **PostgreSQL** (via psycopg2)
- ✅ **MySQL** (via mysqlclient)
- ✅ **SQLite** (native Python support)

This makes VoxCore an **AI Data Governance Platform** for any database your organization uses.

---

## Connection String Formats

### 1. SQL Server (ODBC)

**Format:**
```
mssql+pyodbc://username:password@host:port/database?driver=ODBC+Driver+18+for+SQL+Server
```

**Example:**
```
mssql+pyodbc://sa:YourPassword@102.206.211.24:1433/AdventureWorks2022?driver=ODBC+Driver+18+for+SQL+Server
```

**Components:**
- `sa` - SQL Server authentication username
- `YourPassword` - Your SQL Server password
- `102.206.211.24` - SQL Server host/IP
- `1433` - SQL Server port (default)
- `AdventureWorks2022` - Database name
- `ODBC Driver 18 for SQL Server` - Driver name (must match exactly)

**local development** (using Docker host):
```
mssql+pyodbc://sa:password@host.docker.internal:1433/AdventureWorks2022?driver=ODBC+Driver+18+for+SQL+Server
```

**Encrypted password** (with VoxCore encryption):
```
mssql+pyodbc://sa:ENC:gAAAAABlxyz...@102.206.211.24:1433/AdventureWorks2022?driver=ODBC+Driver+18+for+SQL+Server
```

---

### 2. PostgreSQL

**Format:**
```
postgresql://username:password@host:port/database
```

**Example:**
```
postgresql://postgres:your_password@db.example.com:5432/production_db
```

**Components:**
- `postgres` - PostgreSQL username (default)
- `your_password` - Your password
- `db.example.com` - PostgreSQL host
- `5432` - PostgreSQL port (default)
- `production_db` - Database name

**Local development:**
```
postgresql://postgres:password@localhost:5432/voxcore_dev
```

---

### 3. MySQL

**Format:**
```
mysql://username:password@host:port/database
```

**Example:**
```
mysql://root:your_password@mysql.example.com:3306/analytics_db
```

**Components:**
- `root` - MySQL username (default)
- `your_password` - Your password
- `mysql.example.com` - MySQL host
- `3306` - MySQL port (default)
- `analytics_db` - Database name

**Local development:**
```
mysql://root:password@localhost:3306/voxcore_dev
```

---

### 4. SQLite

**Format:**
```
sqlite:///path/to/database.db
```

**Example:**
```
sqlite:///./data/voxcore.db
```

**Components:**
- `./data/voxcore.db` - Path to SQLite database file (relative or absolute)

**Use Cases:**
- Development/testing
- Single-user analysis
- Local data warehouse

---

## Environment Configuration

### Using `.env` File

Create a `.env` file in your project root:

```env
# SQL Server
DATABASE_URL=mssql+pyodbc://sa:YourPassword@102.206.211.24:1433/AdventureWorks2022?driver=ODBC+Driver+18+for+SQL+Server

# Or PostgreSQL
# DATABASE_URL=postgresql://postgres:password@db.example.com:5432/db_name

# Or MySQL
# DATABASE_URL=mysql://root:password@mysql.example.com:3306/db_name

# Encryption
VOXCORE_ENCRYPTION_KEY=your_fernet_key_here

# Groq API
GROQ_API_KEY=your_groq_api_key

# Redis
REDIS_URL=redis://localhost:6379/0
```

### Using Docker Compose

#### Option 1: Environment File (.env)

```yaml
# docker-compose.prod.yml
services:
  backend:
    environment:
      - DATABASE_URL=${DATABASE_URL}
      - VOXCORE_ENCRYPTION_KEY=${VOXCORE_ENCRYPTION_KEY}
      - GROQ_API_KEY=${GROQ_API_KEY}
```

Then run:
```bash
docker compose --env-file .env up -d
```

#### Option 2: Direct Environment Variables

```yaml
services:
  backend:
    environment:
      - DATABASE_URL=mssql+pyodbc://sa:password@sqlserver:1433/AdventureWorks2022?driver=ODBC+Driver+18+for+SQL+Server
      - REDIS_URL=redis://redis:6379/0
      - VOXCORE_ENCRYPTION_KEY=z0ODAvfvO_K9mJ4...
      - GROQ_API_KEY=gsk_123...
```

#### Option 3: Secrets Manager (Production)

**AWS Secrets Manager:**
```bash
aws secretsmanager create-secret \
  --name voxcore/production/database-url \
  --secret-string "mssql+pyodbc://sa:password@..."

aws secretsmanager create-secret \
  --name voxcore/production/encryption-key \
  --secret-string "z0ODAvfvO_K9mJ4..."
```

Then reference in docker-compose:
```yaml
services:
  backend:
    environment:
      - DATABASE_URL=arn:aws:secretsmanager:region:account:secret:voxcore/production/database-url
```

---

## Testing Your Connection

### 1. Quick Test via CLI

```bash
# Test SQL Server connection
python3 -c "
import pyodbc
conn = pyodbc.connect(
    'Driver={ODBC Driver 18 for SQL Server};'
    'Server=102.206.211.24;'
    'Database=AdventureWorks2022;'
    'UID=sa;'
    'PWD=password'
)
print('✅ SQL Server Connection OK')
conn.close()
"

# Test PostgreSQL connection
python3 -c "
import psycopg2
conn = psycopg2.connect(
    host='db.example.com',
    database='production_db',
    user='postgres',
    password='password'
)
print('✅ PostgreSQL Connection OK')
conn.close()
"

# Test MySQL connection
python3 -c "
import MySQLdb
conn = MySQLdb.connect(
    host='mysql.example.com',
    user='root',
    passwd='password',
    db='analytics_db'
)
print('✅ MySQL Connection OK')
conn.close()
"
```

### 2. Test via Docker Container

```bash
# Once running, test backend health
curl http://localhost:10000/health

# Expected output:
# {"status":"ok","database":"connected"}
```

### 3. Test via VoxCore UI

1. Navigate to **Databases** page
2. Click **Add Database**
3. Enter connection details
4. Click **Test & Connect**
5. If it works, database appears in connected list ✅

---

## Multi-Database Architecture

### Example: Managing 3 Different Databases

```txt
VoxCore AI Governance
├── SQL Server (AdventureWorks) → Financials
│   ├── dbo.Transactions
│   ├── dbo.Accounts
│   └── dbo.Ledger
├── PostgreSQL (Analytics) → Analytics & Metrics
│   ├── public.events
│   ├── public.user_behavior
│   └── public.dashboards
└── MySQL (Operations) → HR & Operations
    ├── hr.employees
    ├── hr.payroll
    └── ops.inventory
```

Each database has:
- ✅ Unified security rules
- ✅ AI query analysis
- ✅ Risk assessment
- ✅ Audit logging
- ✅ Policy enforcement

---

## Security: Encrypted Credentials

Instead of plaintext connection strings:

```
# ❌ DON'T: Plaintext in version control
DATABASE_URL=mssql+pyodbc://sa:MyPassword123@server:1433/db
```

Use encrypted credentials:

```
# ✅ DO: Encrypted in environment
DATABASE_URL=mssql+pyodbc://sa:ENC:gAAAAABlxyz...@server:1433/db
VOXCORE_ENCRYPTION_KEY=z0ODAvfvO_K9mJ4...
```

VoxCore automatically decrypts at runtime using `VOXCORE_ENCRYPTION_KEY`.

**See:** `CREDENTIAL_ENCRYPTION_GUIDE.md` for full encryption setup.

---

## Docker Setup

### Using docker-compose.simple.yml (Recommended)

```bash
# Set environment variables
export DATABASE_URL="mssql+pyodbc://sa:password@102.206.211.24:1433/AdventureWorks2022?driver=ODBC+Driver+18+for+SQL+Server"
export VOXCORE_ENCRYPTION_KEY="your_key_here"
export GROQ_API_KEY="your_groq_key"

# Start VoxCore
docker compose -f docker-compose.simple.yml up -d

# Check status
docker compose -f docker-compose.simple.yml ps

# View logs
docker compose -f docker-compose.simple.yml logs backend
```

### Using docker-compose.prod.yml (Full Stack)

For production with frontend, nginx, etc:

```bash
docker compose -f docker-compose.prod.yml up -d
```

---

## Connection String Builder

Use this template to build your connection string:

### SQL Server Template
```
mssql+pyodbc://{USERNAME}:{PASSWORD}@{HOST}:{PORT}/{DATABASE}?driver=ODBC+Driver+18+for+SQL+Server
```

Replace:
- `{USERNAME}` - Your SQL Server login
- `{PASSWORD}` - Your password
- `{HOST}` - Server IP or hostname
- `{PORT}` - Port (default: 1433)
- `{DATABASE}` - Database name

### PostgreSQL Template
```
postgresql://{USERNAME}:{PASSWORD}@{HOST}:{PORT}/{DATABASE}
```

### MySQL Template
```
mysql://{USERNAME}:{PASSWORD}@{HOST}:{PORT}/{DATABASE}
```

---

## Troubleshooting

### Error: "Can't open lib 'ODBC Driver 18 for SQL Server'"

**Cause:** Backend container missing SQL Server ODBC driver.

**Solution:**
```bash
# Rebuild backend Dockerfile
docker compose -f docker-compose.prod.yml build backend --no-cache
docker compose -f docker-compose.prod.yml up -d backend
```

### Error: "postgresql: command not found"

**Cause:** PostgreSQL client not installed (shouldn't happen with our Dockerfile).

**Solution:**
```bash
# Rebuild with updated requirements.txt
docker compose build backend --no-cache
docker compose up -d
```

### Error: "Connection refused"

**Cause:** Database server not reachable.

**Solution:**
1. Verify host/IP is correct
2. Verify port is open
3. Test from command line: `curl telnet://host:port`
4. Check firewall rules
5. Verify credentials

### Error: "Connection timeout"

**Cause:** Network or firewall blocking connection.

**Solution:**
1. Check if host is accessible: `ping host`
2. Check open ports: `netstat -an | grep port`
3. Check VPC/security groups (if cloud)
4. Increase timeout in connection string

---

## Best Practices

### ✅ DO:

1. **Use environment variables** for all secrets
2. **Encrypt passwords** with VoxCore encryption
3. **Use connection pools** (built into SQLAlchemy)
4. **Test connections** before enabling policies
5. **Monitor query logs** in audit table
6. **Rotate credentials** quarterly
7. **Use managed databases** (AWS RDS, Azure SQL, Google Cloud SQL) in production

### ❌ DON'T:

1. ❌ Hardcode credentials in source code
2. ❌ Commit `.env` files to version control
3. ❌ Use `sa` account for non-admin queries
4. ❌ Store plaintext passwords
5. ❌ Log connection strings with credentials
6. ❌ Use localhost IPs in production
7. ❌ Share credentials across teams

---

## Supported Drivers

| Database | Driver | Status | Requirements |
|----------|--------|--------|--------------|
| SQL Server | ODBC Driver 18 | ✅ | `msodbcsql18` + `unixodbc` |
| PostgreSQL | psycopg2 | ✅ | `postgresql` + `libpq-dev` |
| MySQL | mysqlclient | ✅ | `mysql` + `default-libmysqlclient-dev` |
| SQLite | sqlite3 | ✅ | Built-in (no extra driver) |

All included in `backend/requirements.txt`.

---

## Next Steps

1. **Choose your database** (SQL Server / PostgreSQL / MySQL)
2. **Get connection string** using templates above
3. **Encrypt the password** (optional but recommended)
4. **Set `DATABASE_URL`** environment variable
5. **Start VoxCore** with docker compose
6. **Test connection** via Databases page UI

---

**Last Updated:** March 12, 2026  
**VoxCore Version:** 2.0 Multi-Database Support

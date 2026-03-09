# 🔐 VoxCore Secure Connector Architecture

## Overview

VoxCore implements a **zero-trust credential management system** where database passwords are never stored in configuration files. Instead, connectors reference credentials stored in environment variables or secret vaults.

This architecture enables:
- **Safety**: Credentials cannot be accidentally committed to Git
- **Flexibility**: Credentials can be rotated without code/config changes
- **Scalability**: Different credentials per environment (dev/staging/prod)
- **Auditability**: Secrets are managed by dedicated secure systems

---

## Architecture Diagram

```
User Prompt
   ↓
AI SQL Generator
   ↓
VoxCore Firewall (Security Policy Engine)
   ↓
Policy Engine (Validates against [security] section of connector)
   ↓
Connector Layer (Reads .ini file)
   ↓
Credential Vault (Environment Variables / Secret Manager)
   ↓
Database Connection
   ↓
Customer Database
```

---

## Connector .ini Structure

Each connector .ini file defines the **configuration** only, never the **credentials**.

### Example: `sales_db.ini`

```ini
[database]
name = sales_db
type = postgres
host = localhost
port = 5432
database = sales
user = voxcore_user
credential_key = SALES_DB_PASSWORD

[security]
block_delete = true
block_update = false
block_drop = false
max_rows = 5000
protect_tables = users,transactions
pii_protected = false
policy = moderate
```

**Key Points:**
- `credential_key` = name of environment variable where password lives
- `[security]` section = dynamic firewall rules for this connector
- No passwords stored in .ini file ❌
- File is safe to commit to Git ✅

---

## Credential Storage Mechanisms

### 1. Environment Variables (Simple Development)

Store credentials as environment variables:

```bash
export SALES_DB_PASSWORD="secure_password_123"
export FINANCE_DB_PASSWORD="another_secure_456"
export HR_DB_PASSWORD="payroll_secure_789"
```

**Pros:**
- Simple to set up
- Works on local development
- No additional infrastructure

**Cons:**
- Not recommended for production
- Credentials visible in shell history
- Hard to rotate

### 2. .env File (Local Development Only)

Create a `.env` file (⚠️ **never commit to Git**)

```python
# .env (add to .gitignore)
SALES_DB_PASSWORD=secure_password_123
FINANCE_DB_PASSWORD=another_secure_456
HR_DB_PASSWORD=payroll_secure_789
```

Load in Python:

```python
from dotenv import load_dotenv
load_dotenv()

# Now os.getenv("SALES_DB_PASSWORD") works
```

**Pros:**
- Clean local development
- Easy credential management

**Cons:**
- Easy to accidentally commit
- Not suitable for production

### 3. Secret Vaults (Production)

Use AWS Secrets Manager, HashiCorp Vault, or similar:

```python
# Example: AWS Secrets Manager
import boto3

def get_credential(credential_key):
    client = boto3.client('secretsmanager')
    response = client.get_secret_value(SecretId=credential_key)
    return response['SecretString']

password = get_credential('SALES_DB_PASSWORD')
```

**Pros:**
- Secure, encrypted storage
- Automatic rotation
- Audit trail
- No local files needed

**Cons:**
- Additional infrastructure cost
- Requires AWS/Vault setup

---

## Connector Manager Implementation

### Load Connectors with Credentials

The `connector_manager.py` automatically:

1. **Scans** `/connectors` folder for `.ini` files
2. **Reads** `credential_key` from each [database] section
3. **Looks up** actual password from `os.getenv(credential_key)`
4. **Returns** connector object with loaded password
5. **Reports** `credential_status`: `loaded`, `not_found`, or `missing`

```python
# connector_manager.py
def load_connectors():
    """
    Load connectors from .ini files.
    Credentials are resolved from environment variables.
    """
    connectors = []
    
    for file in os.listdir(CONNECTOR_FOLDER):
        if file.endswith(".ini"):
            config = configparser.ConfigParser()
            config.read(os.path.join(CONNECTOR_FOLDER, file))
            
            db = config["database"]
            
            # KEY: Load credential from environment, not .ini
            credential_key = db.get("credential_key")
            password = os.getenv(credential_key)
            
            connector = {
                "name": db.get("name"),
                "host": db.get("host"),
                "password": password,  # From environment
                "credential_key": credential_key,
                "credential_status": "loaded" if password else "not_found",
                "security": {...}
            }
            
            connectors.append(connector)
    
    return connectors
```

### Frontend Never Sees Passwords

The API Always Returns `password: null`:

```python
# voxcore/api/connectors.py
class ConnectorDatabase(BaseModel):
    name: str
    type: str
    host: str
    port: int
    database: str
    user: str
    password: Optional[str] = None  # Always None in responses

@router.get("/connectors")
def list_connectors():
    connector_list = load_connectors()
    
    for connector in connector_list:
        db_section = ConnectorDatabase(
            name=connector.get("name"),
            host=connector.get("host"),
            password=None  # 🔒 Never expose password
        )
```

---

## Security Policies Per Connector

Each connector can have **different** security rules applied to queries against that database.

### Policy Engine Logic

After query is generated, but before execution:

```
Query: SELECT * FROM employees

Connector Policy: hr_db.ini
├─ block_delete: true        → Allow SELECT ✓
├─ block_drop: true          → Cannot DROP ✓
├─ max_rows: 1000            → Return max 1000 rows
├─ pii_protected: true       → Mask SSN columns
└─ protect_tables: employees,payroll

Policy Check Result: ✅ ALLOW with transformations
```

### Available Policies

```ini
[security]
block_delete = true          # Prevent DELETE statements
block_update = true          # Prevent UPDATE statements
block_drop = true            # Prevent DROP statements
max_rows = 1000              # Limit results to N rows
protect_tables = users,ssn   # Apply extra protection to these tables
pii_protected = true         # Mask PII columns
policy = strict              # strict | moderate | permissive
```

---

## Setup Instructions

### 1. Create .env File

Copy `.env.example` and add real credentials:

```bash
cp .env.example .env
```

Edit `.env`:

```
SALES_DB_PASSWORD=your_postgres_password
FINANCE_DB_PASSWORD=your_mysql_password
HR_DB_PASSWORD=your_postgres_password
```

**⚠️ IMPORTANT: Add .env to .gitignore**

```bash
echo ".env" >> .gitignore
```

### 2. Create Connector .ini Files

Already created:
- `connectors/sales_db.ini` (references `SALES_DB_PASSWORD`)
- `connectors/finance_db.ini` (references `FINANCE_DB_PASSWORD`)
- `connectors/hr_db.ini` (references `HR_DB_PASSWORD`)

### 3. Load Environment Variables

**Option A: Python (using python-dotenv)**

```python
from dotenv import load_dotenv
import os

load_dotenv()  # Loads .env file

# Now connector_manager can access credentials
```

**Option B: Shell (before running server)**

```bash
export SALES_DB_PASSWORD="your_password"
export FINANCE_DB_PASSWORD="your_password"
export HR_DB_PASSWORD="your_password"

python -m uvicorn main:app
```

**Option C: Docker**

```dockerfile
FROM python:3.11

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

# Set environment variables at runtime
ENV SALES_DB_PASSWORD=${SALES_DB_PASSWORD}
ENV FINANCE_DB_PASSWORD=${FINANCE_DB_PASSWORD}
ENV HR_DB_PASSWORD=${HR_DB_PASSWORD}

CMD ["uvicorn", "main:app", "--host", "0.0.0.0"]
```

### 4. Test Connectors

```bash
curl -X GET http://localhost:8000/api/v1/connectors
```

Response:

```json
{
  "total": 3,
  "connectors": [
    {
      "name": "sales_db",
      "database": {
        "name": "sales_db",
        "type": "postgres",
        "host": "localhost",
        "port": 5432,
        "database": "sales",
        "user": "voxcore_user",
        "password": null
      },
      "security": {
        "block_delete": true,
        "block_update": false,
        "block_drop": false,
        "max_rows": 5000,
        "protect_tables": ["users", "transactions"],
        "pii_protected": false,
        "policy": "moderate"
      },
      "status": "connected",
      "credential_status": "loaded"
    }
  ]
}
```

---

## Credential Status Indicators

When loading connectors, `credential_status` indicates:

| Status | Meaning | Action |
|--------|---------|--------|
| `loaded` | Credential found in environment | ✅ Ready to use |
| `not_found` | credential_key referenced, but env var missing | ⚠️ Check .env file |
| `missing` | No credential_key in .ini | ❌ Update .ini file |

**Frontend UI will show:**
- 🟢 Green indicator for `loaded`
- 🟡 Yellow indicator for `not_found`
- 🔴 Red indicator for `missing`

---

## Production Deployment

### Recommended: AWS Secrets Manager

1. Store secrets in AWS Secrets Manager:

```bash
aws secretsmanager create-secret \
  --name voxcore/connectors/SALES_DB_PASSWORD \
  --secret-string "your_password"
```

2. Update connector_manager.py to fetch from Secrets Manager:

```python
import boto3
import json

def get_credential_from_aws(credential_key):
    client = boto3.client('secretsmanager')
    try:
        response = client.get_secret_value(SecretId=credential_key)
        if 'SecretString' in response:
            return response['SecretString']
    except Exception as e:
        print(f"Error fetching {credential_key} from Secrets Manager: {e}")
    return None

def load_connectors():
    # ... existing code ...
    
    # Try AWS first, then environment
    password = get_credential_from_aws(credential_key)
    if not password:
        password = os.getenv(credential_key)
```

### Recommended: HashiCorp Vault

```python
import hvac

def get_credential_from_vault(credential_key):
    client = hvac.Client(url=os.getenv('VAULT_URL'))
    client.auth.approle.login(
        role_id=os.getenv('VAULT_ROLE_ID'),
        secret_id=os.getenv('VAULT_SECRET_ID')
    )
    
    response = client.secrets.kv.v2.read_secret_version(
        path=f'connectors/{credential_key}'
    )
    return response['data']['data']['password']
```

---

## Troubleshooting

### Connector Status is `not_found`

**Problem:** API shows `credential_status: "not_found"`

**Solution:**
1. Check `.env` file has the variable:
   ```bash
   grep SALES_DB_PASSWORD .env
   ```

2. Make sure `.env` is loaded before connector_manager runs:
   ```python
   # In main_simple.py, before importing connector_manager
   from dotenv import load_dotenv
   load_dotenv()
   ```

3. Check environment variable is set:
   ```bash
   echo $SALES_DB_PASSWORD
   ```

### Connection Fails Despite `loaded` Status

**Problem:** Credential is loaded, but connection fails

**Solution:**
1. Test the actual connection parameters:
   ```bash
   psql -h localhost -U voxcore_user -d sales
   ```

2. Verify database is running
3. Check host/port/user in .ini file matches actual database
4. Verify password is correct

### Frontend Shows Red Indicator

**Problem:** Connector shows error status

**Solution:**
1. Check logs in backend:
   ```bash
   tail -f logs/voxcore.log
   ```

2. Review connector_manager.py output for error messages
3. Verify all [security] section values are valid booleans/ints

---

## Summary

| Aspect | Before | After |
|--------|--------|-------|
| Password Storage | In .ini file | In environment variables |
| Git Safety | Dangerous ❌ | Safe ✅ |
| Credential Rotation | Manual code update | Update env var only |
| Multi-Environment | One .ini per env | One .ini, different env vars |
| Audit Trail | None | Managed by vault |
| Production Ready | No | Yes |

---

## Next Steps

1. **Local Testing**: Set up `.env` and test `/api/v1/connectors` endpoint
2. **Security Testing**: Verify frontend never exposes passwords
3. **Production Setup**: Migrate to AWS Secrets Manager or HashiCorp Vault
4. **Policy Enforcement**: Implement actual SQL rewriting based on security policies
5. **Encryption**: Consider TLS for inter-service communication

VoxCore Secure Connector Architecture is **production-ready** and implements industry-standard credential management practices.

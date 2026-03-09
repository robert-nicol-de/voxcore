# VoxCore Multi-Tenant Architecture

## Overview

VoxCore is now a **multi-tenant AI database firewall** supporting enterprise SaaS deployments. Each tenant (customer/company) has completely isolated:

- Database connectors
- Security policies
- Team members and roles
- Usage analytics
- API keys

## Folder Structure

```
voxcore/
├── tenants/
│   ├── tenant_acme_corp/
│   │   ├── connectors/
│   │   │   ├── sales_db.ini
│   │   │   └── finance_db.ini
│   │   ├── policies.ini
│   │   └── users.json
│   │
│   ├── tenant_techstartup_inc/
│   │   ├── connectors/
│   │   │   └── warehouse.ini
│   │   ├── policies.ini
│   │   └── users.json
│   │
│   └── tenant_enterprise_solutions/
│       ├── connectors/
│       │   ├── operational_db.ini
│       │   └── compliance_db.ini
│       ├── policies.ini
│       └── users.json
```

## Tenant Identification

Tenants are identified via HTTP headers (in order of priority):

### 1. X-Tenant-ID Header (Recommended)

```bash
curl -H "X-Tenant-ID: tenant_acme_corp" https://voxcore.com/api/connectors
```

### 2. Query Parameter

```bash
curl https://voxcore.com/api/connectors?tenant=tenant_acme_corp
```

### 3. Subdomain

```bash
curl https://acme-corp.voxcore.com/api/connectors
# Automatically extracts: tenant_acme_corp
```

### 4. Default

If no tenant identifier is found, requests use `default` tenant (for standalone deployments).

## Connector Configuration

Each tenant's connectors are defined in INI files under `tenants/{tenant_id}/connectors/`.

### Example: Acme Corp Sales Database

File: `tenants/tenant_acme_corp/connectors/sales_db.ini`

```ini
[database]
name = sales_db
type = postgresql
host = sales-db.acme-corp.internal
port = 5432
database = sales
credential_key = ACME_SALES_DB_PASSWORD

[security]
block_delete = true
block_update = false
block_drop = true
max_rows = 5000
protect_tables = transactions,customers,orders
pii_protected = true
policy = strict
```

### Credential Management

Passwords are **never stored in .ini files**. Instead, use `credential_key` to reference environment variables:

```bash
export ACME_SALES_DB_PASSWORD="secure_password_here"
export ACME_FINANCE_DB_PASSWORD="another_secure_password"
export TECHSTARTUP_WAREHOUSE_PASSWORD="startup_password"
```

At runtime, `connector_manager.py` loads actual credentials from environment variables:

```python
def load_connectors(tenant_id: str):
    # Load from tenants/{tenant_id}/connectors/
    # For each .ini file:
    # credential_key = "ACME_SALES_DB_PASSWORD"
    # password = os.getenv("ACME_SALES_DB_PASSWORD")
```

## User Management

Each tenant has a `users.json` file defining team members.

### Example: Acme Corp Team

File: `tenants/tenant_acme_corp/users.json`

```json
{
  "tenant_id": "tenant_acme_corp",
  "company_name": "Acme Corp",
  "created_at": "2026-01-15T10:00:00Z",
  "subscription_plan": "Enterprise",
  "users": [
    {
      "id": "user_001",
      "email": "admin@acme-corp.com",
      "name": "Alice Johnson",
      "role": "admin"
    },
    {
      "id": "user_002",
      "email": "data_engineer@acme-corp.com",
      "name": "Bob Smith",
      "role": "developer"
    },
    {
      "id": "user_003",
      "email": "analyst@acme-corp.com",
      "name": "Carol White",
      "role": "viewer"
    }
  ]
}
```

### Roles and Permissions

| Role      | Permissions                          |
|-----------|--------------------------------------|
| `admin`   | Manage connectors, policies, users   |
| `developer` | Run AI queries, view results       |
| `viewer`  | View-only access to results          |

## Policy Configuration

Each tenant can customize security policies in `policies.ini`.

### Example: Enterprise Solutions (Strict Policies)

File: `tenants/tenant_enterprise_solutions/policies.ini`

```ini
[defaults]
query_timeout = 120
max_rows_default = 20000
require_approval = true

[security_policies]
enforce_row_limits = true
block_dangerous_operations = true
audit_all_queries = true
require_column_masking = true

[usage_limits]
daily_queries = 10000
daily_blocked_attacks = 2000
api_key_rotation_days = 30

[notification]
alert_on_blocked_attack = true
alert_on_policy_violation = true
daily_summary = true
```

## API Endpoints

All endpoints support tenant isolation via `X-Tenant-ID` header.

### List Connectors for Tenant

```bash
curl -H "X-Tenant-ID: tenant_acme_corp" \
     https://voxcore.com/api/v1/connectors
```

Response:

```json
{
  "total": 2,
  "tenant_id": "tenant_acme_corp",
  "connectors": [
    {
      "name": "sales_db",
      "database": { ... },
      "security": { ... },
      "credential_status": "loaded",
      "tenant_id": "tenant_acme_corp"
    },
    {
      "name": "finance_db",
      "database": { ... },
      "security": { ... },
      "credential_status": "loaded",
      "tenant_id": "tenant_acme_corp"
    }
  ]
}
```

### Get Specific Connector

```bash
curl -H "X-Tenant-ID: tenant_acme_corp" \
     https://voxcore.com/api/v1/connectors/sales_db
```

### List All Tenants

```bash
curl https://voxcore.com/api/v1/tenants
```

Response:

```json
{
  "total": 3,
  "tenants": [
    "tenant_acme_corp",
    "tenant_techstartup_inc",
    "tenant_enterprise_solutions"
  ]
}
```

### Get Tenant Configuration

```bash
curl https://voxcore.com/api/v1/tenants/tenant_acme_corp/config
```

Response:

```json
{
  "tenant_id": "tenant_acme_corp",
  "company_name": "Acme Corp",
  "subscription_plan": "Enterprise",
  "users": [...],
  "policies": {...}
}
```

## Tenant Isolation Enforcement

The VoxCore backend enforces strict tenant isolation:

### 1. Middleware Layer

`TenantMiddleware` automatically:
- Identifies tenant from request
- Stores tenant_id in request context
- Validates all operations are within tenant boundaries
- Returns 403 Forbidden for cross-tenant access attempts

### 2. Connector Loading

```python
# User from tenant_acme_corp cannot access connectors from tenant_techstartup_inc
load_connectors(tenant_id="tenant_acme_corp")
# Returns only: sales_db, finance_db

load_connectors(tenant_id="tenant_techstartup_inc")
# Returns only: warehouse
```

### 3. User Query Execution

When a user runs a query:

```
User Request (Alice from Acme Corp)
  ↓
Identify Tenant: tenant_acme_corp
  ↓
Validate User: admin@acme-corp.com in tenant_acme_corp ✓
  ↓
Load Connectors: Only Acme Corp connectors (sales_db, finance_db)
  ↓
Apply Tenant Policies: Acme Corp security_policies.ini
  ↓
Execute Query
  ↓
Log to Acme Corp's analytics only
```

## Subscription Plans

VoxCore supports usage-based billing:

| Plan        | Databases | Daily Queries | Storage    | Support        |
|-------------|-----------|---------------|-----------|-----------------|
| Starter     | 1         | 1,000         | 1 GB      | Email           |
| Pro         | 5         | 10,000        | 50 GB     | Priority Email  |
| Enterprise  | Unlimited | Unlimited     | Unlimited | 24/7 Support    |

Plans are defined in `users.json`:

```json
{
  "subscription_plan": "Enterprise"
}
```

## Example: Multi-Tenant Query Flow

### Scenario: Alice from Acme Corp runs a query

**Request:**
```http
POST /api/v1/query
X-Tenant-ID: tenant_acme_corp
Authorization: Bearer token_alice
Content-Type: application/json

{
  "connector": "sales_db",
  "query": "SELECT * FROM customers LIMIT 10"
}
```

**Security Checks:**
1. ✓ Validate token → Alice is admin@acme-corp.com
2. ✓ Validate tenant → User belongs to tenant_acme_corp
3. ✓ Load connectors → Only load from tenants/tenant_acme_corp/connectors/
4. ✓ Validate connector → sales_db exists in Acme Corp's connectors
5. ✓ Apply policies → Enforce Acme Corp's policies.ini (max_rows=5000, block_delete=true, etc)
6. ✓ Load credentials → ACME_SALES_DB_PASSWORD from environment
7. ✓ Mask PII → Apply pii_protected=true rules
8. ✓ Execute query → Run on Acme's database
9. ✓ Log audit → Record to Acme Corp's analytics only

**Response:**
```json
{
  "status": "success",
  "tenant_id": "tenant_acme_corp",
  "connector": "sales_db",
  "rows": 10,
  "execution_time_ms": 245,
  "audit_logged": true
}
```

## Security Best Practices

### 1. Environment Variables

Store credentials in environment variables, never in code:

```bash
# .env (NEVER commit this)
ACME_SALES_DB_PASSWORD=actual_password_here

# .env.example (Safe to commit)
ACME_SALES_DB_PASSWORD=change_me
```

### 2. Role-Based Access Control (RBAC)

Enforce roles at application level:

- **admin**: Can create/modify/delete connectors and policies
- **developer**: Can create and execute queries
- **viewer**: Can only view results

### 3. Audit Logging

All queries are logged per tenant:

```
Tenant: tenant_acme_corp
User: bob@acme-corp.com
Connector: sales_db
Query: SELECT COUNT(*) FROM customers
Result: 25,000 rows
Timestamp: 2026-03-09T14:30:00Z
Status: success
```

### 4. Network Isolation

In production, consider:
- Private network access to databases
- VPN for remote teams
- IP whitelisting per tenant

## Deployment Checklist

### 1. Create Tenant Directories

```bash
mkdir -p voxcore/tenants/my_customer/{connectors}
```

### 2. Configure Connectors

Create `.ini` files for each database:

```bash
cat > voxcore/tenants/my_customer/connectors/db1.ini << 'EOF'
[database]
name = db1
type = postgresql
host = db1.internal
credential_key = MY_CUSTOMER_DB1_PASSWORD

[security]
block_delete = true
pii_protected = true
EOF
```

### 3. Define Users

Create `users.json`:

```bash
cat > voxcore/tenants/my_customer/users.json << 'EOF'
{
  "tenant_id": "my_customer",
  "company_name": "My Customer Inc",
  "subscription_plan": "Pro",
  "users": [
    {
      "id": "user_001",
      "email": "admin@mycustomer.com",
      "role": "admin"
    }
  ]
}
EOF
```

### 4. Set Environment Variables

```bash
export MY_CUSTOMER_DB1_PASSWORD="actual_password"
```

### 5. Start Backend

```bash
cd voxcore/voxquery
python -m uvicorn voxquery.main:app --reload
```

### 6. Test Tenant Access

```bash
curl -H "X-Tenant-ID: my_customer" \
     http://localhost:8000/api/v1/connectors
```

## Architecture Diagram

```
┌─────────────────────────────────────────────┐
│     AI Tools (ChatGPT, Copilot, Claude)     │
└────────────────┬────────────────────────────┘
                 │
                 │ Query + Tenant ID
                 ↓
    ┌────────────────────────────┐
    │    VoxCore API Gateway     │
    │  (Multi-Tenant Firewall)   │
    └────────────────┬───────────┘
                     │
         ┌───────────┼───────────┐
         ↓           ↓           ↓
    ┌────────┐  ┌────────┐  ┌────────┐
    │Tenant A│  │Tenant B│  │Tenant C│
    │ Policy  │  │ Policy  │  │ Policy  │
    │ Engine  │  │ Engine  │  │ Engine  │
    └────┬───┘  └────┬───┘  └────┬───┘
         ↓           ↓           ↓
    ┌─────────┐ ┌──────────┐ ┌──────────┐
    │Acme DB  │ │TechStart │ │Enterprise│
    │Connectors│ │Warehouse │ │Compliance│
    └─────────┘ └──────────┘ └──────────┘
```

## Next Steps

1. **Backend Integration**: Connect ThreatMonitor and SecurityScore to tenant-specific events
2. **Frontend Multi-Tenant UI**: Show tenant name/logo in dashboard
3. **Billing Integration**: Track usage per tenant for SaaS billing
4. **SIEM Integration**: Send tenant-specific security events to customer SIEM
5. **API Key Management**: Per-tenant API keys with rotation policies

## SaaS Platform Vision

VoxCore transforms from:

```
Single Deploy Firewall
         ↓
Multi-Customer SaaS Platform
         ↓
Enterprise Data Security Category
```

This enables VoxCore to compete with:
- **Cloudflare**: Protects web traffic
- **Kong**: Protects API traffic
- **VoxCore**: Protects AI-to-Database traffic ← NEW!

The niche is **AI Data Security Gateway** for enterprises.

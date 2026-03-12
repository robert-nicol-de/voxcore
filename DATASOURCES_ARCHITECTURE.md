# VoxCore Data Source Architecture

**Date**: March 12, 2026  
**Version**: 1.0  
**Status**: MVP Implementation

## Overview

The VoxCore Data Source Architecture enables AI SQL platforms to support multiple data warehouse technologies while maintaining a consistent, semantic-aware query interface. This document describes the system design, platform support, and implementation approach.

---

## 🎯 Strategic Goals

1. **Unified Data Access**: Connect to any supported data platform with a single UI
2. **Semantic Understanding**: Let users define business meanings (entities, metrics) above raw SQL tables
3. **AI-Ready**: Provide rich context to AI systems for better query generation
4. **Enterprise-Grade**: Support massive data warehouses (Snowflake, BigQuery, Redshift)
5. **Flexible Tiers**: Prioritize essential platforms while supporting legacy databases

---

## 🏗️ Architecture Layers

```
┌─────────────────────────────────────────────────────────────────────┐
│                        UI Layer                                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐              │
│  │   Platform   │  │  Connection  │  │  Semantic    │              │
│  │   Selector   │  │   Setup      │  │   Models     │              │
│  └──────────────┘  └──────────────┘  └──────────────┘              │
└─────────────────────────────────────────────────────────────────────┘
                          ↓ API
┌─────────────────────────────────────────────────────────────────────┐
│                      API Layer (/api/v1/datasources)                │
│  • /platforms              - List supported platforms             │
│  • /test-connection       - Validate connection params           │
│  • / (CRUD)               - Manage datasources                   │
│  • /schema                - Discover tables & columns            │
│  • /models                - Manage semantic models               │
└─────────────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────────────┐
│                    Service Layer                                     │
│  • DatasourceService      - Factory, driver selection, caching   │
│  • SemanticModelService   - Entity CRUD, AI context generation   │
└─────────────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────────────┐
│                    Driver Layer                                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐             │
│  │ Snowflake    │  │ SQL Server   │  │ PostgreSQL   │             │
│  │  Driver      │  │  Driver      │  │  Driver      │             │
│  └──────────────┘  └──────────────┘  └──────────────┘             │
│  ┌──────────────┐  ┌──────────────┐                               │
│  │  BigQuery    │  │  Redshift    │                               │
│  │  Driver      │  │  Driver      │                               │
│  └──────────────┘  └──────────────┘                               │
└─────────────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────────────┐
│                  Data Warehouse Layer                                │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 📋 Platform Support Matrix

### Tier 1: Essential 🎯 (Must Have)

| Platform | Priority | Status | Reasoning |
|----------|----------|--------|-----------|
| SQL Server | 1 | ✅ MVP | Your current base; enterprise standard |
| Snowflake | 1 | ✅ MVP | Most popular cloud data warehouse |
| PostgreSQL | 1 | ✅ MVP | Most popular open-source database |

### Tier 2: Enterprise ⭐

| Platform | Priority | Status | Reasoning |
|----------|----------|--------|-----------|
| BigQuery | 2 | 📋 TODO | Huge AI/analytics workloads |
| Redshift | 2 | 📋 TODO | AWS enterprise warehouses |

### Tier 3: Additional 🔧

| Platform | Priority | Status | Reasoning |
|----------|----------|--------|-----------|
| MySQL | 3 | 📋 TODO | Legacy business databases |
| SQLite | 3 | ✅ Partial | Local dev/testing (via schema/drivers) |

---

## 🔌 Driver Interface

Each driver implements the core interface:

```python
class DatabaseDriver:
    """Standard interface for all database drivers."""
    
    def connect() -> bool
    def disconnect() -> None
    def test_connection() -> bool
    def discover_databases() -> List[str]
    def discover_schemas(database: str) -> List[str]
    def discover_schema(database: str, schema: str) -> DatabaseSchema
```

### Schema Discovery Output

```json
{
  "database": "analytics",
  "schema": "public",
  "tables": [
    {
      "name": "customers",
      "rows_estimate": 1000000,
      "columns": [
        {
          "name": "customer_id",
          "type": "INT",
          "nullable": false,
          "primary_key": true,
          "sensitive": null
        },
        {
          "name": "email",
          "type": "VARCHAR(255)",
          "nullable": false,
          "primary_key": false,
          "sensitive": "PII"
        }
      ]
    }
  ]
}
```

---

## 🧠 Semantic Models

A semantic model is a **business abstraction layer** that maps business concepts to SQL tables.

### Purpose

Instead of asking AI "Query the customers table for sum of order_total grouped by status", users can ask:

> "Show me revenue by customer segment"

The semantic model translates this to the correct SQL.

### Data Structure

```python
class SemanticModel:
    id: int
    workspace_id: int
    datasource_id: int  # Links to specific data source
    name: str           # "Customer Analytics"
    entities: Dict[str, SemanticEntity]

class SemanticEntity:
    name: str           # "customers"
    display_name: str   # "Customer"
    sql_table: str      # "customers"
    sql_schema: str     # "public"
    primary_key: str    # "customer_id"
    fields: Dict[str, SemanticField]
    metrics: Dict[str, SemanticMetric]

class SemanticField:
    sql_column: str     # "email"
    display_name: str   # "Email Address"
    field_type: str     # "dimension" or "metric"

class SemanticMetric:
    name: str           # "total_revenue"
    display_name: str   # "Total Revenue"
    sql_expression: str # "SUM(order_total)"
```

### Example Semantic Model

```json
{
  "id": 1,
  "workspace_id": 1,
  "datasource_id": 1,
  "name": "Customer Analytics",
  "entities": {
    "customers": {
      "name": "customers",
      "display_name": "Customer",
      "sql_table": "customers",
      "sql_schema": "public",
      "primary_key": "customer_id",
      "fields": {
        "id": {
          "sql_column": "customer_id",
          "display_name": "Customer ID",
          "field_type": "dimension"
        },
        "email": {
          "sql_column": "email",
          "display_name": "Email Address",
          "field_type": "dimension"
        },
        "segment": {
          "sql_column": "segment",
          "display_name": "Customer Segment",
          "field_type": "dimension"
        }
      },
      "metrics": {
        "total_revenue": {
          "name": "total_revenue",
          "display_name": "Total Revenue",
          "sql_expression": "SUM(order_total)"
        },
        "order_count": {
          "name": "order_count",
          "display_name": "Number of Orders",
          "sql_expression": "COUNT(DISTINCT order_id)"
        }
      }
    }
  }
}
```

---

## 🚀 Two AI Modes

### Mode 1: Direct SQL (Current)

```
User Question
    ↓
VoxQuery AI generates SQL from schema
    ↓
Risk Engine evaluates query
    ↓
Sandbox executes
    ↓
Results
```

**Issue**: AI guesses table/column names, may misunderstand business logic.

### Mode 2: Semantic (New)

```
User Question
    ↓
Semantic Model interprets business meaning
    ↓
AI generates SQL using semantic entities + metrics
    ↓
Risk Engine evaluates query
    ↓
Sandbox executes
    ↓
Results
```

**Benefit**: AI understands business context, generates more accurate queries.

---

## 📦 Backend File Structure

```
backend/datasources/
├── __init__.py
├── models.py          # Pydantic models (DataSource, SemanticModel, etc.)
├── service.py         # Business logic (DatasourceService, SemanticModelService)
├── router.py          # API endpoints (/api/v1/datasources/*)
└── drivers/
    ├── __init__.py
    ├── snowflake_driver.py    # ✅ MVP
    ├── sqlserver_driver.py    # (Can enhance existing schema driver)
    ├── postgres_driver.py     # (Can enhance existing schema driver)
    ├── bigquery_driver.py     # TODO
    └── redshift_driver.py     # TODO
```

---

## 🗄️ Database Schema

### data_sources Table

```sql
CREATE TABLE data_sources (
    id              INTEGER PRIMARY KEY,
    workspace_id    INTEGER NOT NULL REFERENCES workspaces(id),
    platform        TEXT NOT NULL,              -- 'snowflake', 'sql_server', etc.
    name            TEXT NOT NULL,              -- User-friendly name
    credentials     TEXT NOT NULL,              -- JSON (encrypted in practice)
    schema_cache    TEXT,                       -- Cached schema JSON
    schema_cache_at TEXT,                       -- Cache timestamp
    is_active       INTEGER DEFAULT 1,
    created_at      TEXT NOT NULL
)
```

### semantic_models Table

```sql
CREATE TABLE semantic_models (
    id              INTEGER PRIMARY KEY,
    workspace_id    INTEGER NOT NULL REFERENCES workspaces(id),
    datasource_id   INTEGER NOT NULL REFERENCES data_sources(id),
    name            TEXT NOT NULL,              -- "Customer Analytics"
    description     TEXT,
    definition      TEXT NOT NULL,              -- Full model as JSON
    is_active       INTEGER DEFAULT 1,
    created_at      TEXT NOT NULL
)
```

---

## 🔌 API Endpoints

### Platform Discovery

```
GET /api/v1/datasources/platforms
→ List all supported platforms with tier info

Response:
[
  {
    "code": "snowflake",
    "name": "Snowflake",
    "tier": 1,
    "available": true,
    "description": "Connect to Snowflake data warehouse"
  }
]
```

### Connection Management

```
POST /api/v1/datasources/test-connection
?platform=snowflake&credentials={...}
→ Validate connection parameters (doesn't save)

GET /api/v1/datasources/
?workspace_id=1
→ List all datasources in workspace

POST /api/v1/datasources/
?workspace_id=1&req={platform,name,credentials}
→ Create new datasource

DELETE /api/v1/datasources/{datasource_id}
→ Delete datasource + cascade-delete semantic models
```

### Schema Discovery

```
GET /api/v1/datasources/{datasource_id}/schema
?database=analytics&schema=public&force_refresh=false
→ Get full schema (cached 15 minutes unless force_refresh)

GET /api/v1/datasources/{datasource_id}/databases
→ List databases in datasource
```

### Semantic Models

```
GET /api/v1/datasources/models
?workspace_id=1&datasource_id=1
→ List all semantic models

POST /api/v1/datasources/models
?workspace_id=1&req={datasource_id,name,description}
→ Create semantic model

GET /api/v1/datasources/models/{model_id}
→ Get model definition

PATCH /api/v1/datasources/models/{model_id}
→ Update model (name, description, entities)

DELETE /api/v1/datasources/models/{model_id}
→ Delete model

POST /api/v1/datasources/models/{model_id}/entities
?entity_name=customers&entity_def={...}
→ Add/update entity in model

DELETE /api/v1/datasources/models/{model_id}/entities/{entity_name}
→ Remove entity from model
```

---

## 🎨 Frontend Components

### DataSourceSelector

- Displays platfor options in a grid, organized by tier
- Shows "Coming Soon" for unavailable platforms
- User selects platform to proceed to connection setup

**File**: `frontend/src/components/DataSourceSelector.tsx`

### SnowflakeConnectionSetup

- Form with Snowflake-specific fields (user, password, account, warehouse)
- Optional fields: database, schema, role
- "Test Connection" button to validate before saving
- Calls `POST /api/v1/datasources/test-connection` internally

**File**: `frontend/src/components/SnowflakeConnectionSetup.tsx`

### AddDataSourceModal

- Orchestrates the multi-step flow:
  1. Platform selection
  2. Connection setup (form varies by platform)
  3. Success confirmation
- Handles datasource creation and error states

**File**: `frontend/src/components/AddDataSourceModal.tsx`

---

## 🔐 Security Considerations

1. **Credential Storage**
   - Store credentials encrypted in database
   - Never log or expose credentials in traces
   - Use secure connection strings with SSL

2. **Metadata-Only Queries**
   - Schema drivers only read system metadata
   - Query limits: 1000 tables, 200 columns per table
   - 30-second query timeout

3. **Access Control**
   - Datasources are workspace-scoped
   - Users can only query datasources they have access to

4. **Audit Trail**
   - Log datasource creation/updates
   - Track semantic model changes

---

## 📈 Roadmap

**MVP** (Current):
- ✅ Snowflake driver
- ✅ SQL Server, PostgreSQL, MySQL, SQLite (existing drivers)
- ✅ DataSource CRUD
- ✅ UI: Platform selector + Snowflake setup
- ✅ Basic schema discovery and caching

**Phase 2** (Next):
- 📋 BigQuery driver
- 📋 Redshift driver
- 📋 Semantic models UI builder
- 📋 Semantic mode AI integration

**Phase 3**:
- 📋 Advanced caching (Redis integration)
- 📋 Metrics pre-computation
- 📋 Role-based access control (RBAC)
- 📋 Audit logging

---

## 🧪 Testing Checklist

- [ ] Platform list endpoint returns correct tiers
- [ ] Snowflake connection test validates credentials
- [ ] Datasource creation stores credentials securely
- [ ] Schema discovery retrieves tables + columns correctly
- [ ] Semantic model CRUD operations work
- [ ] Frontend builds with 0 errors
- [ ] Modal flow completes end-to-end

---

## 📚 References

- **Snowflake Python Connector**: https://docs.snowflake.com/user-guide/python-connector.html
- **BigQuery Python Client**: https://cloud.google.com/bigquery/docs/reference/rest
- **Amazon Redshift**: https://docs.aws.amazon.com/redshift/
- **FastAPI**: https://fastapi.tiangolo.com/
- **Pydantic**: https://docs.pydantic.dev/

---

**Last Updated**: March 12, 2026  
**Maintainer**: AI Data Governance Team

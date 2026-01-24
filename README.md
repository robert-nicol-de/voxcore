# VoxQuery

Turn everyday business questions into accurate, executable SQL — no more waiting on data teams, no rusty joins, no schema guesswork.

## Core Capabilities

### Natural Language Interface
- Ask questions in plain English: "Show top 10 clients by YTD revenue in ZAR"
- Seamless follow-ups: "Now filter to Western Cape only"
- Conversational context across sessions

### Multi-Warehouse Support
- **Snowflake** - QUALIFY, window functions, stages
- **AWS Redshift** - Distribution keys, sortkeys
- **Google BigQuery** - UNNEST, legacy SQL, dry-run
- **PostgreSQL** - JSONB, CTEs, full-text search
- **SQL Server** - T-SQL, hierarchical queries
- Extensible via SQLAlchemy

### Enterprise Features
- **Secure connections** - OAuth, secrets manager, role-based access
- **Safe execution** - Blocks DDL/DML, dry-run checks
- **Auditable** - Full SQL + execution plan logged
- **Cost-aware** - Query cost guards, warehouse sizing
- **Multi-tenant** - Per-user, per-report isolation

### Smart Results
- Formatted tables with auto-detected currencies (ZAR/R)
- Auto-generated charts (bar, line, scatter)
- One-click CSV/Excel export
- REST API for BI tool integration

## Architecture

```
VoxQuery/
├── backend/
│   ├── voxquery/
│   │   ├── core/              # SQL generation & conversation engine
│   │   ├── warehouses/        # Connection handlers (Snowflake, Redshift, etc)
│   │   ├── api/               # FastAPI routes
│   │   └── formatting/        # Results formatting & charting
│   ├── tests/
│   └── requirements.txt
├── frontend/                   # React/Vue UI
└── docs/                       # Architecture & setup guides
```

## Quick Start

```bash
# Install dependencies
pip install -r backend/requirements.txt

# Set environment variables
export WAREHOUSE_TYPE=snowflake
export WAREHOUSE_HOST=xy12345.us-east-1.snowflakecomputing.com
export WAREHOUSE_USER=voxquery_user
export WAREHOUSE_PASS=***

# Run API server
python backend/main.py

# Ask a question
curl -X POST http://localhost:8000/api/v1/query \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Show top 10 clients by YTD revenue",
    "warehouse": "snowflake"
  }'
```

## Development

```bash
# Run tests
pytest tests/

# Run with auto-reload
uvicorn voxquery.api.main:app --reload

# Check code quality
black . && pylint voxquery/
```

## License

MIT

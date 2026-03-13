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

## VoxCore Dev Stack

```bash
# 1. Start API
uvicorn backend.main:app --reload

# 2. Start Query Worker
python -m backend.workers.query_worker

# 3. Start Frontend
cd frontend && npm run dev
```

For single-process local development, you can opt into background worker autostart by setting `VOXCORE_AUTOSTART_QUERY_WORKER=true` in `.env`.

## VoxCore Control Plane

VoxCore now exposes a first-class Control Plane layer that sits between clients and the execution engines. This is the orchestration boundary that decides how a request moves through governance, semantic intelligence, telemetry, and execution.

Current Control Plane responsibilities:

- route query requests through the correct platform path
- coordinate Semantic Brain, Data Guardian, policy enforcement, and risk evaluation
- attach a canonical `control_plane` envelope to orchestrated query responses
- support both sync execution and queued worker execution through the same orchestration layer
- provide a clean platform story for future agent, copilot, and external AI integrations

Current implementation entry points:

- `backend/control_plane/orchestrator.py` for orchestration
- `backend/control_plane/models.py` for context and route-plan contracts
- `backend/control_plane/context.py` for request normalization and worker request context

The current slice focuses on the query lifecycle first. Agents, platform telemetry, and cross-system coordination can now converge on the same orchestration boundary instead of growing as independent subsystems.

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

# VoxCore One-Page Product and Technical Specification

## 1) Executive Summary
VoxCore is an AI-powered analytics platform that converts business questions into safe, executable SQL across enterprise data sources. It combines natural-language query assistance, schema-aware SQL inspection, governed execution, and visualization/export workflows in a containerized deployment model suitable for production operations.

## 2) Product Positioning
- Category: AI-native analytics and governed NL-to-SQL platform
- Primary value: Faster analytics with lower SQL risk and stronger governance
- Core promise: Ask, inspect, execute, visualize, and export data with guardrails

## 3) Target Users
- Business analysts and operations teams
- Finance and reporting stakeholders
- Data/BI engineers supporting governed self-service analytics
- Technical product teams needing embedded query intelligence

## 4) Core Capabilities
- Natural-language to SQL workflow support
- Live schema discovery (databases, tables, views, columns)
- Query inspection before execution (risk and validity signals)
- Read-only and dangerous keyword safety checks
- Schema-aware validation against discovered metadata
- SQL execution against connected warehouses/databases
- Result rendering for charts/tables and export-friendly outputs
- Authentication and role-aware access controls

## 5) Key API Surface (Current)
- Schema discovery:
  - `GET /api/v1/schema/databases`
  - `GET /api/v1/schema/tables?database=...`
  - `GET /api/v1/schema/views?database=...`
  - `GET /api/v1/schema/columns?database=...`
- Query inspection:
  - `POST /api/v1/query/inspect`
- Query execution/auth:
  - Existing query execution and auth connection/test endpoints with improved SQL Server error handling

## 6) System Architecture
- Frontend: React + TypeScript (Vite build)
- Backend: Python FastAPI + Pydantic
- Data access: SQLAlchemy + connector/driver layer
- Proxy: Nginx reverse proxy for frontend/API routing
- Runtime: Docker Compose service topology
- Deployment model: Git push -> cloud rebuild/deploy (Render)

Logical flow:
User UI -> VoxCore API -> SQL dialect/validation -> connector driver -> database -> results -> chart/export

## 7) Technical Stack and Dependencies
- Backend runtime: Python 3.11
- API stack: FastAPI, Uvicorn, Pydantic
- Query and SQL tooling: SQLAlchemy, sqlglot, sqlparse
- Data tooling: pandas, numpy, polars
- Security/auth: python-jose, passlib, cryptography
- Rate limiting and observability: slowapi, structlog, sentry-sdk
- Connector packages:
  - SQL Server: pyodbc + msodbcsql18 (system package)
  - PostgreSQL: psycopg2-binary
  - Snowflake: snowflake-sqlalchemy + snowflake connector

## 8) Connectivity and Supported Data Platforms
Current supported and provisioned connectors:
- SQL Server (ODBC Driver 18 path)
- PostgreSQL
- Snowflake

Extensibility target:
- MySQL and BigQuery can be integrated through the same connector abstraction without changing UI/API contracts.

## 9) Security, Governance, and Safety Controls
- JWT-based auth patterns and role-aware endpoint protection
- Query inspector endpoint to gate SQL before execution
- Dangerous statement detection (e.g., mutation/destructive patterns)
- Read-only policy checks where required
- Schema/table/column reference validation to reduce hallucinated SQL
- API rate limiting and security-oriented proxy headers

## 10) Deployment and Reliability Specifications
- Containerized backend with health checks
- ODBC system dependencies installed at image build time
- Microsoft package key/repository configuration for SQL Server driver installation
- Automated rebuild/deploy flow in cloud hosting
- Friendly connection error mapping for operational diagnosis

## 11) SQL Server Production Requirements
To ensure stable SQL Server connectivity in Linux containers:
- System package: `msodbcsql18`
- ODBC libs: `unixodbc`, `unixodbc-dev`
- Python package: `pyodbc`
- Typical connection string options:
  - `Driver={ODBC Driver 18 for SQL Server}`
  - `Encrypt=no`
  - `TrustServerCertificate=yes`

Validation command inside backend container:
- `odbcinst -q -d`
Expected driver entry:
- `[ODBC Driver 18 for SQL Server]`

## 12) Functional Outcome for Customers
VoxCore delivers a governed analytics loop:
1. Connect enterprise data
2. Discover schema instantly
3. Generate/inspect SQL with AI assistance
4. Execute safely under policy
5. Visualize and operationalize insights

## 13) Near-Term Roadmap Priorities
- Connector expansion (MySQL, BigQuery)
- Enhanced policy engine for column/table-level enforcement
- Deeper audit trails and explainability metadata
- Advanced semantic layer and reusable business metrics
- Expanded integration tests for deployment parity

## 14) Success Metrics
- Time-to-first-valid-query
- Query approval rate from inspector
- Failed/blocked risky query rate
- Connection success rate by data source
- Dashboard/report generation latency
- User adoption and retention across teams

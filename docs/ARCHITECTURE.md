# VoxQuery Architecture

## System Overview

VoxQuery is a natural language SQL generation system that converts business questions into executable SQL across multiple warehouses.

## Project Structure

```
VoxQuery/
├── backend/
│   ├── voxquery/
│   │   ├── core/                 # SQL generation & conversation engine
│   │   │   ├── engine.py         # Main VoxQueryEngine
│   │   │   ├── sql_generator.py  # LLM-based SQL generation
│   │   │   ├── schema_analyzer.py # Database schema analysis
│   │   │   └── conversation.py   # Conversation context management
│   │   ├── warehouses/           # Warehouse-specific connections
│   │   │   ├── base.py           # Base connection class
│   │   │   ├── snowflake_handler.py
│   │   │   ├── redshift_handler.py
│   │   │   ├── bigquery_handler.py
│   │   │   ├── postgres_handler.py
│   │   │   └── sqlserver_handler.py
│   │   ├── api/                  # FastAPI endpoints
│   │   │   ├── query.py          # Query endpoints
│   │   │   ├── schema.py         # Schema endpoints
│   │   │   ├── auth.py           # Authentication
│   │   │   └── health.py         # Health checks
│   │   ├── formatting/           # Results formatting
│   │   │   ├── formatter.py      # Format results with type detection
│   │   │   └── charts.py         # Chart generation (Plotly/Vega-Lite)
│   │   └── config.py             # Configuration management
│   ├── main.py                   # API entry point
│   ├── requirements.txt           # Python dependencies
│   └── tests/                     # Test suite
├── frontend/
│   ├── Chat.tsx                  # Chat interface component
│   ├── Chat.css                  # Styles
│   └── package.json              # Node dependencies
└── docs/
    └── ARCHITECTURE.md           # This file
```

## Core Components

### 1. SQL Generation Engine (`core/sql_generator.py`)

**Purpose**: Convert natural language questions to SQL using LLM + schema context

**Features**:
- Multi-dialect support (Snowflake, Redshift, BigQuery, PostgreSQL, SQL Server)
- Few-shot examples for financial queries (YTD revenue, budget variance, etc.)
- Dialect-specific SQL features (QUALIFY for Snowflake, UNNEST for BigQuery, etc.)
- Query type detection (SELECT, AGGREGATE, WINDOW, CTE, JOIN)
- Confidence scoring

**Key Methods**:
- `generate(question, context)` - Main generation method
- `_build_prompt()` - Constructs LLM prompt with schema + examples
- `_extract_sql()` - Parses SQL from LLM response
- `_determine_query_type()` - Identifies query type
- `_calculate_confidence()` - Scores confidence

### 2. Schema Analyzer (`core/schema_analyzer.py`)

**Purpose**: Extract database schema for LLM context

**Features**:
- Introspects tables, columns, types
- Detects row counts and primary keys
- Generates human-readable schema context
- Column name autocomplete suggestions

**Key Methods**:
- `analyze_all_tables()` - Scan entire database
- `analyze_table()` - Deep dive into single table
- `get_schema_context()` - Format for LLM prompt
- `get_column_suggestions()` - Autocomplete helper

### 3. Conversation Manager (`core/conversation.py`)

**Purpose**: Maintain context across multi-turn conversations

**Features**:
- Message history (auto-trimmed to 10 messages)
- Context tracking (tables accessed, filters applied)
- Serialization to JSON
- Clear history on demand

**Key Methods**:
- `add_user_message()` / `add_assistant_message()` - Record messages
- `get_conversation_context()` - Format for LLM
- `update_context()` - Track metadata
- `to_dict()` - Serialize session

### 4. Main Engine (`core/engine.py`)

**Purpose**: Orchestrates generation and execution

**Features**:
- Manages engine lifecycle
- Coordinates SQL generation + execution
- Handles multi-warehouse connections
- Cost estimation and dry-run checks

**Key Methods**:
- `ask(question, execute=True, dry_run=True)` - Main entry point
- `_execute_query()` - Run SQL and return results
- `_dry_run_query()` - EXPLAIN plan validation
- `get_schema()` - Expose schema info

### 5. Warehouse Connections

**Base Class** (`warehouses/base.py`):
- Abstract interface for all warehouse types
- Methods: `connect()`, `execute_query()`, `get_schema()`, `test_connection()`, `get_cost_estimate()`

**Implementations**:
- **Snowflake** - `snowflake-connector` native
- **Redshift** - PostgreSQL-compatible, psycopg2
- **BigQuery** - Google Cloud client, dry-run cost estimates
- **PostgreSQL** - psycopg2
- **SQL Server** - pyodbc

### 6. Results Formatting (`formatting/formatter.py`)

**Purpose**: Smart formatting with auto-detection of:
- Currencies (ZAR, USD, EUR, GBP)
- Percentages
- Dates
- Numbers

**Features**:
- Type inference from sample data
- Currency detection from column names
- Export to CSV/Excel
- Structured JSON output with metadata

**Key Methods**:
- `format_results()` - Main formatting
- `_detect_columns()` - Column analysis
- `_infer_type()` - Type detection
- `to_csv()` / `to_excel()` - Export formats

### 7. Chart Generation (`formatting/charts.py`)

**Purpose**: Auto-generate visualizations

**Features**:
- Suggest chart type based on data shape
- Generate Vega-Lite specs
- Generate Plotly JSON
- KPI card generation

**Suggestions**:
- Time series → line chart
- Top-N items → bar chart
- Correlation → scatter plot
- Aggregates → pie chart

### 8. REST API (`api/`)

**Query Endpoint** (`POST /api/v1/query`):
```python
{
    "question": "Show top 10 clients by YTD revenue",
    "warehouse": "snowflake",
    "execute": true,
    "dry_run": true,
    "format": "table"
}
```

Response:
```python
{
    "question": "...",
    "sql": "SELECT ...",
    "query_type": "AGGREGATE",
    "confidence": 0.95,
    "explanation": "...",
    "tables_used": ["customers", "orders"],
    "data": [{...}, {...}],
    "row_count": 100,
    "execution_time_ms": 245.3,
    "chart": {...}  # Vega-Lite spec
}
```

**Schema Endpoints**:
- `GET /api/v1/schema` - Full schema
- `GET /api/v1/schema/tables` - List tables
- `GET /api/v1/schema/tables/{name}` - Table details

**Auth Endpoints**:
- `POST /api/v1/auth/login` - Login
- `POST /api/v1/auth/logout` - Logout

## Data Flow

```
User Question
    ↓
API /query endpoint
    ↓
VoxQueryEngine.ask()
    ↓
SchemaAnalyzer → Fetch database schema
    ↓
SQLGenerator → Build LLM prompt with schema + examples
    ↓
LLM (OpenAI/Anthropic/Local) → Generate SQL
    ↓
Validate SQL (optional dry-run/EXPLAIN)
    ↓
Execute Query → Fetch results
    ↓
ResultsFormatter → Detect types, format currencies/dates
    ↓
ChartGenerator → Suggest + generate visualization
    ↓
Return JSON response
    ↓
Frontend renders table, SQL, chart
```

## Configuration

Environment variables (`.env`):

```env
# Warehouse
WAREHOUSE_TYPE=snowflake
WAREHOUSE_HOST=xy12345.us-east-1.snowflakecomputing.com
WAREHOUSE_USER=voxquery_user
WAREHOUSE_PASSWORD=***
WAREHOUSE_DATABASE=analytics
WAREHOUSE_SCHEMA=PUBLIC

# LLM
LLM_PROVIDER=openai
LLM_MODEL=gpt-4
LLM_API_KEY=***
LLM_TEMPERATURE=0.1

# Security
SECRET_KEY=change-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Query Execution
QUERY_TIMEOUT_SECONDS=300
MAX_RESULT_ROWS=100000

# Cost Guards
ENABLE_COST_TRACKING=true
MAX_QUERY_COST_USD=100.0

# API
API_HOST=0.0.0.0
API_PORT=8000
```

## Security Considerations

1. **No DDL/DML**: Block INSERT, UPDATE, DELETE, DROP, CREATE by default
2. **Query Cost Guards**: Prevent expensive runaway queries
3. **Dry-run Checks**: Use EXPLAIN/dry-run where supported
4. **No Credential Leakage**: Never send creds to third-party LLMs
5. **Role-Based Access**: Per-user connections with warehouse roles
6. **Audit Logging**: Full SQL + execution plan logged

## Observability

Integration points:
- **LangSmith**: Trace LLM calls, latency, token usage
- **Structured Logging**: Query execution, errors, user actions
- **Cost Tracking**: Per-query cost estimates and actuals
- **Query Logs**: SQL executed, results row count, execution time

## Testing

```bash
# Unit tests
pytest tests/test_core.py -v

# API tests
pytest tests/test_api.py -v

# Integration tests (requires warehouse connection)
pytest tests/test_integration.py -v
```

## Deployment

### Local Development
```bash
pip install -r backend/requirements.txt
export OPENAI_API_KEY=***
python backend/main.py
```

### Docker
```bash
docker build -t voxquery .
docker run -p 8000:8000 -e OPENAI_API_KEY=*** voxquery
```

### Cloud (GCP Cloud Run)
```bash
gcloud run deploy voxquery \
  --source . \
  --platform managed \
  --region us-central1 \
  --set-env-vars OPENAI_API_KEY=***
```

## Future Enhancements

1. **Fine-tuned Models**: Train Llama-3.1 on company-specific schemas
2. **RAG**: Vector DB for business glossary, common joins
3. **Finance Domain**: Pre-built patterns for trial balance, cash flow
4. **Explainability**: Show reasoning for SQL generation choices
5. **Caching**: Cache schema + common queries
6. **Performance**: Query result caching, incremental results
7. **Collaboration**: Save/share queries, annotations
8. **BI Integration**: Native Power BI, Tableau, Looker plugins

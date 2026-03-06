# VoxQuery - Design Document

**Feature Name**: voxquery-nlp-sql  
**Version**: 1.0.0  
**Status**: Production Ready  
**Last Updated**: February 18, 2026

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│                    Frontend (React)                      │
│  - Chat interface                                        │
│  - Connection settings                                   │
│  - Chart display                                         │
└────────────────────┬────────────────────────────────────┘
                     │ HTTP/REST
┌────────────────────▼────────────────────────────────────┐
│                  FastAPI Backend                         │
│  ┌──────────────────────────────────────────────────┐   │
│  │ API Routes                                       │   │
│  │ - /api/v1/query (POST)                          │   │
│  │ - /api/v1/auth/connect (POST)                   │   │
│  │ - /api/v1/schema (GET)                          │   │
│  │ - /health (GET)                                 │   │
│  └──────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────┐   │
│  │ Core Engine                                      │   │
│  │ - VoxQueryEngine                                │   │
│  │ - SQLGenerator (Groq LLM)                       │   │
│  │ - SchemaAnalyzer                                │   │
│  │ - ValidationLayer                               │   │
│  └──────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────┐   │
│  │ Warehouse Handlers                               │   │
│  │ - SnowflakeHandler                              │   │
│  │ - SQLServerHandler                              │   │
│  │ - PostgresHandler                               │   │
│  │ - RedshiftHandler                               │   │
│  │ - BigQueryHandler                               │   │
│  └──────────────────────────────────────────────────┘   │
└────────────────────┬────────────────────────────────────┘
                     │ SQL
┌────────────────────▼────────────────────────────────────┐
│              Database Connections                        │
│  - Snowflake                                             │
│  - SQL Server                                            │
│  - PostgreSQL                                            │
│  - Redshift                                              │
│  - BigQuery                                              │
└─────────────────────────────────────────────────────────┘
```

---

## Component Design

### 1. VoxQueryEngine (Core Orchestrator)

**Responsibility**: Main orchestrator for SQL generation and execution

**Key Methods**:
```python
class VoxQueryEngine:
    def ask(question: str, execute: bool = False, dry_run: bool = False) -> QueryResult
    def execute_query(sql: str) -> ExecutionResult
    def get_schema() -> SchemaContext
    def set_connection(warehouse: str, credentials: Dict) -> bool
```

**Key Properties**:
- `schema_analyzer`: SchemaAnalyzer instance
- `sql_generator`: SQLGenerator instance
- `conversation`: ConversationManager instance
- `warehouse_handler`: Current warehouse handler

**Flow**:
1. Receive question from user
2. Load schema from database (or fallback)
3. Generate SQL using Groq LLM
4. Validate SQL (two-layer validation)
5. Execute SQL (if requested)
6. Format results and generate charts
7. Return to user

### 2. SQLGenerator (LLM Integration)

**Responsibility**: Generate SQL from natural language using Groq LLM

**Key Methods**:
```python
class SQLGenerator:
    def generate(question: str, context: Optional[str] = None) -> GeneratedSQL
    def _create_fresh_groq_client() -> ChatGroq
    def _build_prompt(question: str, schema_context: str, context: str) -> str
    def _extract_sql(response_text: str) -> str
    def _validate_sql(sql: str, dialect: str) -> Tuple[bool, str]
```

**Key Features**:
- Fresh Groq client per request (prevents state leakage)
- Temperature 0.2 for deterministic SQL
- Schema context injection to prevent hallucinations
- Multi-question support (splits "MTD and YTD" into two queries)
- Dialect-specific SQL translation
- Few-shot examples for financial queries

**Prompt Structure**:
```
You are an expert SQL developer.

CRITICAL RULES:
1. Only use tables and columns listed below
2. Generate only SELECT queries
3. Do not invent tables or columns
4. Use the exact column names provided

DATABASE SCHEMA:
[schema_context]

CONVERSATION CONTEXT:
[previous_questions_and_results]

USER QUESTION:
[question]

Generate the SQL query:
```

### 3. SchemaAnalyzer (Schema Management)

**Responsibility**: Analyze database schema and provide context to LLM

**Key Methods**:
```python
class SchemaAnalyzer:
    def analyze_all_tables() -> Dict[str, TableSchema]
    def get_schema_context() -> str
    def _populate_schema_cache_from_fallback() -> None
    def analyze_table(table_name: str) -> TableSchema
```

**Key Features**:
- Automatic fallback to hardcoded schema if DB unavailable
- Supports 5 core financial tables (ACCOUNTS, TRANSACTIONS, HOLDINGS, SECURITIES, SECURITY_PRICES)
- Lazy initialization
- Schema caching
- Handles Snowflake case sensitivity

**Fallback Schema**:
```
ACCOUNTS (ACCOUNT_ID, ACCOUNT_NAME, ACCOUNT_TYPE, BALANCE, OPEN_DATE, STATUS)
TRANSACTIONS (TRANSACTION_ID, ACCOUNT_ID, TRANSACTION_DATE, TRANSACTION_TYPE, AMOUNT, DESCRIPTION)
HOLDINGS (HOLDING_ID, ACCOUNT_ID, SECURITY_ID, QUANTITY, PURCHASE_DATE)
SECURITIES (SECURITY_ID, SECURITY_NAME, SECURITY_TYPE, TICKER)
SECURITY_PRICES (SECURITY_ID, PRICE_DATE, PRICE)
```

### 4. Validation Layer (SQL Safety)

**Responsibility**: Two-layer SQL validation for safety and accuracy

**Layer 1: inspect_and_repair()**
```python
def inspect_and_repair(
    generated_sql: str,
    schema_tables: set,
    schema_columns: dict,
    dialect: str = "snowflake"
) -> Tuple[str, float]:
    # Checks:
    # 1. Forbidden keywords (DROP, DELETE, UPDATE, etc.)
    # 2. Table names against schema
    # 3. Column names against schema
    # Returns: (final_sql, confidence_score 0.0-1.0)
```

**Layer 2: validate_sql()**
```python
def validate_sql(
    sql: str,
    allowed_tables: set,
    allowed_columns: dict = None,
    dialect: str = "snowflake"
) -> Tuple[bool, str, float]:
    # Checks:
    # 1. Dangerous DDL/DML keywords
    # 2. Tables against whitelist
    # 3. Columns against whitelist
    # Returns: (is_safe, reason, confidence)
```

**Validation Flow**:
```
Generated SQL
    ↓
Check for forbidden keywords (DROP, DELETE, UPDATE, etc.)
    ↓
Extract table names and validate against schema
    ↓
Extract column names and validate against schema
    ↓
Calculate confidence score (0.0-1.0)
    ↓
If score < 0.5: Use fallback query
If score >= 0.5: Return SQL with confidence
```

### 5. Warehouse Handlers

**Responsibility**: Database-specific connection and query execution

**Base Handler**:
```python
class BaseWarehouseHandler:
    def connect(credentials: Dict) -> bool
    def execute_query(sql: str) -> QueryResult
    def get_schema() -> Dict[str, TableSchema]
    def close() -> None
```

**Specific Handlers**:
- `SnowflakeHandler`: Snowflake-specific logic (QUALIFY, DATE_TRUNC, etc.)
- `SQLServerHandler`: SQL Server-specific logic (TOP, T-SQL, etc.)
- `PostgresHandler`: PostgreSQL-specific logic (JSONB, CTEs, etc.)
- `RedshiftHandler`: Redshift-specific logic (DISTKEY, SORTKEY, etc.)
- `BigQueryHandler`: BigQuery-specific logic (UNNEST, STRUCT, etc.)

### 6. Conversation Manager

**Responsibility**: Maintain conversation history and context

**Key Methods**:
```python
class ConversationManager:
    def add_message(role: str, content: str) -> None
    def get_history() -> List[Message]
    def get_context() -> str
    def clear() -> None
```

**Message Structure**:
```python
@dataclass
class Message:
    role: str  # "user" or "assistant"
    content: str
    timestamp: datetime
    sql: Optional[str] = None
    result: Optional[QueryResult] = None
```

### 7. Results Formatter

**Responsibility**: Format query results for display

**Key Methods**:
```python
class ResultsFormatter:
    def format_table(data: List[Dict]) -> FormattedTable
    def format_currency(value: float, currency: str = "ZAR") -> str
    def format_date(value: datetime) -> str
    def format_number(value: float) -> str
```

### 8. Chart Generator

**Responsibility**: Auto-generate charts from query results

**Key Methods**:
```python
class ChartGenerator:
    def detect_chart_type(data: List[Dict], columns: List[str]) -> str
    def generate_chart(data: List[Dict], chart_type: str) -> Chart
    def generate_multiple_charts(data: List[Dict]) -> List[Chart]
```

**Supported Chart Types**:
- Bar chart (categorical data)
- Line chart (time series)
- Pie chart (proportions)
- Scatter plot (correlations)
- Comparison chart (side-by-side)

---

## Data Flow

### Query Generation Flow

```
1. User enters question
   ↓
2. Frontend sends POST /api/v1/query
   ↓
3. Backend receives question
   ↓
4. SchemaAnalyzer loads schema (DB or fallback)
   ↓
5. SQLGenerator builds prompt with schema context
   ↓
6. Groq LLM generates SQL
   ↓
7. ValidationLayer validates SQL (two-layer)
   ↓
8. If valid: Return SQL with confidence
   If invalid: Return fallback query
   ↓
9. Frontend displays SQL and results
```

### Query Execution Flow

```
1. User clicks "Execute"
   ↓
2. Frontend sends POST /api/v1/query with execute=true
   ↓
3. Backend executes SQL via warehouse handler
   ↓
4. Results formatter formats data
   ↓
5. Chart generator creates charts
   ↓
6. Frontend displays results and charts
```

---

## API Design

### POST /api/v1/query

**Request**:
```json
{
  "question": "What is our YTD sales?",
  "warehouse": "snowflake",
  "execute": true,
  "dry_run": false,
  "format": "table"
}
```

**Response**:
```json
{
  "question": "What is our YTD sales?",
  "sql": "SELECT SUM(AMOUNT) AS ytd_sales FROM TRANSACTIONS WHERE ...",
  "query_type": "AGGREGATE",
  "confidence": 0.95,
  "explanation": "✓ Query executed successfully",
  "tables_used": ["TRANSACTIONS"],
  "data": [{"ytd_sales": 1234567.89}],
  "row_count": 1,
  "execution_time_ms": 245.3,
  "error": null,
  "chart": {...},
  "charts": [...]
}
```

### POST /api/v1/auth/connect

**Request**:
```json
{
  "database": "snowflake",
  "credentials": {
    "host": "ko05278.af-south-1.aws",
    "username": "QUERY",
    "password": "password",
    "database": "FINANCIAL_TEST"
  }
}
```

**Response**:
```json
{
  "success": true,
  "message": "Successfully connected to snowflake",
  "database": "snowflake",
  "host": "ko05278.af-south-1.aws"
}
```

### GET /api/v1/schema

**Response**:
```json
{
  "tables": ["ACCOUNTS", "TRANSACTIONS", "HOLDINGS", "SECURITIES", "SECURITY_PRICES"],
  "schema": "TABLE: ACCOUNTS\n  Columns in ACCOUNTS:\n    - ACCOUNT_ID: VARCHAR (NOT NULL)\n    ..."
}
```

---

## Error Handling

### Error Categories

1. **Connection Errors**
   - Database unreachable
   - Invalid credentials
   - Network timeout

2. **Schema Errors**
   - Table not found
   - Column not found
   - Schema mismatch

3. **SQL Errors**
   - Invalid SQL syntax
   - Forbidden operations (DDL/DML)
   - Hallucinated tables/columns

4. **Execution Errors**
   - Query timeout
   - Out of memory
   - Permission denied

5. **LLM Errors**
   - Groq API unavailable
   - Rate limit exceeded
   - Invalid response format

### Error Response Format

```json
{
  "error": true,
  "error_code": "SCHEMA_MISMATCH",
  "error_message": "Table 'INVALID_TABLE' not found in schema",
  "suggestion": "Did you mean 'TRANSACTIONS'?",
  "fallback_sql": "SELECT * FROM TRANSACTIONS LIMIT 10"
}
```

---

## Security Design

### SQL Injection Prevention
- Two-layer validation (schema-based + whitelist-based)
- SQL parsing with sqlglot
- Forbidden keyword detection
- Table/column whitelist validation

### Access Control
- Read-only enforcement (SELECT only)
- No DDL/DML operations allowed
- Credential management via environment variables
- Optional API key authentication

### Data Protection
- Credentials not logged
- Query results not cached
- Conversation history stored locally
- CORS configured for frontend domain

---

## Performance Design

### Optimization Strategies

1. **Schema Caching**
   - Cache schema after first load
   - Invalidate on connection change
   - Lazy initialization

2. **LLM Optimization**
   - Fresh client per request (prevents state leakage)
   - Temperature 0.2 for deterministic SQL
   - Token limit 1024 for efficiency
   - Few-shot examples for accuracy

3. **Query Optimization**
   - Limit result sets to 10k rows by default
   - Pagination for large results
   - Async chart generation

4. **Frontend Optimization**
   - Lazy load charts
   - Virtual scrolling for large tables
   - Debounce search/filter inputs

### Performance Targets

- SQL generation: < 2 seconds
- Query execution: < 30 seconds
- Chart generation: < 1 second
- API response: < 3 seconds (p95)

---

## Testing Strategy

### Unit Tests
- SQLGenerator: Test SQL extraction, validation, dialect translation
- SchemaAnalyzer: Test schema loading, fallback, caching
- ValidationLayer: Test forbidden keywords, table/column validation
- Warehouse handlers: Test connection, query execution

### Integration Tests
- End-to-end query generation and execution
- Multi-database support
- Error handling and fallback
- Chart generation

### Property-Based Tests
- SQL validation: For all valid/invalid SQL patterns
- Schema validation: For all table/column combinations
- Dialect translation: For all supported dialects

### Manual Tests
- UI/UX testing
- Performance testing
- Security testing
- Accessibility testing

---

## Deployment Design

### Environment Configuration

```bash
# .env file
GROQ_API_KEY=your_groq_api_key
WAREHOUSE_TYPE=snowflake
WAREHOUSE_HOST=your_account.region.aws
WAREHOUSE_USER=your_user
WAREHOUSE_PASSWORD=your_password
WAREHOUSE_DATABASE=your_database
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=false
LLM_MODEL=llama-3.3-70b-versatile
LLM_MAX_TOKENS=1024
LLM_TEMPERATURE=0.2
```

### Docker Deployment

```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY backend/requirements.txt .
RUN pip install -r requirements.txt
COPY backend/ .
CMD ["uvicorn", "voxquery.api:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Production Checklist

- [ ] Environment variables configured
- [ ] Database credentials secured
- [ ] CORS configured for frontend domain
- [ ] Logging configured
- [ ] Error monitoring enabled
- [ ] Performance monitoring enabled
- [ ] Backup strategy in place
- [ ] Disaster recovery plan

---

## Correctness Properties

### Property 1: SQL Safety
**Property**: All generated SQL must be read-only (SELECT only)
**Validation**: No DDL/DML keywords in generated SQL
**Test**: Property-based test with 1000+ random SQL patterns

### Property 2: Schema Validation
**Property**: All table and column names must exist in schema
**Validation**: Extract tables/columns and validate against schema
**Test**: Property-based test with all schema combinations

### Property 3: Confidence Score Accuracy
**Property**: Confidence score must reflect SQL quality
**Validation**: Score 1.0 for valid SQL, 0.0 for invalid
**Test**: Property-based test with known valid/invalid SQL

### Property 4: Fallback Behavior
**Property**: Invalid SQL must fall back to safe query
**Validation**: Fallback query must be valid and executable
**Test**: Property-based test with all invalid SQL patterns

### Property 5: Multi-Question Support
**Property**: Multi-question queries must generate valid UNION ALL
**Validation**: Each sub-query must be valid, UNION ALL must be valid
**Test**: Property-based test with all multi-question patterns

---

## Known Issues & Workarounds

### Issue 1: Groq Response Caching
**Problem**: Groq SDK caches responses at SDK level
**Solution**: Create fresh ChatGroq client per request
**Status**: ✅ Fixed

### Issue 2: Schema Hallucination
**Problem**: LLM generates non-existent tables/columns
**Solution**: Inject schema context into prompt, validate against schema
**Status**: ✅ Fixed

### Issue 3: UI Message Display
**Problem**: User questions not visible in chat
**Solution**: Add flex layout styles to message components
**Status**: ✅ Fixed

### Issue 4: SQL Validation Integration
**Problem**: Valid SQL being rejected
**Solution**: Integrate inspect_and_repair() into generation pipeline
**Status**: ✅ Fixed

---

**Document Owner**: Development Team  
**Last Review**: February 18, 2026  
**Next Review**: March 18, 2026

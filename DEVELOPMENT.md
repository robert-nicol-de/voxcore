# VoxQuery Development Guide

## Quick Start

### Prerequisites
- Python 3.10+
- Node.js 16+
- Warehouse credentials (Snowflake, Redshift, BigQuery, PostgreSQL, or SQL Server)
- OpenAI API key (or compatible LLM)

### Backend Setup

1. **Install Python dependencies**
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

2. **Create `.env` file**
   ```bash
   cp .env.example .env
   # Edit .env with your credentials
   ```

3. **Run API server**
   ```bash
   python main.py
   # API runs on http://localhost:8000
   # Docs: http://localhost:8000/docs
   ```

4. **Run tests**
   ```bash
   pytest tests/ -v --cov=voxquery
   ```

### Frontend Setup

1. **Install Node dependencies**
   ```bash
   cd frontend
   npm install
   ```

2. **Run development server**
   ```bash
   npm run dev
   # Frontend runs on http://localhost:5173
   ```

3. **Build for production**
   ```bash
   npm run build
   npm run preview
   ```

## API Examples

### Ask a Question

```bash
curl -X POST http://localhost:8000/api/v1/query \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Show top 10 clients by YTD revenue in ZAR",
    "warehouse": "snowflake",
    "execute": true,
    "dry_run": true
  }'
```

Response:
```json
{
  "question": "Show top 10 clients by YTD revenue in ZAR",
  "sql": "SELECT client_id, client_name, SUM(amount) as ytd_revenue FROM transactions WHERE YEAR(transaction_date) = 2024 GROUP BY client_id, client_name ORDER BY ytd_revenue DESC LIMIT 10",
  "query_type": "AGGREGATE",
  "confidence": 0.95,
  "explanation": "This query selects data from transactions to answer: Show top 10 clients by YTD revenue in ZAR",
  "tables_used": ["transactions"],
  "data": [
    {"client_id": 1, "client_name": "Acme Corp", "ytd_revenue": 150000.00},
    ...
  ],
  "row_count": 10,
  "execution_time_ms": 245.3,
  "chart": {...}
}
```

### Get Database Schema

```bash
curl http://localhost:8000/api/v1/schema
```

### Validate SQL

```bash
curl -X POST "http://localhost:8000/api/v1/query/validate?sql=SELECT%20*%20FROM%20customers"
```

### Interactive Docs

Visit http://localhost:8000/docs (Swagger UI) or http://localhost:8000/redoc (ReDoc)

## Code Examples

### Python - Direct Engine Usage

```python
from voxquery.core.engine import VoxQueryEngine

# Initialize engine
engine = VoxQueryEngine(
    warehouse_type="snowflake",
    warehouse_host="xy12345.us-east-1.snowflakecomputing.com",
    warehouse_user="your_user",
    warehouse_password="your_password",
    warehouse_database="analytics",
)

# Ask a question
result = engine.ask(
    question="Show top 10 clients by YTD revenue",
    execute=True,
    dry_run=True,
)

print(result["sql"])
print(result["data"])
print(result["chart"])

# Close when done
engine.close()
```

### Python - Custom SQL Generation

```python
from voxquery.core.sql_generator import SQLGenerator
from sqlalchemy import create_engine

# Create connection
engine = create_engine("snowflake://...")

# Initialize generator
generator = SQLGenerator(engine, dialect="snowflake")

# Generate SQL
generated = generator.generate(
    question="List overdue invoices >60 days grouped by region",
    context="User has access to sales database"
)

print(generated.sql)
print(generated.query_type)
print(generated.confidence)
```

### Python - Results Formatting

```python
from voxquery.formatting.formatter import ResultsFormatter

formatter = ResultsFormatter(default_currency="ZAR")

# Format raw results
formatted = formatter.format_results(
    data=[
        {"id": 1, "name": "Alice", "amount": 1234.56},
        {"id": 2, "name": "Bob", "amount": 2345.67},
    ],
    format_type="table"
)

# Export to Excel
excel_bytes = formatter.to_excel(formatted["rows"], sheet_name="Results")

# Export to CSV
csv_string = formatter.to_csv(formatted["rows"])
```

### Python - Chart Generation

```python
from voxquery.formatting.charts import ChartGenerator

generator = ChartGenerator()

# Suggest chart type
chart_type = generator.suggest_chart_type(data, columns)

# Generate Vega-Lite spec
spec = generator.generate_vega_lite(
    data=data,
    title="Top 10 Clients",
    x_axis="client_name",
    y_axis="ytd_revenue",
    chart_type="bar"
)
```

### React/TypeScript - Using Chat Component

```typescript
import { Chat } from './Chat';

export default function App() {
  return (
    <div className="app">
      <Chat />
    </div>
  );
}
```

## Warehouse-Specific Setup

### Snowflake

```env
WAREHOUSE_TYPE=snowflake
WAREHOUSE_HOST=xy12345.us-east-1.snowflakecomputing.com
WAREHOUSE_USER=voxquery_user
WAREHOUSE_PASSWORD=***
WAREHOUSE_DATABASE=analytics
WAREHOUSE_SCHEMA=PUBLIC
```

Key Features:
- QUALIFY for window functions
- Date/time functions (TIMEDIFF, DATE_TRUNC)
- Quoted identifiers with ""
- Recursive CTEs

### AWS Redshift

```env
WAREHOUSE_TYPE=redshift
WAREHOUSE_HOST=cluster.123456.us-east-1.redshift.amazonaws.com
WAREHOUSE_PORT=5439
WAREHOUSE_USER=awsuser
WAREHOUSE_PASSWORD=***
WAREHOUSE_DATABASE=dev
```

Key Features:
- DISTKEY and SORTKEY optimization
- UNLOAD for bulk exports
- Spectrum for S3 querying

### Google BigQuery

```env
WAREHOUSE_TYPE=bigquery
WAREHOUSE_HOST=
WAREHOUSE_DATABASE=my-project-id
WAREHOUSE_SCHEMA=my_dataset
# Uses Google Cloud credentials
```

Key Features:
- UNNEST for arrays
- STRUCT for complex types
- Dry-run cost estimation
- GENERATE_DATE_ARRAY for ranges

### PostgreSQL

```env
WAREHOUSE_TYPE=postgres
WAREHOUSE_HOST=localhost
WAREHOUSE_PORT=5432
WAREHOUSE_USER=postgres
WAREHOUSE_PASSWORD=***
WAREHOUSE_DATABASE=analytics
```

Key Features:
- JSONB operators
- Full-text search (@@)
- Window functions
- ARRAY functions

### SQL Server

```env
WAREHOUSE_TYPE=sqlserver
WAREHOUSE_HOST=server.database.windows.net
WAREHOUSE_PORT=1433
WAREHOUSE_USER=sqladmin
WAREHOUSE_PASSWORD=***
WAREHOUSE_DATABASE=analytics
```

Key Features:
- T-SQL syntax
- PIVOT/UNPIVOT
- STRING_AGG concatenation
- Recursive CTEs

## Performance Tips

1. **Schema Caching**: Analyzer caches schema after first load
2. **Query Limits**: Default 100,000 rows max - adjust if needed
3. **Cost Guards**: Set MAX_QUERY_COST_USD to prevent runaway queries
4. **Connection Pooling**: Configured in SQLAlchemy, adjust pool_size if needed
5. **LLM Caching**: Cache common question patterns server-side

## Debugging

### Enable Debug Logging

```env
DEBUG=true
LOG_LEVEL=DEBUG
```

### Check Schema Introspection

```python
from voxquery.core.engine import VoxQueryEngine

engine = VoxQueryEngine()
schema = engine.get_schema()
print(schema)
```

### Test Warehouse Connection

```bash
curl http://localhost:8000/health
# Response: {"status": "healthy", "version": "0.1.0"}
```

### View API Docs

- Swagger: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Troubleshooting

### "Connection refused" error
- Check warehouse credentials in `.env`
- Verify warehouse is running and accessible
- Check firewall rules

### "Table not found" error
- Verify table name and schema
- Check user has SELECT permissions
- Run schema introspection to see available tables

### "Invalid SQL generated"
- Check schema context is being loaded
- Try rephrasing question more specifically
- Check LLM_MODEL supports SQL generation

### "Query timeout"
- Increase QUERY_TIMEOUT_SECONDS in .env
- Optimize SQL or add WHERE clause
- Check warehouse performance

## Contributing

1. Fork repository
2. Create feature branch: `git checkout -b feature/my-feature`
3. Make changes with tests
4. Run tests: `pytest tests/ -v`
5. Submit pull request

## Support

- Issues: GitHub Issues
- Docs: https://voxquery.dev
- Slack: #voxquery on workspace

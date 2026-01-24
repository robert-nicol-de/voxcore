# VoxQuery Quick Reference

## 🚀 Project At A Glance

**VoxQuery** converts natural language questions into executable SQL across Snowflake, Redshift, BigQuery, PostgreSQL, and SQL Server.

**Key files to understand**:
- `backend/voxquery/core/engine.py` - Main orchestrator
- `backend/voxquery/core/sql_generator.py` - LLM SQL generation
- `backend/voxquery/api/query.py` - REST API
- `frontend/Chat.tsx` - Chat UI

## 📦 Installation (5 minutes)

```bash
# Clone & setup
git clone <repo> voxquery
cd voxquery

# Backend
cd backend
pip install -r requirements.txt
cp .env.example .env
# Edit .env with warehouse credentials + OPENAI_API_KEY

# Frontend
cd ../frontend
npm install
```

## ▶️ Run (2 terminals)

```bash
# Terminal 1: Backend
cd backend && python main.py
# API: http://localhost:8000
# Docs: http://localhost:8000/docs

# Terminal 2: Frontend
cd frontend && npm run dev
# UI: http://localhost:5173
```

## 🔤 Ask Questions

```bash
# Via API
curl -X POST http://localhost:8000/api/v1/query \
  -H "Content-Type: application/json" \
  -d '{"question": "Top 10 clients by revenue", "execute": true}'

# Via Python
from voxquery.core.engine import VoxQueryEngine
engine = VoxQueryEngine()
result = engine.ask("Top 10 clients by revenue", execute=True)
print(result["sql"])
print(result["data"])
```

## 📋 API Endpoints

| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/api/v1/query` | Ask question & get SQL |
| POST | `/api/v1/query/validate` | Validate SQL syntax |
| POST | `/api/v1/query/explain` | Get execution plan |
| GET | `/api/v1/schema` | List tables & columns |
| GET | `/api/v1/schema/tables/{name}` | Table details |
| POST | `/api/v1/auth/login` | Login |
| GET | `/health` | Health check |
| GET | `/ready` | Readiness check |

## 🏗️ Architecture Layers

```
Frontend (React)
    ↓ HTTP
REST API (FastAPI)
    ↓
Core Engine
    ├─ SQL Generator (LLM)
    ├─ Schema Analyzer
    ├─ Conversation Manager
    └─ Results Formatter
    ↓
Warehouse Handlers
    ├─ Snowflake
    ├─ Redshift
    ├─ BigQuery
    ├─ PostgreSQL
    └─ SQL Server
```

## 🔧 Core Classes

### VoxQueryEngine
```python
engine = VoxQueryEngine(warehouse_type="snowflake")
result = engine.ask(question, execute=True, dry_run=True)
schema = engine.get_schema()
engine.close()
```

### SQLGenerator
```python
from voxquery.core.sql_generator import SQLGenerator
gen = SQLGenerator(engine_connection, dialect="snowflake")
sql_obj = gen.generate(question, context)
print(sql_obj.sql)
print(sql_obj.confidence)
```

### ResultsFormatter
```python
from voxquery.formatting.formatter import ResultsFormatter
fmt = ResultsFormatter(default_currency="ZAR")
formatted = fmt.format_results(data)
csv = fmt.to_csv(data)
excel = fmt.to_excel(data)
```

### ChartGenerator
```python
from voxquery.formatting.charts import ChartGenerator
gen = ChartGenerator()
chart_type = gen.suggest_chart_type(data, columns)
spec = gen.generate_vega_lite(data, title="...", x_axis="...", y_axis="...")
```

## 🗄️ Warehouse Setup

### Snowflake
```env
WAREHOUSE_TYPE=snowflake
WAREHOUSE_HOST=xy12345.us-east-1.snowflakecomputing.com
WAREHOUSE_USER=user
WAREHOUSE_PASSWORD=pass
WAREHOUSE_DATABASE=analytics
```

### BigQuery
```env
WAREHOUSE_TYPE=bigquery
WAREHOUSE_DATABASE=my-project-id
# Uses GOOGLE_APPLICATION_CREDENTIALS
```

### Redshift
```env
WAREHOUSE_TYPE=redshift
WAREHOUSE_HOST=cluster.xyz.redshift.amazonaws.com
WAREHOUSE_PORT=5439
WAREHOUSE_USER=awsuser
WAREHOUSE_PASSWORD=pass
```

### PostgreSQL
```env
WAREHOUSE_TYPE=postgres
WAREHOUSE_HOST=localhost
WAREHOUSE_PORT=5432
WAREHOUSE_USER=postgres
WAREHOUSE_PASSWORD=pass
```

### SQL Server
```env
WAREHOUSE_TYPE=sqlserver
WAREHOUSE_HOST=server.database.windows.net
WAREHOUSE_PORT=1433
WAREHOUSE_USER=sqladmin
WAREHOUSE_PASSWORD=pass
```

## 🧪 Testing

```bash
# Run all tests
pytest tests/ -v

# Specific test
pytest tests/test_core.py::test_conversation_manager -v

# With coverage
pytest tests/ --cov=voxquery --cov-report=html
```

## 📊 Response Format

```json
{
  "question": "Show top 10 clients by YTD revenue",
  "sql": "SELECT client_id, client_name, SUM(amount) as ytd_revenue ...",
  "query_type": "AGGREGATE",
  "confidence": 0.95,
  "explanation": "This query selects data from transactions...",
  "tables_used": ["transactions"],
  "data": [
    {"client_id": 1, "client_name": "Acme", "ytd_revenue": 150000},
    ...
  ],
  "row_count": 10,
  "execution_time_ms": 245.3,
  "chart": {
    "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
    "mark": "bar",
    "encoding": {...}
  }
}
```

## 🛡️ Security Features

✅ **Blocks**: DROP, INSERT, UPDATE, DELETE, CREATE  
✅ **Validates**: Dry-run checks, EXPLAIN plans  
✅ **Audits**: Full SQL logging, execution time  
✅ **Guards**: Cost limits, timeout limits  
✅ **Isolates**: Per-user warehouse connections  

## 🐛 Debugging

```bash
# Enable debug mode
export DEBUG=true
export LOG_LEVEL=DEBUG

# Check schema introspection
curl http://localhost:8000/api/v1/schema

# Interactive API docs
open http://localhost:8000/docs

# Check logs
tail -f logs/voxquery.log
```

## 📁 Important Files

| File | Purpose |
|------|---------|
| `backend/voxquery/core/engine.py` | Main orchestrator |
| `backend/voxquery/core/sql_generator.py` | LLM SQL gen |
| `backend/voxquery/core/schema_analyzer.py` | Schema introspection |
| `backend/voxquery/core/conversation.py` | Context management |
| `backend/voxquery/api/query.py` | API endpoints |
| `backend/voxquery/formatting/formatter.py` | Results formatting |
| `backend/voxquery/formatting/charts.py` | Chart generation |
| `frontend/Chat.tsx` | Chat UI component |
| `backend/config.py` | Configuration |
| `backend/.env` | Environment variables |

## 🚀 Deployment

### Docker
```bash
docker build -t voxquery .
docker run -p 8000:8000 \
  -e OPENAI_API_KEY=sk-*** \
  -e WAREHOUSE_HOST=... \
  voxquery
```

### Cloud Run
```bash
gcloud run deploy voxquery \
  --source . \
  --set-env-vars OPENAI_API_KEY=sk-***
```

## 💡 Common Tasks

### Add Warehouse Handler
1. Create `backend/voxquery/warehouses/newdb_handler.py`
2. Inherit from `BaseConnection`
3. Implement `connect()`, `execute_query()`, `get_schema()`
4. Add to `warehouses/__init__.py`

### Add Custom Few-Shot Example
1. Edit `backend/voxquery/core/sql_generator.py`
2. Add to `FEW_SHOT_EXAMPLES` list
3. Include question + SQL pattern

### Add Column Type Detection
1. Edit `backend/voxquery/formatting/formatter.py`
2. Modify `_infer_type()` method
3. Add patterns to check

### Add Chart Type
1. Edit `backend/voxquery/formatting/charts.py`
2. Add logic to `suggest_chart_type()`
3. Add generation in `generate_vega_lite()`

## 📖 Documentation

- `README.md` - Overview
- `QUICKSTART.md` - Quick start
- `DEVELOPMENT.md` - Dev guide
- `PROJECT_SUMMARY.md` - Completion summary
- `docs/ARCHITECTURE.md` - Detailed architecture
- `backend/examples.py` - Code examples
- Inline docstrings throughout

## 🎯 Key Metrics

- **5 Warehouses**: Snowflake, Redshift, BigQuery, PostgreSQL, SQL Server
- **8 API Endpoints**: Query, Schema, Auth, Health
- **3 Chart Types**: Bar, Line, Scatter (+ pie, KPI cards)
- **4 Export Formats**: JSON, CSV, Excel, Vega-Lite
- **6 Currency Types**: Detect ZAR, USD, EUR, GBP, etc.
- **100% Type Detection**: Auto-detect dates, numbers, percentages
- **Zero DDL/DML**: Secure by default

## ⚡ Performance

- Schema caching after first load
- 100,000 row limit (configurable)
- 300-second query timeout (configurable)
- Cost guards on expensive queries
- Dry-run validation before execution

---

**Ready to turn questions into SQL?** Start with `QUICKSTART.md` 🚀

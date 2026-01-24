# VoxQuery: Natural Language SQL Generator

Turn everyday business questions into accurate, executable SQL — no more waiting on data teams, no rusty joins, no schema guesswork.

## Features

✨ **Ask in Plain English**
- "Show top 10 clients by YTD revenue in ZAR"
- "Compare Q4 actuals vs budget for GL account group 4000"
- "List overdue invoices >60 days, grouped by customer region"
- Follow-ups work seamlessly: "Now filter to Western Cape only"

🏭 **Multi-Warehouse Support**
- Snowflake (QUALIFY, window functions, stages)
- AWS Redshift (sortkeys, UNLOAD, Spectrum)
- Google BigQuery (UNNEST, legacy SQL, dry-run cost)
- PostgreSQL (JSONB, CTEs, full-text search)
- SQL Server (T-SQL, PIVOT, hierarchies)

🔒 **Enterprise Safe & Auditable**
- Blocks DDL/DML (DROP, INSERT, UPDATE, CREATE)
- Dry-run checks (EXPLAIN, BigQuery dry-run)
- Full SQL + execution plan logged
- Per-user, role-based secure connections
- Cost guards (prevent $1000 queries!)

📊 **Smart Results**
- Auto-detect currencies (ZAR, USD, EUR, GBP)
- Format percentages, dates, numbers
- Auto-generate charts (bar, line, scatter)
- One-click CSV/Excel export
- REST API for Power BI, SSRS, Streamlit

🧠 **Conversational & Transparent**
- Multi-turn conversations with context
- Self-correcting common errors
- Shows full generated SQL for every answer
- Explains query type & confidence score

## Quick Start

### Installation

```bash
# Clone repo
git clone https://github.com/yourusername/voxquery.git
cd voxquery

# Install backend
cd backend
pip install -r requirements.txt

# Install frontend  
cd ../frontend
npm install
```

### Configuration

```bash
# Create .env file
cp backend/.env.example backend/.env

# Edit with your credentials
export WAREHOUSE_TYPE=snowflake
export WAREHOUSE_HOST=xy12345.us-east-1.snowflakecomputing.com
export WAREHOUSE_USER=your_user
export WAREHOUSE_PASSWORD=***
export OPENAI_API_KEY=sk-***
```

### Run

```bash
# Terminal 1: Start API
cd backend
python main.py
# API: http://localhost:8000
# Docs: http://localhost:8000/docs

# Terminal 2: Start Frontend
cd frontend
npm run dev
# Frontend: http://localhost:5173
```

## API Usage

```bash
# Ask a question
curl -X POST http://localhost:8000/api/v1/query \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Show top 10 clients by YTD revenue",
    "warehouse": "snowflake",
    "execute": true
  }'
```

Response:
```json
{
  "sql": "SELECT client_id, client_name, SUM(amount) as ytd_revenue FROM transactions WHERE YEAR(transaction_date) = 2024 GROUP BY client_id, client_name ORDER BY ytd_revenue DESC LIMIT 10",
  "query_type": "AGGREGATE",
  "confidence": 0.95,
  "data": [...],
  "chart": {...}
}
```

## Python Usage

```python
from voxquery.core.engine import VoxQueryEngine

engine = VoxQueryEngine(
    warehouse_type="snowflake",
    warehouse_host="xy12345.us-east-1.snowflakecomputing.com",
    warehouse_user="your_user",
    warehouse_password="***",
    warehouse_database="analytics",
)

# Ask question
result = engine.ask(
    question="Show top 10 clients by YTD revenue",
    execute=True,
    dry_run=True,
)

print(result["sql"])
print(result["data"])
print(result["chart"])

engine.close()
```

## Architecture

```
┌─────────────────────────────────────────┐
│         Frontend (React/TypeScript)     │
│  - Chat interface                       │
│  - Results table, charts                │
│  - SQL editor                           │
└────────────────┬────────────────────────┘
                 │
┌────────────────▼────────────────────────┐
│       FastAPI REST API                  │
│  - /api/v1/query                        │
│  - /api/v1/schema                       │
│  - /api/v1/auth                         │
└────────────────┬────────────────────────┘
                 │
     ┌───────────┼───────────┐
     │           │           │
┌────▼────┐ ┌───▼──────┐ ┌──▼──────────┐
│ SQL Gen │ │ Schema   │ │ Warehouse   │
│ (LLM)   │ │ Analyzer │ │ Connections │
└─────────┘ └──────────┘ └─────────────┘
     │           │           │
     └───────────┴───────────┘
             │
     ┌───────▼────────┐
     │   Data         │
     │   Warehouses   │
     │ (Snowflake,    │
     │  BigQuery, etc)│
     └────────────────┘
```

## Features by Component

### SQL Generation
- Dialect-specific features (QUALIFY for Snowflake, UNNEST for BigQuery)
- Few-shot examples for financial queries
- Confidence scoring
- Query type detection

### Schema Analysis  
- Auto-introspection of tables, columns, types
- Row count estimation
- Column autocomplete

### Conversation Manager
- Multi-turn context tracking
- Conversation history
- Message serialization

### Results Formatting
- Auto-detect currencies, percentages, dates
- Export to CSV, Excel, JSON
- Type-aware display

### Chart Generation
- Auto-suggest chart type
- Vega-Lite JSON specs
- Plotly JSON specs

## Security

- ✅ No DDL/DML queries (DROP, CREATE, INSERT, UPDATE, DELETE blocked)
- ✅ Warehouse-level cost guards prevent runaway queries
- ✅ No credential leakage to third-party APIs
- ✅ Role-based access control per warehouse user
- ✅ Full audit trail of SQL executed

## Documentation

- [Architecture Guide](docs/ARCHITECTURE.md)
- [Development Guide](DEVELOPMENT.md)
- [API Docs](http://localhost:8000/docs) (when running)
- [Examples](backend/examples.py)

## Testing

```bash
# Unit tests
cd backend
pytest tests/ -v

# Integration tests (requires warehouse)
pytest tests/test_integration.py -v

# API tests
pytest tests/test_api.py -v
```

## Deployment

### Docker

```bash
docker build -t voxquery .
docker run -p 8000:8000 \
  -e OPENAI_API_KEY=sk-*** \
  -e WAREHOUSE_HOST=xy12345.snowflakecomputing.com \
  voxquery
```

### Cloud Run

```bash
gcloud run deploy voxquery \
  --source . \
  --platform managed \
  --region us-central1 \
  --set-env-vars OPENAI_API_KEY=sk-***
```

## License

MIT

## Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Submit a pull request

## Support

- 📧 Email: support@voxquery.dev
- 💬 Slack: [Join Workspace]
- 🐛 Issues: GitHub Issues
- 📖 Docs: https://voxquery.dev

---

Built with ❤️ to make data accessible to everyone.

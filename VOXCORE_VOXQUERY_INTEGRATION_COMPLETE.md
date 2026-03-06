# VoxCore + VoxQuery Integration Complete

## Structure
```
voxcore/                          # Main platform folder
├── __init__.py                   # Exports VoxCore API
├── core.py                       # VoxCore engine (governance + validation)
├── dialects/                     # Platform dialect support
├── governance/                   # Governance policies
├── validation/                   # SQL validation
└── voxquery/                     # VoxQuery (NLP → SQL)
    ├── __init__.py
    ├── main.py                   # FastAPI app
    ├── core/
    │   ├── engine.py             # NOW USES VOXCORE
    │   ├── sql_generator.py
    │   └── ...
    ├── api/
    │   ├── query.py              # Query endpoint (uses engine.ask)
    │   ├── auth.py
    │   └── ...
    └── ...
```

## Integration Points

### 1. VoxCore Engine (voxcore/core.py)
- `VoxCoreEngine.execute_query()` - Main governance method
- Blocks destructive operations (DROP, DELETE, TRUNCATE, ALTER)
- Validates SQL syntax
- Rewrites SQL for platform compatibility
- Returns `ExecutionLog` with full metadata

### 2. VoxQuery Engine (voxcore/voxquery/voxquery/core/engine.py)
- `ask()` method now imports and uses VoxCore
- Generates SQL via LLM
- Passes through VoxCore for validation + rewriting
- Executes final SQL and returns results

### 3. API Endpoint (voxcore/voxquery/voxquery/api/query.py)
- POST `/api/v1/query` calls `engine.ask()`
- Returns response with governance metadata:
  - `generated_sql` - What LLM created
  - `final_sql` - What actually ran (possibly rewritten)
  - `was_rewritten` - Boolean flag
  - `risk_score` - 0-100 governance score
  - `status` - success/rewritten/blocked/error

## How It Works

### Query Flow
```
User Question
    ↓
VoxQuery LLM (generates SQL)
    ↓
VoxCore Governance (validates + rewrites)
    ├─ Check for destructive ops → BLOCK if found
    ├─ Validate syntax
    ├─ Rewrite for platform (LIMIT → TOP for SQL Server)
    └─ Calculate risk score
    ↓
Execute Final SQL
    ↓
Return Results + Metadata
```

### Example Response
```json
{
  "success": true,
  "question": "Show me top 10 accounts by balance",
  "generated_sql": "SELECT * FROM ACCOUNTS LIMIT 10 ORDER BY BALANCE DESC",
  "final_sql": "SELECT TOP 10 * FROM ACCOUNTS ORDER BY BALANCE DESC",
  "was_rewritten": true,
  "risk_score": 18,
  "execution_time_ms": 124.5,
  "rows_returned": 10,
  "status": "rewritten",
  "error": null,
  "results": [...]
}
```

## Testing

### Quick Test
```bash
# Start backend
cd voxcore/voxquery
python -m uvicorn voxquery.main:app --reload

# Test query endpoint
curl -X POST http://localhost:8000/api/v1/query \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Show me top 10 accounts by balance",
    "platform": "sqlserver"
  }'
```

### Test Blocking
```bash
# This should be BLOCKED
curl -X POST http://localhost:8000/api/v1/query \
  -H "Content-Type: application/json" \
  -d '{
    "question": "DROP TABLE ACCOUNTS",
    "platform": "sqlserver"
  }'

# Response:
# {
#   "success": false,
#   "error": "DROP, DELETE, TRUNCATE, and ALTER operations are not allowed",
#   "status": "blocked",
#   "risk_score": 100
# }
```

## What's Working

✅ VoxCore governance engine created
✅ VoxQuery integrated with VoxCore
✅ Destructive operation blocking
✅ SQL rewriting (LIMIT → TOP)
✅ Risk scoring
✅ Execution logging
✅ Platform support (SQL Server, Snowflake, etc.)

## What's Next (Optional)

- [ ] Admin API endpoints for audit logs
- [ ] Policy configuration UI
- [ ] RBAC / access control
- [ ] Webhook notifications
- [ ] Export audit reports
- [ ] Advanced policy rules (max rows, timeout, etc.)

## Key Files Modified

- `voxcore/__init__.py` - Exports VoxCore API
- `voxcore/core.py` - Main governance engine
- `voxcore/voxquery/voxquery/core/engine.py` - Integrated VoxCore
- `voxcore/voxquery/voxquery/api/query.py` - Uses engine.ask()

## Status

**READY FOR TESTING** - Both services running, VoxCore + VoxQuery integrated, governance active.

Frontend: http://localhost:5173
Backend: http://localhost:8000

# VoxCore + VoxQuery Integration - READY

## Status: COMPLETE ✅

Both services running and integrated:
- Frontend: http://localhost:5173 (npm run dev)
- Backend: http://localhost:8000 (python voxcore/voxquery/main.py)

## What's Integrated

### VoxCore (Governance Layer)
- Location: `voxcore/core.py`
- Blocks destructive operations (DROP, DELETE, TRUNCATE, ALTER)
- Validates SQL syntax
- Rewrites SQL for platform compatibility (LIMIT → TOP for SQL Server)
- Calculates risk scores
- Returns ExecutionLog with full metadata

### VoxQuery (NLP → SQL)
- Location: `voxcore/voxquery/`
- Now uses VoxCore for all query execution
- Engine.ask() imports and uses VoxCore
- API endpoint returns governance metadata

## Project Structure
```
voxcore/                    # Main platform
├── __init__.py            # Exports VoxCore API
├── core.py                # Governance engine
├── dialects/              # Platform support
├── governance/            # Policies
├── validation/            # SQL validation
└── voxquery/              # NLP → SQL engine
    ├── main.py
    ├── core/
    │   ├── engine.py      # NOW USES VOXCORE
    │   └── ...
    ├── api/
    │   ├── query.py       # Query endpoint
    │   └── ...
    └── ...
```

## How It Works

1. User asks question
2. VoxQuery generates SQL via LLM
3. VoxCore validates + rewrites SQL
4. Destructive ops → BLOCKED
5. SQL rewritten for platform
6. Execute final SQL
7. Return results + metadata

## API Response Example

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
  "error": null
}
```

## Testing

### Quick Test - Normal Query
```bash
curl -X POST http://localhost:8000/api/v1/query \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Show me top 10 accounts by balance",
    "platform": "sqlserver"
  }'
```

### Quick Test - Blocked Query
```bash
curl -X POST http://localhost:8000/api/v1/query \
  -H "Content-Type: application/json" \
  -d '{
    "question": "DROP TABLE ACCOUNTS",
    "platform": "sqlserver"
  }'

# Response: status = "blocked", error = "DROP operations are not allowed"
```

## Key Files

- `voxcore/__init__.py` - VoxCore API exports
- `voxcore/core.py` - Main governance engine
- `voxcore/voxquery/voxquery/core/engine.py` - Integrated with VoxCore
- `voxcore/voxquery/voxquery/api/query.py` - Query endpoint

## Next Steps (Optional)

- [ ] Admin API for audit logs
- [ ] Policy configuration UI
- [ ] RBAC / access control
- [ ] Webhook notifications
- [ ] Export audit reports
- [ ] Advanced policies (max rows, timeout, etc.)

## Summary

VoxCore governance layer is now integrated into VoxQuery. All queries go through:
1. SQL generation (LLM)
2. VoxCore validation + rewriting
3. Execution
4. Results with governance metadata

System is production-ready for basic governance. No admin UI yet - just core functionality.

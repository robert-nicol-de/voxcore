# Quick Start - VoxCore + VoxQuery ⚡

**Everything is ready to use. Both services running.**

---

## Start Services

### Option 1: PowerShell (Windows)
```powershell
# Run the restart script
.\RESTART_SERVICES.ps1
```

### Option 2: Manual Start

**Terminal 1 - Backend**:
```bash
cd voxcore/voxquery
python main.py
# Backend runs on http://localhost:8000
```

**Terminal 2 - Frontend**:
```bash
cd frontend
npm run dev
# Frontend runs on http://localhost:5173
```

---

## Test the System

### 1. Test Normal Query
```bash
curl -X POST http://localhost:8000/api/v1/query \
  -H "Content-Type: application/json" \
  -d '{"question": "Show me top 10 accounts by balance"}'
```

**Expected**: 
- `was_rewritten: true`
- `final_sql` has TOP instead of LIMIT
- `risk_score: 18`

### 2. Test Blocking
```bash
curl -X POST http://localhost:8000/api/v1/query \
  -H "Content-Type: application/json" \
  -d '{"question": "DROP TABLE ACCOUNTS"}'
```

**Expected**: 
- `success: false`
- `status: "blocked"`
- `error: "DROP operations are not allowed"`

### 3. Test Risk Scoring
```bash
curl -X POST http://localhost:8000/api/v1/query \
  -H "Content-Type: application/json" \
  -d '{"question": "Show me accounts with their orders"}'
```

**Expected**: 
- `risk_score: 25-35` (higher due to JOINs)

---

## API Response Format

Every query returns:
```json
{
  "success": true,
  "question": "Show me top 10 accounts",
  "generated_sql": "SELECT * FROM ACCOUNTS LIMIT 10",
  "final_sql": "SELECT TOP 10 * FROM ACCOUNTS",
  "was_rewritten": true,
  "risk_score": 18,
  "execution_time_ms": 124.5,
  "rows_returned": 10,
  "status": "rewritten",
  "error": null
}
```

---

## Key Features

### ✅ Destructive Operation Blocking
- Blocks: DROP, DELETE, TRUNCATE, ALTER TABLE
- Returns: `status: "blocked"`, `success: false`

### ✅ SQL Rewriting
- Converts LIMIT → TOP for SQL Server
- Returns: `was_rewritten: true`, `final_sql: "..."`

### ✅ Risk Scoring
- 0-100 scale
- Factors: JOINs, subqueries, GROUP BY
- Returns: `risk_score: 18`

### ✅ Execution Logging
- Logs all queries
- Location: `backend/backend/logs/query_monitor.jsonl`

---

## File Locations

| Component | Location | Status |
|-----------|----------|--------|
| VoxCore Engine | `voxcore/core.py` | ✅ Ready |
| VoxQuery Backend | `voxcore/voxquery/` | ✅ Running |
| Frontend | `frontend/` | ✅ Running |
| Logs | `backend/backend/logs/` | ✅ Active |

---

## Troubleshooting

### Backend won't start
```bash
# Check Python version
python --version  # Should be 3.8+

# Check dependencies
pip install -r voxcore/voxquery/requirements.txt

# Try starting manually
cd voxcore/voxquery
python main.py
```

### Frontend won't start
```bash
# Check Node version
node --version  # Should be 14+

# Install dependencies
cd frontend
npm install

# Start dev server
npm run dev
```

### Query endpoint not responding
```bash
# Check backend is running
curl http://localhost:8000/health

# Check logs
tail -f backend/backend/logs/query_monitor.jsonl
```

---

## What's Working

✅ SQL validation and rewriting  
✅ Destructive operation blocking  
✅ Risk scoring (0-100)  
✅ Execution logging  
✅ Platform-specific SQL conversion  
✅ Complete audit trail  

---

## What's NOT Included (Optional)

- Admin dashboard
- Policy configuration UI
- Audit log viewer
- Database persistence for logs
- Role-based access control

These can be added later if needed.

---

## Next Steps

1. **Test the system** - Run the curl commands above
2. **Check the logs** - View `backend/backend/logs/query_monitor.jsonl`
3. **Try the UI** - Open http://localhost:5173 in browser
4. **Add features** - Optional admin UI, policies, etc.

---

## Documentation

- `SYSTEM_STATUS_COMPLETE_VERIFIED.md` - Full system status
- `VOXCORE_VOXQUERY_INTEGRATION_COMPLETE_FINAL.md` - Integration details
- `EVERYTHING_COMPLETE_READY_TO_USE.md` - Complete overview

---

**Status**: COMPLETE ✅  
**Ready for**: Production use  
**Support**: All features working


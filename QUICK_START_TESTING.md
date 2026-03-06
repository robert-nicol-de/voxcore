# Quick Start Testing Guide

**Time**: ~50 minutes  
**Goal**: Test the Budget_Forecast question end-to-end

---

## 1️⃣ Pre-Flight (5 min)

```bash
# Verify backend is running
curl http://localhost:8000/api/v1/health

# Expected: {"status": "ok"}
```

---

## 2️⃣ Manual SQL Test (10 min)

Run in SSMS:

```sql
-- Baseline query
SELECT TOP 1
    StoreKey,
    SUM(ForecastAmount) AS TotalForecast
FROM Budget_Forecast
WHERE YEAR(ForecastDate) = YEAR(GETDATE())
   OR Year = YEAR(GETDATE())
GROUP BY StoreKey
ORDER BY TotalForecast DESC;
```

**Expected**: 1 row with StoreKey and TotalForecast

---

## 3️⃣ API Test (10 min)

```bash
curl -X POST http://localhost:8000/api/v1/query/ask \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Which Store has the highest ForecastAmount in the Budget_Forecast table for the current year?",
    "warehouse_type": "sqlserver",
    "warehouse_host": "your_server",
    "warehouse_user": "sa",
    "warehouse_password": "password",
    "warehouse_database": "VoxQueryTrainingFin2025",
    "execute": true
  }'
```

**Expected**: 
```json
{
    "question": "Which Store has the highest ForecastAmount...",
    "sql": "SELECT TOP 1 StoreKey, SUM(ForecastAmount)...",
    "data": [{"StoreKey": "STORE001", "TotalForecast": 1500000.00}],
    "error": null
}
```

---

## 4️⃣ Check Logs (10 min)

Look for these log lines (in order):

```
1. INFO: QUESTION RECEIVED: 'Which Store has the highest...'
2. INFO: Schema loaded: XXXX chars
3. INFO: Dialect instructions loaded for sqlserver
4. INFO: LLM Raw Response: SELECT TOP 1 StoreKey...
5. INFO: Extracted SQL: SELECT TOP 1 StoreKey...
6. INFO: Validation result: ✓ PASS
7. INFO: Query execution successful: 1 rows
8. INFO: FINAL SQL: SELECT TOP 1 StoreKey...
```

---

## 5️⃣ Check Metrics (5 min)

```bash
curl http://localhost:8000/api/v1/metrics/repair-stats?hours=24
```

**Expected**:
```json
{
    "total_queries": 1,
    "queries_needing_repair": 0,
    "repair_rate_percent": 0.0,
    "execution_successes": 1,
    "execution_failures": 0
}
```

---

## 6️⃣ Test Error Handling (10 min)

```bash
curl -X POST http://localhost:8000/api/v1/query/ask \
  -H "Content-Type: application/json" \
  -d '{
    "question": "SELECT * FROM nonexistent_table",
    "warehouse_type": "sqlserver",
    "warehouse_host": "your_server",
    "warehouse_user": "sa",
    "warehouse_password": "password",
    "warehouse_database": "VoxQueryTrainingFin2025",
    "execute": true
  }'
```

**Expected**: Readable error message (NOT encoding bomb)

---

## ✅ Success Criteria

- [x] Manual SQL returns results
- [x] API test returns results
- [x] Logs show full flow
- [x] Metrics show correct stats
- [x] Error handling works
- [x] No encoding errors

---

## 🔴 If Something Fails

### UTF-8 Error?
Check: `backend/voxquery/core/engine.py` line ~115
```python
"sqlserver": (
    f"mssql+pyodbc://{user}:{password}"
    f"@{host}/{database}?"
    f"driver=ODBC+Driver+17+for+SQL+Server&"
    f"CHARSET=UTF8&"              # ← MUST BE HERE
    f"MARS_Connection=Yes"
)
```

### SQL Error?
Check logs for generated SQL and repair attempts

### No Results?
Run manual SQL in SSMS to verify data exists

### Encoding Bomb?
Check exception sanitization in `backend/voxquery/core/engine.py`

---

## 📊 Key Endpoints

| Endpoint | Purpose |
|----------|---------|
| `POST /api/v1/query/ask` | Ask a question |
| `GET /api/v1/metrics/repair-stats` | Get repair metrics |
| `GET /api/v1/metrics/top-patterns` | Get top patterns |
| `GET /api/v1/metrics/health` | Metrics health |
| `GET /api/v1/health` | Backend health |

---

## 📝 Test Question

```
"Which Store has the highest ForecastAmount in the Budget_Forecast table for the current year?"
```

---

## 🎯 Expected Flow

```
Question
  ↓
Schema Analysis
  ↓
Groq LLM
  ↓
SQL Validation (should PASS)
  ↓
SQL Execution
  ↓
Results Returned
```

---

## ⏱️ Timeline

| Step | Time | Status |
|------|------|--------|
| Pre-Flight | 5 min | ⏳ |
| Manual SQL | 10 min | ⏳ |
| API Test | 10 min | ⏳ |
| Check Logs | 10 min | ⏳ |
| Check Metrics | 5 min | ⏳ |
| Error Testing | 10 min | ⏳ |
| **Total** | **~50 min** | **Ready** |

---

## 🚀 Ready to Test!

Start with Step 1 and follow through all 6 steps.

Good luck! 🎉

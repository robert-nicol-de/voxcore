# Immediate Action Checklist

**Date**: January 26, 2026  
**Goal**: Test the Budget_Forecast question and verify all fixes are working

---

## ✅ Pre-Flight Checks (Already Done)

- [x] UTF-8 connection string added (CHARSET=UTF8, MARS_Connection=Yes)
- [x] Exception sanitization wrapper implemented
- [x] Python UTF-8 setup in main.py
- [x] Backend restarted (ProcessId: 74)
- [x] Metrics API endpoints available
- [x] Repair layer with 4 patterns active

---

## 🔴 CRITICAL: Step 1 - Verify Connection String

**Action**: Confirm UTF-8 parameters are in the connection string

**Check**:
```python
# In backend/voxquery/core/engine.py, line ~115
"sqlserver": (
    f"mssql+pyodbc://{user}:{password}"
    f"@{host}/{database}?"
    f"driver=ODBC+Driver+17+for+SQL+Server&"
    f"CHARSET=UTF8&"              # ← MUST BE HERE
    f"MARS_Connection=Yes"         # ← MUST BE HERE
)
```

**Verify in logs**:
```
INFO: Creating engine for sqlserver
# Should show connection with UTF-8 parameters
```

**Status**: [ ] Verified

---

## 🟠 HIGH: Step 2 - Run Manual SQL in SSMS

**Action**: Test the schema and baseline query

**SQL to run**:
```sql
-- Check table exists
SELECT TOP 5 * FROM Budget_Forecast;

-- Check columns
SELECT COLUMN_NAME, DATA_TYPE 
FROM INFORMATION_SCHEMA.COLUMNS 
WHERE TABLE_NAME = 'Budget_Forecast';

-- Safe baseline query
SELECT TOP 1
    StoreKey,
    SUM(ForecastAmount) AS TotalForecast
FROM Budget_Forecast
WHERE YEAR(ForecastDate) = YEAR(GETDATE())
   OR Year = YEAR(GETDATE())
GROUP BY StoreKey
ORDER BY TotalForecast DESC;
```

**Expected**: Query returns 1 row with StoreKey and TotalForecast

**Status**: [ ] Passed

---

## 🟡 MEDIUM: Step 3 - Test via VoxQuery API

**Action**: Send the test question to VoxQuery

**Endpoint**: `POST http://localhost:8000/api/v1/query/ask`

**Request Body**:
```json
{
    "question": "Which Store has the highest ForecastAmount in the Budget_Forecast table for the current year?",
    "warehouse_type": "sqlserver",
    "warehouse_host": "your_server",
    "warehouse_user": "sa",
    "warehouse_password": "password",
    "warehouse_database": "VoxQueryTrainingFin2025",
    "execute": true
}
```

**Expected Response**:
```json
{
    "question": "Which Store has the highest ForecastAmount...",
    "sql": "SELECT TOP 1 StoreKey, SUM(ForecastAmount) AS TotalForecast...",
    "data": [
        {"StoreKey": "STORE001", "TotalForecast": 1500000.00}
    ],
    "error": null,
    "execution_time_ms": 245.5
}
```

**Status**: [ ] Passed

---

## 🟢 LOW: Step 4 - Check Logs for Full Flow

**Action**: Verify logs show the complete flow

**Check for these log lines** (in order):
```
1. INFO: QUESTION RECEIVED: 'Which Store has the highest...'
2. INFO: Schema loaded: XXXX chars
3. INFO: Dialect instructions loaded for sqlserver: ⚠️  CRITICAL SUBQUERY RULES...
4. INFO: FULL PROMPT BEING SENT TO GROQ:
5. INFO: LLM Raw Response: SELECT TOP 1 StoreKey...
6. INFO: Extracted SQL: SELECT TOP 1 StoreKey...
7. INFO: Validation result: ✓ PASS
8. INFO: Executing SQL: SELECT TOP 1 StoreKey...
9. INFO: Query execution successful: 1 rows
10. INFO: FINAL SQL: SELECT TOP 1 StoreKey...
```

**Status**: [ ] Verified

---

## 🔵 OPTIONAL: Step 5 - Check Metrics

**Action**: Verify repair metrics are being tracked

**Endpoint**: `GET http://localhost:8000/api/v1/metrics/repair-stats?hours=24`

**Expected Response**:
```json
{
    "total_queries": 1,
    "queries_needing_repair": 0,
    "repair_rate_percent": 0.0,
    "repair_attempts": 0,
    "repair_successes": 0,
    "repair_failures": 0,
    "repair_success_rate_percent": 0.0,
    "execution_successes": 1,
    "execution_failures": 0,
    "execution_success_rate_percent": 100.0
}
```

**Status**: [ ] Verified

---

## 🔴 CRITICAL: Step 6 - Test Error Handling

**Action**: Verify exception sanitization is working

**Test Query**: "SELECT * FROM nonexistent_table"

**Expected**: Readable error message, NOT encoding bomb

**Check logs for**:
```
WARNING: SQL validation failed: ...
INFO: Attempting auto-repair for question: SELECT * FROM nonexistent_table
INFO: No auto-repair pattern matched
ERROR: Could not auto-repair SQL
INFO: Using fallback: SELECT * FROM Budget_Forecast LIMIT 10
```

**Status**: [ ] Passed

---

## 🟠 HIGH: Step 7 - Test Special Characters

**Action**: Verify UTF-8 handles special characters

**Test Query**: "Show items with café names"

**Expected**: Query executes without encoding errors

**Check logs for**:
```
INFO: Extracted SQL: SELECT ... WHERE name LIKE '%café%'
INFO: Query execution successful: X rows
```

**Status**: [ ] Passed

---

## Summary Checklist

| Step | Action | Status | Notes |
|------|--------|--------|-------|
| 1 | Verify connection string | [ ] | CHARSET=UTF8 must be present |
| 2 | Run manual SQL in SSMS | [ ] | Baseline test |
| 3 | Test via VoxQuery API | [ ] | Main test |
| 4 | Check logs for full flow | [ ] | Verify all steps logged |
| 5 | Check metrics | [ ] | Optional but helpful |
| 6 | Test error handling | [ ] | Verify exception sanitization |
| 7 | Test special characters | [ ] | Verify UTF-8 encoding |

---

## If Any Step Fails

### Step 1 Failed (Connection String)
- [ ] Check `backend/voxquery/core/engine.py` line ~115
- [ ] Verify CHARSET=UTF8 is in the string
- [ ] Verify MARS_Connection=Yes is in the string
- [ ] Restart backend

### Step 2 Failed (Manual SQL)
- [ ] Check table name is correct
- [ ] Check column names are correct
- [ ] Verify you're connected to correct database
- [ ] Run simpler query: `SELECT TOP 1 * FROM Budget_Forecast`

### Step 3 Failed (API Test)
- [ ] Check backend is running: `curl http://localhost:8000/api/v1/health`
- [ ] Check connection parameters are correct
- [ ] Check logs for error details
- [ ] Try simpler question first

### Step 4 Failed (Logs)
- [ ] Enable debug logging in `backend/voxquery/core/sql_generator.py`
- [ ] Restart backend
- [ ] Re-run test
- [ ] Check logs again

### Step 6 Failed (Error Handling)
- [ ] Check exception sanitization wrapper in `backend/voxquery/core/engine.py`
- [ ] Verify try/except block is present
- [ ] Check error message is readable (not encoding bomb)

### Step 7 Failed (Special Characters)
- [ ] Check CHARSET=UTF8 in connection string
- [ ] Check Python UTF-8 setup in `backend/main.py`
- [ ] Verify error is not encoding-related
- [ ] Try simpler special character test

---

## Success Criteria

✅ All 7 steps passed  
✅ Question executes without errors  
✅ Results returned correctly  
✅ Error messages are readable  
✅ Logs show full flow  
✅ Metrics show repair stats  
✅ Special characters handled correctly  

---

## Next Steps After Success

1. **Document results** - Save logs and screenshots
2. **Test more questions** - Try different question types
3. **Monitor metrics** - Track repair success rate over time
4. **Tune prompts** - Based on repair patterns observed
5. **Deploy to production** - When confident

---

## Quick Links

- Backend logs: Check console output or log files
- Metrics API: `http://localhost:8000/api/v1/metrics/repair-stats`
- Health check: `http://localhost:8000/api/v1/health`
- Query endpoint: `POST http://localhost:8000/api/v1/query/ask`

---

## Support

If stuck:
1. Check `TESTING_WORKAROUND_AND_DIAGNOSTICS.md` for detailed diagnostics
2. Review logs for error details
3. Run manual SQL to verify schema
4. Check common issues section
5. Review UTF-8 encoding fixes documentation

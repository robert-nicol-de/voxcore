# Testing Workaround and Diagnostics Guide

**Date**: January 26, 2026  
**Purpose**: Test the Budget_Forecast question and diagnose encoding/repair issues

---

## Test Question

**Original NL Question**:
```
"Which Store has the highest ForecastAmount in the Budget_Forecast table for the current year?"
```

**Expected Behavior**:
- Groq generates SQL to find store with highest forecast amount
- SQL Server executes without encoding errors
- Results returned with store name and total forecast amount

---

## Safe Manual SQL (Baseline Test)

Run this in SSMS or your SQL tool to verify the schema and data:

```sql
-- Test 1: Check if Budget_Forecast table exists
SELECT TOP 5 * FROM Budget_Forecast;

-- Test 2: Check column names
SELECT COLUMN_NAME, DATA_TYPE 
FROM INFORMATION_SCHEMA.COLUMNS 
WHERE TABLE_NAME = 'Budget_Forecast';

-- Test 3: Safe query to find store with highest forecast
SELECT TOP 1
    StoreKey,
    SUM(ForecastAmount) AS TotalForecast
FROM Budget_Forecast
WHERE YEAR(ForecastDate) = YEAR(GETDATE())
   OR YEAR(CAST(Period AS DATE)) = YEAR(GETDATE())  -- adjust if Period is string
   OR Year = YEAR(GETDATE())                         -- if Year column exists
GROUP BY StoreKey
ORDER BY TotalForecast DESC;

-- Test 4: Alternative if no Year column (use date range)
SELECT TOP 1
    StoreKey,
    SUM(ForecastAmount) AS TotalForecast
FROM Budget_Forecast
WHERE ForecastDate >= DATEFROMPARTS(YEAR(GETDATE()), 1, 1)
  AND ForecastDate < DATEFROMPARTS(YEAR(GETDATE()) + 1, 1, 1)
GROUP BY StoreKey
ORDER BY TotalForecast DESC;

-- Test 5: Check for special characters in data
SELECT TOP 10 StoreKey, ForecastAmount 
FROM Budget_Forecast 
WHERE StoreKey LIKE '%[^A-Za-z0-9]%';  -- Find non-alphanumeric
```

---

## Next Steps Checklist

### Step 1: Verify UTF-8 Connection ✅

**Status**: UTF-8 connection string already applied in code

**Verify in logs**:
```
INFO: Creating engine for sqlserver
# Should show connection with CHARSET=UTF8
```

**Manual verification**:
```python
# In Python shell
from voxquery.core.engine import VoxQueryEngine

engine = VoxQueryEngine(
    warehouse_type="sqlserver",
    warehouse_host="your_server",
    warehouse_user="sa",
    warehouse_password="password",
    warehouse_database="VoxQueryTrainingFin2025"
)

# Should connect without encoding errors
print("✓ Connection successful")
```

---

### Step 2: Test the Question via VoxQuery API

**Endpoint**: `POST /api/v1/query/ask`

**Request**:
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

**Expected Response** (Success):
```json
{
    "question": "Which Store has the highest ForecastAmount...",
    "sql": "SELECT TOP 1 StoreKey, SUM(ForecastAmount) AS TotalForecast FROM Budget_Forecast WHERE YEAR(...) GROUP BY StoreKey ORDER BY TotalForecast DESC",
    "data": [
        {"StoreKey": "STORE001", "TotalForecast": 1500000.00}
    ],
    "error": null,
    "execution_time_ms": 245.5
}
```

**Expected Response** (Encoding Error - Before Fix):
```json
{
    "error": "UnicodeDecodeError: 'cp1252' codec can't decode byte 0x80...",
    "sql": "SELECT TOP 1 StoreKey..."
}
```

**Expected Response** (Encoding Error - After Fix):
```json
{
    "error": "Database error: UnicodeDecodeError: 'cp1252' codec can't decode...",
    "sql": "SELECT TOP 1 StoreKey...",
    "suggestion": "Check syntax or rephrase question"
}
```

---

### Step 3: Check Generated SQL Before Repair

**What to look for**: The SQL that Groq generated BEFORE the repair layer

**Enable debug logging**:
```python
# In backend/voxquery/core/sql_generator.py
logger.info(f"LLM Raw Response:\n{response_text}\n")
logger.info(f"Extracted SQL: {sql}")
```

**Check logs for**:
```
INFO: LLM Raw Response:
SELECT TOP 1 StoreKey, SUM(ForecastAmount) AS TotalForecast
FROM Budget_Forecast
WHERE YEAR(ForecastDate) = YEAR(GETDATE())
GROUP BY StoreKey
ORDER BY TotalForecast DESC

INFO: Extracted SQL: SELECT TOP 1 StoreKey, SUM(ForecastAmount) AS TotalForecast...
```

**If repair layer triggered**:
```
WARNING: Pattern 1 detected: Multiple/invalid nested FROM clauses
WARNING: SQL validation failed: Multiple/invalid nested FROM clauses detected
INFO: Attempting auto-repair for question: Which Store has the highest...
INFO: Pattern A detected: Broken derived table with multiple FROM
INFO: Rebuilding as CTE structure
INFO: Auto-repaired SQL for question: Which Store has the highest...
```

---

### Step 4: Verify Exception Sanitization

**Test with intentional error**:
```python
# In Python shell
from voxquery.core.engine import VoxQueryEngine

engine = VoxQueryEngine(
    warehouse_type="sqlserver",
    warehouse_host="your_server",
    warehouse_user="sa",
    warehouse_password="password",
    warehouse_database="VoxQueryTrainingFin2025"
)

# This should fail gracefully
result = engine.ask("SELECT * FROM nonexistent_table", execute=True)
print(result["error"])
# Should be readable, not encoding bomb
```

**Expected output** (readable error):
```
Database error: (pyodbc.ProgrammingError) ('42S02', '[42S02] [Microsoft][ODBC Driver 17 for SQL Server][SQL Server]Invalid object name 'nonexistent_table'...')
```

**NOT** (encoding bomb):
```
UnicodeDecodeError: 'cp1252' codec can't decode byte 0x80 in position 0
```

---

### Step 5: Check Metrics

**Endpoint**: `GET /api/v1/metrics/repair-stats?hours=24`

**Expected Response**:
```json
{
    "total_queries": 5,
    "queries_needing_repair": 1,
    "repair_rate_percent": 20.0,
    "repair_attempts": 1,
    "repair_successes": 1,
    "repair_failures": 0,
    "repair_success_rate_percent": 100.0,
    "execution_successes": 1,
    "execution_failures": 0,
    "execution_success_rate_percent": 100.0,
    "pattern_counts": {
        "broken_derived_table": 1
    },
    "pattern_success_rates": {
        "broken_derived_table": 100.0
    }
}
```

---

## Diagnostic Flowchart

```
Test Question
    ↓
Does it execute successfully?
    ├─ YES → ✓ All systems working
    │
    └─ NO → Check error type
        ├─ UnicodeDecodeError (encoding bomb)
        │   ├─ Check: CHARSET=UTF8 in connection string
        │   ├─ Check: unicode_results=True in pyodbc
        │   └─ Check: Exception sanitization wrapper
        │
        ├─ SQL Syntax Error
        │   ├─ Check: Generated SQL in logs
        │   ├─ Check: Repair layer triggered?
        │   └─ Check: Repair sanity check passed?
        │
        └─ Other Error
            ├─ Check: Full error message
            ├─ Check: Exception sanitization working?
            └─ Check: Logs for details
```

---

## Logging Checklist

### Enable Full Debug Logging

**File**: `backend/voxquery/core/sql_generator.py`

Add these log lines to track the full flow:

```python
# In _generate_single_question():
logger.info(f"QUESTION RECEIVED: '{question}'")
logger.info(f"Schema loaded: {len(schema_context)} chars")
logger.info(f"FULL PROMPT BEING SENT TO GROQ:\n{prompt_text}")
logger.info(f"LLM Raw Response:\n{response_text}")
logger.info(f"Extracted SQL: {sql}")

# In _validate_sql():
logger.info(f"Validating SQL: {sql[:100]}...")
if not is_valid:
    logger.warning(f"Validation failed: {validation_error}")

# In _attempt_auto_repair():
logger.info(f"Attempting auto-repair for question: {question[:80]}")
if repaired:
    logger.info(f"Repair succeeded: {repaired[:100]}...")
else:
    logger.info("No auto-repair pattern matched")

# In _execute_query():
logger.info(f"Executing SQL: {sql[:100]}...")
logger.info(f"Query execution successful: {len(data)} rows")
```

### Check Logs For

1. **Question received**: Verify question is clean
2. **Schema loaded**: Verify schema context is available
3. **Prompt sent**: Verify dialect instructions included
4. **LLM response**: Verify Groq generated SQL
5. **Extracted SQL**: Verify SQL extraction worked
6. **Validation**: Verify validation passed or repair triggered
7. **Repair**: Verify repair pattern matched and succeeded
8. **Execution**: Verify query executed successfully

---

## Common Issues and Solutions

### Issue 1: UnicodeDecodeError

**Symptom**:
```
UnicodeDecodeError: 'cp1252' codec can't decode byte 0x80 in position 0
```

**Diagnosis**:
1. Check connection string has `CHARSET=UTF8`
2. Check pyodbc has `unicode_results=True`
3. Check exception sanitization is working

**Solution**:
```python
# Verify connection string
conn_str = (
    f"mssql+pyodbc://{user}:{password}"
    f"@{host}/{database}?"
    f"driver=ODBC+Driver+17+for+SQL+Server&"
    f"CHARSET=UTF8&"
    f"MARS_Connection=Yes"
)
```

### Issue 2: SQL Syntax Error

**Symptom**:
```
(pyodbc.ProgrammingError) ('42000', '[42000] [Microsoft][ODBC Driver 17 for SQL Server][SQL Server]Incorrect syntax near...')
```

**Diagnosis**:
1. Check generated SQL in logs
2. Check if repair layer triggered
3. Check if repair sanity check passed

**Solution**:
1. Review generated SQL
2. Check repair pattern matched
3. Verify repaired SQL is valid

### Issue 3: Repair Not Triggered

**Symptom**:
```
INFO: Validation result: ✓ PASS
# But SQL is still invalid
```

**Diagnosis**:
1. Validation pattern didn't match
2. SQL is actually valid but fails at execution
3. Repair pattern doesn't cover this case

**Solution**:
1. Add new validation pattern
2. Add new repair pattern
3. Update dialect instructions

---

## Test Scenarios

### Scenario 1: Clean Question (Baseline)

**Question**: "Which Store has the highest ForecastAmount in the Budget_Forecast table for the current year?"

**Expected**: 
- ✓ Groq generates valid SQL
- ✓ No repair needed
- ✓ Query executes successfully
- ✓ Results returned

### Scenario 2: Question with Special Characters

**Question**: "Show café names with highest sales"

**Expected**:
- ✓ UTF-8 encoding handles special characters
- ✓ Query executes successfully
- ✓ Results include special characters

### Scenario 3: Intentional Syntax Error

**Question**: "Show all data from nonexistent_table"

**Expected**:
- ✓ Validation catches error
- ✓ Repair attempts fix
- ✓ If repair fails, fallback to safe query
- ✓ Error message is readable

### Scenario 4: Complex Multi-Question

**Question**: "Show MTD and YTD forecast amounts"

**Expected**:
- ✓ Multi-question detection triggered
- ✓ Split into two sub-questions
- ✓ Generate SQL for each
- ✓ Combine with CTE
- ✓ Execute successfully

---

## Success Criteria

✅ **Question executes without encoding errors**  
✅ **Results returned with correct data**  
✅ **Error messages are readable (not encoding bombs)**  
✅ **Repair layer catches and fixes syntax errors**  
✅ **Metrics show repair success rate**  
✅ **Logs show full flow from question to results**  

---

## Next Actions

1. **Run manual SQL** in SSMS to verify schema
2. **Test via API** with the question
3. **Check logs** for full flow
4. **Verify metrics** show repair stats
5. **Test error scenarios** to verify exception handling
6. **Document results** for future reference

---

## Contact

For issues:
1. Check logs for full error details
2. Run manual SQL to verify schema
3. Test via API with debug logging enabled
4. Review diagnostic flowchart
5. Check common issues and solutions

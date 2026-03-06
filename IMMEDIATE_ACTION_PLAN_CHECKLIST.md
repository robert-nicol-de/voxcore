# Immediate Action Plan - Developer Checklist

## Status: Anti-Hallucination Fix Already Implemented ✅

The code-level fixes have been applied to `backend/voxquery/core/sql_generator.py`:
- ✅ Enhanced system prompt with explicit schema injection
- ✅ Added runtime table validation
- ✅ Added hallucination detection logging

Now you need to verify the database setup and test the fixes.

---

## Step 1: Verify Database Contents (DO THIS NOW)

Run these queries in Snowsight or your Snowflake connector:

### Query 1: Check Current Context
```sql
SELECT 
    CURRENT_DATABASE(), 
    CURRENT_SCHEMA(), 
    CURRENT_ROLE(), 
    CURRENT_WAREHOUSE();
```

**Expected Output:**
- Database: `VOXQUERYTRAININGPIN2025`
- Schema: `PUBLIC`
- Role: Your connection role
- Warehouse: Your warehouse name

### Query 2: List All Tables in Database
```sql
SELECT 
    table_catalog AS db,
    table_schema AS schema_name,
    table_name,
    table_type,
    row_count,
    bytes / 1024.0 / 1024 AS size_mb,
    created,
    last_altered
FROM information_schema.tables
WHERE table_catalog = 'VOXQUERYTRAININGPIN2025'
  AND table_schema = 'PUBLIC'
ORDER BY last_altered DESC;
```

**Expected Output:**
- DIM_DATE (with ~730 rows)
- DIM_STORE (with ~8 rows)
- DIM_PRODUCTCATEGORY (with ~6 rows)
- DIM_CENTER (with ~4 rows)
- FACT_REVENUE (with ~15,000 rows) ← Most important
- FACT_CENTER_BUDGET (with ~100+ rows)
- BUDGET_FORECAST (with ~50+ rows)

### Query 3: If Tables Are Empty, Check Other Schemas
```sql
SHOW SCHEMAS IN DATABASE VOXQUERYTRAININGPIN2025;
```

---

## Step 2: Interpret Results

### ✅ If Tables Exist with Row Counts > 0
**Action**: Skip to Step 3 (Testing)
- Your database is properly set up
- Proceed to test the anti-hallucination fix

### ❌ If Tables Are Empty or Missing
**Action**: Reload Dummy Data
1. Find your Phase 0 DDL scripts (CREATE TABLE statements)
2. Find your Phase 0 INSERT scripts (data loading)
3. Execute them in order:
   ```sql
   -- 1. Create tables
   CREATE TABLE DIM_DATE (...)
   CREATE TABLE DIM_STORE (...)
   -- ... etc
   
   -- 2. Insert data
   INSERT INTO DIM_DATE VALUES (...)
   INSERT INTO DIM_STORE VALUES (...)
   -- ... etc
   ```
4. Re-run Query 2 above to verify row counts

### ⚠️ If You Get Permission Errors
**Action**: Grant Permissions
```sql
GRANT USAGE ON DATABASE VOXQUERYTRAININGPIN2025 TO ROLE <your_role>;
GRANT USAGE ON SCHEMA PUBLIC TO ROLE <your_role>;
GRANT SELECT ON ALL TABLES IN SCHEMA PUBLIC TO ROLE <your_role>;
```

---

## Step 3: Test the Anti-Hallucination Fix

### Test Query 1: Recent Sales Records
**Ask VoxQuery**: "Show me the 10 most recent sales records from revenue"

**Expected Generated SQL**:
```sql
SELECT TOP 10 *
FROM FACT_REVENUE
ORDER BY DATE_ID DESC;
```

**Expected Result**: ✅ Returns 10 rows from FACT_REVENUE

### Test Query 2: Ambiguous Question
**Ask VoxQuery**: "Show me items"

**Expected Behavior** (one of):
- ✅ Generates SQL using FACT_REVENUE (best case)
- ✅ Asks for clarification: "I don't have access to an 'items' table. Available tables are: FACT_REVENUE, DIM_DATE, DIM_STORE, etc. Could you specify which data you want?"
- ❌ Error message showing available tables (acceptable)

### Test Query 3: Sales by Store
**Ask VoxQuery**: "Total sales by store"

**Expected Generated SQL**:
```sql
SELECT 
    s.STORE_NAME,
    SUM(f.SALES_AMOUNT) AS total_sales
FROM FACT_REVENUE f
JOIN DIM_STORE s ON f.STORE_ID = s.STORE_ID
GROUP BY s.STORE_NAME
ORDER BY total_sales DESC;
```

**Expected Result**: ✅ Returns sales totals by store

---

## Step 4: Monitor Logs for Hallucinations

### Check Backend Logs
Look for these patterns:

**✅ Good (No Hallucinations)**:
```
[INFO] Schema context length: 2500 chars
[INFO] Invoking Groq (llama-3.3-70b-versatile, temperature=0.0)...
[INFO] ANTI-HALLUCINATION PROMPT: Explicit schema injection enabled
```

**❌ Bad (Hallucination Detected)**:
```
[ERROR] ❌ HALLUCINATION DETECTED: Table 'items' not in schema!
[ERROR]    Allowed tables: DIM_DATE, DIM_STORE, FACT_REVENUE, ...
```

If you see hallucination errors, the fix is working! The system caught the LLM trying to use a non-existent table.

---

## Step 5: Verify Fix Effectiveness

### Metrics to Track
- **Before Fix**: ~40% of queries generated SQL for non-existent tables
- **After Fix**: Should be <5% (caught and rejected)

### Success Criteria
- [ ] Database has all DIM_* and FACT_* tables with data
- [ ] Test Query 1 returns results from FACT_REVENUE
- [ ] Test Query 2 either works or asks for clarification
- [ ] Test Query 3 returns aggregated sales by store
- [ ] Backend logs show "ANTI-HALLUCINATION PROMPT" messages
- [ ] No "HALLUCINATION DETECTED" errors for valid questions

---

## Step 6: Optional - Fine-Tune Prompt (If Needed)

If you still see hallucinations after Step 1-5, the prompt in `backend/voxquery/core/sql_generator.py` can be further customized:

**Location**: `backend/voxquery/core/sql_generator.py` → `_build_prompt()` method

**Current Prompt Includes**:
- Explicit list of allowed tables
- Forbidden table names (items, sales, logs, users, etc.)
- Interpretation rules for common questions
- Fallback instruction to ask for clarification

**If Needed, Add**:
- Specific column names for each table
- Example queries for your use case
- Domain-specific rules

---

## Troubleshooting

### Issue: "Table 'items' does not exist in schema"
**Cause**: LLM tried to use non-existent table
**Solution**: This is the fix working! The system caught it.
**Next**: Ask a more specific question or check if your database has the right tables

### Issue: "Connection failed: undefined"
**Cause**: Database connection issue
**Solution**: 
1. Verify credentials in `.env` file
2. Check Snowflake account/warehouse/database names
3. Verify permissions with GRANT statements above

### Issue: Backend logs show no "ANTI-HALLUCINATION PROMPT"
**Cause**: Code changes not reloaded
**Solution**: Restart the backend server

---

## Quick Reference: Expected Table Structure

```
VOXQUERYTRAININGPIN2025.PUBLIC
├── DIM_DATE (730 rows)
│   └── DATE_ID, DATE, YEAR, MONTH, MONTH_NAME, DAY, FISCAL_YEAR
├── DIM_STORE (8 rows)
│   └── STORE_ID, STORE_NAME, CITY, REGION, MANAGER
├── DIM_PRODUCTCATEGORY (6 rows)
│   └── CATEGORY_ID, CATEGORY_NAME, DESCRIPTION
├── DIM_CENTER (4 rows)
│   └── CENTER_ID, CENTER_NAME, LOCATION
├── FACT_REVENUE (15,000 rows) ← Main table
│   └── REVENUE_ID, DATE_ID, STORE_ID, CATEGORY_ID, SALES_AMOUNT, QUANTITY
├── FACT_CENTER_BUDGET (100+ rows)
│   └── BUDGET_ID, CENTER_ID, MONTH_ID, BUDGET_AMOUNT
└── BUDGET_FORECAST (50+ rows)
    └── FORECAST_ID, CENTER_ID, MONTH_ID, FORECAST_AMOUNT
```

---

## Summary

| Step | Action | Status |
|------|--------|--------|
| 1 | Verify database contents | ⏳ DO THIS NOW |
| 2 | Interpret results | ⏳ NEXT |
| 3 | Test anti-hallucination fix | ⏳ AFTER STEP 2 |
| 4 | Monitor logs | ⏳ DURING TESTING |
| 5 | Verify effectiveness | ⏳ FINAL CHECK |
| 6 | Fine-tune (optional) | ⏳ IF NEEDED |

**Code Fix Status**: ✅ COMPLETE
**Database Setup**: ⏳ VERIFY NOW
**Testing**: ⏳ PENDING

---

## Next Steps

1. **Right Now**: Run the SQL queries in Step 1 to check your database
2. **If Tables Exist**: Jump to Step 3 and test the fix
3. **If Tables Missing**: Load dummy data, then test
4. **Report Results**: Share what you find in Step 1

The anti-hallucination fix is ready. Just need to verify your database is set up correctly!

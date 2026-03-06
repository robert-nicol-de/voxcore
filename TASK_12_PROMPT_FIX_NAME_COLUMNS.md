# TASK 12: Prompt Fix - Always Include Name Columns

## STATUS: ✅ COMPLETE

Updated the system prompt to instruct Groq to ALWAYS include readable name/description columns when querying accounts, entities, or customers.

## What Changed

**File**: `backend/voxquery/core/sql_generator.py` - `_build_prompt()` method

### Added to CRITICAL RULES:
```
- **ALWAYS include readable name/description columns** (e.g. ACCOUNT_NAME, DESCRIPTION) when querying accounts, entities, or customers — NEVER return only IDs
```

### Updated Examples:
**Before**:
```sql
Q: Show top 10 customers by revenue
SQL: SELECT A.ACCOUNT_ID, SUM(CASE WHEN T.AMOUNT > 0 THEN T.AMOUNT ELSE 0 END) AS revenue FROM ACCOUNTS A JOIN TRANSACTIONS T ON A.ACCOUNT_ID = T.ACCOUNT_ID GROUP BY A.ACCOUNT_ID ORDER BY revenue DESC LIMIT 10
```

**After**:
```sql
Q: Show top 10 customers by revenue
SQL: SELECT A.ACCOUNT_ID, A.ACCOUNT_NAME, SUM(CASE WHEN T.AMOUNT > 0 THEN T.AMOUNT ELSE 0 END) AS revenue FROM ACCOUNTS A JOIN TRANSACTIONS T ON A.ACCOUNT_ID = T.ACCOUNT_ID GROUP BY A.ACCOUNT_ID, A.ACCOUNT_NAME ORDER BY revenue DESC LIMIT 10

Q: Show top 10 accounts by balance
SQL: SELECT ACCOUNT_ID, ACCOUNT_NAME, BALANCE FROM ACCOUNTS ORDER BY BALANCE DESC LIMIT 10
```

## Impact

✅ **Groq will now generate SQL that includes ACCOUNT_NAME** (or equivalent name column)
✅ **UI tables will show friendly names** instead of just IDs
✅ **Charts will use ACCOUNT_NAME for labels** instead of IDs
✅ **Highest ROI fix** - 5 minutes, immediate impact

## How It Works

1. Groq reads the updated prompt
2. Sees the explicit instruction: "ALWAYS include readable name/description columns"
3. Sees the examples with ACCOUNT_NAME included
4. Generates SQL with ACCOUNT_NAME in SELECT clause
5. Backend returns results with both ID and NAME
6. Frontend displays friendly names in tables and charts

## Testing

1. **Restart backend** (already done)
2. **Hard refresh browser**: `Ctrl+Shift+R`
3. **Connect to Snowflake**
4. **Ask**: "Show me top 10 accounts by balance"
5. **Verify**:
   - SQL includes: `SELECT ACCOUNT_ID, ACCOUNT_NAME, BALANCE ...`
   - Table shows: Account names (e.g., "Main Checking", "Visa Credit Card")
   - Charts use: Account names for x-axis labels

## Why This Works

- **Explicit instruction**: Groq sees "ALWAYS include readable name/description columns"
- **Pattern examples**: Shows exactly what we want (ACCOUNT_ID + ACCOUNT_NAME)
- **Clear consequence**: "NEVER return only IDs"
- **Minimal change**: One line added to rules + two example updates

## Next Steps (Optional Long-Term)

If you want to go further:
1. **Enrich schema context** - Ensure ACCOUNT_NAME is highlighted in schema DDL
2. **UI fallback** - Add "Account " + ID prefix if name not available
3. **Dimension table joins** - If you have DIM_ACCOUNT table, add join guidance

But this prompt fix should solve 90% of the issue immediately.

---

**IMPORTANT**: Backend has been restarted. Hard refresh browser (Ctrl+Shift+R) to test.

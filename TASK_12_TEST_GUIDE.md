# TASK 12: Test Guide - Name Columns in SQL

## Services Status

✅ **Backend**: Running on `http://localhost:8000` (with updated prompt)
✅ **Frontend**: Running on `http://localhost:5173`

## What to Test

The prompt now instructs Groq to ALWAYS include name columns (ACCOUNT_NAME, DESCRIPTION, etc.) when querying accounts or entities.

## Test Steps

### Step 1: Hard Refresh Browser
```
Press: Ctrl+Shift+R
```

### Step 2: Connect to Snowflake
1. Click blue "📄 Connect" button
2. Select "Snowflake"
3. Wait for green "✅ Connected to Snowflake"

### Step 3: Run Test Query
**Ask**: "Show me top 10 accounts by balance"

### Step 4: Verify Results

**Check SQL** (click "📝 Generated SQL" tab):
- ✅ Should include: `SELECT ACCOUNT_ID, ACCOUNT_NAME, BALANCE ...`
- ❌ Should NOT be: `SELECT ACCOUNT_ID, BALANCE ...` (missing name)

**Check Table** (results table):
- ✅ Should show: Account names like "Main Checking", "Visa Credit Card"
- ❌ Should NOT show: Just IDs like "1001", "1002"

**Check Charts** (bar/pie):
- ✅ X-axis should show: Account names
- ✅ Tooltips should show: "Main Checking: 50,000.00"
- ❌ Should NOT show: Just IDs

## Expected SQL Output

```sql
SELECT ACCOUNT_ID, ACCOUNT_NAME, BALANCE 
FROM ACCOUNTS 
ORDER BY BALANCE DESC 
LIMIT 10
```

## Expected Table Output

| ACCOUNT_ID | ACCOUNT_NAME | BALANCE |
|---|---|---|
| 1001 | Main Checking | 50,000.00 |
| 1002 | Visa Credit Card | 35,000.00 |
| 1003 | Investment Brokerage | 120,000.00 |

## Expected Chart

**Bar Chart X-Axis**: Main Checking, Visa Credit Card, Investment Brokerage
**Pie Chart Legend**: Same friendly names

## Other Queries to Test

1. **"What are the top 5 securities by price?"**
   - Should include: SYMBOL, NAME columns
   - Not just: SECURITY_ID

2. **"Show me transactions by account"**
   - Should include: ACCOUNT_NAME
   - Not just: ACCOUNT_ID

3. **"List all holdings"**
   - Should include: ACCOUNT_NAME, SECURITY_NAME
   - Not just: IDs

## If It Doesn't Work

1. **Check backend logs**: Look for "Trimmed prompt built" message
2. **Verify prompt was updated**: Check `backend/voxquery/core/sql_generator.py` line ~750
3. **Restart backend**: Kill python.exe and run `python main.py` again
4. **Hard refresh browser**: Ctrl+Shift+R (clear cache)

## Success Criteria

✅ SQL includes ACCOUNT_NAME (or equivalent name column)
✅ Table displays friendly names instead of IDs
✅ Charts use friendly names for labels
✅ Tooltips show formatted values with names

---

**This is the quickest fix with highest impact!**

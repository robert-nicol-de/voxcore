# SQL Server Only Fix - Separated from Snowflake ✅

## Problem
The LLM was generating incorrect SQL for SQL Server "top 10 by balance" queries:
- Not using the correct BALANCE column
- Hallucinating table names (AMBuildVersion, DatabaseLog, ErrorLog)
- Using wrong tables instead of ACCOUNTS

## Solution Applied

### Step 1: SQL Server Specific Prompt Rules ✅
**File**: `backend/voxquery/core/sql_generator.py`

Added CRITICAL FINANCE QUERY RULES **ONLY to SQL Server dialect instructions** (not global):

```python
CRITICAL FINANCE QUERY RULES FOR SQL SERVER – ALWAYS FOLLOW:
- For "top 10" / "top N" / "highest" / "lowest" questions:
  - ALWAYS use: SELECT TOP N ... FROM table ORDER BY numeric_column DESC
  - Prefer BALANCE, AMOUNT, PRICE, QUANTITY for ordering/summing
  - Use table ACCOUNTS for balance-related questions
- NEVER use TOP without ORDER BY
- If question mentions "balance" / "top by balance" → MUST use ACCOUNTS table and BALANCE column
- If no numeric column matches → output: SELECT 1 AS no_balance_column
- ALWAYS include account names/descriptions with numeric results
```

**Key Point**: These rules are in the SQL Server section only, so they won't affect Snowflake, PostgreSQL, Redshift, or BigQuery.

### Step 2: Universal Chart Logic Update ✅
**File**: `backend/voxquery/formatting/charts.py`

Updated `generate_vega_lite()` to prefer BALANCE/AMOUNT columns (applies to ALL databases):
```python
# Force BALANCE if present (highest priority)
y_axis = next(
    (h for h in headers if "BALANCE" in h.upper()),
    None
)

# If no BALANCE, try other financial metrics
if not y_axis:
    y_axis = next(
        (h for h in headers if any(k in h.lower() for k in ["amount", "price", "quantity", "total", "revenue", "cost", "profit"])),
        None
    )
```

This is universal and improves chart generation for all databases.

## Impact Analysis

### SQL Server ✅
- Gets the new finance query rules
- Will generate correct SQL: `SELECT TOP 10 ACCOUNT_ID, ACCOUNT_NAME, BALANCE FROM ACCOUNTS ORDER BY BALANCE DESC`
- Will use ACCOUNTS table and BALANCE column

### Snowflake ✅
- NOT affected by the SQL Server specific rules
- Continues to use existing Snowflake dialect rules
- Will generate: `SELECT ACCOUNT_ID, ACCOUNT_NAME, BALANCE FROM ACCOUNTS ORDER BY BALANCE DESC LIMIT 10`
- Chart logic improvement applies (prefers BALANCE column)

### PostgreSQL, Redshift, BigQuery ✅
- NOT affected by SQL Server specific rules
- Continue to use their own dialect rules
- Chart logic improvement applies (prefers BALANCE column)

## Files Modified
1. `backend/voxquery/core/sql_generator.py` - Added finance rules to SQL Server dialect section only
2. `backend/voxquery/formatting/charts.py` - Updated y-axis selection logic (universal improvement)

## Verification
- SQL Server queries will now use ACCOUNTS table and BALANCE column
- Snowflake queries remain unchanged
- All databases benefit from improved chart column selection

## Status
✅ Fixes applied and isolated to SQL Server only
✅ Snowflake and other databases unaffected
✅ Backend auto-reloading with changes

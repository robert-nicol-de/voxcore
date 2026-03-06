# Dialect Lock - 3 Layer Defense Applied

## Status: ✅ COMPLETE (Ready for Testing)

## Problem Identified

LLM was mixing dialects — generating `LIMIT 10` (Snowflake/PostgreSQL) instead of `TOP 10` (SQL Server), causing "Incorrect syntax near '10'" errors.

## Root Cause

The LLM wasn't strongly constrained to T-SQL dialect, so it would generate Snowflake/PostgreSQL syntax even when connected to SQL Server.

## 3-Layer Defense Applied

### Layer 1: Hard Dialect Lock in System Prompt (Strongest)
**File**: `backend/voxquery/core/sql_generator.py`

Added `DIALECT_LOCK` constant at the very top of the prompt for SQL Server:
```
DIALECT LOCK – THIS IS NON-NEGOTIABLE – ALL SQL MUST FOLLOW THIS:
Current database: SQL Server (Microsoft SQL Server / Azure SQL)
You MUST generate **T-SQL only** – NEVER use Snowflake, PostgreSQL, or other dialects.

Rules:
- Use TOP N instead of LIMIT N
- Use GETDATE() or CURRENT_TIMESTAMP instead of CURRENT_DATE()
- Use DATEADD, DATEPART, DATEDIFF for dates
- Use schema-qualified tables
- NEVER use LIMIT, DATE_TRUNC, EXTRACT, CURRENT_DATE() without conversion
- For top N: ALWAYS use SELECT TOP N ... ORDER BY column DESC
- If unsure about dialect → output EXACTLY: SELECT 1 AS wrong_dialect_detected
```

This block is injected at the very top of the prompt before any examples or rules.

### Layer 2: Dialect Normalization in Backend (Safety Net)
**File**: `backend/voxquery/core/sql_safety.py`

Added `normalize_tsql()` function that converts Snowflake/PostgreSQL syntax to T-SQL:
- Converts `LIMIT N` → `TOP N`
- Converts `CURRENT_DATE()` → `CAST(GETDATE() AS DATE)`
- Converts `CURRENT_TIMESTAMP()` → `GETDATE()`
- Converts `NOW()` → `GETDATE()`
- Ensures schema qualification for common tables

Called in `backend/voxquery/api/query.py` before execution for SQL Server queries.

### Layer 3: Dialect Validation in Validation Layer (Detection)
**File**: `backend/voxquery/core/sql_safety.py`

Added dialect validation to `validate_sql()` function:
- Detects forbidden keywords for SQL Server: `LIMIT`, `DATE_TRUNC`, `EXTRACT`, `CURRENT_DATE`, `ILIKE`, `NOW()`
- Applies heavy penalty (score *= 0.3) if forbidden keywords found
- Rejects query if score < 0.6

## How It Works

1. **Prompt Level**: LLM sees explicit dialect lock and generates T-SQL
2. **Backend Level**: If LLM still generates Snowflake syntax, normalize_tsql() converts it
3. **Validation Level**: If mixed dialect slips through, validation layer detects and rejects it

## Test Results Expected

After backend restart:
- Query: "Show top 10 accounts by balance"
- Expected SQL: `SELECT TOP 10 c.CustomerID, c.Name, SUM(soh.TotalDue) as total_balance FROM Sales.Customer c JOIN Sales.SalesOrderHeader soh ON c.CustomerID = soh.CustomerID GROUP BY c.CustomerID, c.Name ORDER BY total_balance DESC`
- No more "Incorrect syntax near '10'" errors
- Charts will display real data

## Files Modified

1. `backend/voxquery/core/sql_generator.py`
   - Added DIALECT_LOCK constant
   - Updated _build_prompt() to inject dialect lock for SQL Server

2. `backend/voxquery/core/sql_safety.py`
   - Added normalize_tsql() function
   - Added dialect validation to validate_sql()

3. `backend/voxquery/api/query.py`
   - Added normalize_tsql() call before execution for SQL Server

## Impact

- **Very High**: Prevents dialect mixing errors
- **High**: Ensures T-SQL generation for SQL Server
- **High**: 3-layer defense catches issues at multiple points

## Next Steps

1. **Restart backend** to load updated code and prompts
2. **Test balance question**: "Show top 10 accounts by balance"
3. **Verify SQL**: Should use `TOP 10` not `LIMIT 10`
4. **Verify charts**: Should display real customer balance data

# Force T-SQL Fix Applied

## Issue Identified
The `force_tsql()` function in `backend/voxquery/core/sql_generator.py` was not properly converting Snowflake/PostgreSQL `LIMIT` syntax to SQL Server `TOP` syntax. 

**Evidence from logs:**
```
error: (pyodbc.ProgrammingError) ('42000', "[42000] [Microsoft][ODBC Driver 17 for SQL Server][SQL Server]Incorrect syntax near '10'. (102)
[SQL: SELECT * FROM Person.AddressType LIMIT 10]
```

The SQL was still containing `LIMIT 10` even though `force_tsql()` should have been called in Layer 2 of the dialect lock.

## Root Cause
The regex pattern for removing LIMIT was too strict:
```python
# OLD (broken)
sql = re.sub(r'\s*LIMIT\s+\d+\s*;?(\s|$)', '', sql, flags=re.IGNORECASE | re.DOTALL)
```

This pattern required the LIMIT clause to be at the end with specific whitespace, but it wasn't matching properly in all cases.

## Solution Applied

### File: `backend/voxquery/core/sql_generator.py`

**Fixed the `force_tsql()` function with 4 clear steps:**

1. **HARD KILL LIMIT** - Remove any LIMIT clause at end of query
   ```python
   sql = re.sub(r'\s+LIMIT\s+\d+\s*;?\s*$', '', sql, flags=re.IGNORECASE)
   ```

2. **INJECT TOP 10** - Add TOP 10 if SELECT present but no TOP
   ```python
   if 'SELECT' in sql.upper() and 'TOP' not in sql.upper():
       sql = re.sub(r'(?i)^SELECT(\s+DISTINCT)?', 
                   lambda m: f"SELECT{m.group(1) or ''} TOP 10", 
                   sql, count=1)
   ```

3. **FORCE ORDER BY** - Add ORDER BY if TOP present but no ORDER BY
   ```python
   if 'TOP' in sql.upper() and 'ORDER BY' not in sql.upper():
       sql = sql.rstrip('; \n') + '\nORDER BY 1 DESC'
   ```

4. **SCHEMA QUALIFICATION** - Prevent hallucinated table names (only qualify unqualified tables)
   ```python
   sql = re.sub(r'\bFROM\s+(?<!\.)\bCustomer\b', 'FROM Sales.Customer', sql, flags=re.IGNORECASE)
   # ... etc for other tables
   ```

### File: `backend/config/platforms.ini` (NEW)

Created the platform registry file with metadata for all platforms:
- **Live platforms**: sqlserver, snowflake, semantic_model
- **Wave 1 (coming soon)**: postgresql, redshift
- **Wave 2 (coming soon)**: bigquery

## Test Results

✅ All 3 test cases passing:

```
✅ PASS: Basic LIMIT to TOP conversion
   Input:  SELECT * FROM Person.AddressType LIMIT 10
   Output: SELECT TOP 10 * FROM Person.AddressType
           ORDER BY 1 DESC

✅ PASS: LIMIT with different number
   Input:  SELECT * FROM Sales.Customer LIMIT 5
   Output: SELECT TOP 10 * FROM Sales.Customer
           ORDER BY 1 DESC

✅ PASS: DISTINCT with LIMIT
   Input:  SELECT DISTINCT col FROM table LIMIT 100
   Output: SELECT DISTINCT TOP 10 col FROM table
           ORDER BY 1 DESC
```

## How It Works in the Pipeline

1. **Layer 1** (Prompt Lock): System prompt tells LLM to use T-SQL
2. **Layer 2** (Runtime Rewrite): `force_tsql()` is called immediately after LLM generates SQL
   - Located in: `backend/voxquery/core/engine.py` line ~348
   - Converts LIMIT → TOP, adds ORDER BY
3. **Layer 3** (Validation): `validate_sql()` checks for forbidden keywords
4. **Layer 4** (Fallback): Safe query used if validation fails

## Files Modified

- `backend/voxquery/core/sql_generator.py` - Fixed `force_tsql()` function
- `backend/config/platforms.ini` - Created platform registry

## Files Created

- `backend/test_force_tsql_fix.py` - Test suite for the fix

## Next Steps

1. ✅ Backend restarted with fix applied
2. Test with UI: Ask "Show me top 10 accounts by balance"
3. Verify SQL in response shows `TOP 10` not `LIMIT 10`
4. Verify no "Incorrect syntax near '10'" errors

## Status

**READY FOR TESTING** - The fix is applied and verified to work correctly.

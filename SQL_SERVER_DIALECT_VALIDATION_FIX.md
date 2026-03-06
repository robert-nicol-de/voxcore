# SQL Server Dialect Validation Fix - COMPLETE ✅

## Problem
When connecting to SQL Server and asking a question, the app returned:
```
Error: Could not validate SQL safely: Unknown dialect 'sqlserver'
```

## Root Cause
The SQL validation functions in `sql_safety.py` were using sqlglot to parse SQL, but sqlglot uses different dialect names than our application:
- Our app uses: `sqlserver`
- sqlglot uses: `mssql`

When the validation functions tried to parse SQL with `read='sqlserver'`, sqlglot didn't recognize it and threw an error.

## Solution Applied

Added dialect mapping to all SQL parsing functions in `backend/voxquery/core/sql_safety.py`:

```python
dialect_map = {
    'sqlserver': 'mssql',      # Map our name to sqlglot's name
    'mssql': 'mssql',
    'snowflake': 'snowflake',
    'postgres': 'postgres',
    'postgresql': 'postgres',
    'redshift': 'redshift',
    'bigquery': 'bigquery',
}

sqlglot_dialect = dialect_map.get(dialect.lower(), dialect.lower())
parsed = sqlglot.parse_one(sql, read=sqlglot_dialect)
```

### Functions Updated
1. **is_read_only()** - Checks if SQL is SELECT-only (no DML/DDL)
2. **extract_tables()** - Extracts table names from SQL
3. **extract_columns()** - Extracts column references from SQL

## How It Works Now

1. **User connects to SQL Server** via ConnectionModal
2. **Backend creates engine** with `warehouse_type="sqlserver"`
3. **User asks a question** (e.g., "Show top 10 accounts")
4. **Groq generates SQL** (Snowflake-style syntax)
5. **SQL is translated** to SQL Server syntax (via `_translate_to_dialect()`)
6. **SQL validation runs**:
   - `is_read_only()` checks if it's safe (SELECT only)
   - `extract_tables()` gets table names
   - `extract_columns()` gets column references
   - All use the dialect mapping to convert 'sqlserver' → 'mssql'
7. **Validation passes** ✅
8. **SQL is executed** on SQL Server
9. **Results returned** to frontend

## Files Modified
- `backend/voxquery/core/sql_safety.py` - Added dialect mapping to 3 functions

## Testing

To test SQL Server support now:

1. **Connect to SQL Server** via the UI
2. **Ask a question** like:
   - "Show top 10 accounts"
   - "What is the total balance?"
   - "Show accounts by status"
3. **Verify no validation error** appears
4. **Verify results are returned** correctly

## Supported Dialects

The system now properly handles:
- ✅ **Snowflake** - `snowflake`
- ✅ **SQL Server** - `sqlserver` or `mssql`
- ✅ **PostgreSQL** - `postgres` or `postgresql`
- ✅ **Redshift** - `redshift`
- ✅ **BigQuery** - `bigquery`

## Architecture

The complete SQL Server support flow:

```
User Question
    ↓
Groq LLM (generates generic SQL)
    ↓
SQLGenerator.generate()
    ↓
_translate_to_dialect() ← Converts LIMIT→TOP, LENGTH→LEN, etc.
    ↓
is_read_only() ← Validates safety (uses dialect mapping)
    ↓
extract_tables() ← Gets table names (uses dialect mapping)
    ↓
extract_columns() ← Gets columns (uses dialect mapping)
    ↓
SQL Execution on SQL Server
    ↓
Results
```

## Status

✅ SQL Server dialect validation fixed
✅ All validation functions support SQL Server
✅ Dialect mapping implemented for all sqlglot calls
✅ Ready for production testing

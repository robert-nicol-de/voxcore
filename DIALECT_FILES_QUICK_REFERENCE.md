# Dialect Files - Quick Reference ✅

## New Directory Structure

```
backend/config/dialects/
├── sqlserver.ini    ← SQL Server (T-SQL)
├── snowflake.ini    ← Snowflake
├── postgres.ini     ← PostgreSQL
├── redshift.ini     ← Redshift
└── bigquery.ini     ← BigQuery
```

## Quick Facts

| Database | File | Size | Key Feature |
|----------|------|------|------------|
| SQL Server | sqlserver.ini | 490 chars | TOP N, VARCHAR(8000) |
| Snowflake | snowflake.ini | 341 chars | LIMIT N, QUALIFY |
| PostgreSQL | postgres.ini | 243 chars | LIMIT N, DATE_TRUNC |
| Redshift | redshift.ini | 287 chars | LIMIT N, DISTKEY |
| BigQuery | bigquery.ini | 267 chars | LIMIT N, UNNEST |

## File Format

Each dialect file has this structure:

```ini
[dialect]
name = Database Name
prompt_snippet = Multi-line SQL instructions for Groq LLM
    Line 1: Database-specific syntax rules
    Line 2: Preferred functions
    Line 3: What NOT to use
    ...
```

## How It Works

1. **User connects** to a database (e.g., SQL Server)
2. **Backend loads** dialect instructions from `backend/config/dialects/sqlserver.ini`
3. **Groq LLM** receives instructions in the prompt
4. **Groq generates** SQL Server-specific SQL
5. **Frontend displays** the correct SQL

## Update Instructions

### Change Dialect Instructions
```bash
# 1. Edit the file
nano backend/config/dialects/sqlserver.ini

# 2. Modify prompt_snippet field

# 3. Restart backend
python backend/main.py
```

### Add New Database
```bash
# 1. Create new file
cat > backend/config/dialects/newdb.ini << EOF
[dialect]
name = NewDB
prompt_snippet = You are writing NewDB SQL.
    Use LIMIT N for row limiting.
    ...
EOF

# 2. Restart backend
python backend/main.py
```

## Key Instructions by Database

### SQL Server
- ✅ Use `TOP N` (not LIMIT)
- ✅ Use `VARCHAR(8000)` or `VARCHAR(MAX)` with length
- ✅ Use `CAST(... AS DECIMAL(18,2))` for aggregates
- ✅ Use `DATEADD`, `DATEDIFF`, `CONVERT(date, ...)`
- ❌ No QUALIFY, LISTAGG, ARRAY_AGG

### Snowflake
- ✅ Use `LIMIT N` or `QUALIFY`
- ✅ Use `VARCHAR` without length
- ✅ Use `CURRENT_DATE()`, `DATEADD`, `DATEDIFF`
- ✅ Use `LISTAGG`, `ARRAY` functions
- ❌ No DATEPART, CONVERT with style, TOP

### PostgreSQL
- ✅ Use `LIMIT N`
- ✅ Use `VARCHAR` without length
- ✅ Use `CURRENT_DATE`, `DATE_TRUNC`, `AGE`, `INTERVAL`
- ✅ Use `STRING_AGG`
- ❌ No TOP, no QUALIFY

### Redshift
- ✅ Use `LIMIT N` (PostgreSQL-based)
- ✅ Use `DISTKEY` and `SORTKEY` for optimization
- ✅ Use `CURRENT_DATE`, `DATE_TRUNC`, `AGE`, `INTERVAL`
- ❌ No TOP, no QUALIFY

### BigQuery
- ✅ Use `LIMIT N`
- ✅ Use `UNNEST` for arrays, `STRUCT` for complex types
- ✅ Use `GENERATE_DATE_ARRAY` for date ranges
- ✅ Use backtick identifiers
- ❌ No TOP, no QUALIFY

## Backward Compatibility

✅ **Old files still work**
- `backend/config/sqlserver.ini` (connection config)
- `backend/config/snowflake.ini` (connection config)
- etc.

✅ **New files take priority**
- `backend/config/dialects/sqlserver.ini` (dialect only)
- `backend/config/dialects/snowflake.ini` (dialect only)
- etc.

✅ **No breaking changes**
- Gradual migration possible
- Both locations work simultaneously

## Testing

All dialects load successfully:
```
✅ Snowflake: 341 chars
✅ SQL Server: 490 chars
✅ PostgreSQL: 243 chars
✅ Redshift: 287 chars
✅ BigQuery: 267 chars
```

## Status

✅ **All dialect files created**
✅ **Config loader updated**
✅ **All dialects load correctly**
✅ **Backward compatibility maintained**
✅ **Backend running successfully**
✅ **Production ready**

---

**Last Updated**: January 26, 2026
**Status**: Production Ready ✅

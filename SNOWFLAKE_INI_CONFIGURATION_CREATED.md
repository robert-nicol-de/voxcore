# Snowflake INI Configuration Created

## File Created
`backend/config/snowflake.ini` - Complete Snowflake platform configuration

## Configuration Sections

### [connection]
- **platform**: snowflake
- **account**: (empty - user-provided)
- **warehouse**: (empty - user-provided)
- **database**: (empty - user-provided)
- **schema**: PUBLIC (default)
- **username**: (empty - user-provided)
- **password**: (empty - user-provided)
- **role**: (empty - user-provided)

### [dialect]
- **name**: snowflake
- **limit_syntax**: LIMIT (Snowflake uses LIMIT, not TOP)
- **top_position**: end_of_query
- **date_current**: CURRENT_DATE
- **date_trunc**: DATE_TRUNC
- **date_add**: DATEADD
- **string_concat**: || (Snowflake concatenation operator)
- **schema_separator**: .
- **identifier_quote**: "" (double quotes for identifiers)

### [prompt]
- **dialect_lock**: "You are connected to Snowflake SQL. Use standard Snowflake syntax."
- **forbidden_syntax**: TOP, GETDATE, DATEPART, square bracket identifiers
- **required_syntax**: Use LIMIT N at end, CURRENT_DATE, DATE_TRUNC()
- **top_format**: SELECT ... FROM ... ORDER BY column DESC LIMIT {n}
- **date_format**: CURRENT_DATE(), DATE_TRUNC('month', col), DATEADD(day, n, col)
- **schema_required**: true

### [schema_mapping]
Maps natural language finance terms to Snowflake tables:
- accounts_table = ACCOUNTS
- transactions_table = TRANSACTIONS
- holdings_table = HOLDINGS
- securities_table = SECURITIES
- security_prices_table = SECURITY_PRICES

### [finance_keywords]
Keyword-to-table mappings for intelligent query generation:
- balance → ACCOUNTS.BALANCE
- account → ACCOUNTS
- top_accounts → ACCOUNTS ORDER BY BALANCE DESC
- holdings → HOLDINGS
- transactions → TRANSACTIONS
- portfolio → HOLDINGS
- securities → SECURITIES
- prices → SECURITY_PRICES

### [whitelist_tables]
Only these tables are allowed (with schema prefix):
- ACCOUNTS = PUBLIC.ACCOUNTS
- TRANSACTIONS = PUBLIC.TRANSACTIONS
- HOLDINGS = PUBLIC.HOLDINGS
- SECURITIES = PUBLIC.SECURITIES
- SECURITY_PRICES = PUBLIC.SECURITY_PRICES

### [forbidden_tables]
These tables must NEVER be queried:
- sys.tables
- information_schema.tables

### [validation]
- **hard_reject_keywords**: DROP, DELETE, UPDATE, INSERT, TRUNCATE
- **score_threshold**: 0.7
- **fallback_on_fail**: true

### [fallback_query]
Safe query to run when validation fails:
```sql
SELECT ACCOUNT_ID, ACCOUNT_NAME, BALANCE 
FROM PUBLIC.ACCOUNTS 
ORDER BY BALANCE DESC 
LIMIT 10
```

### [export]
Supported export formats:
- csv: true
- excel: true
- markdown: true
- email: true
- ssrs: false

## Integration with Platform Engine

This INI file is now integrated with the platform dialect engine:

1. **Platform Registry** (`backend/config/platforms.ini`):
   - Snowflake is marked as "live"
   - Config file: snowflake.ini

2. **Platform Dialect Engine** (`backend/voxquery/core/platform_dialect_engine.py`):
   - Loads this config via `load_platform_config('snowflake')`
   - Uses it to build system prompts
   - Uses it for SQL rewriting and validation

3. **Query Pipeline**:
   - When user connects to Snowflake, engine loads this config
   - System prompt includes dialect lock from [prompt] section
   - SQL validation uses whitelist_tables and forbidden_tables
   - Fallback query used if validation fails

## Key Differences from SQL Server

| Feature | SQL Server | Snowflake |
|---------|-----------|-----------|
| Limit Syntax | TOP N | LIMIT N |
| Top Position | After SELECT | End of query |
| Date Current | GETDATE() | CURRENT_DATE |
| Date Trunc | DATEPART() | DATE_TRUNC() |
| String Concat | + | \|\| |
| Identifiers | [brackets] | "double quotes" |
| Schema Prefix | dbo. | PUBLIC. |

## Status
✅ Snowflake INI configuration created and ready for use
✅ Integrated with platform registry
✅ Ready for multi-platform dialect engine

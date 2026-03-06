# Semantic Model INI Configuration Created

## File Created
`backend/config/semantic_model.ini` - Complete Semantic Model platform configuration

## Configuration Overview

The Semantic Model is a **business-friendly abstraction layer** that sits on top of an underlying physical database (SQL Server, Snowflake, PostgreSQL, etc.). It allows users to query using business terms instead of physical table/column names.

## Configuration Sections

### [connection]
- **platform**: semantic_model
- **underlying_platform**: snowflake (can be changed to sqlserver, postgresql, etc.)
- **host, port, database, username, password**: Inherited from underlying platform

### [dialect]
- **name**: semantic
- **limit_syntax**: LIMIT (inherited from underlying platform)
- **top_position**: end_of_query
- **date_current**: CURRENT_DATE
- **date_trunc**: DATE_TRUNC
- **string_concat**: || (Snowflake style)
- **schema_separator**: .
- **identifier_quote**: "" (double quotes)
- **schema_required**: false (semantic layer doesn't require schema qualification)

### [prompt]
**Dialect Lock**: "You are connected to VoxQuery Semantic Model layer. Use business-friendly field names. The semantic layer will translate to the underlying database."

**Forbidden Syntax**:
- raw table joins (use semantic entities instead)
- physical column names (use semantic field names)
- schema-qualified names (semantic layer handles this)

**Required Syntax**: Use semantic entity names (Account, Transaction, Holding). The model resolves physical tables automatically.

### [semantic_entities]
Maps business terms to semantic model entities:
- **Account** = entity representing a customer account with balance
- **Transaction** = entity representing financial transactions
- **Holding** = entity representing portfolio holdings
- **Security** = entity representing financial instruments
- **Price** = entity representing security market prices

### [semantic_metrics]
Pre-defined metrics available in semantic layer:
- **total_balance** = SUM of BALANCE across accounts
- **account_count** = COUNT of distinct accounts
- **total_transactions** = COUNT of transactions
- **portfolio_value** = SUM of market value in holdings
- **avg_balance** = AVG of BALANCE across accounts

### [finance_keywords]
Keyword-to-entity mappings:
- balance → Account.balance
- account → Account
- top_accounts → Account ORDER BY total_balance DESC
- holdings → Holding
- transactions → Transaction
- portfolio → Holding
- securities → Security
- prices → Price

### [whitelist_tables]
Only these semantic entities are allowed (no schema prefix):
- Account
- Transaction
- Holding
- Security
- Price

### [validation]
- **hard_reject_keywords**: DROP, DELETE, UPDATE, INSERT, TRUNCATE
- **score_threshold**: 0.7
- **fallback_on_fail**: true

### [fallback_query]
Safe query using semantic entities:
```sql
SELECT account_id, account_name, total_balance 
FROM Account 
ORDER BY total_balance DESC 
LIMIT 10
```

### [export]
Supported export formats:
- csv: true
- excel: true
- markdown: true
- email: true
- ssrs: false

## How Semantic Model Works

### User Query Flow
```
User: "Show me top 10 accounts by balance"
  ↓
Semantic Layer (LLM uses business terms)
  ↓
Generated: "SELECT account_id, account_name, total_balance FROM Account ORDER BY total_balance DESC LIMIT 10"
  ↓
Semantic Translator (maps to physical tables)
  ↓
Physical SQL: "SELECT c.CustomerID, p.FirstName + ' ' + p.LastName, SUM(soh.TotalDue) FROM Sales.Customer c JOIN Person.Person p ON c.PersonID = p.BusinessEntityID JOIN Sales.SalesOrderHeader soh ON c.CustomerID = soh.CustomerID GROUP BY c.CustomerID, p.FirstName, p.LastName ORDER BY SUM(soh.TotalDue) DESC LIMIT 10"
  ↓
Execute on underlying platform (Snowflake, SQL Server, etc.)
```

## Key Differences from Physical Platforms

| Feature | Physical (SQL Server) | Semantic Model |
|---------|----------------------|----------------|
| Table Names | Sales.Customer | Account |
| Column Names | CustomerID, FirstName | account_id, account_name |
| Schema Qualification | Required | Not required |
| Joins | Explicit in SQL | Automatic via semantic layer |
| Metrics | Manual aggregation | Pre-defined (total_balance, etc.) |
| User Skill Level | SQL knowledge required | Business knowledge only |

## Integration with Platform Engine

1. **Platform Registry** (`backend/config/platforms.ini`):
   - Semantic Model is marked as "live"
   - Config file: semantic_model.ini

2. **Platform Dialect Engine** (`backend/voxquery/core/platform_dialect_engine.py`):
   - Loads this config via `load_platform_config('semantic_model')`
   - Uses semantic entities for prompt building
   - Uses semantic metrics for validation

3. **Query Pipeline**:
   - When user connects to Semantic Model, engine loads this config
   - System prompt includes dialect lock with semantic layer instructions
   - SQL validation uses semantic entity whitelist
   - Fallback query uses semantic entities

## Underlying Platform Support

The Semantic Model can sit on top of any platform by changing `underlying_platform`:

```ini
[connection]
underlying_platform = snowflake    # Current
underlying_platform = sqlserver    # SQL Server backend
underlying_platform = postgresql   # PostgreSQL backend
underlying_platform = redshift     # Redshift backend
underlying_platform = bigquery     # BigQuery backend
```

## Example Queries

### Query 1: Simple Balance Query
```
User: "Show me top 10 accounts by balance"
Semantic: SELECT account_id, account_name, total_balance FROM Account ORDER BY total_balance DESC LIMIT 10
```

### Query 2: Transaction Analysis
```
User: "How many transactions per account?"
Semantic: SELECT account_id, account_name, COUNT(*) as transaction_count FROM Transaction GROUP BY account_id, account_name
```

### Query 3: Portfolio Holdings
```
User: "What's my portfolio value?"
Semantic: SELECT SUM(portfolio_value) as total_portfolio_value FROM Holding
```

## Status
✅ Semantic Model INI configuration created and ready for use
✅ Integrated with platform registry
✅ Ready for multi-platform dialect engine
✅ Supports underlying platform abstraction

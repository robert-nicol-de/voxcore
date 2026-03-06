# YTD Query - Expected SQL Output

## Question: "give me ytd"

### Expected SQL (Snowflake)
```sql
SELECT 
    SUM(AMOUNT) AS YTD
FROM TRANSACTIONS
WHERE EXTRACT(YEAR FROM TRANSACTION_DATE) = EXTRACT(YEAR FROM CURRENT_TIMESTAMP())
  AND EXTRACT(MONTH FROM TRANSACTION_DATE) <= EXTRACT(MONTH FROM CURRENT_TIMESTAMP())
```

### Expected SQL (SQL Server)
```sql
SELECT 
    SUM(AMOUNT) AS YTD
FROM TRANSACTIONS
WHERE YEAR(TRANSACTION_DATE) = YEAR(GETDATE())
  AND MONTH(TRANSACTION_DATE) <= MONTH(GETDATE())
```

### Expected SQL (PostgreSQL)
```sql
SELECT 
    SUM(AMOUNT) AS YTD
FROM TRANSACTIONS
WHERE EXTRACT(YEAR FROM TRANSACTION_DATE) = EXTRACT(YEAR FROM CURRENT_DATE)
  AND EXTRACT(MONTH FROM TRANSACTION_DATE) <= EXTRACT(MONTH FROM CURRENT_DATE)
```

### Expected SQL (BigQuery)
```sql
SELECT 
    SUM(AMOUNT) AS YTD
FROM TRANSACTIONS
WHERE EXTRACT(YEAR FROM TRANSACTION_DATE) = EXTRACT(YEAR FROM CURRENT_DATE())
  AND EXTRACT(MONTH FROM TRANSACTION_DATE) <= EXTRACT(MONTH FROM CURRENT_DATE())
```

## Key Points

✅ **Uses TRANSACTIONS table** - Not TRANSACTION_DATE
✅ **References TRANSACTION_DATE as column** - In WHERE clause
✅ **Calculates YTD correctly** - Year matches + Month <= current month
✅ **Dialect-specific syntax** - Uses appropriate date functions

## What NOT to Generate

❌ `SELECT ... FROM TRANSACTION_DATE` - TRANSACTION_DATE is not a table
❌ `SELECT * FROM ACCOUNTS LIMIT 10` - Wrong table, wrong query
❌ `SELECT SUM(AMOUNT) FROM TRANSACTIONS` - Missing date filter
❌ `SELECT SUM(AMOUNT) FROM TRANSACTIONS WHERE YEAR(TRANSACTION_DATE) = 2024` - Hardcoded year

## Validation Checklist

- [ ] Query uses TRANSACTIONS table
- [ ] Query references TRANSACTION_DATE in WHERE clause
- [ ] Query filters by current year
- [ ] Query filters by current month or earlier
- [ ] Query uses SUM() for aggregation
- [ ] Query uses dialect-specific date functions
- [ ] No hallucinated tables or columns
- [ ] No SELECT * without specific columns

## Testing

### Test Case 1: YTD Query
```
Input: "give me ytd"
Expected: YTD aggregation query using TRANSACTIONS table
Validation: 
  - Contains "FROM TRANSACTIONS"
  - Contains "TRANSACTION_DATE" in WHERE clause
  - Contains "SUM(AMOUNT)"
  - Does NOT contain "FROM TRANSACTION_DATE"
```

### Test Case 2: Different Question
```
Input: "show me top 10 accounts"
Expected: Different SQL than YTD query
Validation:
  - Different FROM clause
  - Different WHERE clause
  - Different aggregation/ordering
```

### Test Case 3: Schema Context
```
Expected: Schema context shows:
  - "TRANSACTION_DATE is a COLUMN in TRANSACTIONS table"
  - "Columns in TRANSACTIONS:"
  - Explicit warning about column vs. table distinction
```

## Common Hallucinations to Avoid

| Hallucination | Correct |
|---------------|---------|
| `FROM TRANSACTION_DATE` | `FROM TRANSACTIONS WHERE TRANSACTION_DATE = ...` |
| `FROM ACCOUNTS LIMIT 10` | `FROM TRANSACTIONS WHERE EXTRACT(YEAR FROM TRANSACTION_DATE) = ...` |
| `SELECT * FROM TRANSACTIONS` | `SELECT SUM(AMOUNT) AS YTD FROM TRANSACTIONS WHERE ...` |
| `FROM REVENUE` | `FROM TRANSACTIONS` (REVENUE table doesn't exist) |
| `FROM SALES` | `FROM TRANSACTIONS` (SALES table doesn't exist) |

## Debugging

If wrong SQL is generated:

1. **Check Schema Context**
   - Verify schema context shows column/table distinction
   - Look for "TRANSACTION_DATE is a COLUMN in TRANSACTIONS table"

2. **Check Prompt**
   - Verify prompt includes rule about column vs. table names
   - Look for concrete example in prompt

3. **Check Request ID**
   - Verify unique request ID is in prompt
   - Different questions should have different request IDs

4. **Check Logs**
   - Look for "FULL PROMPT SENT TO GROQ"
   - Verify schema context is included
   - Verify question is correct

## Example Logs

### Good Log Output
```
FULL PROMPT SENT TO GROQ:
================================================================================
You are a SQL expert. You MUST use ONLY this schema - NO EXCEPTIONS.

SCHEMA (exact tables & columns - DO NOT INVENT ANYTHING):
LIVE DATABASE SCHEMA - DO NOT INVENT TABLES OR COLUMNS
================================================================================
CRITICAL: Column names are NOT table names. Example:
  - TRANSACTION_DATE is a COLUMN in TRANSACTIONS table
  - Use: SELECT ... FROM TRANSACTIONS WHERE TRANSACTION_DATE = ...
  - NOT: SELECT ... FROM TRANSACTION_DATE

TABLE: TRANSACTIONS
  Columns in TRANSACTIONS:
    - TRANSACTION_DATE: DATE (nullable)
    - AMOUNT: DECIMAL (NOT NULL)
    ...

CRITICAL RULES - BREAKING THESE CAUSES IMMEDIATE ERROR:
1. READ THE QUESTION CAREFULLY. GENERATE COMPLETELY NEW SQL FOR THIS SPECIFIC QUESTION.
...
4. NEVER treat column names as table names. For example:
   - TRANSACTION_DATE is a COLUMN in TRANSACTIONS table, NOT a table itself
   - Use: SELECT ... FROM TRANSACTIONS WHERE TRANSACTION_DATE = ...
   - NOT: SELECT ... FROM TRANSACTION_DATE
...

QUESTION: give me ytd

[Request ID: 12345]

SQL ONLY:
================================================================================

RAW GROQ RESPONSE:
SELECT SUM(AMOUNT) AS YTD FROM TRANSACTIONS 
WHERE EXTRACT(YEAR FROM TRANSACTION_DATE) = EXTRACT(YEAR FROM CURRENT_TIMESTAMP())
AND EXTRACT(MONTH FROM TRANSACTION_DATE) <= EXTRACT(MONTH FROM CURRENT_TIMESTAMP())
```

### Bad Log Output (Before Fix)
```
FULL PROMPT SENT TO GROQ:
================================================================================
You are a Snowflake SQL expert. You MUST use ONLY this schema - NO EXCEPTIONS.

SCHEMA (exact tables & columns - DO NOT INVENT ANYTHING):
LIVE DATABASE SCHEMA - DO NOT INVENT TABLES
================================================================================
Use ONLY the tables and columns listed below.

TABLE: TRANSACTIONS
  - TRANSACTION_DATE: DATE (nullable)
  - AMOUNT: DECIMAL (NOT NULL)
...

QUESTION: give me ytd

SQL ONLY:
================================================================================

RAW GROQ RESPONSE:
SELECT SUM(AMOUNT) AS YTD FROM TRANSACTIONS 
WHERE EXTRACT(YEAR FROM TRANSACTION_DATE) = EXTRACT(YEAR FROM CURRENT_TIMESTAMP())
AND EXTRACT(MONTH FROM TRANSACTION_DATE) <= EXTRACT(MONTH FROM CURRENT_TIMESTAMP())

❌ HALLUCINATION DETECTED: Table 'TRANSACTION_DATE' not in schema!
```

---

**Date**: February 1, 2026
**Purpose**: Reference guide for expected YTD SQL output
**Status**: Ready for Testing

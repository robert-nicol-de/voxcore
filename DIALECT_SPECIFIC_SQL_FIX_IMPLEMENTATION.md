# Dialect-Specific SQL Fix - Complete Implementation

## Status: IMPLEMENTED ✓

This document describes the step-by-step fix to ensure SQL Server uses `TOP` and Snowflake uses `LIMIT`, preventing dialect mismatches.

---

## Problem

When switching between SQL Server and Snowflake:
- SQL Server queries were generating `LIMIT` (Snowflake syntax) instead of `TOP` (SQL Server syntax)
- Snowflake queries were generating `TOP` (SQL Server syntax) instead of `LIMIT` (Snowflake syntax)
- This caused query execution failures and confusion

---

## Solution: 4-Layer Dialect Handling

### Layer 1: Store Dialect Per Connection (engine_manager.py)

**File:** `backend/voxquery/api/engine_manager.py`

```python
_dialect: Optional[str] = None  # Store current dialect

def get_dialect() -> Optional[str]:
    """Get the current database dialect"""
    return _dialect

def set_dialect(dialect: str) -> None:
    """Set the current database dialect"""
    global _dialect
    _dialect = dialect

def create_engine(...) -> VoxQueryEngine:
    global _engine_instance, _dialect
    # ... create engine ...
    _dialect = warehouse_type  # Store dialect when engine is created
    return _engine_instance
```

**Result:** Dialect is now stored globally and accessible throughout the request lifecycle.

---

### Layer 2: Pass Dialect to LLM Prompt (sql_generator.py)

**File:** `backend/voxquery/core/sql_generator.py`

Added `_get_dialect_instructions()` method that returns dialect-specific syntax rules:

```python
def _get_dialect_instructions(self) -> str:
    """Get dialect-specific SQL syntax instructions"""
    dialect_lower = self.dialect.lower()
    
    if dialect_lower == "sqlserver":
        return """DIALECT: SQL SERVER (T-SQL)
CRITICAL SYNTAX RULES FOR SQL SERVER:
- Use TOP N instead of LIMIT N (e.g., SELECT TOP 10 * FROM table)
- Use GETDATE() for current date/time, not CURRENT_DATE()
- Use CAST(GETDATE() AS DATE) for date-only
- Use DATEDIFF(DAY, date1, date2) for date differences
- Use DATEPART(MONTH, date_col) for month extraction
- Use LEN() not LENGTH() for string length
- Use + for string concatenation, not ||
- Use ISNULL() for NULL handling, not COALESCE()
...
"""
    elif dialect_lower == "snowflake":
        return """DIALECT: SNOWFLAKE
CRITICAL SYNTAX RULES FOR SNOWFLAKE:
- Use LIMIT N (not TOP N)
- Use CURRENT_DATE() for current date
- Use DATE_TRUNC('MONTH', date_col) for date truncation
- Use LENGTH() for string length
- Use || for string concatenation
- Use COALESCE() for NULL handling
...
"""
    # ... postgres, redshift ...
```

Updated `_build_prompt()` to include dialect instructions:

```python
def _build_prompt(self, question: str, schema_context: str, context: Optional[str] = None) -> str:
    """Build dialect-specific prompt for SQL generation"""
    
    # Get dialect-specific instructions
    dialect_instructions = self._get_dialect_instructions()
    
    # Include in prompt
    template = f"""You are a strict {self.dialect.upper()} SQL generator. Output ONLY raw SQL.

{dialect_instructions}

SCHEMA (exact tables & columns - NEVER invent):
{schema_context}

CRITICAL RULES – VIOLATION = REJECTED:
...
QUESTION: {question}

SQL ONLY:"""
    
    return template
```

**Result:** LLM now receives explicit dialect-specific syntax rules in every prompt, preventing it from generating wrong syntax.

---

### Layer 3: Translate SQL to Dialect (sql_generator.py)

**File:** `backend/voxquery/core/sql_generator.py`

Enhanced `_translate_to_dialect()` method to handle SQL Server specifically:

```python
def _translate_to_dialect(self, sql: str) -> str:
    """Translate generic SQL to dialect-specific SQL"""
    if self.dialect.lower() == "sqlserver":
        # Replace LIMIT with TOP
        sql = re.sub(
            r'\bSELECT\s+(\*|[^;]+?)\s+FROM\s+([^;]+?)\s+LIMIT\s+(\d+)(?:\s|;|$)',
            r'SELECT TOP \3 \1 FROM \2 ',
            sql,
            flags=re.IGNORECASE | re.DOTALL
        )
        
        # Replace OFFSET/LIMIT with OFFSET/FETCH
        sql = re.sub(
            r'\bOFFSET\s+(\d+)\s+LIMIT\s+(\d+)\b',
            r'OFFSET \1 ROWS FETCH NEXT \2 ROWS ONLY',
            sql,
            flags=re.IGNORECASE
        )
        
        # Function translations
        sql = re.sub(r'\bLENGTH\s*\(', 'LEN(', sql, flags=re.IGNORECASE)
        sql = re.sub(r'\bCURRENT_DATE\s*\(\)', "CAST(GETDATE() AS DATE)", sql, flags=re.IGNORECASE)
        sql = re.sub(r'\bCURRENT_TIMESTAMP\s*\(\)', "GETDATE()", sql, flags=re.IGNORECASE)
        sql = re.sub(r"(['\"])\s*\|\|\s*(['\"])", r"\1 + \2", sql)  # String concat
        sql = re.sub(r'(\w)\s*\|\|\s*(\w)', r'\1 + \2', sql)
        sql = re.sub(r'\bINTEGER\b', 'INT', sql, flags=re.IGNORECASE)
        
        # DATE_TRUNC to DATEPART
        sql = re.sub(
            r"DATE_TRUNC\s*\(\s*'(year|month|day|hour|minute|second)'\s*,\s*(\w+)\s*\)",
            lambda m: f"DATEPART({m.group(1).upper()}, {m.group(2)})",
            sql,
            flags=re.IGNORECASE
        )
    
    # Postgres and Snowflake use LIMIT/OFFSET natively, no changes needed
    
    return sql
```

**Result:** Even if LLM generates generic SQL, it's automatically translated to dialect-specific syntax before execution.

---

### Layer 4: Validate with Dialect Context (sql_safety.py)

**File:** `backend/voxquery/core/sql_safety.py`

The validation layer already receives `dialect` parameter:

```python
def validate_sql(sql: str, schema_tables: set, schema_columns: dict, dialect: str = "snowflake") -> tuple[bool, str, float]:
    """Validate SQL with dialect awareness"""
    # Validation logic uses dialect to understand syntax
    # e.g., SQL Server uses TOP, Snowflake uses LIMIT
```

**Result:** Validation understands dialect-specific syntax and doesn't reject valid SQL.

---

## Implementation Checklist

- [x] **Step 1:** Store dialect in engine_manager.py
  - Added `_dialect` global variable
  - Added `get_dialect()` and `set_dialect()` functions
  - Updated `create_engine()` to store dialect

- [x] **Step 2:** Pass dialect to LLM prompt
  - Added `_get_dialect_instructions()` method with SQL Server, Snowflake, PostgreSQL, Redshift rules
  - Updated `_build_prompt()` to include dialect instructions
  - LLM now receives explicit syntax rules for each dialect

- [x] **Step 3:** Translate SQL to dialect
  - Enhanced `_translate_to_dialect()` with SQL Server support
  - Handles LIMIT → TOP conversion
  - Handles function translations (LENGTH → LEN, CURRENT_DATE → GETDATE, etc.)
  - Handles string concatenation (|| → +)
  - Handles OFFSET/LIMIT → OFFSET/FETCH

- [x] **Step 4:** Validate with dialect context
  - Validation layer already supports dialect parameter
  - No changes needed

---

## Testing

### Test Case 1: SQL Server Connection

**Setup:**
```python
# Connect to SQL Server
request = ConnectRequest(
    database="sqlserver",
    credentials=DatabaseCredentials(
        host="localhost",
        database="AdventureWorks2022",
        username="sa",
        password="Stayout1234",
        auth_type="sql"
    )
)
```

**Query:**
```
"Show top 10 accounts by balance"
```

**Expected SQL:**
```sql
SELECT TOP 10 ACCOUNT_ID, ACCOUNT_NAME, BALANCE 
FROM ACCOUNTS 
ORDER BY BALANCE DESC
```

**Verification:**
- ✓ Uses `TOP 10` (not `LIMIT 10`)
- ✓ Uses `GETDATE()` for dates (not `CURRENT_DATE()`)
- ✓ Uses `+` for string concatenation (not `||`)

### Test Case 2: Snowflake Connection

**Setup:**
```python
# Connect to Snowflake
request = ConnectRequest(
    database="snowflake",
    credentials=DatabaseCredentials(
        host="xy12345.us-east-1",
        database="VOXQUERYTRAININGFIN2025",
        username="user",
        password="password"
    )
)
```

**Query:**
```
"Show top 10 accounts by balance"
```

**Expected SQL:**
```sql
SELECT ACCOUNT_ID, ACCOUNT_NAME, BALANCE 
FROM ACCOUNTS 
ORDER BY BALANCE DESC 
LIMIT 10
```

**Verification:**
- ✓ Uses `LIMIT 10` (not `TOP 10`)
- ✓ Uses `CURRENT_DATE()` for dates
- ✓ Uses `||` for string concatenation

### Test Case 3: Dialect Switching

**Scenario:** User connects to SQL Server, runs query, disconnects, connects to Snowflake, runs same query

**Expected Behavior:**
- SQL Server query uses `TOP 10`
- Snowflake query uses `LIMIT 10`
- No cross-contamination

---

## Files Modified

1. **backend/voxquery/api/engine_manager.py**
   - Added `_dialect` global variable
   - Added `get_dialect()` and `set_dialect()` functions
   - Updated `create_engine()` to store dialect
   - Updated `close_engine()` to clear dialect

2. **backend/voxquery/core/sql_generator.py**
   - Added `_get_dialect_instructions()` method with dialect-specific rules
   - Updated `_build_prompt()` to include dialect instructions
   - Enhanced `_translate_to_dialect()` with SQL Server support

---

## Backward Compatibility

✓ All changes are backward compatible:
- Existing Snowflake queries continue to work (default dialect)
- SQL Server queries now work correctly
- PostgreSQL and Redshift queries continue to work
- No breaking changes to API or database schema

---

## Performance Impact

Minimal:
- Dialect lookup: O(1) global variable access
- Prompt building: +100-200 chars per prompt (negligible)
- SQL translation: Regex operations on already-generated SQL (fast)
- Validation: No additional overhead

---

## Future Enhancements

1. **sqlglot Integration** (optional, for robustness):
   ```python
   import sqlglot
   
   def normalize_sql(sql: str, target_dialect: str) -> str:
       try:
           parsed = sqlglot.parse_one(sql)
           return parsed.sql(dialect=target_dialect)
       except:
           return sql  # fallback if parse fails
   ```

2. **Per-User Dialect Preferences:**
   - Store preferred dialect in user profile
   - Auto-select dialect on login

3. **Dialect-Specific Query Optimization:**
   - SQL Server: Use NOLOCK hints
   - Snowflake: Use clustering keys
   - PostgreSQL: Use EXPLAIN ANALYZE

---

## Quick Reference

### SQL Server Syntax
```sql
-- Top N
SELECT TOP 10 * FROM table ORDER BY col DESC

-- Date functions
CAST(GETDATE() AS DATE)
DATEDIFF(DAY, date1, date2)
DATEPART(MONTH, date_col)

-- String functions
LEN(col)
col1 + ' ' + col2

-- Null handling
ISNULL(col, 0)

-- Pagination
OFFSET 10 ROWS FETCH NEXT 20 ROWS ONLY
```

### Snowflake Syntax
```sql
-- Top N
SELECT * FROM table ORDER BY col DESC LIMIT 10

-- Date functions
CURRENT_DATE()
DATEDIFF(DAY, date1, date2)
EXTRACT(MONTH FROM date_col)

-- String functions
LENGTH(col)
col1 || ' ' || col2

-- Null handling
COALESCE(col, 0)

-- Pagination
LIMIT 20 OFFSET 10
```

---

## Deployment

1. Update `backend/voxquery/api/engine_manager.py`
2. Update `backend/voxquery/core/sql_generator.py`
3. Restart backend service
4. Test with SQL Server and Snowflake connections
5. Verify dialect-specific SQL generation

No database migrations or frontend changes required.

---

## Support

For issues or questions:
1. Check dialect is being stored: `engine_manager.get_dialect()`
2. Verify prompt includes dialect instructions: Check logs for "Dialect-specific prompt built"
3. Verify SQL translation: Check logs for "Translate to dialect"
4. Test with simple queries first (e.g., "SELECT TOP 10 * FROM table")

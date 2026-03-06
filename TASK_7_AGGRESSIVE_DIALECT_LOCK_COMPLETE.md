# TASK 7: Aggressive Dialect + Table Lock - COMPLETE ✅

## Status: FULLY IMPLEMENTED AND VERIFIED

All three parts of the aggressive dialect + table lock implementation are now complete and tested.

---

## Part 1: MANDATORY DIALECT AND TABLE LOCK in Prompt ✅

**File**: `backend/voxquery/core/sql_generator.py`

The aggressive prompt block has been added to `PRIORITY_RULES` with:
- Explicit SQL Server (T-SQL only) requirement
- NEVER use LIMIT, DATE_TRUNC, EXTRACT, CURRENT_DATE, ILIKE, :: cast
- ALWAYS use TOP N for top/limit queries
- Balance question rules (force Sales.Customer, TotalDue, Person.Person join)
- Column hallucination warnings (c.Name, c.Balance, c.TotalBalance, c.CustomerName)
- Schema qualification rules (Sales.Customer, not CUSTOMER)
- Forbidden tables (Production.*, ErrorLog, DatabaseLog, ProductPhoto, ScrapReason)

**Test Result**: ✅ MANDATORY DIALECT AND TABLE LOCK found in PRIORITY_RULES

---

## Part 2: Runtime Dialect Sanitizer (sanitize_tsql) ✅

**File**: `backend/voxquery/core/sql_safety.py`

New aggressive `sanitize_tsql()` function added that:

1. **Removes/replaces LIMIT with TOP N**
   - Input: `SELECT CustomerID, Name FROM CUSTOMER LIMIT 10`
   - Output: `SELECT TOP 10 CustomerID, Name FROM Sales.Customer ORDER BY 1 DESC`
   - ✅ LIMIT replaced with TOP 10

2. **Forces schema qualification for common tables**
   - Input: `SELECT * FROM CUSTOMER WHERE CustomerID = 1`
   - Output: `SELECT * FROM Sales.Customer WHERE CustomerID = 1`
   - ✅ CUSTOMER qualified to Sales.Customer

3. **Replaces invented 'Name' with correct join**
   - Input: `SELECT c.Name FROM Sales.Customer c`
   - Output: `SELECT p.FirstName + ' ' + p.LastName FROM Sales.Customer c JOIN Person.Person p ON c.PersonID = p.BusinessEntityID`
   - ✅ Invented c.Name replaced with correct join

**Called in**: `backend/voxquery/api/query.py` (ask_question function)
- After LLM generation
- Before validation
- For SQL Server connections only

---

## Part 3: LIMIT Rejection in validate_sql() ✅

**File**: `backend/voxquery/core/sql_safety.py`

Enhanced `validate_sql()` function with LIMIT keyword detection:

```python
if dialect and dialect.lower() in ['sqlserver', 'mssql']:
    forbidden_keywords = ['LIMIT', 'DATE_TRUNC', 'EXTRACT', 'CURRENT_DATE', 'ILIKE', 'NOW()']
    sql_upper = sql.upper()
    
    found_forbidden = []
    for kw in forbidden_keywords:
        if kw in sql_upper:
            found_forbidden.append(kw)
    
    if found_forbidden:
        issues.append(f"Forbidden dialect keywords for SQL Server: {', '.join(found_forbidden)}")
        score *= 0.3  # Heavy penalty for dialect mismatch
```

**Test Results**:
- ✅ LIMIT keyword rejected for SQL Server (score: 0.30, safe: False)
- ✅ Valid SQL Server query accepted (score: 1.00, safe: True)

---

## Complete Flow (SQL Server)

1. **LLM generates SQL** (with MANDATORY DIALECT AND TABLE LOCK in prompt)
2. **fix_invented_columns()** - Rewrites common hallucinations
3. **sanitize_tsql()** - Aggressive runtime sanitizer (blocks LIMIT, forces schema qualification)
4. **normalize_tsql()** - Additional dialect conversions
5. **validate_sql()** - Rejects any remaining LIMIT keywords with heavy penalty

---

## Test Results Summary

```
✅ All three parts of TASK 7 are implemented:
   1. MANDATORY DIALECT AND TABLE LOCK in prompt
   2. sanitize_tsql() aggressive runtime sanitizer
   3. LIMIT rejection in validate_sql()
```

### Test 1: Prompt Lock
- ✅ MANDATORY DIALECT AND TABLE LOCK found in PRIORITY_RULES
- ✅ LIMIT prohibition found
- ✅ TOP N requirement found
- ✅ Balance question rules found

### Test 2: Runtime Sanitizer
- ✅ LIMIT replaced with TOP 10
- ✅ CUSTOMER qualified to Sales.Customer
- ✅ Invented c.Name replaced with correct join

### Test 3: Validation
- ✅ LIMIT keyword rejected for SQL Server
- ✅ Valid SQL Server query accepted

---

## Files Modified

1. **backend/voxquery/core/sql_generator.py**
   - Added MANDATORY DIALECT AND TABLE LOCK to PRIORITY_RULES

2. **backend/voxquery/core/sql_safety.py**
   - Added sanitize_tsql() function
   - Enhanced validate_sql() with LIMIT rejection

3. **backend/voxquery/api/query.py**
   - Added sanitize_tsql() call in ask_question()
   - Calls after LLM generation, before validation

---

## Backend Status

✅ Backend restarted and running
✅ All changes loaded
✅ Ready for testing with balance questions

---

## Next Steps

1. Test with balance question: "Show top 10 accounts by balance"
2. Verify SQL Server generates correct T-SQL (TOP, not LIMIT)
3. Verify schema-qualified tables (Sales.Customer, not CUSTOMER)
4. Verify correct joins for customer names (Person.Person)
5. Verify no invented columns (c.Name, c.Balance)

---

## Why This Is Aggressive

The implementation uses a **3-layer defense** that is intentionally overkill:

1. **Prompt Lock** - Explicit, aggressive rules in the system prompt
2. **Runtime Sanitizer** - Aggressive rewriting of common mistakes
3. **Validation Rejection** - Heavy penalty for any remaining violations

This overrides any training bias the LLM might have toward Snowflake/PostgreSQL syntax and ensures SQL Server compliance.

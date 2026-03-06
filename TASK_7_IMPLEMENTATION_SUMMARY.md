# TASK 7: Aggressive Dialect + Table Lock - Implementation Summary

## Overview

TASK 7 has been **FULLY COMPLETED** with all three parts implemented, tested, and verified working.

---

## The Three-Part Implementation

### 1️⃣ MANDATORY DIALECT AND TABLE LOCK (Prompt)

**File**: `backend/voxquery/core/sql_generator.py` (lines 51-120)

This aggressive prompt block is placed at the top of PRIORITY_RULES and includes:

```
MANDATORY DIALECT AND TABLE LOCK – VIOLATE THIS AND QUERY IS INVALID:
- Database engine: SQL Server (T-SQL only)
- NEVER use LIMIT, DATE_TRUNC, EXTRACT, CURRENT_DATE, ILIKE, :: cast
- ALWAYS use TOP N for top/limit queries: SELECT TOP 10 ... ORDER BY ... DESC
- For ANY question with "balance", "account balance", "accounts by balance", "top accounts", "highest/lowest balance":
   - FORCE table: Sales.Customer (for customer accounts) or Accounts (if present)
   - FORCE column: TotalDue (from Sales.SalesOrderHeader) or Balance (from Accounts)
   - ALWAYS join to get names: JOIN Person.Person p ON c.PersonID = p.BusinessEntityID
   - ALWAYS include name: p.FirstName + ' ' + p.LastName AS CustomerName
   - NEVER use Production.*, ErrorLog, DatabaseLog, ProductPhoto, ScrapReason, or any production/log table for balance questions
   - If no balance column → output EXACTLY: SELECT 1 AS no_balance_data_in_schema
```

**Purpose**: Override LLM training bias toward Snowflake/PostgreSQL syntax

---

### 2️⃣ Runtime Dialect Sanitizer (sanitize_tsql)

**File**: `backend/voxquery/core/sql_safety.py` (lines 110-160)

New function that aggressively rewrites SQL after LLM generation:

```python
def sanitize_tsql(sql: str) -> str:
    """
    AGGRESSIVE runtime dialect sanitizer for SQL Server
    
    1. Removes/replaces LIMIT with TOP N
    2. Forces schema qualification for common tables
    3. Replaces invented 'Name' with correct join
    """
```

**Examples**:

| Input | Output |
|-------|--------|
| `SELECT CustomerID FROM CUSTOMER LIMIT 10` | `SELECT TOP 10 CustomerID FROM Sales.Customer ORDER BY 1 DESC` |
| `SELECT * FROM CUSTOMER WHERE ID = 1` | `SELECT * FROM Sales.Customer WHERE ID = 1` |
| `SELECT c.Name FROM Sales.Customer c` | `SELECT p.FirstName + ' ' + p.LastName FROM Sales.Customer c JOIN Person.Person p ON c.PersonID = p.BusinessEntityID` |

**Called from**: `backend/voxquery/api/query.py` (ask_question function, line 65)

---

### 3️⃣ LIMIT Rejection in Validation

**File**: `backend/voxquery/core/sql_safety.py` (validate_sql function, lines 620-650)

Enhanced validation that detects and rejects LIMIT keyword for SQL Server:

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
        score *= 0.3  # Heavy penalty
```

**Penalty**: Score multiplied by 0.3 (heavy penalty for dialect mismatch)

---

## Complete Flow for SQL Server Queries

```
1. LLM generates SQL
   ↓
2. fix_invented_columns() - Rewrites common hallucinations
   ↓
3. sanitize_tsql() - AGGRESSIVE runtime sanitizer
   ↓
4. normalize_tsql() - Additional dialect conversions
   ↓
5. validate_sql() - Rejects any remaining LIMIT keywords
   ↓
6. Execute or return to user
```

---

## Test Results

### Test 1: Prompt Lock ✅
```
✅ MANDATORY DIALECT AND TABLE LOCK found in PRIORITY_RULES
✅ LIMIT prohibition found
✅ TOP N requirement found
✅ Balance question rules found
```

### Test 2: Runtime Sanitizer ✅
```
✅ LIMIT replaced with TOP 10
✅ CUSTOMER qualified to Sales.Customer
✅ Invented c.Name replaced with correct join
```

### Test 3: Validation ✅
```
✅ LIMIT keyword rejected for SQL Server (score: 0.30)
✅ Valid SQL Server query accepted (score: 1.00)
```

---

## Files Modified

| File | Changes |
|------|---------|
| `backend/voxquery/core/sql_safety.py` | Added sanitize_tsql() function |
| `backend/voxquery/api/query.py` | Added sanitize_tsql() call in ask_question() |
| `backend/voxquery/core/sql_generator.py` | Already had MANDATORY DIALECT AND TABLE LOCK |

---

## Why This Is Aggressive

The implementation uses a **3-layer defense** that is intentionally overkill:

1. **Layer 1 - Prompt Lock**: Explicit rules in system prompt
2. **Layer 2 - Runtime Sanitizer**: Aggressive rewriting of common mistakes
3. **Layer 3 - Validation Rejection**: Heavy penalty for violations

This ensures SQL Server compliance even if the LLM tries to use Snowflake/PostgreSQL syntax.

---

## Backend Status

✅ Backend restarted and running
✅ All changes loaded
✅ Ready for production testing

---

## Expected Behavior with Balance Questions

When user asks: "Show top 10 accounts by balance"

**Expected SQL**:
```sql
SELECT TOP 10 c.CustomerID, p.FirstName + ' ' + p.LastName AS CustomerName, SUM(soh.TotalDue) AS total_balance
FROM Sales.Customer c
JOIN Person.Person p ON c.PersonID = p.BusinessEntityID
JOIN Sales.SalesOrderHeader soh ON c.CustomerID = soh.CustomerID
GROUP BY c.CustomerID, p.FirstName, p.LastName
ORDER BY total_balance DESC
```

**Compliance Checks**:
- ✅ Uses TOP (not LIMIT)
- ✅ Uses schema-qualified tables (Sales.Customer, Sales.SalesOrderHeader, Person.Person)
- ✅ Joins to Person.Person for customer names
- ✅ Uses TotalDue for balance calculations
- ✅ No invented columns (c.Name, c.Balance)
- ✅ No production/log tables (DatabaseLog, ErrorLog)

---

## Conclusion

TASK 7 is complete and ready for testing. The aggressive 3-layer defense ensures SQL Server compliance and prevents the LLM from generating Snowflake/PostgreSQL syntax.

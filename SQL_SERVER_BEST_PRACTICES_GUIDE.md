# SQL Server Best Practices Guide for Groq ✅

## Critical SQL Server Syntax Rules

### 1. Subquery Structure (MOST IMPORTANT)

❌ **WRONG** - Bare FROM inside subquery:
```sql
SELECT COUNT(DISTINCT Object) AS unique_objects
FROM (
    FROM DatabaseLog
    (Object, COUNT(*) AS modification_count)
    GROUP BY Object
) AS modifications
```

✅ **CORRECT** - Full SELECT ... FROM ... WHERE ... GROUP BY:
```sql
SELECT COUNT(DISTINCT Object) AS unique_objects
FROM (
    SELECT Object, COUNT(*) AS modification_count
    FROM DatabaseLog
    WHERE Object IS NOT NULL
    GROUP BY Object
) t
```

**Rule**: Every subquery must be a complete SELECT statement with:
- SELECT clause (what columns)
- FROM clause (which table)
- WHERE clause (optional, but recommended)
- GROUP BY clause (if aggregating)

### 2. AVG() with INT Columns

❌ **WRONG** - Truncates to integer:
```sql
SELECT AVG(modification_count) AS average_modifications
FROM modifications
-- Returns: 3 (truncated)
```

✅ **CORRECT** - Force decimal division:
```sql
SELECT AVG(1.0 * modification_count) AS average_modifications
FROM modifications
-- Returns: 3.45 (proper decimal)
```

**Rule**: Multiply INT columns by 1.0 before AVG() to force decimal division.

### 3. UNION ALL Syntax

❌ **WRONG** - Incomplete SELECT statements:
```sql
SELECT * FROM (
    UNION ALL SELECT Object, COUNT(*) FROM DatabaseLog
) t
```

✅ **CORRECT** - Both sides are complete SELECT statements:
```sql
SELECT Object, modification_count FROM (
    SELECT Object, COUNT(*) AS modification_count
    FROM DatabaseLog
    WHERE Object IS NOT NULL
    GROUP BY Object
    UNION ALL
    SELECT 'TOTAL', COUNT(*)
    FROM DatabaseLog
) t
```

**Rule**: UNION ALL requires both sides to be complete SELECT statements with identical column counts.

### 4. CTEs (WITH Clause) - Preferred for Complex Queries

❌ **WRONG** - Deeply nested subqueries:
```sql
SELECT * FROM (
    SELECT * FROM (
        SELECT * FROM (
            SELECT * FROM DatabaseLog
        ) t1
    ) t2
) t3
```

✅ **CORRECT** - Use CTEs for clarity:
```sql
WITH mods AS (
    SELECT Object, COUNT(*) AS modification_count
    FROM DatabaseLog
    WHERE Object IS NOT NULL
    GROUP BY Object
)
SELECT 
    COUNT(*) AS unique_objects,
    AVG(1.0 * modification_count) AS average_modifications
FROM mods
```

**Rule**: Use CTEs (WITH clause) for multi-step queries — cleaner, more readable, and often faster.

## Common Patterns

### Pattern 1: Count Distinct + Average

**Problem**: "What is the distribution of ErrorSeverity levels in the ErrorLog, if it were populated?"

✅ **Solution**:
```sql
SELECT 
    ErrorSeverity,
    COUNT(*) AS error_count
FROM ErrorLog
WHERE ErrorSeverity IS NOT NULL
GROUP BY ErrorSeverity
ORDER BY error_count DESC
```

### Pattern 2: Unique Objects + Average Modifications

**Problem**: "How many unique Objects are modified in the DatabaseLog, and what is the average number of modifications per Object?"

✅ **Solution 1** (with subquery):
```sql
SELECT 
    COUNT(DISTINCT Object) AS unique_objects,
    AVG(1.0 * modification_count) AS average_modifications
FROM (
    SELECT Object, COUNT(*) AS modification_count
    FROM DatabaseLog
    WHERE Object IS NOT NULL
    GROUP BY Object
) t
```

✅ **Solution 2** (with CTE - preferred):
```sql
WITH mods AS (
    SELECT Object, COUNT(*) AS modification_count
    FROM DatabaseLog
    WHERE Object IS NOT NULL
    GROUP BY Object
)
SELECT 
    COUNT(*) AS unique_objects,
    AVG(1.0 * modification_count) AS average_modifications
FROM mods
```

### Pattern 3: Top N by Aggregate

**Problem**: "Show top 10 customers by total sales"

✅ **Solution**:
```sql
SELECT TOP 10
    CustomerID,
    SUM(CAST(TotalDue AS DECIMAL(18,2))) AS total_sales
FROM Sales.SalesOrderHeader
WHERE CustomerID IS NOT NULL
GROUP BY CustomerID
ORDER BY total_sales DESC
```

## SQL Server Specific Features

### 1. TOP N (instead of LIMIT)
```sql
SELECT TOP 10 * FROM Sales.Customer
```

### 2. VARCHAR with Length
```sql
DECLARE @name VARCHAR(100)  -- Always specify length
```

### 3. CAST for Type Conversion
```sql
CAST(amount AS DECIMAL(18,2))  -- For money
CAST(date_str AS DATE)          -- For dates
CAST(count AS FLOAT)            -- For division
```

### 4. DATEADD for Date Math
```sql
DATEADD(DAY, -30, GETDATE())    -- 30 days ago
DATEADD(MONTH, 1, GETDATE())    -- Next month
```

### 5. DATEDIFF for Date Difference
```sql
DATEDIFF(DAY, start_date, end_date)
DATEDIFF(MONTH, hire_date, GETDATE())
```

## What NOT to Do

❌ **Don't use LIMIT** - Use TOP instead
```sql
-- WRONG
SELECT * FROM Sales.Customer LIMIT 10

-- CORRECT
SELECT TOP 10 * FROM Sales.Customer
```

❌ **Don't use QUALIFY** - That's Snowflake
```sql
-- WRONG
SELECT * FROM Sales.Customer QUALIFY ROW_NUMBER() OVER (ORDER BY CustomerID) = 1

-- CORRECT
SELECT TOP 1 * FROM Sales.Customer ORDER BY CustomerID
```

❌ **Don't use ARRAY_AGG** - That's PostgreSQL/Snowflake
```sql
-- WRONG
SELECT ARRAY_AGG(ProductName) FROM Products

-- CORRECT
SELECT STRING_AGG(ProductName, ', ') FROM Products
```

❌ **Don't write bare FROM in subqueries**
```sql
-- WRONG
FROM (
    FROM DatabaseLog
    WHERE Object IS NOT NULL
)

-- CORRECT
FROM (
    SELECT * FROM DatabaseLog
    WHERE Object IS NOT NULL
)
```

## Performance Tips

1. **Use CTEs instead of nested subqueries** - More readable and often faster
2. **Filter early with WHERE** - Reduce rows before aggregating
3. **Use TOP instead of LIMIT** - SQL Server native syntax
4. **Avoid SELECT *** - Specify only needed columns
5. **Use proper indexes** - Schema already has them

## Updated Dialect Instructions

The SQL Server dialect file now includes:
- ✅ Subquery structure rules
- ✅ AVG() with INT columns (1.0 * column)
- ✅ UNION ALL requirements
- ✅ CTE recommendations
- ✅ No table invention rule

---

**Last Updated**: January 26, 2026
**Status**: Production Ready ✅

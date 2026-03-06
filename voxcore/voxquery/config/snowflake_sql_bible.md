# Snowflake SQL Bible - Complete Reference

## Core Syntax

### SELECT Statement
```sql
SELECT [ DISTINCT ] <select_list>
FROM <table_reference>
[ WHERE <condition> ]
[ GROUP BY <grouping_columns> ]
[ HAVING <condition> ]
[ ORDER BY <sort_list> ]
[ LIMIT <number> ]
```

### Data Types
- VARCHAR, STRING - Text
- NUMBER, DECIMAL, NUMERIC - Decimal numbers
- INT, INTEGER, BIGINT - Whole numbers
- FLOAT, DOUBLE - Floating point
- DATE - Date only
- TIMESTAMP, TIMESTAMP_NTZ - Date and time
- BOOLEAN - True/False
- ARRAY - Array type
- OBJECT - JSON object
- VARIANT - Semi-structured data

### Operators
- `=`, `!=`, `<>` - Equality
- `<`, `>`, `<=`, `>=` - Comparison
- `AND`, `OR`, `NOT` - Logical
- `IN`, `NOT IN` - List membership
- `BETWEEN` - Range
- `LIKE`, `ILIKE` - Pattern matching
- `IS NULL`, `IS NOT NULL` - Null checks

## Common Functions

### String Functions
```sql
UPPER(string) - Convert to uppercase
LOWER(string) - Convert to lowercase
LENGTH(string) - String length
SUBSTRING(string, start, length) - Extract substring
CONCAT(str1, str2, ...) - Concatenate strings
TRIM(string) - Remove leading/trailing spaces
REPLACE(string, from, to) - Replace text
SPLIT_PART(string, delimiter, position) - Split string
```

### Numeric Functions
```sql
ABS(number) - Absolute value
ROUND(number, decimals) - Round to decimals
CEIL(number) - Round up
FLOOR(number) - Round down
MOD(number, divisor) - Modulo
POWER(base, exponent) - Power
SQRT(number) - Square root
```

### Date Functions
```sql
CURRENT_DATE() - Today's date
CURRENT_TIMESTAMP() - Current date and time
DATE_TRUNC(unit, date) - Truncate date to unit
DATEADD(unit, number, date) - Add to date
DATEDIFF(unit, date1, date2) - Difference between dates
EXTRACT(unit FROM date) - Extract part of date
TO_DATE(string, format) - Convert string to date
TO_TIMESTAMP(string, format) - Convert string to timestamp
YEAR(date), MONTH(date), DAY(date) - Extract parts
QUARTER(date) - Get quarter (1-4)
WEEK(date) - Get week number
DAYOFWEEK(date) - Day of week (1=Sunday)
```

### Aggregate Functions
```sql
COUNT(*) - Count all rows
COUNT(column) - Count non-null values
COUNT(DISTINCT column) - Count distinct values
SUM(column) - Sum of values
AVG(column) - Average of values
MIN(column) - Minimum value
MAX(column) - Maximum value
STDDEV(column) - Standard deviation
VARIANCE(column) - Variance
LISTAGG(column, delimiter) - Concatenate values
```

### Window Functions
```sql
ROW_NUMBER() OVER (PARTITION BY col ORDER BY col) - Row number
RANK() OVER (PARTITION BY col ORDER BY col) - Rank with gaps
DENSE_RANK() OVER (PARTITION BY col ORDER BY col) - Rank without gaps
LAG(column) OVER (ORDER BY col) - Previous row value
LEAD(column) OVER (ORDER BY col) - Next row value
FIRST_VALUE(column) OVER (ORDER BY col) - First value in window
LAST_VALUE(column) OVER (ORDER BY col) - Last value in window
SUM(column) OVER (PARTITION BY col ORDER BY col) - Running sum
AVG(column) OVER (PARTITION BY col ORDER BY col) - Running average
```

## JOIN Types

### INNER JOIN
```sql
SELECT a.col1, b.col2
FROM table_a a
INNER JOIN table_b b ON a.id = b.id
```

### LEFT JOIN (LEFT OUTER JOIN)
```sql
SELECT a.col1, b.col2
FROM table_a a
LEFT JOIN table_b b ON a.id = b.id
```

### RIGHT JOIN (RIGHT OUTER JOIN)
```sql
SELECT a.col1, b.col2
FROM table_a a
RIGHT JOIN table_b b ON a.id = b.id
```

### FULL OUTER JOIN
```sql
SELECT a.col1, b.col2
FROM table_a a
FULL OUTER JOIN table_b b ON a.id = b.id
```

### CROSS JOIN
```sql
SELECT a.col1, b.col2
FROM table_a a
CROSS JOIN table_b b
```

## GROUP BY and HAVING

```sql
SELECT 
    category,
    COUNT(*) as count,
    SUM(amount) as total,
    AVG(amount) as average
FROM sales
WHERE date >= '2024-01-01'
GROUP BY category
HAVING SUM(amount) > 1000
ORDER BY total DESC
```

## Common Table Expressions (CTEs)

```sql
WITH sales_summary AS (
    SELECT 
        category,
        SUM(amount) as total
    FROM sales
    GROUP BY category
)
SELECT * FROM sales_summary WHERE total > 1000
```

## CASE Statements

```sql
SELECT 
    name,
    CASE 
        WHEN age < 18 THEN 'Minor'
        WHEN age < 65 THEN 'Adult'
        ELSE 'Senior'
    END as age_group
FROM users
```

## Subqueries

```sql
SELECT * FROM (
    SELECT id, name, amount
    FROM sales
    WHERE amount > 100
) subquery
WHERE name LIKE 'A%'
```

## Set Operations

```sql
-- UNION (removes duplicates)
SELECT col1 FROM table1
UNION
SELECT col1 FROM table2

-- UNION ALL (keeps duplicates)
SELECT col1 FROM table1
UNION ALL
SELECT col1 FROM table2

-- INTERSECT (common rows)
SELECT col1 FROM table1
INTERSECT
SELECT col1 FROM table2

-- EXCEPT (rows in first but not second)
SELECT col1 FROM table1
EXCEPT
SELECT col1 FROM table2
```

## Filtering and Sorting

```sql
-- WHERE clause
WHERE column = value
WHERE column IN (1, 2, 3)
WHERE column BETWEEN 10 AND 20
WHERE column LIKE 'A%'
WHERE column IS NULL
WHERE column IS NOT NULL

-- ORDER BY
ORDER BY column ASC
ORDER BY column DESC
ORDER BY col1 ASC, col2 DESC

-- LIMIT
LIMIT 10
LIMIT 10 OFFSET 20
```

## Common Patterns

### Year-to-Date (YTD)
```sql
SELECT SUM(amount) as ytd_total
FROM sales
WHERE YEAR(sale_date) = YEAR(CURRENT_DATE())
```

### Month-to-Date (MTD)
```sql
SELECT SUM(amount) as mtd_total
FROM sales
WHERE YEAR(sale_date) = YEAR(CURRENT_DATE())
  AND MONTH(sale_date) = MONTH(CURRENT_DATE())
```

### Quarter-to-Date (QTD)
```sql
SELECT SUM(amount) as qtd_total
FROM sales
WHERE YEAR(sale_date) = YEAR(CURRENT_DATE())
  AND QUARTER(sale_date) = QUARTER(CURRENT_DATE())
```

### Last N Days
```sql
SELECT * FROM sales
WHERE sale_date >= DATEADD(DAY, -30, CURRENT_DATE())
```

### Last N Months
```sql
SELECT * FROM sales
WHERE sale_date >= DATEADD(MONTH, -3, CURRENT_DATE())
```

### Top N by Group
```sql
SELECT * FROM (
    SELECT 
        category,
        product,
        sales,
        ROW_NUMBER() OVER (PARTITION BY category ORDER BY sales DESC) as rn
    FROM products
)
WHERE rn <= 5
```

### Running Total
```sql
SELECT 
    date,
    amount,
    SUM(amount) OVER (ORDER BY date) as running_total
FROM sales
ORDER BY date
```

### Percent of Total
```sql
SELECT 
    category,
    SUM(amount) as total,
    SUM(amount) / SUM(SUM(amount)) OVER () * 100 as percent
FROM sales
GROUP BY category
```

## Snowflake-Specific Features

### QUALIFY Clause (Snowflake-specific)
```sql
SELECT 
    category,
    product,
    sales,
    ROW_NUMBER() OVER (PARTITION BY category ORDER BY sales DESC) as rn
FROM products
QUALIFY rn <= 5
```

### PIVOT
```sql
SELECT *
FROM (
    SELECT month, region, sales FROM sales_data
)
PIVOT (
    SUM(sales)
    FOR region IN ('North', 'South', 'East', 'West')
)
```

### UNPIVOT
```sql
SELECT *
FROM sales_pivot
UNPIVOT (
    sales
    FOR region IN (north, south, east, west)
)
```

### FLATTEN (for JSON/ARRAY)
```sql
SELECT *
FROM table_with_json,
LATERAL FLATTEN(input => json_column)
```

### LATERAL (for correlated subqueries)
```sql
SELECT t1.id, t2.value
FROM table1 t1,
LATERAL (
    SELECT value FROM table2 WHERE table2.id = t1.id
) t2
```

## Performance Tips

1. Use WHERE to filter early
2. Use LIMIT to reduce result set
3. Use appropriate data types
4. Avoid SELECT * when possible
5. Use indexes on frequently filtered columns
6. Use PARTITION BY in window functions
7. Use QUALIFY instead of WHERE for window functions
8. Avoid nested subqueries when possible
9. Use CTEs for readability
10. Use DISTINCT sparingly

## Common Mistakes to Avoid

1. ❌ Forgetting GROUP BY when using aggregates
2. ❌ Using non-aggregated columns without GROUP BY
3. ❌ Comparing with NULL using = (use IS NULL)
4. ❌ Using HAVING without GROUP BY
5. ❌ Forgetting ORDER BY in window functions
6. ❌ Using UNION instead of UNION ALL when duplicates are OK
7. ❌ Not using PARTITION BY in window functions
8. ❌ Forgetting to alias subqueries
9. ❌ Using SELECT * in production queries
10. ❌ Not considering NULL values in calculations

## Examples

### Sales Analysis
```sql
SELECT 
    DATE_TRUNC('MONTH', sale_date) as month,
    region,
    COUNT(*) as transaction_count,
    SUM(amount) as total_sales,
    AVG(amount) as avg_sale,
    MIN(amount) as min_sale,
    MAX(amount) as max_sale
FROM sales
WHERE sale_date >= DATEADD(MONTH, -12, CURRENT_DATE())
GROUP BY DATE_TRUNC('MONTH', sale_date), region
ORDER BY month DESC, region
```

### Customer Segmentation
```sql
SELECT 
    customer_id,
    customer_name,
    COUNT(*) as purchase_count,
    SUM(amount) as total_spent,
    AVG(amount) as avg_purchase,
    MAX(purchase_date) as last_purchase,
    CASE 
        WHEN SUM(amount) > 10000 THEN 'VIP'
        WHEN SUM(amount) > 5000 THEN 'Premium'
        ELSE 'Standard'
    END as segment
FROM orders
GROUP BY customer_id, customer_name
HAVING COUNT(*) > 5
ORDER BY total_spent DESC
```

### Time Series Analysis
```sql
SELECT 
    DATE_TRUNC('DAY', event_date) as day,
    event_type,
    COUNT(*) as event_count,
    COUNT(DISTINCT user_id) as unique_users,
    SUM(CASE WHEN status = 'success' THEN 1 ELSE 0 END) as success_count
FROM events
WHERE event_date >= DATEADD(DAY, -30, CURRENT_DATE())
GROUP BY DATE_TRUNC('DAY', event_date), event_type
ORDER BY day DESC, event_type
```

---

**This is the complete Snowflake SQL reference. Use these patterns and functions to generate accurate SQL queries.**

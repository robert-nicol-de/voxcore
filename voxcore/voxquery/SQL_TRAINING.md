# SQL Generation Training Guide

## Overview
The VoxQuery LLM has been trained to generate accurate SQL queries using:
1. **Few-shot examples** - Real SQL patterns for common queries
2. **SQL rules** - Best practices for query generation
3. **Schema validation** - Automatic table/column name correction
4. **Query optimization** - Proper use of aggregation, filtering, and sorting

## SQL Generation Rules

The LLM follows these rules when generating SQL:

### 1. Aggregation
- Always use proper aggregation functions: SUM, COUNT, AVG, MAX, MIN
- Use GROUP BY when aggregating
- Example: `SELECT category, COUNT(*) as item_count FROM items GROUP BY category`

### 2. Filtering
- Use WHERE clause for filtering
- Use HAVING for filtering aggregated results
- Example: `SELECT category, COUNT(*) FROM items GROUP BY category HAVING COUNT(*) > 5`

### 3. Sorting
- Use ORDER BY to sort results
- Use DESC for descending order
- Example: `SELECT * FROM sales ORDER BY amount DESC LIMIT 10`

### 4. Limiting Results
- Use LIMIT to restrict rows (Snowflake, PostgreSQL)
- Use TOP for SQL Server
- Example: `SELECT * FROM customers LIMIT 100`

### 5. Joins
- Use JOIN for related tables
- Specify join conditions clearly
- Example: `SELECT c.name, COUNT(o.id) FROM customers c LEFT JOIN orders o ON c.id = o.customer_id GROUP BY c.id`

### 6. Date Functions
- Use appropriate date functions for your database
- Snowflake: DATE_TRUNC, DATEDIFF
- PostgreSQL: DATE_TRUNC, EXTRACT
- SQL Server: DATEPART, DATEDIFF
- Example: `SELECT DATE_TRUNC('month', order_date) as month, SUM(amount) FROM orders GROUP BY DATE_TRUNC('month', order_date)`

## Few-Shot Examples

The LLM learns from these examples:

### Example 1: Top Items by Sales
**Question:** Show top 5 items by sales
**SQL:** 
```sql
SELECT item_name, SUM(sales) as total_sales 
FROM sales 
GROUP BY item_name 
ORDER BY total_sales DESC 
LIMIT 5
```

### Example 2: Category Analysis
**Question:** Which category has most items?
**SQL:**
```sql
SELECT category, COUNT(*) as item_count 
FROM items 
GROUP BY category 
ORDER BY item_count DESC 
LIMIT 1
```

### Example 3: Average by Category
**Question:** Average price by category
**SQL:**
```sql
SELECT category, AVG(price) as avg_price 
FROM items 
GROUP BY category 
ORDER BY avg_price DESC
```

## Schema Validation

The system automatically:
1. **Validates table names** - Corrects case sensitivity issues
2. **Validates column names** - Ensures columns exist in tables
3. **Fixes references** - Automatically corrects table/column references

## Performance Optimization

The LLM is configured for:
- **Temperature: 0.1** - Deterministic, consistent SQL generation
- **Max tokens: 200** - Balanced between quality and speed
- **Few-shot learning** - Learns from examples for better accuracy

## Troubleshooting

### Issue: "Table does not exist"
**Solution:** The LLM may have used the wrong table name. Check:
1. Table names in your schema
2. Case sensitivity (Snowflake is case-sensitive)
3. Schema/database prefix if needed

### Issue: "Column does not exist"
**Solution:** Verify the column exists in the table. The system will try to auto-correct, but check:
1. Column spelling
2. Column case sensitivity
3. Table alias usage

### Issue: Slow SQL generation
**Solution:** 
1. Use a faster model: `ollama pull mistral:7b`
2. Reduce schema complexity
3. Ask simpler questions

## Customization

To add more training examples, edit the `_build_prompt` method in `backend/voxquery/core/sql_generator.py`:

```python
examples = """EXAMPLES:
Q: Your question here
A: SELECT ... your SQL here

Q: Another question
A: SELECT ... another SQL here"""
```

## Database-Specific Features

### Snowflake
- Use QUALIFY for window functions
- Use DATE_TRUNC for date truncation
- Case-sensitive identifiers (use quotes)

### PostgreSQL
- Use EXTRACT for date parts
- Use ARRAY_AGG for array aggregation
- Full-text search with @@

### SQL Server
- Use TOP instead of LIMIT
- Use DATEPART for date functions
- Use STRING_AGG for concatenation

### BigQuery
- Use UNNEST for arrays
- Use STRUCT for complex types
- Use backticks for identifiers

### Redshift
- Similar to PostgreSQL
- Use DISTKEY/SORTKEY for optimization
- Use UNLOAD for exports

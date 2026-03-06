# Golden Set - Expected SQL Added (3 of 12)

## Status
✅ Added production-ready Snowflake SQL for the first 3 priority questions (val set)

## Questions Updated

### 1. What are my YTD sales vs budget by store and category?
**Split**: val  
**Difficulty**: Intermediate  
**Key Patterns**:
- FULL OUTER JOIN (handles stores/categories with only budget or only sales)
- DATE_TRUNC('year') for YTD filtering
- COALESCE for NULL handling
- Variance calculation ($ and %)
- NULLS LAST for clean ordering

**Tables**: sales_fact, product_dim, budget_plan, store_dim  
**Key Columns**: transaction_date, revenue_amount, store_id, category_name, budget_amount, budget_year

---

### 2. Show gross profit percent MTD versus same month last year by department.
**Split**: val  
**Difficulty**: Intermediate  
**Key Patterns**:
- Dual CTEs for current MTD vs same month last year
- DATEADD(year, -1, ...) for YoY comparison
- Margin % calculation with NULL-safe division
- Margin change in percentage points (not relative %)
- FULL OUTER JOIN for departments appearing in only one period

**Tables**: sales_fact, product_dim  
**Key Columns**: transaction_date, revenue_amount, cogs_amount, department_name

---

### 3. Weekly sales trend for Electronics category over the last 12 weeks — show as line-ready data.
**Split**: val  
**Difficulty**: Beginner-Intermediate  
**Key Patterns**:
- DATE_TRUNC('week') for time-series grouping
- DATEADD(week, -12, ...) for 12-week lookback
- Category filter in WHERE clause
- One row per week (perfect for line charts)
- Optional metrics: transaction_count, avg_price_per_unit

**Tables**: sales_fact, product_dim  
**Key Columns**: transaction_date, revenue_amount, category_name, transaction_id, units

---

## Snowflake Best Practices Demonstrated

✅ **CTEs for Readability**: All queries use WITH clauses to break logic into digestible steps  
✅ **Date Handling**: DATE_TRUNC + DATEADD for precise period filtering  
✅ **NULL Safety**: COALESCE, NULLIF, and CASE for division by zero  
✅ **Proper Joins**: FULL OUTER JOIN where needed, LEFT JOIN for lookups  
✅ **Rounding**: ROUND(..., 2) for currency/percentages  
✅ **Ordering**: Business-sensible ORDER BY with NULLS LAST  
✅ **No T-SQL**: No TOP, no +, no CONVERT — pure Snowflake  

---

## Next Steps

### Immediate (This Week)
- [ ] Add expected_sql for remaining 9 golden set questions (4-12)
- [ ] Test these 3 queries against your actual Snowflake schema
- [ ] Adjust table/column names if they differ from schema

### Week 2
- [ ] Build evaluation harness (Python script)
- [ ] Run baseline metrics on current Groq performance
- [ ] Document any schema mismatches

### Week 3
- [ ] Use these 3 as few-shot examples in Groq prompt
- [ ] Iterate on prompt wording
- [ ] Track improvement on val set

---

## Schema Assumptions

These queries assume the following table structure:

```sql
-- sales_fact
CREATE TABLE sales_fact (
  transaction_id INT,
  transaction_date DATE,
  store_id INT,
  product_id INT,
  revenue_amount DECIMAL(12,2),
  cogs_amount DECIMAL(12,2),
  units INT
);

-- product_dim
CREATE TABLE product_dim (
  product_id INT,
  category_name VARCHAR,
  department_name VARCHAR
);

-- budget_plan
CREATE TABLE budget_plan (
  store_id INT,
  category_name VARCHAR,
  budget_amount DECIMAL(12,2),
  budget_year INT,
  budget_period VARCHAR
);

-- store_dim
CREATE TABLE store_dim (
  store_id INT,
  store_name VARCHAR,
  region VARCHAR
);
```

**If your schema differs**, update the table/column names in the expected_sql field.

---

## Testing These Queries

To validate these queries work with your data:

```python
import snowflake.connector

conn = snowflake.connector.connect(
    user='YOUR_USER',
    password='YOUR_PASSWORD',
    account='YOUR_ACCOUNT',
    warehouse='YOUR_WAREHOUSE',
    database='YOUR_DATABASE'
)

queries = [
    # Query 1: YTD sales vs budget
    "WITH sales_ytd AS (...)",
    # Query 2: MTD gross profit
    "WITH mtd_current AS (...)",
    # Query 3: Weekly trend
    "SELECT DATE_TRUNC('week', ..."
]

for i, query in enumerate(queries, 1):
    try:
        cursor = conn.cursor()
        cursor.execute(query)
        results = cursor.fetchall()
        print(f"✅ Query {i}: {len(results)} rows returned")
    except Exception as e:
        print(f"❌ Query {i}: {e}")
```

---

## Files Updated
- `backend/training_questions.json` - Added expected_sql, relevant_tables, key_columns for questions 1, 2, 5

## Files to Create Next
- `backend/evaluation_harness.py` - Python script to test generated vs expected SQL
- `backend/GOLDEN_SET_SQL_ADDED_4_12.md` - Document for remaining 9 questions

---

**Status**: Ready for schema validation and evaluation harness build

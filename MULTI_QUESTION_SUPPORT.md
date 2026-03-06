# Multi-Question Support in VoxQuery

## Overview

VoxQuery now supports handling multiple questions in a single prompt. You can ask questions like:
- "Show me MTD and YTD revenue"
- "Compare Q1 and Q2 sales"
- "Give me revenue and costs"
- "Top 5 items and bottom 5 items"

## How It Works

### Detection
The system automatically detects multi-question requests by looking for patterns:
- `and` keyword between metrics (e.g., "MTD and YTD")
- Comma-separated questions (e.g., "revenue, and costs")
- Time period comparisons (e.g., "this month and last month")

### Processing

**Option 1: LLM Optimization (Default)**
When the LLM can intelligently combine the questions into a single optimized query, it does so:
```sql
-- Example: "Show me revenue and costs"
SELECT 
  SUM(sale_price_usd) as revenue,
  SUM(cost_of_goods_usd) as costs
FROM menu
```

**Option 2: UNION ALL Combination**
When the LLM generates multiple SELECT statements, they are automatically combined with UNION ALL:
```sql
-- Example: "Top 5 items and bottom 5 items"
SELECT menu_item_name, sale_price_usd FROM menu ORDER BY sale_price_usd DESC LIMIT 5
UNION ALL
SELECT menu_item_name, sale_price_usd FROM menu ORDER BY sale_price_usd ASC LIMIT 5
```

## Supported Patterns

### Time Period Comparisons
- "MTD and YTD" → Month-to-date and Year-to-date
- "Q1 and Q2" → Quarter 1 and Quarter 2
- "This month and last month"
- "This year and last year"
- "This week and last week"

### Metric Comparisons
- "Revenue and costs"
- "Sales and returns"
- "Profit and loss"

### Data Range Comparisons
- "Top 5 and bottom 5"
- "High performers and low performers"
- "Best and worst"

## Examples

### Example 1: MTD vs YTD
```
User: "Show me revenue MTD and YTD"

Generated SQL:
SELECT 
  SUM(CASE WHEN MONTH(date_column) = MONTH(CURRENT_DATE) 
           AND YEAR(date_column) = YEAR(CURRENT_DATE)
      THEN sale_price_usd ELSE 0 END) AS mtd_revenue,
  SUM(CASE WHEN YEAR(date_column) = YEAR(CURRENT_DATE)
      THEN sale_price_usd ELSE 0 END) AS ytd_revenue
FROM menu
```

### Example 2: Quarterly Comparison
```
User: "Compare Q1 and Q2 sales"

Generated SQL:
SELECT 
  menu_item_name,
  SUM(CASE WHEN QUARTER(date_column) = 1 THEN sale_price_usd ELSE 0 END) AS q1_sales,
  SUM(CASE WHEN QUARTER(date_column) = 2 THEN sale_price_usd ELSE 0 END) AS q2_sales
FROM menu
GROUP BY menu_item_name
```

### Example 3: Multiple Metrics
```
User: "Give me revenue and costs"

Generated SQL:
SELECT 
  SUM(sale_price_usd) as revenue,
  SUM(cost_of_goods_usd) as costs
FROM menu
```

### Example 4: Top and Bottom (UNION ALL)
```
User: "Top 5 items and bottom 5 items"

Generated SQL:
SELECT menu_item_name, sale_price_usd FROM menu ORDER BY sale_price_usd DESC LIMIT 5
UNION ALL
SELECT menu_item_name, sale_price_usd FROM menu ORDER BY sale_price_usd ASC LIMIT 5
```

## Implementation Details

### Files Modified
- `backend/voxquery/core/sql_generator.py`
  - Added `_is_multi_question()` - Detects multi-question patterns
  - Added `_generate_multi_question()` - Handles multi-question logic
  - Added `_split_multi_question()` - Splits questions into sub-questions
  - Added `_combine_multiple_selects()` - Combines multiple SELECTs with UNION ALL
  - Added `_get_cte_name()` - Generates meaningful CTE names
  - Modified `_extract_sql()` - Detects and combines multiple SELECT statements
  - Modified `generate()` - Routes to single or multi-question handler

### Detection Patterns
```python
multi_patterns = [
    r'\band\b',  # " and "
    r',\s*(?:and\s+)?(?:also\s+)?(?:show|give|get)',  # ", and show"
    r'(?:MTD|YTD|QTD|Q\d|month|quarter|year)\s+(?:and|vs|versus)',  # "MTD and YTD"
]
```

### SQL Combining Logic
When the LLM generates multiple SELECT statements:
1. Detect multiple SELECT keywords in the response
2. Split by SELECT keyword boundaries
3. Clean up each statement (remove semicolons, ensure SELECT prefix)
4. Join with UNION ALL
5. Return combined SQL

Example transformation:
```
Input:  "SELECT ... FROM menu; SELECT ... FROM menu;"
Output: "SELECT ... FROM menu UNION ALL SELECT ... FROM menu"
```

## Limitations

1. **Column Compatibility**: UNION ALL requires compatible column structures
2. **Performance**: Multiple queries can impact performance on large datasets
3. **Warehouse Support**: Some warehouses may have limitations on UNION depth
4. **Result Rows**: Each SELECT contributes to the row limit

## Testing

The SQL combining logic has been tested with:
- Two simple SELECTs ✓
- Multiple SELECTs with different queries ✓
- Three or more SELECTs ✓

All tests confirm proper UNION ALL structure generation.

## Future Enhancements

1. **Smart Result Formatting**: Automatically format results side-by-side for comparisons
2. **Visualization**: Generate comparison charts automatically
3. **Caching**: Cache sub-question results for faster execution
4. **Parallel Execution**: Execute sub-questions in parallel for better performance
5. **Natural Language Refinement**: Better parsing of complex multi-question patterns

## Troubleshooting

### Issue: "Actual statement count 5 did not match the desired statement count 1"
**Solution**: This error means multiple SELECT statements were generated. The fix automatically combines them with UNION ALL. If you still see this error, ensure the backend has been restarted after the update.

### Issue: UNION ALL returns incompatible columns
**Solution**: Ensure both sub-questions return the same number and type of columns. Rephrase to make the queries more compatible.

### Issue: Query is too slow
**Solution**: Simplify the questions or add WHERE clauses to limit data scope.

## Best Practices

1. **Be Specific**: Use clear metric names (MTD, YTD, Q1, Q2)
2. **Consistent Structure**: Ensure sub-questions have similar structure
3. **Limit Complexity**: Keep to 2-3 sub-questions per prompt
4. **Use Keywords**: Use "and", "vs", "versus" to clearly separate questions
5. **Test First**: Test individual questions before combining them

# LLM SQL Generation Fix - Complete Guide

## Problem Identified

The LLM was returning the same SQL query regardless of the question asked. This is a common issue with LLM-based SQL generation.

### Root Causes

1. **Temperature Too Low (0.1)** - Made LLM return cached/similar responses
2. **Generic Prompt** - Didn't differentiate between different question types
3. **Limited Few-Shot Examples** - All examples were similar "TOP N" queries
4. **Insufficient Logging** - Couldn't debug what was happening

---

## Fixes Applied

### 1. Increased Temperature ✅
**Before**: `temperature=0.1` (deterministic, but repetitive)
**After**: `temperature=0.3` (more variety, still reasonable)

```python
self.llm = OllamaLLM(
    model=settings.llm_model,
    temperature=0.3,  # Increased for more variety
    base_url=settings.ollama_base_url,
    num_predict=500,  # Increased from 200
)
```

**Why**: Temperature controls randomness. 0.1 is too low and causes the LLM to return similar responses. 0.3 provides good balance between variety and quality.

### 2. Increased Token Limit ✅
**Before**: `num_predict=200`
**After**: `num_predict=500`

**Why**: Allows LLM to generate more complex SQL queries without truncation.

### 3. Enhanced Prompt with Diverse Examples ✅
**Before**: 6 similar examples (mostly TOP N queries)
**After**: 10 diverse examples covering:
- Aggregation queries
- Filtering queries
- Sorting queries
- Counting queries
- Grouping queries
- Conditional logic

```python
examples = """EXAMPLES:
Q: Show top 5 items by sales
A: SELECT item_name, SUM(sales) as total_sales FROM sales GROUP BY item_name ORDER BY total_sales DESC LIMIT 5;

Q: Which category has most items?
A: SELECT category, COUNT(*) as item_count FROM items GROUP BY category ORDER BY item_count DESC LIMIT 1;

Q: Average price by category
A: SELECT category, AVG(price) as avg_price FROM items GROUP BY category ORDER BY avg_price DESC;

Q: How many records in the menu table?
A: SELECT COUNT(*) as total_records FROM menu;

Q: Show me menu_id grouped by menu_type_id from menu
A: SELECT menu_type_id, COUNT(*) as count FROM menu GROUP BY menu_type_id;

Q: What are the top 10 values in menu_id from menu?
A: SELECT menu_id, COUNT(*) as count FROM menu GROUP BY menu_id ORDER BY count DESC LIMIT 10;

Q: List all items with price greater than 100
A: SELECT * FROM items WHERE price > 100 ORDER BY price DESC;

Q: Count items by category and show only categories with more than 5 items
A: SELECT category, COUNT(*) as item_count FROM items GROUP BY category HAVING COUNT(*) > 5;

Q: Show items sorted by price ascending
A: SELECT item_name, price FROM items ORDER BY price ASC;

Q: Find the most expensive item
A: SELECT item_name, price FROM items ORDER BY price DESC LIMIT 1;"""
```

### 4. Improved SQL Rules ✅
Added explicit rule to prevent repetition:

```
14. IMPORTANT: Generate DIFFERENT SQL for DIFFERENT questions - don't repeat the same query
```

### 5. Enhanced Logging ✅
Added detailed logging to debug LLM behavior:

```python
logger.info(f"=== GENERATING SQL FOR QUESTION: {question} ===")
logger.info(f"Schema context loaded: {len(schema_context)} characters")
logger.info(f"Prompt built: {len(prompt_text)} characters")
logger.info(f"Invoking LLM with temperature=0.3, num_predict=500")
logger.info(f"LLM Response (first 300 chars): {response_text[:300]}")
logger.info(f"Extracted SQL: {sql}")
logger.info(f"=== FINAL SQL: {sql} ===")
```

---

## How to Verify the Fix

### Step 1: Restart Backend
```bash
# Stop backend (Ctrl+C)
# Start backend
python backend/main.py
```

### Step 2: Test Different Questions
Ask VoxQuery different questions:

1. **"Show top 5 items by sales"**
   - Expected: `SELECT item_name, SUM(sales) as total_sales FROM sales GROUP BY item_name ORDER BY total_sales DESC LIMIT 5;`

2. **"How many items are in each category?"**
   - Expected: `SELECT category, COUNT(*) as item_count FROM items GROUP BY category;`

3. **"List all items with price greater than 100"**
   - Expected: `SELECT * FROM items WHERE price > 100 ORDER BY price DESC;`

4. **"Find the most expensive item"**
   - Expected: `SELECT item_name, price FROM items ORDER BY price DESC LIMIT 1;`

5. **"Average price by category"**
   - Expected: `SELECT category, AVG(price) as avg_price FROM items GROUP BY category;`

### Step 3: Check Logs
Monitor backend logs to see:
- Question being asked
- Schema context loaded
- LLM response
- Final SQL generated

```bash
# Watch logs
tail -f backend/logs/voxquery.log
```

---

## Configuration Parameters

### Temperature Settings
```
0.0  = Deterministic (always same response)
0.1  = Very low (mostly same responses) ← OLD SETTING
0.3  = Low-Medium (good variety) ← NEW SETTING
0.5  = Medium (more variety)
0.7  = High (very creative)
1.0  = Maximum randomness
```

### Token Limits
```
200  = Short queries only ← OLD SETTING
500  = Complex queries ← NEW SETTING
1000 = Very complex queries
```

---

## If Issues Persist

### Check 1: Verify Ollama is Running
```bash
curl http://localhost:11434/api/tags
```

### Check 2: Verify Model is Loaded
```bash
ollama list
```

### Check 3: Test LLM Directly
```bash
curl http://localhost:11434/api/generate -d '{
  "model": "qwen3:4b",
  "prompt": "SELECT * FROM",
  "stream": false
}'
```

### Check 4: Increase Temperature Further
If still getting same queries, try:
```python
temperature=0.5  # Even more variety
```

### Check 5: Check Schema Context
Verify schema is being loaded:
```python
schema_context = self.schema_analyzer.get_schema_context()
print(schema_context)  # Should show tables and columns
```

---

## Advanced Tuning

### For More Variety
```python
temperature=0.5
num_predict=1000
```

### For More Accuracy
```python
temperature=0.2
num_predict=300
```

### For Balanced Performance
```python
temperature=0.3  # Current setting
num_predict=500  # Current setting
```

---

## Files Modified

- `backend/voxquery/core/sql_generator.py`
  - Increased temperature from 0.1 to 0.3
  - Increased num_predict from 200 to 500
  - Enhanced prompt with diverse examples
  - Added explicit rule against repetition
  - Added comprehensive logging

---

## Expected Behavior After Fix

✅ Different questions generate different SQL
✅ Similar questions generate similar but not identical SQL
✅ Complex questions generate appropriate complex SQL
✅ Simple questions generate simple SQL
✅ Logs show detailed LLM interaction
✅ Schema context is properly loaded
✅ SQL is properly extracted and validated

---

## Monitoring

### Key Metrics to Watch
1. **SQL Diversity** - Are different questions generating different SQL?
2. **SQL Quality** - Are generated queries correct and executable?
3. **Response Time** - Is generation still fast?
4. **Error Rate** - Are there any SQL syntax errors?

### Log Patterns to Look For
```
=== GENERATING SQL FOR QUESTION: Show top 5 items ===
Schema context loaded: 1234 characters
Prompt built: 5678 characters
Invoking LLM with temperature=0.3, num_predict=500
LLM Response (first 300 chars): SELECT item_name, SUM(sales)...
Extracted SQL: SELECT item_name, SUM(sales) as total_sales FROM sales GROUP BY item_name ORDER BY total_sales DESC LIMIT 5;
=== FINAL SQL: SELECT item_name, SUM(sales) as total_sales FROM sales GROUP BY item_name ORDER BY total_sales DESC LIMIT 5; ===
```

---

## Troubleshooting

### Issue: Still Getting Same SQL
**Solution**: 
1. Increase temperature to 0.5
2. Check schema context is loaded
3. Verify Ollama is running
4. Check LLM logs for errors

### Issue: SQL Quality Decreased
**Solution**:
1. Decrease temperature to 0.2
2. Improve few-shot examples
3. Add more SQL rules to prompt

### Issue: Response Time Increased
**Solution**:
1. Decrease num_predict to 300
2. Reduce schema context size
3. Use faster LLM model

---

## Summary

The LLM SQL generation fix addresses the root cause of repetitive queries by:

1. ✅ Increasing temperature for more variety
2. ✅ Increasing token limit for complex queries
3. ✅ Providing diverse few-shot examples
4. ✅ Adding explicit anti-repetition rules
5. ✅ Adding comprehensive logging for debugging

**Status**: ✨ Backend restarted with fixes applied. Ready to test!

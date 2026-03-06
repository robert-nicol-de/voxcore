# Golden Set Organization - Snowflake Training Dataset

## Overview
The `training_questions.json` file has been reorganized with 12 priority questions marked as the **golden set** for Snowflake SQL generation training and evaluation.

## Split Organization

### Priority Golden Set (12 questions)
These are the highest-frequency, most representative questions from real retail/finance Snowflake deployments.

**Validation Set (6 questions)** - `"split": "val"`
1. What are my YTD sales vs budget by store and category?
2. Show gross profit percent MTD versus same month last year by department.
3. Top 10 slow-moving items this week by store — include days on hand and current stock.
4. Which stores are more than 15% below YTD sales target? Show variance amount too.
5. Weekly sales trend for Electronics category over the last 12 weeks — show as line-ready data.
6. MTD revenue and COGS by channel — Retail, Online, Wholesale.

**Test Set (6 questions)** - `"split": "test"` (HOLD-OUT - Never use in prompt engineering)
7. Bottom 5 stores by sales per square meter this quarter.
8. Year-over-year growth rate for top 20 products by revenue last month.
9. Which categories have the highest return rate YTD? Include return value and % of sales.
10. Monthly operating expenses trend last 12 months with % change.
11. Gross profit bridge — show volume, mix, cost, price impact YTD vs LY.
12. Full P&L summary YTD — revenue, COGS, gross profit, op ex, EBITDA, net income — with % variance to budget and LY.

### Training Set (38 questions)
All remaining questions marked with `"split": "train"` - use these as few-shot examples in Groq prompts.

## Why This Split?

**Val Set (6)**: Quick iteration during prompt engineering
- Test prompt changes without leaking test data
- Verify improvements in real-time
- Covers core patterns: YTD, MTD, YoY, variance, ranking

**Test Set (6)**: Final evaluation (NEVER use during development)
- Hold-out forever until you have real user data
- Represents harder questions: bridges, P&L, advanced variance
- True measure of generalization

**Train Set (38)**: Few-shot examples
- Use 4-6 examples per Groq prompt
- Rotate examples to avoid overfitting
- Covers full spectrum of patterns

## Next Steps

### 1. Add Expected SQL (Week 1)
For each of the 12 golden set questions, write clean Snowflake SQL:
```json
{
  "natural_language_question": "What are my YTD sales vs budget by store and category?",
  "priority_golden_set": true,
  "split": "val",
  "expected_sql": "WITH ytd_sales AS (\n  SELECT \n    store_id,\n    category,\n    SUM(revenue) AS ytd_revenue\n  FROM sales_fact\n  WHERE transaction_date >= DATE_TRUNC('year', CURRENT_DATE())\n  GROUP BY 1, 2\n),\nbudget_data AS (\n  SELECT \n    store_id,\n    category,\n    SUM(budget_amount) AS ytd_budget\n  FROM budget_plan\n  WHERE fiscal_year = YEAR(CURRENT_DATE())\n  GROUP BY 1, 2\n)\nSELECT \n  s.store_id,\n  s.category,\n  s.ytd_revenue,\n  b.ytd_budget,\n  ROUND(s.ytd_revenue - b.ytd_budget, 2) AS variance_amount,\n  ROUND(100.0 * (s.ytd_revenue - b.ytd_budget) / NULLIF(b.ytd_budget, 0), 2) AS variance_pct\nFROM ytd_sales s\nLEFT JOIN budget_data b ON s.store_id = b.store_id AND s.category = b.category\nORDER BY s.store_id, s.category;"
}
```

### 2. Add Schema Context (Week 1)
Add relevant tables and key columns:
```json
{
  "relevant_tables": ["sales_fact", "budget_plan", "store_dim", "product_dim"],
  "key_columns": ["transaction_date", "revenue", "store_id", "category", "budget_amount"]
}
```

### 3. Build Evaluation Harness (Week 2)
```python
import json
from snowflake.connector import connect
from difflib import SequenceMatcher

with open("backend/training_questions.json") as f:
    data = json.load(f)

# Filter only test set
test_set = [q for q in data if q.get("split") == "test"]

for example in test_set:
    nl = example["natural_language_question"]
    golden_sql = example.get("expected_sql")
    
    if not golden_sql:
        print(f"⚠️  No expected_sql for: {nl[:60]}...")
        continue
    
    # Call your Groq LLM
    generated_sql = call_voxquery_llm(nl)
    
    # Execute both
    try:
        golden_df = snowflake_query(golden_sql)
        generated_df = snowflake_query(generated_sql)
        result_match = (golden_df == generated_df).all().all()
    except Exception as e:
        result_match = False
        print(f"  Execution error: {e}")
    
    # SQL similarity
    sql_sim = SequenceMatcher(None, golden_sql, generated_sql).ratio()
    
    print(f"Q: {nl[:60]}...")
    print(f"  Result match: {result_match} | SQL similarity: {sql_sim:.2f}")
```

### 4. Few-Shot Prompt Engineering (Week 3)
Use train set examples in your Groq prompt:
```python
few_shot_examples = [q for q in data if q.get("split") == "train"][:6]

prompt = f"""
You are a Snowflake SQL expert. Generate clean, production-ready Snowflake SQL.

Examples:
{format_examples(few_shot_examples)}

Now generate SQL for: {user_question}
"""
```

## Key Metrics to Track

- **Result Match %**: Percentage of test queries producing identical results
- **SQL Similarity**: Average SequenceMatcher ratio (0-1)
- **Execution Success %**: Percentage of generated SQL that runs without errors
- **Val Set Performance**: Track improvement during prompt iteration

## Files to Update

- `backend/training_questions.json` - Add `expected_sql` and `relevant_tables` fields
- `backend/evaluation_harness.py` - Create evaluation script
- `backend/voxquery/core/sql_generator.py` - Update Groq prompt with few-shot examples

## Important Rules

✅ **DO**:
- Use val set for prompt iteration
- Hold test set completely separate
- Rotate train set examples to avoid memorization
- Track metrics over time

❌ **DON'T**:
- Use test set during development
- Leak test questions into prompts
- Hardcode test set answers
- Use all 38 train examples at once (causes token bloat)

---

**Status**: Ready for Week 1 implementation
**Priority**: Add expected_sql for all 12 golden set questions first

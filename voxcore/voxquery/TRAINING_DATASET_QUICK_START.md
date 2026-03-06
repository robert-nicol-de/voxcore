# Training Dataset - Quick Start Guide

## What You Have

✅ **52 Snowflake SQL training questions** organized into:
- **7 Validation questions** (with SQL) - for prompt tuning
- **6 Test questions** (no SQL) - for blind evaluation
- **39 Training questions** (no SQL) - for few-shot examples

## Quick Commands

### Verify Setup
```bash
python backend/verify_setup.py
```
Shows dataset stats and validation checks.

### Check Splits
```bash
python backend/check_splits.py
```
Lists all questions by split with SQL status.

### Run Evaluation
```bash
python backend/evaluation_harness.py
```
Evaluates SQL generation quality (requires Groq integration).

## Using in Groq Prompts

### 1. Get Few-Shot Examples
```python
import json

with open('backend/training_questions.json') as f:
    data = json.load(f)

# Get 4-6 train set examples
train_examples = [q for q in data if q.get('split') == 'train' and q.get('expected_sql')][:6]

for ex in train_examples:
    print(f"Q: {ex['natural_language_question']}")
    print(f"SQL: {ex['expected_sql']}\n")
```

### 2. Build Prompt with Few-Shot
```python
few_shot = "\n\n".join([
    f"Q: {q['natural_language_question']}\nSQL:\n{q['expected_sql']}"
    for q in train_examples
])

prompt = f"""You are a Snowflake SQL expert. Generate clean, production-ready SQL.

Examples:
{few_shot}

Now generate SQL for: {user_question}"""
```

### 3. Test with Validation Set
```python
val_set = [q for q in data if q.get('split') == 'validation']

for q in val_set:
    nl = q['natural_language_question']
    expected = q['expected_sql']
    
    # Call your Groq LLM
    generated = call_groq(nl)
    
    # Compare
    similarity = compare_sql(expected, generated)
    print(f"{nl[:50]}... → {similarity:.2f}")
```

## File Locations

```
backend/
├── training_questions.json          # Main dataset (52 questions)
├── verify_setup.py                  # Verification script
├── check_splits.py                  # Split checker
├── evaluation_harness.py            # Evaluation framework
├── TRAINING_DATASET_COMPLETE.md     # Full documentation
├── TRAINING_DATASET_QUICK_START.md  # This file
├── GOLDEN_SET_ORGANIZATION.md       # Split strategy
└── GOLDEN_SET_SQL_ADDED.md          # SQL patterns reference
```

## Dataset Structure

Each question has:
```json
{
  "natural_language_question": "What are my YTD sales vs budget?",
  "domain": "retail",
  "priority_golden_set": true,
  "split": "validation",
  "expected_features": ["YTD", "JOIN", "variance"],
  "relevant_tables": ["sales_fact", "budget_plan"],
  "key_columns": ["transaction_date", "revenue_amount"],
  "expected_sql": "SELECT ...",
  "paraphrases": ["Alternative phrasings..."]
}
```

## Key Patterns in Validation Set

1. **YTD/MTD Aggregations** - DATE_TRUNC, DATEADD
2. **YoY Comparisons** - DATEADD(year, -1, ...)
3. **Variance Calculations** - (actual - budget) / budget * 100
4. **Window Functions** - ROW_NUMBER, LAG, QUALIFY
5. **Multi-Table Joins** - INNER, LEFT, FULL OUTER
6. **CTEs** - WITH clauses for complex logic
7. **Ranking** - QUALIFY ROW_NUMBER() <= N
8. **Percentage Calculations** - ROUND(..., 2)

## Workflow

### Phase 1: Baseline (Week 1)
1. Run evaluation harness with current Groq prompt
2. Measure baseline SQL similarity on validation set
3. Document results

### Phase 2: Iterate (Week 2)
1. Add few-shot examples to prompt
2. Include schema context
3. Test on validation set
4. Refine based on failures

### Phase 3: Validate (Week 3)
1. Achieve >80% SQL similarity on validation set
2. Run test set evaluation (hold-out)
3. Compare results
4. Document final prompt

### Phase 4: Deploy (Week 4)
1. Use train set for ongoing few-shot examples
2. Monitor SQL generation quality
3. Collect real user feedback
4. Plan for fine-tuning

## Important Rules

🚫 **NEVER**:
- Use test set during development
- Leak test questions into prompts
- Hardcode test set answers

✅ **ALWAYS**:
- Use validation set for iteration
- Hold test set separate
- Rotate train set examples
- Track metrics over time

## Metrics to Track

| Metric | Target | Acceptable | Poor |
|--------|--------|-----------|------|
| SQL Similarity | >0.8 | 0.6-0.8 | <0.6 |
| Execution Success | >95% | 80-95% | <80% |
| Result Match | >80% | 60-80% | <60% |

## Example: Adding a New Question

```python
import json

with open('backend/training_questions.json') as f:
    data = json.load(f)

new_q = {
    "natural_language_question": "Your question here",
    "domain": "retail",  # or "finance"
    "priority_golden_set": False,
    "split": "train",  # or "validation" or "test"
    "expected_features": ["pattern1", "pattern2"],
    "relevant_tables": ["table1", "table2"],
    "key_columns": ["col1", "col2"],
    "expected_sql": "SELECT ...",
    "paraphrases": ["Alternative 1", "Alternative 2"]
}

data.append(new_q)

with open('backend/training_questions.json', 'w') as f:
    json.dump(data, f, indent=2)
```

## Troubleshooting

### "Could not initialize VoxQuery"
The evaluation harness needs VoxQuery to be properly configured. This is expected during development.

### "No expected_sql for test set"
This is correct! Test set questions are hold-out and should not have SQL during development.

### "Train set showing 0 questions"
Train set questions don't have expected_sql by design. They're used as few-shot examples only.

## Next Steps

1. **Integrate Groq**: Update `evaluation_harness.py` to call Groq API
2. **Test Baseline**: Run evaluation on validation set
3. **Iterate Prompt**: Add few-shot examples and schema context
4. **Measure Progress**: Track SQL similarity improvements
5. **Final Eval**: Run test set when validation >80%

---

**Quick Links**:
- Full docs: `TRAINING_DATASET_COMPLETE.md`
- Split strategy: `GOLDEN_SET_ORGANIZATION.md`
- SQL patterns: `GOLDEN_SET_SQL_ADDED.md`
- Evaluation: `evaluation_harness.py`

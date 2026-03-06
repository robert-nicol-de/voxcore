# Training Dataset - Complete Implementation

## Status: ✅ COMPLETE

All 52 questions organized with proper splits and validation set SQL added.

## Dataset Summary

### Total Questions: 52
- **Validation Set**: 7 questions (all with expected_sql)
- **Test Set**: 6 questions (hold-out, no SQL)
- **Training Set**: 39 questions (few-shot examples)

### Priority Golden Set: 13 questions
- 7 in validation set (for prompt tuning)
- 6 in test set (for blind evaluation)

## Validation Set (7 Questions) - Ready for Prompt Engineering

All 7 questions have production-ready Snowflake SQL:

### 1. YTD Sales vs Budget by Store and Category
**Question**: "What are my YTD sales vs budget by store and category?"
**Domain**: Retail
**Key Patterns**: YTD aggregation, JOIN, variance calculation, GROUP BY multiple dimensions
**SQL Status**: ✓ Complete

### 2. Gross Profit % MTD vs Same Month Last Year
**Question**: "Show gross profit percent MTD versus same month last year by department."
**Domain**: Retail
**Key Patterns**: MTD, YoY comparison, percentage calculation, FULL OUTER JOIN
**SQL Status**: ✓ Complete

### 3. Top 10 Slow-Moving Items by Store
**Question**: "Top 10 slow-moving items this week by store — include days on hand and current stock."
**Domain**: Retail
**Key Patterns**: QUALIFY ROW_NUMBER(), inventory math, per-store ranking
**SQL Status**: ✓ Complete

### 4. Stores Below YTD Sales Target
**Question**: "Which stores are more than 15% below YTD sales target? Show variance amount too."
**Domain**: Retail
**Key Patterns**: YTD aggregation, percentage variance filter, exception reporting
**SQL Status**: ✓ Complete

### 5. Weekly Sales Trend (12 weeks)
**Question**: "Weekly sales trend for Electronics category over the last 12 weeks — show as line-ready data."
**Domain**: Retail
**Key Patterns**: DATE_TRUNC('week'), time-series, category filter, ORDER BY
**SQL Status**: ✓ Complete

### 6. MTD Revenue and COGS by Channel
**Question**: "MTD revenue and COGS by channel — Retail, Online, Wholesale."
**Domain**: Retail
**Key Patterns**: MTD, multiple metrics, channel grouping, margin calculation
**SQL Status**: ✓ Complete

### 7. Monthly Operating Expenses Trend
**Question**: "Monthly operating expenses trend last 12 months with % change."
**Domain**: Finance
**Key Patterns**: Monthly grouping, LAG for MoM %, 12-month window
**SQL Status**: ✓ Complete

## Test Set (6 Questions) - Hold-Out for Blind Evaluation

These questions are reserved for final evaluation and should NEVER be used during prompt engineering:

1. Bottom 5 stores by sales per square meter this quarter
2. Year-over-year growth rate for top 20 products by revenue last month
3. Show average transaction value by day of week for the last 90 days
4. Which categories have the highest return rate YTD?
5. Gross profit bridge — show volume, mix, cost, price impact YTD vs LY
6. Full P&L summary YTD — revenue, COGS, gross profit, op ex, EBITDA, net income

## Training Set (39 Questions) - Few-Shot Examples

Use these for few-shot prompting to Groq. Rotate 4-6 examples per query to avoid overfitting.

Examples include:
- Compare online vs in-store sales mix
- Stores with inventory turnover below 4x
- Top 15 items by units sold (momentum detection)
- Gross margin by supplier
- Comp sales growth tracking
- Markdown analysis
- Customer metrics (count, basket size)
- Inventory reorder analysis
- Store format performance
- Running totals and cumulative metrics
- Category contribution analysis
- Shrink analysis
- Footfall and conversion trends
- Negative margin detection
- Labor productivity
- Cross-channel behavior
- Forecast vs actual
- Category share of wallet
- Slow sellers with high markdown
- Store performance scorecard
- Budget vs actual by cost center
- And 19 more...

## Implementation Checklist

### ✅ Phase 1: Dataset Organization (COMPLETE)
- [x] Created 52 questions with natural language and domain tags
- [x] Marked 13 as priority golden set
- [x] Organized into validation (7), test (6), train (39) splits
- [x] Added expected_features for all questions
- [x] Added relevant_tables and key_columns for schema context

### ✅ Phase 2: Validation Set SQL (COMPLETE)
- [x] Added production-ready Snowflake SQL for all 7 validation questions
- [x] Included schema context (relevant_tables, key_columns)
- [x] Added paraphrases for each question
- [x] Verified JSON syntax and structure

### ⏳ Phase 3: Evaluation Harness (IN PROGRESS)
- [x] Created evaluation_harness.py
- [x] Implemented SQL similarity metrics
- [x] Added few-shot example extraction
- [ ] Integrate with Groq LLM API
- [ ] Run validation set evaluation
- [ ] Measure baseline performance

### ⏳ Phase 4: Prompt Engineering (READY TO START)
- [ ] Build Groq prompt with few-shot examples
- [ ] Include dialect-specific instructions
- [ ] Add schema context to prompt
- [ ] Test with validation set
- [ ] Iterate until >80% SQL similarity

### ⏳ Phase 5: Test Set Evaluation (READY)
- [ ] Run blind evaluation on test set
- [ ] Compare to validation performance
- [ ] Measure generalization
- [ ] Document results

## Key Metrics to Track

### SQL Similarity (0-1 scale)
- **Target**: >0.8 for validation set
- **Acceptable**: 0.6-0.8
- **Poor**: <0.6

### Result Match %
- Percentage of generated SQL producing identical results to expected SQL
- Strongest signal of quality

### Execution Success %
- Percentage of generated SQL that runs without errors
- Indicates syntax correctness

## Files Created/Updated

### New Files
- `backend/evaluation_harness.py` - Main evaluation framework
- `backend/add_validation_sql.py` - Script to add validation SQL
- `backend/add_q7_sql.py` - Script to add Q7 SQL
- `backend/check_splits.py` - Utility to verify splits
- `backend/TRAINING_DATASET_COMPLETE.md` - This file

### Updated Files
- `backend/training_questions.json` - Added expected_sql for validation set
- `backend/verify_setup.py` - Fixed 'val' → 'validation' reference
- `backend/fix_splits.py` - Already executed

## Next Steps (Priority Order)

### Week 1: Groq Integration
1. Update `evaluation_harness.py` to call VoxQuery API
2. Test with 1-2 validation questions
3. Measure baseline SQL similarity
4. Document results

### Week 2: Prompt Engineering
1. Build few-shot prompt with 4-6 train set examples
2. Add dialect-specific instructions from `backend/config/dialects/snowflake.ini`
3. Include schema context in prompt
4. Iterate on validation set until >80% similarity

### Week 3: Validation & Testing
1. Run full validation set evaluation
2. Analyze failure patterns
3. Refine prompt based on failures
4. Run test set evaluation (hold-out)

### Week 4: Production Ready
1. Document final prompt template
2. Set up monitoring for SQL generation quality
3. Create feedback loop for real user queries
4. Plan for future fine-tuning

## Important Rules

✅ **DO**:
- Use validation set for prompt iteration
- Hold test set completely separate
- Rotate train set examples to avoid memorization
- Track metrics over time
- Document all prompt changes

❌ **DON'T**:
- Use test set during development
- Leak test questions into prompts
- Hardcode test set answers
- Use all 39 train examples at once (causes token bloat)
- Share test set results until final evaluation

## SQL Patterns Covered

The validation set covers these critical Snowflake patterns:

1. **Date Functions**: DATE_TRUNC, DATEADD, CURRENT_DATE
2. **Aggregations**: SUM, COUNT, AVG with GROUP BY
3. **Window Functions**: ROW_NUMBER, LAG, QUALIFY
4. **Joins**: INNER, LEFT, FULL OUTER
5. **CTEs**: Multiple WITH clauses for complex logic
6. **Calculations**: Variance %, margin %, growth rates
7. **Filtering**: HAVING, QUALIFY, WHERE conditions
8. **Ordering**: ORDER BY with DESC/ASC and NULLS handling

## Schema Context

Each validation question includes:
- **relevant_tables**: 3-5 tables needed for the query
- **key_columns**: 5-8 critical columns for the analysis
- **expected_features**: SQL patterns and functions required

This context helps the LLM understand:
- What tables to join
- What columns to select
- What calculations to perform
- What time periods to filter

## Evaluation Framework

The `evaluation_harness.py` provides:

1. **SQL Similarity Scoring**: SequenceMatcher-based comparison
2. **Few-Shot Example Extraction**: Get train set examples for prompting
3. **Set-Based Evaluation**: Run validation or test set
4. **Metrics Reporting**: Average, min, max, distribution
5. **Extensibility**: Easy to add result matching and execution testing

## Success Criteria

✅ **Phase 2 Complete** (Current):
- All 7 validation questions have expected_sql
- All questions have schema context
- JSON is valid and properly formatted
- Splits are correctly organized

✅ **Phase 3 Target**:
- Evaluation harness integrated with Groq
- Baseline metrics established
- Few-shot examples working

✅ **Phase 4 Target**:
- Validation set >80% SQL similarity
- No syntax errors in generated SQL
- Prompt documented and versioned

✅ **Phase 5 Target**:
- Test set >75% SQL similarity (slight drop expected)
- Generalization confirmed
- Ready for production

---

**Last Updated**: January 28, 2026
**Status**: Phase 2 Complete, Phase 3 Ready to Start
**Next Action**: Integrate evaluation harness with Groq LLM API

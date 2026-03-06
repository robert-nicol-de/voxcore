#!/usr/bin/env python3
"""Add expected_sql for Q7 validation question."""

import json

# Load data
with open('backend/training_questions.json', 'r') as f:
    data = json.load(f)

# Find and update Q7
for i, q in enumerate(data):
    if q.get('split') != 'validation':
        continue
    
    nl = q['natural_language_question']
    
    # Q7: Monthly operating expenses trend
    if 'Monthly operating expenses trend' in nl and not q.get('expected_sql'):
        q['expected_sql'] = """WITH monthly_opex AS (
  SELECT
    DATE_TRUNC('month', expense_date) AS expense_month,
    SUM(expense_amount) AS monthly_opex
  FROM operating_expenses
  WHERE expense_date >= DATEADD(month, -12, DATE_TRUNC('month', CURRENT_DATE()))
    AND expense_date < DATE_TRUNC('month', CURRENT_DATE()) + INTERVAL '1 month'
  GROUP BY DATE_TRUNC('month', expense_date)
)
SELECT
  expense_month,
  monthly_opex,
  LAG(monthly_opex) OVER (ORDER BY expense_month) AS prior_month_opex,
  ROUND(monthly_opex - LAG(monthly_opex) OVER (ORDER BY expense_month), 2) AS mom_change_amount,
  CASE
    WHEN LAG(monthly_opex) OVER (ORDER BY expense_month) = 0 THEN NULL
    ELSE ROUND(100.0 * (monthly_opex - LAG(monthly_opex) OVER (ORDER BY expense_month)) / LAG(monthly_opex) OVER (ORDER BY expense_month), 2)
  END AS mom_change_pct
FROM monthly_opex
ORDER BY expense_month ASC;"""
        if 'relevant_tables' not in q:
            q['relevant_tables'] = ["operating_expenses"]
        if 'key_columns' not in q:
            q['key_columns'] = ["expense_date", "expense_amount", "expense_category"]
        print(f"✓ Added SQL for Q7: {nl[:50]}...")

# Save updated data
with open('backend/training_questions.json', 'w') as f:
    json.dump(data, f, indent=2)

print("\n✅ Q7 SQL added and saved!")

# Verify
val_with_sql = len([q for q in data if q.get('split') == 'validation' and q.get('expected_sql')])
val_total = len([q for q in data if q.get('split') == 'validation'])
print(f"Validation set: {val_with_sql}/{val_total} with expected_sql")

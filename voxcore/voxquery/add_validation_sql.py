#!/usr/bin/env python3
"""Add expected_sql for validation set questions that are missing it."""

import json

# Load data
with open('backend/training_questions.json', 'r') as f:
    data = json.load(f)

# Find and update validation questions
for i, q in enumerate(data):
    if q.get('split') != 'validation':
        continue
    
    nl = q['natural_language_question']
    
    # Q3: Top 10 slow-moving items
    if 'Top 10 slow-moving items' in nl and not q.get('expected_sql'):
        q['expected_sql'] = """SELECT
  s.store_id,
  p.product_id,
  p.product_name,
  SUM(s.units) AS units_sold_week,
  i.on_hand_quantity,
  CASE
    WHEN SUM(s.units) > 0 THEN ROUND(i.on_hand_quantity / SUM(s.units), 1)
    ELSE NULL
  END AS days_on_hand,
  ROW_NUMBER() OVER (PARTITION BY s.store_id ORDER BY SUM(s.units) ASC) AS rank_by_store
FROM sales_fact s
JOIN product_dim p ON s.product_id = p.product_id
JOIN inventory_snapshot i ON s.product_id = i.product_id AND s.store_id = i.store_id
WHERE s.transaction_date >= DATE_TRUNC('week', CURRENT_DATE())
  AND s.transaction_date < DATE_TRUNC('week', CURRENT_DATE()) + INTERVAL '1 week'
GROUP BY s.store_id, p.product_id, p.product_name, i.on_hand_quantity
QUALIFY ROW_NUMBER() OVER (PARTITION BY s.store_id ORDER BY SUM(s.units) ASC) <= 10
ORDER BY s.store_id, rank_by_store;"""
        if 'relevant_tables' not in q:
            q['relevant_tables'] = ["sales_fact", "product_dim", "inventory_snapshot"]
        if 'key_columns' not in q:
            q['key_columns'] = ["transaction_date", "units", "product_id", "store_id", "on_hand_quantity"]
        print(f"✓ Added SQL for Q3: {nl[:50]}...")
    
    # Q4: Which stores are more than 15% below YTD sales target
    elif 'Which stores are more than 15% below' in nl and not q.get('expected_sql'):
        q['expected_sql'] = """WITH ytd_sales AS (
  SELECT
    s.store_id,
    SUM(s.revenue_amount) AS actual_ytd_sales
  FROM sales_fact s
  WHERE s.transaction_date >= DATE_TRUNC('year', CURRENT_DATE())
    AND s.transaction_date < DATE_TRUNC('year', CURRENT_DATE()) + INTERVAL '1 year'
  GROUP BY s.store_id
),
ytd_targets AS (
  SELECT
    store_id,
    SUM(target_amount) AS ytd_target
  FROM sales_target
  WHERE target_year = YEAR(CURRENT_DATE())
  GROUP BY store_id
)
SELECT
  COALESCE(s.store_id, t.store_id) AS store_id,
  s.actual_ytd_sales,
  t.ytd_target,
  ROUND(s.actual_ytd_sales - t.ytd_target, 2) AS variance_amount,
  ROUND(100.0 * (s.actual_ytd_sales - t.ytd_target) / NULLIF(t.ytd_target, 0), 2) AS variance_pct
FROM ytd_sales s
FULL OUTER JOIN ytd_targets t ON s.store_id = t.store_id
WHERE ROUND(100.0 * (s.actual_ytd_sales - t.ytd_target) / NULLIF(t.ytd_target, 0), 2) < -15
ORDER BY variance_pct ASC;"""
        if 'relevant_tables' not in q:
            q['relevant_tables'] = ["sales_fact", "sales_target", "store_dim"]
        if 'key_columns' not in q:
            q['key_columns'] = ["transaction_date", "revenue_amount", "store_id", "target_amount", "target_year"]
        print(f"✓ Added SQL for Q4: {nl[:50]}...")
    
    # Q6: MTD revenue and COGS by channel
    elif 'MTD revenue and COGS by channel' in nl and not q.get('expected_sql'):
        q['expected_sql'] = """SELECT
  s.channel,
  SUM(s.revenue_amount) AS mtd_revenue,
  SUM(s.cogs_amount) AS mtd_cogs,
  ROUND(SUM(s.revenue_amount) - SUM(s.cogs_amount), 2) AS mtd_gross_profit,
  CASE
    WHEN SUM(s.revenue_amount) = 0 THEN NULL
    ELSE ROUND(100.0 * (SUM(s.revenue_amount) - SUM(s.cogs_amount)) / SUM(s.revenue_amount), 2)
  END AS gross_margin_pct
FROM sales_fact s
WHERE s.transaction_date >= DATE_TRUNC('month', CURRENT_DATE())
  AND s.transaction_date < DATE_TRUNC('month', CURRENT_DATE()) + INTERVAL '1 month'
  AND s.channel IN ('Retail', 'Online', 'Wholesale')
GROUP BY s.channel
ORDER BY mtd_revenue DESC;"""
        if 'relevant_tables' not in q:
            q['relevant_tables'] = ["sales_fact"]
        if 'key_columns' not in q:
            q['key_columns'] = ["transaction_date", "revenue_amount", "cogs_amount", "channel"]
        print(f"✓ Added SQL for Q6: {nl[:50]}...")

# Save updated data
with open('backend/training_questions.json', 'w') as f:
    json.dump(data, f, indent=2)

print("\n✅ Validation SQL added and saved!")

# Verify
val_with_sql = len([q for q in data if q.get('split') == 'validation' and q.get('expected_sql')])
val_total = len([q for q in data if q.get('split') == 'validation'])
print(f"Validation set: {val_with_sql}/{val_total} with expected_sql")

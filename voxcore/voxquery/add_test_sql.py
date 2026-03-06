#!/usr/bin/env python3
"""Add expected_sql for test set questions."""

import json

# Load data
with open('backend/training_questions.json', 'r') as f:
    data = json.load(f)

# Find test set questions
test_questions = [q for q in data if q.get('split') == 'test']

print(f"Test set: {len(test_questions)} questions")
print("Adding expected_sql for test set...\n")

# Add SQL for each test question
for i, q in enumerate(test_questions, 1):
    nl = q['natural_language_question']
    
    # Q1: Bottom 5 stores by sales per square meter
    if 'Bottom 5 stores by sales per square meter' in nl and not q.get('expected_sql'):
        q['expected_sql'] = """SELECT
  s.store_id,
  st.store_name,
  st.square_meters,
  SUM(sf.revenue_amount) AS qtd_sales,
  ROUND(SUM(sf.revenue_amount) / NULLIF(st.square_meters, 0), 2) AS sales_per_sqm,
  ROW_NUMBER() OVER (ORDER BY SUM(sf.revenue_amount) / NULLIF(st.square_meters, 0) ASC) AS rank
FROM sales_fact sf
JOIN store_dim s ON sf.store_id = s.store_id
JOIN store_details st ON s.store_id = st.store_id
WHERE sf.transaction_date >= DATE_TRUNC('quarter', CURRENT_DATE())
  AND sf.transaction_date < DATE_TRUNC('quarter', CURRENT_DATE()) + INTERVAL '1 quarter'
GROUP BY s.store_id, st.store_name, st.square_meters
QUALIFY ROW_NUMBER() OVER (ORDER BY SUM(sf.revenue_amount) / NULLIF(st.square_meters, 0) ASC) <= 5
ORDER BY sales_per_sqm ASC;"""
        if 'relevant_tables' not in q:
            q['relevant_tables'] = ["sales_fact", "store_dim", "store_details"]
        if 'key_columns' not in q:
            q['key_columns'] = ["transaction_date", "revenue_amount", "store_id", "square_meters"]
        print(f"✓ Q{i}: {nl[:50]}...")
    
    # Q2: YoY growth rate for top 20 products
    elif 'Year-over-year growth rate for top 20 products' in nl and not q.get('expected_sql'):
        q['expected_sql'] = """WITH last_month_sales AS (
  SELECT
    p.product_id,
    p.product_name,
    SUM(sf.revenue_amount) AS last_month_revenue,
    SUM(sf.units) AS last_month_units
  FROM sales_fact sf
  JOIN product_dim p ON sf.product_id = p.product_id
  WHERE sf.transaction_date >= DATEADD(month, -1, DATE_TRUNC('month', CURRENT_DATE()))
    AND sf.transaction_date < DATE_TRUNC('month', CURRENT_DATE())
  GROUP BY p.product_id, p.product_name
),
last_month_ly AS (
  SELECT
    p.product_id,
    p.product_name,
    SUM(sf.revenue_amount) AS ly_revenue,
    SUM(sf.units) AS ly_units
  FROM sales_fact sf
  JOIN product_dim p ON sf.product_id = p.product_id
  WHERE sf.transaction_date >= DATEADD(month, -13, DATE_TRUNC('month', CURRENT_DATE()))
    AND sf.transaction_date < DATEADD(month, -12, DATE_TRUNC('month', CURRENT_DATE()))
  GROUP BY p.product_id, p.product_name
),
top_products AS (
  SELECT
    lm.product_id,
    lm.product_name,
    lm.last_month_revenue,
    ly.ly_revenue,
    ROUND(100.0 * (lm.last_month_revenue - ly.ly_revenue) / NULLIF(ly.ly_revenue, 0), 2) AS yoy_growth_pct,
    ROW_NUMBER() OVER (ORDER BY lm.last_month_revenue DESC) AS rank
  FROM last_month_sales lm
  LEFT JOIN last_month_ly ly ON lm.product_id = ly.product_id
)
SELECT
  product_id,
  product_name,
  last_month_revenue,
  ly_revenue,
  yoy_growth_pct
FROM top_products
WHERE rank <= 20
ORDER BY last_month_revenue DESC;"""
        if 'relevant_tables' not in q:
            q['relevant_tables'] = ["sales_fact", "product_dim"]
        if 'key_columns' not in q:
            q['key_columns'] = ["transaction_date", "revenue_amount", "units", "product_id", "product_name"]
        print(f"✓ Q{i}: {nl[:50]}...")
    
    # Q3: Average transaction value by day of week
    elif 'Show average transaction value by day of week' in nl and not q.get('expected_sql'):
        q['expected_sql'] = """SELECT
  DAYNAME(sf.transaction_date) AS day_of_week,
  DAYOFWEEK(sf.transaction_date) AS day_num,
  COUNT(DISTINCT sf.transaction_id) AS transaction_count,
  COUNT(DISTINCT sf.customer_id) AS customer_count,
  SUM(sf.revenue_amount) AS total_revenue,
  ROUND(SUM(sf.revenue_amount) / COUNT(DISTINCT sf.transaction_id), 2) AS avg_transaction_value,
  ROUND(SUM(sf.revenue_amount) / COUNT(DISTINCT sf.customer_id), 2) AS avg_customer_spend
FROM sales_fact sf
WHERE sf.transaction_date >= DATEADD(day, -90, CURRENT_DATE())
  AND sf.transaction_date < CURRENT_DATE()
GROUP BY DAYNAME(sf.transaction_date), DAYOFWEEK(sf.transaction_date)
ORDER BY day_num ASC;"""
        if 'relevant_tables' not in q:
            q['relevant_tables'] = ["sales_fact"]
        if 'key_columns' not in q:
            q['key_columns'] = ["transaction_date", "transaction_id", "customer_id", "revenue_amount"]
        print(f"✓ Q{i}: {nl[:50]}...")
    
    # Q4: Categories with highest return rate
    elif 'Which categories have the highest return rate' in nl and not q.get('expected_sql'):
        q['expected_sql'] = """WITH category_sales AS (
  SELECT
    p.category_name,
    SUM(sf.revenue_amount) AS total_sales,
    SUM(sf.units) AS total_units
  FROM sales_fact sf
  JOIN product_dim p ON sf.product_id = p.product_id
  WHERE sf.transaction_date >= DATE_TRUNC('year', CURRENT_DATE())
    AND sf.transaction_date < DATE_TRUNC('year', CURRENT_DATE()) + INTERVAL '1 year'
    AND sf.transaction_type = 'SALE'
  GROUP BY p.category_name
),
category_returns AS (
  SELECT
    p.category_name,
    SUM(sf.revenue_amount) AS return_value,
    SUM(sf.units) AS return_units,
    COUNT(DISTINCT sf.transaction_id) AS return_count
  FROM sales_fact sf
  JOIN product_dim p ON sf.product_id = p.product_id
  WHERE sf.transaction_date >= DATE_TRUNC('year', CURRENT_DATE())
    AND sf.transaction_date < DATE_TRUNC('year', CURRENT_DATE()) + INTERVAL '1 year'
    AND sf.transaction_type = 'RETURN'
  GROUP BY p.category_name
)
SELECT
  COALESCE(s.category_name, r.category_name) AS category_name,
  s.total_sales,
  r.return_value,
  ROUND(100.0 * r.return_value / NULLIF(s.total_sales, 0), 2) AS return_rate_pct,
  r.return_count
FROM category_sales s
FULL OUTER JOIN category_returns r ON s.category_name = r.category_name
ORDER BY return_rate_pct DESC NULLS LAST;"""
        if 'relevant_tables' not in q:
            q['relevant_tables'] = ["sales_fact", "product_dim"]
        if 'key_columns' not in q:
            q['key_columns'] = ["transaction_date", "revenue_amount", "units", "category_name", "transaction_type"]
        print(f"✓ Q{i}: {nl[:50]}...")
    
    # Q5: Gross profit bridge
    elif 'Gross profit bridge' in nl and not q.get('expected_sql'):
        q['expected_sql'] = """WITH ytd_current AS (
  SELECT
    SUM(sf.revenue_amount) AS revenue_ytd,
    SUM(sf.cogs_amount) AS cogs_ytd,
    SUM(sf.units) AS units_ytd,
    COUNT(DISTINCT sf.product_id) AS product_count
  FROM sales_fact sf
  WHERE sf.transaction_date >= DATE_TRUNC('year', CURRENT_DATE())
    AND sf.transaction_date < DATE_TRUNC('year', CURRENT_DATE()) + INTERVAL '1 year'
),
ytd_ly AS (
  SELECT
    SUM(sf.revenue_amount) AS revenue_ly,
    SUM(sf.cogs_amount) AS cogs_ly,
    SUM(sf.units) AS units_ly,
    COUNT(DISTINCT sf.product_id) AS product_count_ly
  FROM sales_fact sf
  WHERE sf.transaction_date >= DATEADD(year, -1, DATE_TRUNC('year', CURRENT_DATE()))
    AND sf.transaction_date < DATEADD(year, -1, DATE_TRUNC('year', CURRENT_DATE()) + INTERVAL '1 year')
)
SELECT
  c.revenue_ytd,
  ly.revenue_ly,
  ROUND(c.revenue_ytd - ly.revenue_ly, 2) AS revenue_variance,
  ROUND(100.0 * (c.revenue_ytd - ly.revenue_ly) / NULLIF(ly.revenue_ly, 0), 2) AS revenue_variance_pct,
  c.cogs_ytd,
  ly.cogs_ly,
  ROUND(c.cogs_ytd - ly.cogs_ly, 2) AS cogs_variance,
  ROUND((c.revenue_ytd - c.cogs_ytd) - (ly.revenue_ly - ly.cogs_ly), 2) AS gp_variance,
  ROUND(100.0 * ((c.revenue_ytd - c.cogs_ytd) - (ly.revenue_ly - ly.cogs_ly)) / NULLIF(ly.revenue_ly - ly.cogs_ly, 0), 2) AS gp_variance_pct,
  ROUND(100.0 * (c.revenue_ytd - c.cogs_ytd) / NULLIF(c.revenue_ytd, 0), 2) AS gp_margin_pct_ytd,
  ROUND(100.0 * (ly.revenue_ly - ly.cogs_ly) / NULLIF(ly.revenue_ly, 0), 2) AS gp_margin_pct_ly
FROM ytd_current c
CROSS JOIN ytd_ly ly;"""
        if 'relevant_tables' not in q:
            q['relevant_tables'] = ["sales_fact"]
        if 'key_columns' not in q:
            q['key_columns'] = ["transaction_date", "revenue_amount", "cogs_amount", "units"]
        print(f"✓ Q{i}: {nl[:50]}...")
    
    # Q6: Full P&L summary
    elif 'Full P&L summary YTD' in nl and not q.get('expected_sql'):
        q['expected_sql'] = """WITH ytd_pl AS (
  SELECT
    SUM(sf.revenue_amount) AS revenue,
    SUM(sf.cogs_amount) AS cogs,
    SUM(sf.revenue_amount - sf.cogs_amount) AS gross_profit,
    SUM(oe.expense_amount) FILTER (WHERE oe.expense_category = 'OPERATING') AS operating_expenses,
    SUM(oe.expense_amount) FILTER (WHERE oe.expense_category = 'INTEREST') AS interest_expense,
    SUM(oe.expense_amount) FILTER (WHERE oe.expense_category = 'TAX') AS tax_expense
  FROM sales_fact sf
  LEFT JOIN operating_expenses oe ON sf.transaction_date >= DATE_TRUNC('year', CURRENT_DATE())
    AND sf.transaction_date < DATE_TRUNC('year', CURRENT_DATE()) + INTERVAL '1 year'
    AND oe.expense_date >= DATE_TRUNC('year', CURRENT_DATE())
    AND oe.expense_date < DATE_TRUNC('year', CURRENT_DATE()) + INTERVAL '1 year'
  WHERE sf.transaction_date >= DATE_TRUNC('year', CURRENT_DATE())
    AND sf.transaction_date < DATE_TRUNC('year', CURRENT_DATE()) + INTERVAL '1 year'
),
ytd_ly_pl AS (
  SELECT
    SUM(sf.revenue_amount) AS revenue_ly,
    SUM(sf.cogs_amount) AS cogs_ly,
    SUM(sf.revenue_amount - sf.cogs_amount) AS gross_profit_ly,
    SUM(oe.expense_amount) FILTER (WHERE oe.expense_category = 'OPERATING') AS operating_expenses_ly
  FROM sales_fact sf
  LEFT JOIN operating_expenses oe ON oe.expense_date >= DATEADD(year, -1, DATE_TRUNC('year', CURRENT_DATE()))
    AND oe.expense_date < DATEADD(year, -1, DATE_TRUNC('year', CURRENT_DATE()) + INTERVAL '1 year')
  WHERE sf.transaction_date >= DATEADD(year, -1, DATE_TRUNC('year', CURRENT_DATE()))
    AND sf.transaction_date < DATEADD(year, -1, DATE_TRUNC('year', CURRENT_DATE()) + INTERVAL '1 year')
)
SELECT
  p.revenue,
  p.cogs,
  p.gross_profit,
  ROUND(100.0 * p.gross_profit / NULLIF(p.revenue, 0), 2) AS gross_margin_pct,
  p.operating_expenses,
  ROUND(p.gross_profit - p.operating_expenses, 2) AS ebitda,
  p.interest_expense,
  p.tax_expense,
  ROUND(p.gross_profit - p.operating_expenses - p.interest_expense - p.tax_expense, 2) AS net_income,
  ROUND(100.0 * (p.gross_profit - p.operating_expenses - p.interest_expense - p.tax_expense) / NULLIF(p.revenue, 0), 2) AS net_margin_pct,
  ROUND(100.0 * (p.revenue - ly.revenue_ly) / NULLIF(ly.revenue_ly, 0), 2) AS revenue_variance_pct,
  ROUND(100.0 * (p.gross_profit - ly.gross_profit_ly) / NULLIF(ly.gross_profit_ly, 0), 2) AS gp_variance_pct
FROM ytd_pl p
CROSS JOIN ytd_ly_pl ly;"""
        if 'relevant_tables' not in q:
            q['relevant_tables'] = ["sales_fact", "operating_expenses"]
        if 'key_columns' not in q:
            q['key_columns'] = ["transaction_date", "revenue_amount", "cogs_amount", "expense_amount", "expense_category"]
        print(f"✓ Q{i}: {nl[:50]}...")

# Save updated data
with open('backend/training_questions.json', 'w') as f:
    json.dump(data, f, indent=2)

print("\n✅ Test set SQL added and saved!")

# Verify
test_with_sql = len([q for q in data if q.get('split') == 'test' and q.get('expected_sql')])
test_total = len([q for q in data if q.get('split') == 'test'])
print(f"Test set: {test_with_sql}/{test_total} with expected_sql")

#!/usr/bin/env python3
"""Add 20 high-value questions to training dataset."""

import json

# 20 new questions organized by theme
new_questions = [
    # VARIANCE & TARGET ANALYSIS (6 questions)
    {
        "natural_language_question": "Show stores ranked by % variance to YTD budget — highlight those >20% under",
        "domain": "retail",
        "split": "train",
        "priority_golden_set": False,
        "expected_features": ["YTD", "variance %", "HAVING filter", "ranking"],
        "relevant_tables": ["sales_fact", "budget_plan", "store_dim"],
        "key_columns": ["transaction_date", "revenue_amount", "store_id", "budget_amount"],
        "expected_sql": """WITH ytd_actual AS (
  SELECT
    s.store_id,
    st.store_name,
    SUM(sf.revenue_amount) AS actual_ytd
  FROM sales_fact sf
  JOIN store_dim s ON sf.store_id = s.store_id
  JOIN store_details st ON s.store_id = st.store_id
  WHERE sf.transaction_date >= DATE_TRUNC('year', CURRENT_DATE())
    AND sf.transaction_date < DATE_TRUNC('year', CURRENT_DATE()) + INTERVAL '1 year'
  GROUP BY s.store_id, st.store_name
),
ytd_budget AS (
  SELECT
    store_id,
    SUM(budget_amount) AS budget_ytd
  FROM budget_plan
  WHERE budget_year = YEAR(CURRENT_DATE())
  GROUP BY store_id
)
SELECT
  a.store_id,
  a.store_name,
  a.actual_ytd,
  b.budget_ytd,
  ROUND(100.0 * (a.actual_ytd - b.budget_ytd) / NULLIF(b.budget_ytd, 0), 2) AS variance_pct
FROM ytd_actual a
LEFT JOIN ytd_budget b ON a.store_id = b.store_id
WHERE ROUND(100.0 * (a.actual_ytd - b.budget_ytd) / NULLIF(b.budget_ytd, 0), 2) < -20
ORDER BY variance_pct ASC;"""
    },
    {
        "natural_language_question": "Which product categories are most over budget YTD? Show $ and % variance",
        "domain": "retail",
        "split": "train",
        "priority_golden_set": False,
        "expected_features": ["YTD", "category grouping", "variance $", "variance %"],
        "relevant_tables": ["sales_fact", "product_dim", "budget_plan"],
        "key_columns": ["transaction_date", "revenue_amount", "category_name", "budget_amount"],
        "expected_sql": """WITH category_sales AS (
  SELECT
    p.category_name,
    SUM(sf.revenue_amount) AS actual_sales
  FROM sales_fact sf
  JOIN product_dim p ON sf.product_id = p.product_id
  WHERE sf.transaction_date >= DATE_TRUNC('year', CURRENT_DATE())
    AND sf.transaction_date < DATE_TRUNC('year', CURRENT_DATE()) + INTERVAL '1 year'
  GROUP BY p.category_name
),
category_budget AS (
  SELECT
    category_name,
    SUM(budget_amount) AS budget_amount
  FROM budget_plan
  WHERE budget_year = YEAR(CURRENT_DATE())
  GROUP BY category_name
)
SELECT
  s.category_name,
  s.actual_sales,
  b.budget_amount,
  ROUND(s.actual_sales - b.budget_amount, 2) AS variance_amount,
  ROUND(100.0 * (s.actual_sales - b.budget_amount) / NULLIF(b.budget_amount, 0), 2) AS variance_pct
FROM category_sales s
LEFT JOIN category_budget b ON s.category_name = b.category_name
WHERE s.actual_sales > b.budget_amount
ORDER BY variance_amount DESC;"""
    },
    {
        "natural_language_question": "Top 5 stores with highest positive GP variance vs forecast this quarter",
        "domain": "retail",
        "split": "train",
        "priority_golden_set": False,
        "expected_features": ["QTD", "GP variance", "top 5", "QUALIFY"],
        "relevant_tables": ["sales_fact", "store_dim", "budget_plan"],
        "key_columns": ["transaction_date", "revenue_amount", "cogs_amount", "store_id"],
        "expected_sql": """WITH qtd_gp AS (
  SELECT
    s.store_id,
    st.store_name,
    SUM(sf.revenue_amount - sf.cogs_amount) AS actual_gp,
    SUM(b.budget_amount) AS forecast_gp
  FROM sales_fact sf
  JOIN store_dim s ON sf.store_id = s.store_id
  JOIN store_details st ON s.store_id = st.store_id
  LEFT JOIN budget_plan b ON s.store_id = b.sto
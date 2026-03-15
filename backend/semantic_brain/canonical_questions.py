"""
VoxCore Canonical Analytics Questions
====================================

This module defines the canonical set of analytics questions for VoxCore Brain.
Each question is a dict with structured metadata for robust benchmarking, training, and semantic coverage analysis.

SCHEMA:
    {
        "category": str,              # e.g. "revenue_sales", "grouped_analysis", ...
        "question": str,              # The natural language question
        "expected_intent": str,       # e.g. "aggregation", "trend", "ranking", ...
        "expected_metric": str,       # e.g. "revenue", "orders", ...
        "expected_dimension": str|None, # e.g. "region", "month", ...
        "expected_sql": str|None,     # Example SQL for the question
        ... (optional fields)
    }

USAGE:
    - Used by benchmark_runner.py and semantic_coverage_analyzer.py
    - Extend this list to improve test and training coverage
    - Regenerate using generate_canonical_questions.py if needed
"""

CANONICAL_QUESTIONS = [
    # 1️⃣ Revenue & Sales Questions
    {
        "category": "revenue_sales",
        "question": "What is our total revenue?",
        "expected_intent": "aggregation",
        "expected_metric": "revenue",
        "expected_dimension": None,
        "expected_sql": "SELECT SUM(sales_amount) AS revenue FROM sales;"
    },
    {
        "category": "revenue_sales",
        "question": "What is total revenue this month?",
        "expected_intent": "aggregation",
        "expected_metric": "revenue",
        "expected_dimension": "month",
        "expected_sql": "SELECT EXTRACT(MONTH FROM order_date) AS month, SUM(sales_amount) AS revenue FROM sales WHERE order_date >= DATE_TRUNC('month', CURRENT_DATE) GROUP BY month;"
    },
    {
        "category": "revenue_sales",
        "question": "What were total sales last year?",
        "expected_intent": "aggregation",
        "expected_metric": "revenue",
        "expected_dimension": "year",
        "expected_sql": "SELECT EXTRACT(YEAR FROM order_date) AS year, SUM(sales_amount) AS revenue FROM sales WHERE order_date >= DATE_TRUNC('year', CURRENT_DATE) GROUP BY year;"
    },
    {
        "category": "revenue_sales",
        "question": "How many orders were placed today?",
        "expected_intent": "aggregation",
        "expected_metric": "orders",
        "expected_dimension": "day",
        "expected_sql": "SELECT COUNT(order_id) AS orders FROM sales WHERE order_date = CURRENT_DATE;"
    },
    {
        "category": "revenue_sales",
        "question": "What is the total number of customers?",
        "expected_intent": "aggregation",
        "expected_metric": "customers",
        "expected_dimension": None,
        "expected_sql": "SELECT COUNT(DISTINCT customer_id) AS customers FROM sales;"
    },
    {
        "category": "revenue_sales",
        "question": "What is the average order value?",
        "expected_intent": "aggregation",
        "expected_metric": "avg_order_value",
        "expected_dimension": None,
        "expected_sql": "SELECT SUM(sales_amount) / NULLIF(COUNT(order_id), 0) AS avg_order_value FROM sales;"
    },
    {
        "category": "revenue_sales",
        "question": "What is total profit this quarter?",
        "expected_intent": "aggregation",
        "expected_metric": "profit",
        "expected_dimension": "quarter",
        "expected_sql": "SELECT EXTRACT(QUARTER FROM order_date) AS quarter, SUM(profit) AS profit FROM sales WHERE order_date >= DATE_TRUNC('quarter', CURRENT_DATE) GROUP BY quarter;"
    },
    {
        "category": "revenue_sales",
        "question": "What were total refunds last month?",
        "expected_intent": "aggregation",
        "expected_metric": "refunds",
        "expected_dimension": "month",
        "expected_sql": "SELECT EXTRACT(MONTH FROM order_date) AS month, SUM(refund_amount) AS refunds FROM sales WHERE order_date >= DATE_TRUNC('month', CURRENT_DATE, -1) AND order_date < DATE_TRUNC('month', CURRENT_DATE) GROUP BY month;"
    },
    # 2️⃣ Grouped Analysis (16–30)
    {"category": "grouped_analysis", "question": "Revenue by region", "expected_intent": "grouped_aggregation", "expected_metric": "total_revenue", "expected_dimension": "region", "time_filter": None, "expected_sql": "SELECT region, SUM(order_amount) FROM orders GROUP BY region"},
    {"category": "grouped_analysis", "question": "Revenue by district", "expected_intent": "grouped_aggregation", "expected_metric": "total_revenue", "expected_dimension": "district", "time_filter": None, "expected_sql": "SELECT district, SUM(order_amount) FROM orders GROUP BY district"},
    {"category": "grouped_analysis", "question": "Sales by product category", "expected_intent": "grouped_aggregation", "expected_metric": "total_revenue", "expected_dimension": "product_category", "time_filter": None, "expected_sql": "SELECT product_category, SUM(order_amount) FROM orders GROUP BY product_category"},
    {"category": "grouped_analysis", "question": "Orders by sales channel", "expected_intent": "grouped_aggregation", "expected_metric": "total_orders", "expected_dimension": "sales_channel", "time_filter": None, "expected_sql": "SELECT sales_channel, COUNT(order_id) FROM orders GROUP BY sales_channel"},
    {"category": "grouped_analysis", "question": "Revenue by store", "expected_intent": "grouped_aggregation", "expected_metric": "total_revenue", "expected_dimension": "store", "time_filter": None, "expected_sql": "SELECT store, SUM(order_amount) FROM orders GROUP BY store"},
    {"category": "grouped_analysis", "question": "Profit by product category", "expected_intent": "grouped_aggregation", "expected_metric": "total_profit", "expected_dimension": "product_category", "time_filter": None, "expected_sql": "SELECT product_category, SUM(profit) FROM orders GROUP BY product_category"},
    {"category": "grouped_analysis", "question": "Customers by country", "expected_intent": "grouped_aggregation", "expected_metric": "total_customers", "expected_dimension": "country", "time_filter": None, "expected_sql": "SELECT country, COUNT(DISTINCT customer_id) FROM orders GROUP BY country"},
    {"category": "grouped_analysis", "question": "Orders by payment method", "expected_intent": "grouped_aggregation", "expected_metric": "total_orders", "expected_dimension": "payment_method", "time_filter": None, "expected_sql": "SELECT payment_method, COUNT(order_id) FROM orders GROUP BY payment_method"},
    {"category": "grouped_analysis", "question": "Sales by salesperson", "expected_intent": "grouped_aggregation", "expected_metric": "total_revenue", "expected_dimension": "salesperson", "time_filter": None, "expected_sql": "SELECT salesperson, SUM(order_amount) FROM orders GROUP BY salesperson"},
    {"category": "grouped_analysis", "question": "Revenue by marketing campaign", "expected_intent": "grouped_aggregation", "expected_metric": "total_revenue", "expected_dimension": "marketing_campaign", "time_filter": None, "expected_sql": "SELECT marketing_campaign, SUM(order_amount) FROM orders GROUP BY marketing_campaign"},
    {"category": "grouped_analysis", "question": "Orders by day of the week", "expected_intent": "grouped_aggregation", "expected_metric": "total_orders", "expected_dimension": "day_of_week", "time_filter": None, "expected_sql": "SELECT day_of_week, COUNT(order_id) FROM orders GROUP BY day_of_week"},
    {"category": "grouped_analysis", "question": "Revenue by month", "expected_intent": "grouped_aggregation", "expected_metric": "total_revenue", "expected_dimension": "month", "time_filter": None, "expected_sql": "SELECT month, SUM(order_amount) FROM orders GROUP BY month"},
    {"category": "grouped_analysis", "question": "Revenue by quarter", "expected_intent": "grouped_aggregation", "expected_metric": "total_revenue", "expected_dimension": "quarter", "time_filter": None, "expected_sql": "SELECT quarter, SUM(order_amount) FROM orders GROUP BY quarter"},
    {"category": "grouped_analysis", "question": "Orders by product brand", "expected_intent": "grouped_aggregation", "expected_metric": "total_orders", "expected_dimension": "product_brand", "time_filter": None, "expected_sql": "SELECT product_brand, COUNT(order_id) FROM orders GROUP BY product_brand"},
    {"category": "grouped_analysis", "question": "Revenue by customer segment", "expected_intent": "grouped_aggregation", "expected_metric": "total_revenue", "expected_dimension": "customer_segment", "time_filter": None, "expected_sql": "SELECT customer_segment, SUM(order_amount) FROM orders GROUP BY customer_segment"},
    # 3️⃣ Ranking Queries (31–45)
    {"category": "customer", "question": "Top 10 customers by revenue", "expected_intent": "ranking", "expected_metric": "revenue", "expected_dimension": "customer", "expected_sql": "SELECT customer_id, SUM(sales_amount) AS revenue FROM sales GROUP BY customer_id ORDER BY revenue DESC LIMIT 10;"},
    {"category": "product", "question": "Top 5 products by sales", "expected_intent": "ranking", "expected_metric": "sales", "expected_dimension": "product", "expected_sql": "SELECT product_id, SUM(sales_amount) AS sales FROM sales GROUP BY product_id ORDER BY sales DESC LIMIT 5;"},
    {"category": "geography", "question": "Top regions by revenue", "expected_intent": "ranking", "expected_metric": "revenue", "expected_dimension": "region", "expected_sql": "SELECT region, SUM(sales_amount) AS revenue FROM sales GROUP BY region ORDER BY revenue DESC LIMIT 10;"},
    {"category": "store", "question": "Top stores by profit", "expected_intent": "ranking", "expected_metric": "profit", "expected_dimension": "store", "expected_sql": "SELECT store, SUM(profit) AS profit FROM sales GROUP BY store ORDER BY profit DESC LIMIT 10;"},
    {"category": "product", "question": "Top categories by revenue", "expected_intent": "ranking", "expected_metric": "revenue", "expected_dimension": "product_category", "expected_sql": "SELECT product_category, SUM(sales_amount) AS revenue FROM sales GROUP BY product_category ORDER BY revenue DESC LIMIT 10;"},
    {"category": "salesperson", "question": "Top salespeople by revenue", "expected_intent": "ranking", "expected_metric": "revenue", "expected_dimension": "salesperson", "expected_sql": "SELECT salesperson, SUM(sales_amount) AS revenue FROM sales GROUP BY salesperson ORDER BY revenue DESC LIMIT 10;"},
    {"category": "marketing", "question": "Top marketing campaigns by conversion rate", "expected_intent": "ranking", "expected_metric": "conversion_rate", "expected_dimension": "marketing_campaign", "expected_sql": "SELECT marketing_campaign, SUM(conversions)::float / NULLIF(SUM(clicks),0) AS conversion_rate FROM marketing GROUP BY marketing_campaign ORDER BY conversion_rate DESC LIMIT 10;"},
    {"category": "geography", "question": "Top cities by order volume", "expected_intent": "ranking", "expected_metric": "orders", "expected_dimension": "city", "expected_sql": "SELECT city, COUNT(order_id) AS orders FROM sales GROUP BY city ORDER BY orders DESC LIMIT 10;"},
    {"category": "customer", "question": "Top 20 customers by order value", "expected_intent": "ranking", "expected_metric": "order_value", "expected_dimension": "customer", "expected_sql": "SELECT customer_id, SUM(sales_amount) AS order_value FROM sales GROUP BY customer_id ORDER BY order_value DESC LIMIT 20;"},
    {"category": "product", "question": "Top products by profit margin", "expected_intent": "ranking", "expected_metric": "profit_margin", "expected_dimension": "product", "expected_sql": "SELECT product_id, SUM(profit)::float / NULLIF(SUM(sales_amount),0) AS profit_margin FROM sales GROUP BY product_id ORDER BY profit_margin DESC LIMIT 10;"},
    {"category": "product", "question": "Bottom 10 products by sales", "expected_intent": "ranking", "expected_metric": "sales", "expected_dimension": "product", "expected_sql": "SELECT product_id, SUM(sales_amount) AS sales FROM sales GROUP BY product_id ORDER BY sales ASC LIMIT 10;"},
    {"category": "store", "question": "Lowest performing stores by revenue", "expected_intent": "ranking", "expected_metric": "revenue", "expected_dimension": "store", "expected_sql": "SELECT store, SUM(sales_amount) AS revenue FROM sales GROUP BY store ORDER BY revenue ASC LIMIT 10;"},
    {"category": "geography", "question": "Lowest revenue regions", "expected_intent": "ranking", "expected_metric": "revenue", "expected_dimension": "region", "expected_sql": "SELECT region, SUM(sales_amount) AS revenue FROM sales GROUP BY region ORDER BY revenue ASC LIMIT 10;"},
    {"category": "product", "question": "Lowest profit products", "expected_intent": "ranking", "expected_metric": "profit", "expected_dimension": "product", "expected_sql": "SELECT product_id, SUM(profit) AS profit FROM sales GROUP BY product_id ORDER BY profit ASC LIMIT 10;"},
    {"category": "marketing", "question": "Worst performing campaigns", "expected_intent": "ranking", "expected_metric": "conversion_rate", "expected_dimension": "marketing_campaign", "expected_sql": "SELECT marketing_campaign, SUM(conversions)::float / NULLIF(SUM(clicks),0) AS conversion_rate FROM marketing GROUP BY marketing_campaign ORDER BY conversion_rate ASC LIMIT 10;"},
    # 4️⃣ Time Comparisons (46–60)
    {"category": "time", "question": "Revenue month over month", "expected_intent": "trend", "expected_metric": "revenue", "expected_dimension": "month", "expected_sql": "SELECT EXTRACT(MONTH FROM order_date) AS month, SUM(sales_amount) AS revenue FROM sales GROUP BY month ORDER BY month;"},
    {"category": "time", "question": "Sales year over year", "expected_intent": "trend", "expected_metric": "sales", "expected_dimension": "year", "expected_sql": "SELECT EXTRACT(YEAR FROM order_date) AS year, SUM(sales_amount) AS sales FROM sales GROUP BY year ORDER BY year;"},
    {"category": "time", "question": "Orders week over week", "expected_intent": "trend", "expected_metric": "orders", "expected_dimension": "week", "expected_sql": "SELECT EXTRACT(WEEK FROM order_date) AS week, COUNT(order_id) AS orders FROM sales GROUP BY week ORDER BY week;"},
    {"category": "time", "question": "Revenue this month vs last month", "expected_intent": "comparison", "expected_metric": "revenue", "expected_dimension": "month", "expected_sql": "SELECT EXTRACT(MONTH FROM order_date) AS month, SUM(sales_amount) AS revenue FROM sales WHERE order_date >= DATE_TRUNC('month', CURRENT_DATE, -1) GROUP BY month ORDER BY month DESC LIMIT 2;"},
    {"category": "time", "question": "Sales this quarter vs last quarter", "expected_intent": "comparison", "expected_metric": "sales", "expected_dimension": "quarter", "expected_sql": "SELECT EXTRACT(QUARTER FROM order_date) AS quarter, SUM(sales_amount) AS sales FROM sales WHERE order_date >= DATE_TRUNC('quarter', CURRENT_DATE, -1) GROUP BY quarter ORDER BY quarter DESC LIMIT 2;"},
    {"category": "time", "question": "Orders today vs yesterday", "expected_intent": "comparison", "expected_metric": "orders", "expected_dimension": "day", "expected_sql": "SELECT order_date, COUNT(order_id) AS orders FROM sales WHERE order_date IN (CURRENT_DATE, CURRENT_DATE - INTERVAL '1 day') GROUP BY order_date ORDER BY order_date DESC;"},
    {"category": "time", "question": "Revenue this year vs last year", "expected_intent": "comparison", "expected_metric": "revenue", "expected_dimension": "year", "expected_sql": "SELECT EXTRACT(YEAR FROM order_date) AS year, SUM(sales_amount) AS revenue FROM sales WHERE order_date >= DATE_TRUNC('year', CURRENT_DATE, -1) GROUP BY year ORDER BY year DESC LIMIT 2;"},
    {"category": "time", "question": "Average order value month over month", "expected_intent": "trend", "expected_metric": "avg_order_value", "expected_dimension": "month", "expected_sql": "SELECT EXTRACT(MONTH FROM order_date) AS month, SUM(sales_amount) / NULLIF(COUNT(order_id),0) AS avg_order_value FROM sales GROUP BY month ORDER BY month;"},
    {"category": "customer", "question": "Customer growth month over month", "expected_intent": "trend", "expected_metric": "customer_growth", "expected_dimension": "month", "expected_sql": "SELECT EXTRACT(MONTH FROM order_date) AS month, COUNT(DISTINCT customer_id) AS new_customers FROM sales GROUP BY month ORDER BY month;"},
    {"category": "time", "question": "Revenue growth rate year over year", "expected_intent": "trend", "expected_metric": "revenue_growth_rate", "expected_dimension": "year", "expected_sql": "SELECT EXTRACT(YEAR FROM order_date) AS year, (SUM(sales_amount) - LAG(SUM(sales_amount)) OVER (ORDER BY EXTRACT(YEAR FROM order_date))) / NULLIF(LAG(SUM(sales_amount)) OVER (ORDER BY EXTRACT(YEAR FROM order_date)),0) AS growth_rate FROM sales GROUP BY year ORDER BY year;"},
    {"category": "time", "question": "Orders this week compared to last week", "expected_intent": "comparison", "expected_metric": "orders", "expected_dimension": "week", "expected_sql": "SELECT EXTRACT(WEEK FROM order_date) AS week, COUNT(order_id) AS orders FROM sales WHERE order_date >= DATE_TRUNC('week', CURRENT_DATE, -1) GROUP BY week ORDER BY week DESC LIMIT 2;"},
    {"category": "time", "question": "Revenue for the last 12 months", "expected_intent": "trend", "expected_metric": "revenue", "expected_dimension": "month", "expected_sql": "SELECT EXTRACT(MONTH FROM order_date) AS month, SUM(sales_amount) AS revenue FROM sales WHERE order_date >= CURRENT_DATE - INTERVAL '12 months' GROUP BY month ORDER BY month;"},
    {"category": "time", "question": "Sales trend for the past 6 months", "expected_intent": "trend", "expected_metric": "sales", "expected_dimension": "month", "expected_sql": "SELECT EXTRACT(MONTH FROM order_date) AS month, SUM(sales_amount) AS sales FROM sales WHERE order_date >= CURRENT_DATE - INTERVAL '6 months' GROUP BY month ORDER BY month;"},
    {"category": "time", "question": "Profit trend over the last year", "expected_intent": "trend", "expected_metric": "profit", "expected_dimension": "month", "expected_sql": "SELECT EXTRACT(MONTH FROM order_date) AS month, SUM(profit) AS profit FROM sales WHERE order_date >= CURRENT_DATE - INTERVAL '12 months' GROUP BY month ORDER BY month;"},
    {"category": "time", "question": "Revenue trend for the past 30 days", "expected_intent": "trend", "expected_metric": "revenue", "expected_dimension": "day", "expected_sql": "SELECT order_date, SUM(sales_amount) AS revenue FROM sales WHERE order_date >= CURRENT_DATE - INTERVAL '30 days' GROUP BY order_date ORDER BY order_date;"},
    # 5️⃣ Filtering Queries (61–70)
    {"category": "geography", "question": "Revenue in the North region", "expected_intent": "filter", "expected_metric": "revenue", "expected_dimension": "region", "expected_sql": "SELECT SUM(sales_amount) AS revenue FROM sales WHERE region = 'North';"},
    {"category": "product", "question": "Sales for Product X", "expected_intent": "filter", "expected_metric": "sales", "expected_dimension": "product", "expected_sql": "SELECT SUM(sales_amount) AS sales FROM sales WHERE product_name = 'Product X';"},
    {"category": "customer", "question": "Orders from new customers", "expected_intent": "filter", "expected_metric": "orders", "expected_dimension": "customer_type", "expected_sql": "SELECT COUNT(order_id) AS orders FROM sales WHERE customer_type = 'new';"},
    {"category": "customer", "question": "Revenue from returning customers", "expected_intent": "filter", "expected_metric": "revenue", "expected_dimension": "customer_type", "expected_sql": "SELECT SUM(sales_amount) AS revenue FROM sales WHERE customer_type = 'returning';"},
    {"category": "product", "question": "Sales for the Electronics category", "expected_intent": "filter", "expected_metric": "sales", "expected_dimension": "product_category", "expected_sql": "SELECT SUM(sales_amount) AS sales FROM sales WHERE product_category = 'Electronics';"},
    {"question": "Revenue in the United States"},
    {"question": "Orders from the online store"},
    {"question": "Revenue for premium customers"},
    {"question": "Sales for customers under subscription plans"},
    {"question": "Orders from mobile devices"},
    # 6️⃣ Multi-Dimension Analysis (71–85)
    {"question": "Revenue by region and product category"},
    {"question": "Sales by store and month"},
    {"question": "Orders by product and region"},
    {"question": "Revenue by customer segment and region"},
    {"question": "Profit by product category and quarter"},
    {"question": "Sales by marketing channel and month"},
    {"question": "Orders by day of week and region"},
    {"question": "Revenue by salesperson and region"},
    {"question": "Profit by store and product category"},
    {"question": "Orders by customer segment and product category"},
    {"question": "Revenue by city and month"},
    {"question": "Sales by campaign and region"},
    {"question": "Orders by payment method and region"},
    {"question": "Revenue by product category and year"},
    {"question": "Sales by brand and region"},
    # 7️⃣ Ratios and Metrics (86–95)
    {"question": "Conversion rate by marketing campaign"},
    {"question": "Profit margin by product"},
    {"question": "Average revenue per user"},
    {"question": "Customer lifetime value"},
    {"question": "Revenue per store"},
    {"question": "Orders per customer"},
    {"question": "Revenue per salesperson"},
    {"question": "Profit margin by category"},
    {"question": "Average order value by region"},
    {"question": "Customer retention rate"},
    # 8️⃣ Operational Questions (96–100)
    {"question": "Which products are running out of stock?"},
    {"question": "Which stores have declining sales?"},
    {"question": "Which regions have the highest growth?"},
    {"question": "Which customers generate the most revenue?"},
    {"question": "Which products drive the most profit?"},
]

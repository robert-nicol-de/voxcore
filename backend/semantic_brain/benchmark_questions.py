# VoxCore Brain — 12 Benchmark Questions + Paraphrases
# This file can be imported by training/benchmark scripts

BENCHMARK_QUESTIONS = [
    {
        "question": "Show revenue for the past 12 months.",
        "intent": "trend",
        "metric": "revenue",
        "dimension": "month",
        "chart_type": "line",
        "paraphrases": [
            "Revenue trend for the last year",
            "Monthly revenue for the past 12 months",
            "How has revenue changed over the last year?",
            "Show me revenue by month for the last year",
            "Revenue for each month in the past year",
            "12-month revenue trend",
            "What was revenue each month this year?",
            "Monthly sales totals for the last 12 months",
            "Revenue by month, last year",
            "How did revenue perform month by month?"
        ]
    },
    {
        "question": "Show revenue by region.",
        "intent": "aggregate",
        "metric": "revenue",
        "dimension": "region",
        "chart_type": "bar",
        "paraphrases": [
            "Revenue for each region",
            "How much revenue did each region generate?",
            "Regional revenue breakdown",
            "Show me sales by region",
            "Revenue split by region",
            "Sales by region",
            "Revenue per region",
            "How is revenue distributed across regions?",
            "Compare revenue across regions",
            "Region-wise revenue"
        ]
    },
    {
        "question": "Who are the top 10 customers by revenue?",
        "intent": "ranking",
        "metric": "revenue",
        "dimension": "customer",
        "limit": 10,
        "chart_type": "bar",
        "paraphrases": [
            "Top 10 revenue customers",
            "Which customers generated the most revenue?",
            "Highest revenue customers",
            "Show top customers by revenue",
            "List the 10 biggest customers by revenue",
            "Top ten customers by sales",
            "Who are the highest paying customers?",
            "Customers ranked by revenue",
            "Top customers in terms of revenue",
            "Who spent the most?"
        ]
    },
    {
        "question": "Compare revenue this month vs last month.",
        "intent": "time_comparison",
        "metric": "revenue",
        "dimension": "month",
        "chart_type": "bar",
        "paraphrases": [
            "Revenue this month compared to last month",
            "How did revenue change from last month to this month?",
            "Month-over-month revenue comparison",
            "Revenue difference between this and last month",
            "Compare this month's revenue to last month's",
            "Revenue growth from last month",
            "Change in revenue month over month",
            "Revenue this month vs previous month",
            "How much did revenue increase or decrease since last month?",
            "Month to month revenue change"
        ]
    },
    {
        "question": "Show revenue by product category.",
        "intent": "aggregate",
        "metric": "revenue",
        "dimension": "product_category",
        "chart_type": "bar",
        "paraphrases": [
            "Revenue for each product category",
            "Product category revenue breakdown",
            "Sales by product category",
            "How much revenue did each category generate?",
            "Revenue split by product category",
            "Show me sales by category",
            "Revenue per product category",
            "Compare revenue across product categories",
            "Category-wise revenue",
            "Product categories ranked by revenue"
        ]
    },
    {
        "question": "What are the bottom 5 products by sales?",
        "intent": "ranking",
        "metric": "sales",
        "dimension": "product",
        "limit": 5,
        "chart_type": "bar",
        "paraphrases": [
            "Lowest 5 products by sales",
            "Which products sold the least?",
            "Bottom five products in sales",
            "Products with lowest sales",
            "Show me the 5 worst selling products",
            "Products ranked lowest by sales",
            "Least popular products by sales",
            "Products with the fewest sales",
            "Bottom sales products",
            "Lowest selling products"
        ]
    },
    {
        "question": "Which regions have the fastest revenue growth?",
        "intent": "ranking",
        "metric": "revenue_growth",
        "dimension": "region",
        "chart_type": "bar",
        "paraphrases": [
            "Regions with highest revenue growth",
            "Top growing regions by revenue",
            "Which regions are growing fastest?",
            "Show revenue growth by region",
            "Fastest growing regions",
            "Regions ranked by revenue growth",
            "Where is revenue increasing the most?",
            "Revenue growth rate by region",
            "Compare revenue growth across regions",
            "Regions with the biggest revenue increase"
        ]
    },
    {
        "question": "What is the average order value by region?",
        "intent": "aggregate",
        "metric": "average_order_value",
        "dimension": "region",
        "chart_type": "bar",
        "paraphrases": [
            "Average order value for each region",
            "AOV by region",
            "How much is the average order in each region?",
            "Show average order value by region",
            "Region-wise average order value",
            "Compare AOV across regions",
            "Average sales per order by region",
            "What is the mean order value by region?",
            "Average order size by region",
            "How does AOV vary by region?"
        ]
    },
    {
        "question": "Which customer segments generate the most revenue?",
        "intent": "ranking",
        "metric": "revenue",
        "dimension": "customer_segment",
        "chart_type": "bar",
        "paraphrases": [
            "Top customer segments by revenue",
            "Customer segments with highest revenue",
            "Which segments are most profitable?",
            "Show revenue by customer segment",
            "Customer segment revenue breakdown",
            "Segments ranked by revenue",
            "Most valuable customer segments",
            "Revenue per customer segment",
            "Compare revenue across segments",
            "Customer segments generating most sales"
        ]
    },
    {
        "question": "Which products drive the most revenue?",
        "intent": "ranking",
        "metric": "revenue",
        "dimension": "product",
        "chart_type": "bar",
        "paraphrases": [
            "Top products by revenue",
            "Products generating the most revenue",
            "Which products have the highest sales?",
            "Show revenue by product",
            "Products ranked by revenue",
            "Most profitable products",
            "Revenue per product",
            "Compare revenue across products",
            "Products with highest revenue",
            "Best selling products by revenue"
        ]
    },
    {
        "question": "Why did revenue drop last quarter?",
        "intent": "diagnostic",
        "metric": "revenue",
        "dimension": "quarter",
        "chart_type": "bar",
        "paraphrases": [
            "Reason for revenue decline last quarter",
            "What caused revenue to fall last quarter?",
            "Explain the drop in revenue last quarter",
            "Revenue decrease analysis for last quarter",
            "Why was revenue lower last quarter?",
            "Root cause of revenue drop last quarter",
            "Breakdown of revenue decline last quarter",
            "What led to the revenue drop last quarter?",
            "Factors behind revenue decrease last quarter",
            "Why did sales go down last quarter?"
        ]
    },
    {
        "question": "Were there any unusual spikes in sales recently?",
        "intent": "anomaly_detection",
        "metric": "sales",
        "dimension": "time",
        "chart_type": "line",
        "paraphrases": [
            "Any recent sales spikes?",
            "Did sales spike recently?",
            "Unusual sales increases lately?",
            "Were there any sales anomalies?",
            "Recent outliers in sales?",
            "Did sales jump unexpectedly?",
            "Any abnormal sales activity recently?",
            "Were there any sales surges?",
            "Did sales have any big jumps lately?",
            "Any recent sales outliers?"
        ]
    }
]

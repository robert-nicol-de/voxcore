"""
Few-shot SQL templates for training the LLM on common query patterns.
These templates teach the model how to generate correct SQL for different intents.
"""

FEW_SHOT_TEMPLATES = [
    {
        "intent": "Top N by Metric",
        "english": "Show me the top 10 entities by total revenue this year.",
        "sql": """SELECT TOP (@TopN)
    {dimension_name},
    SUM({metric_column}) AS TotalValue
FROM {fact_table}
WHERE YEAR({date_column}) >= 2013
GROUP BY {dimension_name}
ORDER BY TotalValue DESC""",
        "governance": [
            "Must contain TOP",
            "Must contain GROUP BY if SUM used",
            "Use YEAR() >= 2013 for historical data",
            "No SELECT *"
        ]
    },
    {
        "intent": "Bottom N by Metric",
        "english": "Show me the bottom 5 products by sales in the last 30 days.",
        "sql": """SELECT TOP (@TopN)
    {dimension_name},
    SUM({metric_column}) AS TotalValue
FROM {fact_table}
WHERE YEAR({date_column}) >= 2013
GROUP BY {dimension_name}
ORDER BY TotalValue ASC""",
        "governance": [
            "Use YEAR() >= 2013 for historical data",
            "ASC sorting for bottom logic"
        ]
    },
    {
        "intent": "Monthly Trend",
        "english": "Show monthly revenue for the last 12 months.",
        "sql": """SELECT
    DATEFROMPARTS(YEAR({date_column}), MONTH({date_column}),1) AS MonthStart,
    SUM({metric_column}) AS Revenue
FROM {fact_table}
WHERE YEAR({date_column}) >= 2013
GROUP BY DATEFROMPARTS(YEAR({date_column}), MONTH({date_column}),1)
ORDER BY MonthStart""",
        "governance": [
            "Must group by month expression",
            "Use YEAR() >= 2013 for historical data",
            "Must order chronologically"
        ]
    },
    {
        "intent": "Year-over-Year Comparison",
        "english": "Compare revenue this year vs last year.",
        "sql": """SELECT
    YEAR({date_column}) AS Year,
    SUM({metric_column}) AS Revenue
FROM {fact_table}
WHERE YEAR({date_column}) IN (2014, 2013)
GROUP BY YEAR({date_column})
ORDER BY Year""",
        "governance": [
            "Use specific years (2013, 2014) not GETDATE()",
            "GROUP BY must match select"
        ]
    },
    {
        "intent": "Count-Based Metric",
        "english": "How many orders were placed in the last 7 days?",
        "sql": """SELECT COUNT(*) AS RecordCount
FROM {fact_table}
WHERE YEAR({date_column}) >= 2013""",
        "governance": [
            "COUNT allowed",
            "Use YEAR() >= 2013 for historical data"
        ]
    },
    {
        "intent": "Average Calculation",
        "english": "What is the average order value this month?",
        "sql": """SELECT AVG({metric_column}) AS AverageValue
FROM {fact_table}
WHERE YEAR({date_column}) >= 2013""",
        "governance": [
            "AVG allowed",
            "Use YEAR() >= 2013 for historical data"
        ]
    },
    {
        "intent": "Percentage Contribution",
        "english": "What percentage of total revenue does each region contribute?",
        "sql": """WITH totals AS (
    SELECT SUM({metric_column}) AS GrandTotal
    FROM {fact_table}
    WHERE YEAR({date_column}) >= 2013
)
SELECT
    {dimension_name},
    SUM({metric_column}) * 1.0 / t.GrandTotal AS ContributionPct
FROM {fact_table}
WHERE YEAR({date_column}) >= 2013
CROSS JOIN totals t
GROUP BY {dimension_name}, t.GrandTotal
ORDER BY ContributionPct DESC""",
        "governance": [
            "Prevent divide by zero",
            "Enforce float division",
            "Use YEAR() >= 2013 for historical data"
        ]
    },
    {
        "intent": "Variance vs Previous Period",
        "english": "Show month-over-month revenue growth.",
        "sql": """WITH monthly AS (
    SELECT
        DATEFROMPARTS(YEAR({date_column}),MONTH({date_column}),1) AS MonthStart,
        SUM({metric_column}) AS Revenue
    FROM {fact_table}
    WHERE YEAR({date_column}) >= 2013
    GROUP BY DATEFROMPARTS(YEAR({date_column}),MONTH({date_column}),1)
)
SELECT
    cur.MonthStart,
    cur.Revenue,
    prev.Revenue AS PrevRevenue,
    CASE WHEN prev.Revenue = 0 THEN NULL
         ELSE (cur.Revenue - prev.Revenue)/prev.Revenue END AS GrowthRate
FROM monthly cur
LEFT JOIN monthly prev ON DATEADD(MONTH,-1,cur.MonthStart)=prev.MonthStart
ORDER BY cur.MonthStart""",
        "governance": [
            "Require NULLIF logic for divide-by-zero",
            "Use YEAR() >= 2013 for historical data"
        ]
    },
    {
        "intent": "Threshold Alert",
        "english": "Show products where stock is below reorder level.",
        "sql": """SELECT
    {product_name},
    {quantity_column},
    {reorder_column}
FROM {inventory_table}
WHERE {quantity_column} < {reorder_column}
ORDER BY {quantity_column} ASC""",
        "governance": [
            "Comparison operator validated",
            "No aggregation needed",
            "No date filter needed for inventory"
        ]
    },
    {
        "intent": "Distinct Count",
        "english": "How many unique customers placed orders this quarter?",
        "sql": """SELECT COUNT(DISTINCT {customer_id_column}) AS UniqueCustomers
FROM {fact_table}
WHERE YEAR({date_column}) >= 2013""",
        "governance": [
            "DISTINCT usage validated",
            "Use YEAR() >= 2013 for historical data"
        ]
    },
    {
        "intent": "Top Customers by Revenue",
        "english": "Show me top 10 customers by revenue",
        "sql": """SELECT TOP 10
    c.CustomerID,
    p.FirstName + ' ' + p.LastName AS CustomerName,
    SUM(soh.TotalDue) AS total_revenue
FROM Sales.Customer c
INNER JOIN Person.Person p ON c.PersonID = p.BusinessEntityID
INNER JOIN Sales.SalesOrderHeader soh ON c.CustomerID = soh.CustomerID
GROUP BY c.CustomerID, p.FirstName, p.LastName
ORDER BY total_revenue DESC""",
        "governance": [
            "MUST use Sales.Customer, Person.Person, Sales.SalesOrderHeader",
            "MUST join Customer -> Person for names",
            "MUST use SUM(TotalDue) for revenue",
            "MUST GROUP BY CustomerID and name columns",
            "MUST ORDER BY total_revenue DESC",
            "Use TOP 10 for SQL Server",
            "Never use AWBuildVersion, ErrorLog, or DatabaseLog tables"
        ]
    }
]

def get_few_shot_prompt() -> str:
    """Generate a few-shot prompt from the templates for the LLM."""
    prompt = """You are a SQL Server expert. Generate SQL Server T-SQL queries based on user questions.

CRITICAL RULES FOR DATE FILTERING:
⚠️  IMPORTANT: AdventureWorks data is HISTORICAL (2011-2014). Do NOT use GETDATE() for date ranges.
⚠️  If user asks about "last 12 months", "this year", "recent", use actual data range: WHERE YEAR(date_column) >= 2013
⚠️  If user asks about "monthly revenue", "trends", "history", use: WHERE YEAR(date_column) >= 2011
⚠️  NEVER filter for dates beyond 2014 - the data doesn't exist there
⚠️  When in doubt, remove the WHERE clause entirely to return all available data

IMPORTANT RULES:
1. Use TOP instead of LIMIT for SQL Server
2. Always include proper date filtering (but use actual data range, not GETDATE())
3. Use GROUP BY when aggregating
4. Avoid SELECT * - specify columns explicitly
5. Use DATEFROMPARTS, DATEADD, DATEDIFF for date logic
6. Use CASE WHEN for conditional logic
7. Prevent divide-by-zero errors with CASE or NULLIF
8. Use CTEs (WITH) for complex queries
9. Always order results meaningfully
10. Use meaningful column aliases

EXAMPLE PATTERNS:

"""
    
    for i, template in enumerate(FEW_SHOT_TEMPLATES, 1):
        prompt += f"\n{i}. {template['intent']}\n"
        prompt += f"   Question: {template['english']}\n"
        prompt += f"   SQL:\n"
        for line in template['sql'].split('\n'):
            prompt += f"   {line}\n"
        prompt += f"   Rules: {', '.join(template['governance'])}\n"
    
    return prompt

def get_template_by_intent(intent: str) -> dict:
    """Get a template by intent name."""
    for template in FEW_SHOT_TEMPLATES:
        if template['intent'].lower() == intent.lower():
            return template
    return None

def get_all_intents() -> list:
    """Get list of all available intents."""
    return [t['intent'] for t in FEW_SHOT_TEMPLATES]

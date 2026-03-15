"""
VoxCore SQL Reasoning Engine (SRE)
Handles multi-step analytical questions by building and executing reasoning plans.
"""
from typing import List, Dict

# Example reasoning plan patterns (could be loaded from YAML)
REASONING_PATTERNS = {
    "growth_comparison": [
        {"step": "aggregate_revenue", "sql_pattern": "revenue_by_product_quarter"},
        {"step": "compute_growth", "sql_pattern": "lag_growth"},
        {"step": "rank_results", "sql_pattern": "top_growth"},
    ],
    "churn_detection": [
        {"step": "last_purchase", "sql_pattern": "last_purchase_by_customer"},
        {"step": "churn_filter", "sql_pattern": "churn_window_filter"},
    ],
    "trend_analysis": [
        {"step": "monthly_revenue", "sql_pattern": "revenue_by_region_month"},
        {"step": "trend_detection", "sql_pattern": "lag_trend"},
        {"step": "identify_decline", "sql_pattern": "decline_filter"},
    ],
}

def build_reasoning_plan(question: str) -> str:
    """
    Detect reasoning type from question.
    Args:
        question (str): User question
    Returns:
        str: Reasoning type
    """
    q = question.lower()
    if "growth" in q:
        return "growth_comparison"
    if "churn" in q:
        return "churn_detection"
    if "declining" in q or "trend" in q:
        return "trend_analysis"
    return "simple"

def get_reasoning_steps(reasoning_type: str) -> List[Dict]:
    return REASONING_PATTERNS.get(reasoning_type, [])

def generate_sql(step: Dict) -> str:
    # TODO: Map sql_pattern to actual SQL templates or generation logic
    return f"-- SQL for {step['sql_pattern']}"

def run_query(sql: str):
    # TODO: Connect to DB and run the SQL, return results
    return f"[Result for: {sql}]"

def execute_reasoning(question: str):
    reasoning_type = build_reasoning_plan(question)
    steps = get_reasoning_steps(reasoning_type)
    results = []
    for step in steps:
        sql = generate_sql(step)
        result = run_query(sql)
        results.append({"step": step["step"], "sql": sql, "result": result})
    return results

if __name__ == "__main__":
    question = "Which products grew the fastest quarter over quarter?"
    results = execute_reasoning(question)
    for r in results:
        print(f"Step: {r['step']}\nSQL: {r['sql']}\nResult: {r['result']}\n---")

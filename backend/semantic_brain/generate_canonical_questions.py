"""
Auto-generate canonical benchmark questions from the semantic layer.
Run this script after updating metrics/dimensions to refresh canonical_questions.py.
"""
import json
from pathlib import Path

# Example: Replace with actual imports from your semantic layer
# from .metric_registry import METRICS
# from .dimension_catalog import DIMENSIONS

# --- Example semantic layer definitions (replace with real imports) ---
METRICS = [
    {
        "metric_name": "total_revenue",
        "table": "orders",
        "formula": "SUM(order_amount)",
        "time_dimension": "created_at"
    },
    {
        "metric_name": "total_orders",
        "table": "orders",
        "formula": "COUNT(order_id)",
        "time_dimension": "created_at"
    },
    {
        "metric_name": "total_profit",
        "table": "orders",
        "formula": "SUM(profit)",
        "time_dimension": "created_at"
    }
]

DIMENSIONS = ["product", "region", "customer", "month", "year"]

# --- Question generation logic ---
def generate_metric_questions(metric):
    return [{
        "category": "revenue" if "revenue" in metric["metric_name"] else "metric",
        "question": f"What is {metric['metric_name'].replace('_', ' ')}?",
        "expected_intent": "aggregation",
        "expected_metric": metric["metric_name"],
        "expected_dimension": None,
        "time_filter": None,
        "expected_sql": f"SELECT {metric['formula']} FROM {metric['table']}"
    }]

def generate_grouped_questions(metric, dimensions):
    questions = []
    for dim in dimensions:
        questions.append({
            "category": "grouped_analysis",
            "question": f"{metric['metric_name'].replace('_', ' ').capitalize()} by {dim}",
            "expected_intent": "grouped_aggregation",
            "expected_metric": metric["metric_name"],
            "expected_dimension": dim,
            "time_filter": None,
            "expected_sql": f"SELECT {dim}, {metric['formula']} FROM {metric['table']} GROUP BY {dim}"
        })
    return questions

def generate_ranking_questions(metric, dimensions):
    questions = []
    for dim in dimensions:
        questions.append({
            "category": "ranking",
            "question": f"Top 5 {dim}s by {metric['metric_name'].replace('_', ' ')}",
            "expected_intent": "ranking",
            "expected_metric": metric["metric_name"],
            "expected_dimension": dim,
            "time_filter": None,
            "expected_sql": f"SELECT {dim}, {metric['formula']} FROM {metric['table']} GROUP BY {dim} ORDER BY {metric['formula']} DESC LIMIT 5"
        })
    return questions

def generate_time_questions(metric):
    time_questions = []
    if metric.get("time_dimension"):
        td = metric["time_dimension"]
        # Last month
        time_questions.append({
            "category": "time",
            "question": f"{metric['metric_name'].replace('_', ' ').capitalize()} last month",
            "expected_intent": "time_filter",
            "expected_metric": metric["metric_name"],
            "expected_dimension": None,
            "time_filter": "previous_month",
            "expected_sql": f"SELECT {metric['formula']} FROM {metric['table']} WHERE {td} >= DATE_TRUNC('month', CURRENT_DATE - INTERVAL '1 month') AND {td} < DATE_TRUNC('month', CURRENT_DATE)"
        })
        # This year
        time_questions.append({
            "category": "time",
            "question": f"{metric['metric_name'].replace('_', ' ').capitalize()} this year",
            "expected_intent": "time_filter",
            "expected_metric": metric["metric_name"],
            "expected_dimension": None,
            "time_filter": "current_year",
            "expected_sql": f"SELECT {metric['formula']} FROM {metric['table']} WHERE EXTRACT(YEAR FROM {td}) = EXTRACT(YEAR FROM CURRENT_DATE)"
        })
        # By month
        time_questions.append({
            "category": "time",
            "question": f"{metric['metric_name'].replace('_', ' ').capitalize()} by month",
            "expected_intent": "grouped_aggregation",
            "expected_metric": metric["metric_name"],
            "expected_dimension": "month",
            "time_filter": None,
            "expected_sql": f"SELECT EXTRACT(MONTH FROM {td}) AS month, {metric['formula']} FROM {metric['table']} GROUP BY month"
        })
        # By year
        time_questions.append({
            "category": "time",
            "question": f"{metric['metric_name'].replace('_', ' ').capitalize()} by year",
            "expected_intent": "grouped_aggregation",
            "expected_metric": metric["metric_name"],
            "expected_dimension": "year",
            "time_filter": None,
            "expected_sql": f"SELECT EXTRACT(YEAR FROM {td}) AS year, {metric['formula']} FROM {metric['table']} GROUP BY year"
        })
    return time_questions

def main():
    questions = []
    for metric in METRICS:
        questions.extend(generate_metric_questions(metric))
        questions.extend(generate_grouped_questions(metric, DIMENSIONS))
        questions.extend(generate_ranking_questions(metric, DIMENSIONS))
        questions.extend(generate_time_questions(metric))

    # Write to canonical_questions.py
    py_path = Path(__file__).parent / "canonical_questions.py"
    with open(py_path, "w", encoding="utf-8") as f:
        f.write("# AUTO-GENERATED. Edit generate_canonical_questions.py, not this file.\n")
        f.write("CANONICAL_QUESTIONS = ")
        json.dump(questions, f, indent=4)
        f.write("\n")
    print(f"Wrote {len(questions)} canonical questions to {py_path}")

if __name__ == "__main__":
    main()

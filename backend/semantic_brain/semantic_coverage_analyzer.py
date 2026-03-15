"""
VoxCore Semantic Coverage Analyzer
==================================

Analyzes canonical_questions.py and the semantic layer to report:
    - Category coverage
    - Metric coverage
    - Dimension coverage
    - Time intelligence coverage

Outputs a semantic_coverage_report.txt file in the same directory and prints a summary to the console.

USAGE:
    python semantic_coverage_analyzer.py

OUTPUT:
    - Prints a summary report to the console
    - Writes semantic_coverage_report.txt in backend/semantic_brain/

EXAMPLE OUTPUT:
    VoxCore Semantic Coverage Report
    Total Questions: 70
    Category Coverage:
    revenue_sales: 10
    grouped_analysis: 15
    ...
    Metric Coverage:
    revenue: 12
    orders: 8
    ...
    Dimension Coverage:
    region: 5
    month: 7
    ...

NOTES:
    - Update canonical_questions.py to add new questions or categories.
    - Extend METRICS and DIMENSIONS imports for full semantic layer coverage.
"""

# --- Imports ---
from collections import Counter
from canonical_questions import CANONICAL_QUESTIONS
# Example: Replace with actual imports from your semantic layer
# from .metric_registry import METRICS
# from .dimension_catalog import DIMENSIONS

# --- Example semantic layer definitions (replace with real imports) ---
METRICS = [
    "total_revenue",
    "total_orders",
    "total_profit"
]
DIMENSIONS = ["product", "region", "customer", "month", "year"]

# --- Coverage analysis ---
categories = Counter()
metrics = Counter()
dimensions = Counter()

# Count coverage for each canonical question
for q in CANONICAL_QUESTIONS:
    categories[q.get("category")] += 1
    metrics[q.get("expected_metric")] += 1
    dimensions[q.get("expected_dimension")] += 1

# --- Build report ---
report = []
report.append("VoxCore Semantic Coverage Report\n")
report.append(f"Total Questions: {len(CANONICAL_QUESTIONS)}\n")

report.append("Category Coverage:")
for k, v in categories.items():
    report.append(f"{k}: {v}")

report.append("\nMetric Coverage:")
for k, v in metrics.items():
    report.append(f"{k}: {v}")

report.append("\nDimension Coverage:")
for k, v in dimensions.items():
    report.append(f"{k}: {v}")

output = "\n".join(report)
print(output)

# --- Write report to file ---
import os
output_path = os.path.join(os.path.dirname(__file__), "semantic_coverage_report.txt")
with open(output_path, "w", encoding="utf-8") as f:
    f.write(output)
print(f"[INFO] Semantic coverage report written to {output_path}")

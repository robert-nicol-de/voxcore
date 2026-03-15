"""
VoxCore Benchmark Runner
=======================

Runs all benchmark and canonical analytics questions through the VoxCore Brain and logs results.

INPUTS:
    - BENCHMARK_QUESTIONS: List of dicts with keys: question, intent, metric, dimension, paraphrases, category
    - CANONICAL_QUESTIONS: List of dicts with keys: question, expected_intent, expected_metric, expected_dimension, expected_sql, category

OUTPUTS:
    - benchmark_results.json: Contains all results, per-category scores, and overall score
    - Logs progress and summary to the console

USAGE:
    python benchmark_runner.py

EXAMPLE OUTPUT:
    {
        "results": [...],
        "category_scores": {"revenue_sales": 90, ...},
        "overall_score": 87
    }

NOTES:
    - Extend BENCHMARK_QUESTIONS and CANONICAL_QUESTIONS to improve coverage.
    - Results are used for CI/CD analytics and dashboard reporting.
"""

import os
import sys
# Add project root to sys.path for backend imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

import logging

from backend.semantic_brain.benchmark_questions import BENCHMARK_QUESTIONS
from backend.semantic_brain.canonical_questions import CANONICAL_QUESTIONS
from backend.semantic_brain.training_dataset import TrainingDataset
from backend.semantic_brain.semantic_service import SemanticBrainService

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')

def run_benchmark():
    """
    Runs all benchmark and canonical questions, logs results, and writes a summary JSON file.
    """
    dataset = TrainingDataset()
    brain = SemanticBrainService()
    results = []

    # --- Run benchmark questions and paraphrases ---
    for q in BENCHMARK_QUESTIONS:
        all_phrases = [q["question"]] + q.get("paraphrases", [])
        for phr in all_phrases:
            logging.info(f"Running benchmark: {phr}")
            result = brain.build_payload(phr, workspace_id=1, ai_context={})
            results.append({
                "input": phr,
                "expected_intent": q["intent"],
                "expected_metric": q["metric"],
                "expected_dimension": q["dimension"],
                "result": result,
                "type": "benchmark",
                "category": q.get("category", "benchmark")
            })

    # --- Run canonical questions with structured expectations ---
    for q in CANONICAL_QUESTIONS:
        phr = q["question"]
        logging.info(f"Running canonical: {phr}")
        result = brain.build_payload(phr, workspace_id=1, ai_context={})
        results.append({
            "input": phr,
            "expected_intent": q.get("expected_intent"),
            "expected_metric": q.get("expected_metric"),
            "expected_dimension": q.get("expected_dimension"),
            "expected_sql": q.get("expected_sql"),
            "result": result,
            "type": "canonical",
            "category": q.get("category", "uncategorized")
        })

    # --- Scoring logic: compare expected vs actual for each canonical question ---
    category_scores = {}
    category_totals = {}
    for r in results:
        if r["type"] != "canonical":
            continue
        cat = r.get("category", "uncategorized")
        category_totals[cat] = category_totals.get(cat, 0) + 1
        actual = r["result"]
        # Compare intent, metric, dimension (case-insensitive, None-safe)
        match = True
        if r.get("expected_intent") and actual.get("intent", {}).get("intent_type"):
            match = match and (str(r["expected_intent"]).lower() == str(actual["intent"]["intent_type"]).lower())
        if r.get("expected_metric") and actual.get("intent", {}).get("metric"):
            match = match and (str(r["expected_metric"]).lower() == str(actual["intent"]["metric"]).lower())
        if r.get("expected_dimension") and actual.get("intent", {}).get("dimension"):
            match = match and (str(r["expected_dimension"]).lower() == str(actual["intent"]["dimension"]).lower())
        if match:
            category_scores[cat] = category_scores.get(cat, 0) + 1

    # --- Compute percentage scores ---
    category_percent = {cat: int(100 * category_scores.get(cat, 0) / total) for cat, total in category_totals.items()}
    overall_score = int(sum(category_scores.values()) * 100 / max(1, sum(category_totals.values())))

    # --- Write results and scores to a file ---
    with open("benchmark_results.json", "w", encoding="utf-8") as f:
        import json
        output = {
            "results": results,
            "category_scores": category_percent,
            "overall_score": overall_score
        }
        json.dump(output, f, indent=2, ensure_ascii=False)
    logging.info(f"Benchmark complete. Results written to benchmark_results.json")
    logging.info(f"VoxCore Intelligence Score: {overall_score}% by category: {category_percent}")

if __name__ == "__main__":
    run_benchmark()

"""
VoxCore SQL Benchmark Runner
Professional, enterprise-grade test harness for SQL engine evaluation.
"""
import yaml
import os

BENCHMARK_PATH = os.path.join(os.path.dirname(__file__), '../training/sql_benchmark_500.yaml')


def load_benchmark():
    with open(BENCHMARK_PATH, encoding='utf-8') as f:
        data = yaml.safe_load(f)
    return data["examples"]


def run_benchmark(engine, verbose=True):
    examples = load_benchmark()
    passed = 0
    failed = 0
    failures = []

    for ex in examples:
        question = ex["question"]
        expected_sql = ex["sql"].strip()
        generated_sql = engine.generate_sql(question).strip()

        if generated_sql == expected_sql:
            passed += 1
        else:
            failed += 1
            failures.append({
                "id": ex.get("id"),
                "category": ex.get("category"),
                "question": question,
                "expected": expected_sql,
                "actual": generated_sql
            })
            if verbose:
                print(f"FAILED: {question}\nExpected:\n{expected_sql}\nActual:\n{generated_sql}\n---")

    print(f"PASSED: {passed}")
    print(f"FAILED: {failed}")
    if failed > 0:
        print("\nFailure details:")
        for fail in failures:
            print(f"ID: {fail['id']} | Category: {fail['category']}\nQ: {fail['question']}\nExpected:\n{fail['expected']}\nActual:\n{fail['actual']}\n---")
    return passed, failed, failures


if __name__ == "__main__":
    class DummyEngine:
        def generate_sql(self, question):
            # Placeholder for integration
            return ""

    run_benchmark(DummyEngine())

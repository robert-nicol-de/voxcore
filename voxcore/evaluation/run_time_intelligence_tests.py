
"""
SQL Time Intelligence Benchmark Runner
Runs SQL generation tests using the time intelligence dataset and reports accuracy metrics.
"""
from voxcore.training.load_sql_training import load_sql_training_dataset

def compare_sql(generated, expected):
    # Simple comparison, can be improved for whitespace, case, etc.
    return generated.strip().lower() == expected.strip().lower()



def run_time_intelligence_tests(dataset_path, sql_generator):
    dataset = load_sql_training_dataset(dataset_path)
    total = 0
    passed = 0
    failed = 0
    for example in dataset.get("examples", []):
        question = example.get("question")
        expected_sql = example.get("expected_sql") or example.get("sql")
        generated_sql = sql_generator(question)
        if compare_sql(generated_sql, expected_sql):
            result = "PASS"
            passed += 1
        else:
            result = "FAIL"
            failed += 1
        print(f"Q: {question}\nResult: {result}\n")
        total += 1
    accuracy = (passed / total * 100) if total else 0
    print("Time Intelligence Benchmark Results")
    print(f"Total Tests: {total}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"Accuracy: {accuracy:.1f}%")

if __name__ == "__main__":
    # Example: plug in your SQL generator here
    def dummy_sql_generator(question):
        return "-- SQL output for: " + question
    run_time_intelligence_tests("voxcore/training/sql_time_intelligence.yaml", dummy_sql_generator)

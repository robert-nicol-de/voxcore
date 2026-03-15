import sys
from pathlib import Path
import yaml

def load_time_intelligence_dataset(path=None):
    if path is None:
        path = Path(__file__).parent.parent / "training" / "sql_time_intelligence.yaml"
    with open(path, "r") as file:
        data = yaml.safe_load(file)
    return data

def compare_sql(generated, expected):
    # Simple whitespace-insensitive comparison
    return generated.strip().replace("\n", " ").replace("  ", " ") == expected.strip().replace("\n", " ").replace("  ", " ")

# Dummy VUSE SQL generator for demonstration
class DummyVUSE:
    def generate_sql(self, question):
        # In real use, call the actual VUSE engine
        return "-- SQL output for: " + question

if __name__ == "__main__":
    dataset = load_time_intelligence_dataset()
    vuse = DummyVUSE()
    total = len(dataset["examples"])
    passed = 0
    for example in dataset["examples"]:
        generated_sql = vuse.generate_sql(example["question"])
        expected_sql = example["sql"]
        if compare_sql(generated_sql, expected_sql):
            result = "PASS"
            passed += 1
        else:
            result = "FAIL"
        print(f"{example['question']} => {result}")
    print(f"\nTime Intelligence Benchmark Results\nTotal Tests: {total}\nPassed: {passed}\nFailed: {total - passed}\nAccuracy: {passed/total*100:.1f}%")

import yaml
from pathlib import Path

DATASET_PATH = Path(__file__).parent / "sql_training_dataset.yaml"

def load_sql_training_data():
    with open(DATASET_PATH, "r") as f:
        data = yaml.safe_load(f)
    return data["examples"]

def get_example(example_id):
    examples = load_sql_training_data()
    for ex in examples:
        if ex["id"] == example_id:
            return ex
    return None

# Usage example:
if __name__ == "__main__":
    examples = load_sql_training_data()
    for example in examples:
        print(example["question"])

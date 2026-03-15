import yaml
from pathlib import Path

def load_time_intelligence_dataset(path=None):
    if path is None:
        path = Path(__file__).parent / "sql_time_intelligence.yaml"
    with open(path, "r") as file:
        data = yaml.safe_load(file)
    return data

if __name__ == "__main__":
    dataset = load_time_intelligence_dataset()
    for example in dataset["examples"]:
        print(example["question"])

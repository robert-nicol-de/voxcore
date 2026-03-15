"""
SQL Training Dataset Loader
Loads YAML datasets for SQL training and benchmarking.
"""
import yaml
from pathlib import Path

def load_dataset(dataset_path):
    with open(dataset_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return data["examples"]

def load_all_datasets():
    dataset_folder = Path(__file__).parent / "datasets"
    datasets = []
    for file in dataset_folder.glob("*.yaml"):
        datasets.extend(load_dataset(file))
    return datasets

if __name__ == "__main__":
    # Example: load and print all questions from all datasets
    all_examples = load_all_datasets()
    for example in all_examples:
        print(example.get("question"))

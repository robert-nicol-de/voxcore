import yaml
from pathlib import Path

PATTERN_FILE = Path(__file__).parent / "query_patterns.yaml"

def load_patterns():
    with open(PATTERN_FILE, "r") as f:
        return yaml.safe_load(f)["patterns"]

PATTERNS = load_patterns()

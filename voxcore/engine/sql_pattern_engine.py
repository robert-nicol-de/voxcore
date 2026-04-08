import yaml
from pathlib import Path

class SQLPatternEngine:
    def __init__(self, path=None):
        if path is None:
            path = Path(__file__).parent.parent / 'training' / 'sql_patterns.yaml'
        with open(path, 'r', encoding='utf-8') as f:
            self.patterns = yaml.safe_load(f)["patterns"]

    def detect_pattern(self, question):
        # Only use for query shape classification, not for semantic meaning extraction
        q = question.lower()
        for name, pat in self.patterns.items():
            for kw in pat.get("question_pattern", []):
                if kw in q:
                    # Ensure this is not used for metric/dimension/meaning extraction
                    return name
        return "default"

    def get_template(self, pattern_name):
        return self.patterns.get(pattern_name, {}).get("sql_template")

    def fill_template(self, template, **kwargs):
        return template.format(**kwargs)

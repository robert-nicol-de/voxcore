import yaml
from pathlib import Path

class InsightMemory:
    def __init__(self, path=None):
        self.path = path or (Path(__file__).parent.parent / 'insights' / 'insight_memory.yaml')
        self.insights = []
        self.relationships = []
        self.load()

    def load(self):
        if Path(self.path).exists():
            with open(self.path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
                if isinstance(data, list):
                    self.insights = data
                    self.relationships = []
                elif isinstance(data, dict):
                    self.insights = data.get('insights', [])
                    self.relationships = data.get('relationships', [])
        else:
            self.insights = []
            self.relationships = []

    def save(self):
        with open(self.path, 'w', encoding='utf-8') as f:
            yaml.safe_dump(self.insights + [{'relationships': self.relationships}], f)

    def store_insight(self, insight):
        self.insights.append(insight)
        self.save()

    def link_insights(self, parent, child, relationship):
        self.relationships.append({
            'from': parent,
            'to': child,
            'relationship': relationship
        })
        self.save()

    def find_related_insights(self, metric=None, entity=None):
        matches = []
        for insight in self.insights:
            if (metric is None or insight.get('metric') == metric) and \
               (entity is None or insight.get('entity') == entity):
                matches.append(insight)
        return matches

    def get_all_insights(self):
        return self.insights

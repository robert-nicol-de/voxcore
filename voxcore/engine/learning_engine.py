class LearningEngine:
    def detect_patterns(self, memory):
        insights = memory.get_all_insights()
        patterns = {}
        for i in insights:
            key = i.get("metric")
            patterns.setdefault(key, 0)
            patterns[key] += 1
        return patterns

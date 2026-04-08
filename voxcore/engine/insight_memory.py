from backend.db.insight_store import store_insight, get_all_insights

class InsightMemory:
    def store_insight(self, insight, score=0.0):
        store_insight(insight, score)

    def get_all_insights(self):
        return get_all_insights()

"""
VoxCore Timeline Engine
Builds a chronological timeline of insights, anomalies, trends, root causes, and alerts from Insight Memory.
"""
from datetime import datetime, timedelta

class TimelineEngine:
    def __init__(self, insight_memory):
        self.insight_memory = insight_memory

    def build_timeline(self, start_date=None, end_date=None, days=None, entity=None, metric=None):
        insights = self.insight_memory.get_all_insights()
        # Filter by date range
        if days is not None:
            end = datetime.now().date()
            start = end - timedelta(days=days)
        else:
            start = datetime.strptime(start_date, "%Y-%m-%d").date() if start_date else None
            end = datetime.strptime(end_date, "%Y-%m-%d").date() if end_date else None
        def in_range(insight):
            if "detected_at" not in insight:
                return False
            try:
                d = datetime.strptime(insight["detected_at"], "%Y-%m-%d").date()
            except Exception:
                return False
            if start and d < start:
                return False
            if end and d > end:
                return False
            return True
        filtered = [i for i in insights if in_range(i)]
        if entity:
            filtered = [i for i in filtered if i.get("entity") == entity]
        if metric:
            filtered = [i for i in filtered if i.get("metric") == metric]
        timeline = sorted(filtered, key=lambda x: x.get("detected_at", ""))
        return timeline

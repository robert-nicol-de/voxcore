"""
VoxCore Insight Narrative Engine
Converts technical outputs and root cause chains into clear, human-style explanations.
"""
class InsightNarrativeEngine:
    def generate(self, insight):
        t = insight.get("type")
        if t == "trend_decline":
            return f"{insight.get('metric', '').capitalize()} declined {insight.get('percent_change', '')}% in {insight.get('entity', '')} during {insight.get('period', '')}."
        if t == "top_performer":
            return f"{insight.get('entity', '')} generated the highest {insight.get('metric', '')}."
        if t == "root_cause":
            return f"Root cause: {insight.get('cause', '')} for {insight.get('entity', '')}."
        if t == "exploration":
            return f"Explore {insight.get('metric', '')} by {insight.get('dimension', '')}."
        return "Insight detected."

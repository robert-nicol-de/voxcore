# Query Planning Engine for VoxCore
from backend.neutral_query import NeutralQuery
from typing import Dict, Any

class QueryPlanner:
    @staticmethod
    def plan(user_intent: Dict[str, Any]) -> NeutralQuery:
        """
        Convert parsed user intent into a NeutralQuery.
        user_intent: dict with keys like metric, table, group_by, filters, etc.
        """
        return NeutralQuery(**user_intent)

# Example usage:
# user_intent = {"metric": "revenue", "table": "orders", "group_by": ["region"], "time_filter": "last_30_days", "limit": 10, "sort": "revenue DESC"}
# nq = QueryPlanner.plan(user_intent)

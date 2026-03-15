# Example SQL Benchmark Test: revenue_by_region
from backend.query_planner import QueryPlanner
from backend.sql_dialects.registry import get_sql_engine
from backend.neutral_query import NeutralQuery

def test_revenue_by_region():
    user_intent = {
        "metric": "revenue",
        "table": "orders",
        "group_by": ["region"],
        "time_filter": "last_30_days",
        "limit": 10,
        "sort": "revenue DESC"
    }
    nq = QueryPlanner.plan(user_intent)
    sql = get_sql_engine("postgres").to_sql(nq)
    assert "SELECT" in sql and "FROM orders" in sql
    # Add more assertions for correctness, performance, and result accuracy

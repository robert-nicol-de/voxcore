import time
from typing import Dict, Any

from voxcore.engine.conversation_state_engine import ConversationStateEngine
from voxcore.engine.sql_pattern_engine import SQLPatternEngine
from voxcore.engine.sql_knowledge_graph import SQLKnowledgeGraph
from voxcore.engine.query_cost_analyzer import estimate_query_cost
from voxcore.engine.adaptive_query_optimizer import optimize_query
from voxcore.engine.insight_engine import generate_insights
from voxcore.engine.insight_narrative_engine import InsightNarrativeEngine
from voxcore.engine.exploration_engine import generate_related_queries

# --- Initialize shared components ---
state_engine = ConversationStateEngine()
pattern_engine = SQLPatternEngine()
narrative_engine = InsightNarrativeEngine()

# Optional: load KG if you have schema yaml
# knowledge_graph = SQLKnowledgeGraph("path_to_schema.yaml")

# --- SIMPLE SQL GENERATOR (replace later with full planner) ---
def generate_sql(plan: Dict[str, Any]) -> str:
    metric = plan.get("metric", "revenue")
    dimension = plan.get("dimension", "region")
    table = plan.get("table", "sales")

    return f"""
    SELECT {dimension}, SUM({metric}) as value
    FROM {table}
    GROUP BY {dimension}
    ORDER BY value DESC
    """

# --- MOCK EXECUTION (replace with real DB call) ---
def execute_sql(sql: str, db_connection=None):
    # TODO: Replace with real DB execution
    # Simulated dataset
    return [
        {"region": "North", "value": 120000},
        {"region": "South", "value": 95000},
        {"region": "West", "value": 87000},
        {"region": "East", "value": 65000},
    ]

# --- BUILD QUERY PLAN ---
def build_query_plan(question: str, state: Dict[str, Any]) -> Dict[str, Any]:
    q = question.lower()

    plan = {
        "metric": state.get("metric", "revenue"),
        "dimension": state.get("dimension", "region"),
        "table": "sales",
        "filters": [],
    }

    if "product" in q:
        plan["dimension"] = "product"

    if "customer" in q:
        plan["dimension"] = "customer"

    return plan

# --- MAIN PIPELINE ---
def execute_pipeline(question: str, session_id: str, db_connection=None) -> Dict[str, Any]:
    start_time = time.time()

    # 1. STATE
    state = state_engine.get_state(session_id)

    updates = {}
    q = question.lower()
    if "revenue" in q:
        updates["metric"] = "revenue"
    if "sales" in q:
        updates["metric"] = "sales"
    if "region" in q:
        updates["dimension"] = "region"
    if "product" in q:
        updates["dimension"] = "product"

    state = state_engine.update_state(session_id, updates)

    # 2. PLAN
    plan = build_query_plan(question, state)

    # 3. SQL GENERATION
    sql = generate_sql(plan)

    # 4. COST ESTIMATION
    cost_score = estimate_query_cost(
        join_count=0,
        has_filter=False,
        estimated_rows=50000,
        result_rows=1000
    )

    if cost_score > 80:
        return {
            "narrative": "Query blocked due to high cost risk.",
            "insights": [],
            "chart": None,
            "data": [],
            "suggestions": [],
            "metadata": {
                "cost_score": cost_score,
                "execution_time": 0
            }
        }

    # 5. OPTIMIZATION
    sql = optimize_query(sql)

    # 6. EXECUTION
    data = execute_sql(sql, db_connection)

    # 7. INSIGHTS
    insights = generate_insights("top_performers", data)

    # 8. NARRATIVE
    narrative = insights[0]["insight"] if insights else "No insights found."

    # 9. CHART CONFIG
    chart = {
        "type": "bar",
        "x_axis": list(data[0].keys())[0] if data else "x",
        "y_axis": list(data[0].keys())[1] if data else "y"
    }

    # 10. SUGGESTIONS
    suggestions = [
        f"{plan['metric']} by product",
        f"{plan['metric']} trend over time",
        f"{plan['metric']} by customer"
    ]

    execution_time = int((time.time() - start_time) * 1000)

    return {
        "narrative": narrative,
        "insights": insights,
        "chart": chart,
        "data": data,
        "suggestions": suggestions,
        "metadata": {
            "cost_score": cost_score,
            "execution_time": execution_time
        }
    }

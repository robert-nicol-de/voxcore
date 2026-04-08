"""
VoxCore Query Router
Routes user questions to either the SQL Reasoning Engine (SRE) or the standard SQL pipeline.
"""
from voxcore.engine.sql_reasoning_engine import execute_reasoning
from voxcore.engine.sql_pipeline import execute_sql_pipeline

REASONING_KEYWORDS = [
    "why",
    "reason",
    "cause",
    "explain",
    "drop",
    "decline",
    "increase",
    "change",
    "anomaly",
    "spike",
    "trend",
    "growth",
    "declining",
    "churn",
    "decrease"
]

def is_reasoning_query(question: str):
    q = question.lower()
    return any(k in q for k in REASONING_KEYWORDS)

"""
DEPRECATED: route_query is no longer used. Use QueryPipeline instead.
"""
# def route_query(question, sql, metadata, db_connection):
#     if is_reasoning_query(question):
        # Multi-step reasoning: use SRE, run each step through the pipeline
        steps = []
        results = []
        plan = execute_reasoning(question)
        for step in plan:
            step_sql = step["sql"]
            step_metadata = {
                "join_count": step_sql.upper().count("JOIN"),
                "has_filter": "WHERE" in step_sql.upper(),
                "estimated_rows": 0,
                "result_rows": 0
            }
            result = execute_sql_pipeline(step_sql, db_connection, step_metadata)
            steps.append(f"Step: {step['step']} | SQL: {step_sql}")
            results.append({"step": step["step"], "sql": step_sql, "result": result})
        # Example: add a combined insight (placeholder)
        insight = {"summary": "Multi-step reasoning complete. See steps for details."}
        return {
            "steps": steps,
            "results": results,
            "insight": insight
        }
    # Simple query: use standard pipeline
    return execute_sql_pipeline(sql, db_connection, metadata)

if __name__ == "__main__":
    print("Query router ready. Integrate with your main engine.")

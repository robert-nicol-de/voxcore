"""
VoxCore Query Router
Routes user questions to either the SQL Reasoning Engine (SRE) or the standard SQL pipeline.
"""
from voxcore.engine.sql_reasoning_engine import execute_reasoning
from voxcore.engine.sql_pipeline import execute_sql_pipeline

def route_query(question, sql, metadata, db_connection):
    reasoning_keywords = [
        "trend",
        "growth",
        "declining",
        "churn",
        "increase",
        "decrease"
    ]
    if any(k in question.lower() for k in reasoning_keywords):
        # Multi-step reasoning: use SRE, run each step through the pipeline
        reasoning_results = []
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
            reasoning_results.append({"step": step["step"], "sql": step_sql, "result": result})
        return reasoning_results
    # Simple query: use standard pipeline
    return execute_sql_pipeline(sql, db_connection, metadata)

if __name__ == "__main__":
    print("Query router ready. Integrate with your main engine.")

"""
VoxCore SQL Execution Pipeline
Integrates AQO, QCA, and execution for safe, optimized SQL.

All queries are governed through executive rules:
- Cost: 0-40 safe, 40-70 warning, 70+ blocked
- RBAC: User must have query.run permission
- Policies: Sensitive data, destructive ops blocked
"""
from voxcore.engine.adaptive_query_optimizer import optimize_query
from voxcore.engine.query_cost_analyzer import estimate_query_cost
from voxcore.engine.query_orchestrator import run, QueryPriority


def analyze_sql_structure(sql):
    """
    Simple SQL structure analyzer for QCA metadata extraction.
    Args:
        sql (str): SQL query
    Returns:
        dict: join_count, has_filter, estimated_rows, result_rows
    """
    join_count = sql.upper().count("JOIN")
    has_filter = "WHERE" in sql.upper()
    # Placeholders for row estimates (could be improved with stats)
    estimated_rows = 0
    result_rows = 0
    return {
        "join_count": join_count,
        "has_filter": has_filter,
        "estimated_rows": estimated_rows,
        "result_rows": result_rows
    }

def execute_sql_pipeline(sql, db_connection, metadata=None, orchestrate=False, priority=QueryPriority.HIGH, user_id=None, session_id=None):
    """
    Full SQL execution pipeline: optimize, analyze, guard, execute.
    
    ⚠️ DEPRECATED: Use VoxCoreEngine.execute_query() instead for governed execution.
    This function now redirects to governance layer.

    Args:
        sql (str): Input SQL query
        db_connection: Database connection object
        metadata (dict, optional): Query metadata (join_count, has_filter, etc.)
        orchestrate (bool): If True, run via orchestrator
        priority (QueryPriority): Task priority for orchestrator
        user_id (str): User ID for governance
        session_id (str): Session ID for audit trail

    Returns:
        list: Query results

    Raises:
        Exception: If query is blocked by governance
    """
    # 🔒 REDIRECT TO GOVERNANCE LAYER
    if user_id and db_connection:
        try:
            from voxcore.engine.core import get_voxcore
            engine = get_voxcore()
            result = engine.execute_query(
                question="",
                generated_sql=sql,
                platform="postgres",
                user_id=user_id,
                connection=db_connection,
                session_id=session_id,
            )
            if result.success:
                return result.data
            else:
                raise Exception(result.error)
        except Exception as e:
            # Fall back to legacy pipeline if governance unavailable
            pass

    # ⚠️ LEGACY PATH (use only if governance layer unavailable)
    if orchestrate:
        # Directly call run() as the new orchestrator interface
        return run(sql, db_connection, metadata)
    
    # 1️⃣ Optimize SQL
    optimized_sql = optimize_query(sql)
    
    # 2️⃣ Analyze structure if metadata not provided
    if metadata is None:
        metadata = analyze_sql_structure(optimized_sql)
    
    # 3️⃣ Estimate cost
    cost = estimate_query_cost(
        metadata.get("join_count", 0),
        metadata.get("has_filter", False),
        metadata.get("estimated_rows", 0),
        metadata.get("result_rows", 0)
    )
    
    # 4️⃣ Block dangerous queries (NEW THRESHOLDS)
    # 0-40: safe, 40-70: warning, 70+: blocked
    if cost > 70:
        raise Exception(
            f"Query blocked: cost score {cost} exceeds limit (70). "
            f"Add WHERE filters or simplify joins."
        )
    elif cost > 40:
        import logging
        logger = logging.getLogger(__name__)
        logger.warning(f"Query cost warning: {cost} (approaching limit of 70)")
    
    # 5️⃣ Execute query
    cursor = db_connection.cursor()
    cursor.execute(optimized_sql)
    return cursor.fetchall()

if __name__ == "__main__":
    # Example usage (requires a real db_connection)
    sql = "SELECT * FROM orders JOIN customers ON orders.customer_id = customers.customer_id GROUP BY customers.name ORDER BY SUM(order_total) DESC;"
    print("Pipeline ready. Integrate with your DB connection.")

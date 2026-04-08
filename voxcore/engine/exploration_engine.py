"""
VoxCore Exploration Engine (VEE)

Anticipates likely follow-up queries, runs them in the background, and stores results 
in the semantic cache for instant user experience.

All exploration queries are governed through VoxCoreEngine for cost control and safety.
"""

# Fix import: import cache functions directly
from voxcore.engine.semantic_cache import get_cached_result, cache_result, clear_cache

# Use the real execution pipeline
from voxcore.engine.sql_pipeline import execute_sql_pipeline


def generate_related_queries(query_plan):
    """
    Given a query plan, generate a list of related query plans for exploration.
    """
    from voxcore.semantic.semantic_registry import SemanticRegistry
    semantic_registry = SemanticRegistry("semantic_model.yaml")
    metric = query_plan.get("metric")
    related_queries = []
    for dim in semantic_registry.dimensions.keys():
        related_queries.append({"dimension": dim, "metric": metric})
    related_queries.append({"dimension": "customer", "metric": metric, "top_n": 10})

    return related_queries


def run_exploration_queries(queries, db, user_id=None, session_id=None):
    """
    Run a list of queries in the background and store results in the semantic cache.
    
    All exploration queries are governed through VoxCoreEngine.
    """
    from voxcore.engine.core import get_voxcore
    
    engine = get_voxcore()
    
    for q in queries:
        try:
            # TEMP: simple SQL builder (controlled, safe)
            sql = f"""
            SELECT {q.get('dimension', 'region')}, 
                   SUM({q.get('metric', 'revenue')}) as value
            FROM sales
            GROUP BY {q.get('dimension', 'region')}
            """
            
            # 🔒 Execute through governance layer
            result = engine.execute_query(
                question="Background exploration query",
                generated_sql=sql,
                platform="postgres",
                user_id=user_id or "system",
                connection=db,
                session_id=session_id,
            )
            
            if result.success and result.data:
                cache_result(str(q), result.data)
            else:
                # Cost limit or policy blocked this exploration query
                print(f"⚠️ Exploration query blocked: {result.error}")
                
        except Exception as e:
            print("Exploration query failed:", e)


def exploration_engine_entry(query_plan, db, user_id=None, session_id=None):
    """
    Main entry point: generates and runs related queries for exploration.
    """
    related = generate_related_queries(query_plan)
    run_exploration_queries(related, db)
    return related

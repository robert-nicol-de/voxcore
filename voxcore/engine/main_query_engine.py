
"""
VoxCore Main Query Engine
Entry point for all user questions, routing through the full SQL intelligence stack.
"""
from voxcore.engine.query_router import route_query
from voxcore.engine.explain_my_data import explain_dataset
from voxcore.schema.load_schema_model import load_schema_model


def process_user_question(question, db_connection, sql=None, metadata=None, mode=None, schema_path=None):
    """
    Main entry point for user questions.
    Routes to the correct engine (simple, reasoning, or explain mode).
    Args:
        question (str): User's natural language question
        db_connection: Database connection object
        sql (str, optional): Pre-generated SQL (for simple queries)
        metadata (dict, optional): Query metadata (for simple queries)
        mode (str, optional): If 'explain', runs Explain My Data mode
        schema_path (str, optional): Path to schema YAML (for explain mode)
    Returns:
        Any: Query or reasoning result
    """
    if mode == "explain":
        schema = load_schema_model(schema_path) if schema_path else load_schema_model()
        insights = explain_dataset(schema, db_connection)
        return {
            "mode": "Explain My Data",
            "insights": insights
        }
    return route_query(
        question=question,
        sql=sql,
        metadata=metadata,
        db_connection=db_connection
    )

if __name__ == "__main__":
    print("Main Query Engine ready. Integrate with your API or CLI.")

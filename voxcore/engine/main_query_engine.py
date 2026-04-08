
"""
VoxCore Main Query Engine
Entry point for all user questions, routing through the full SQL intelligence stack.
"""


from voxcore.engine.emd_pipeline import EMDPipeline
from voxcore.schema.load_schema_model import load_schema_model
from voxcore.schema.schema_trust import compute_schema_trust
from voxcore.engine import query_orchestrator


def process_user_question(question, db_connection, sql=None, metadata=None, mode=None, schema_path=None, connection_id=None):
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
        pipeline = EMDPipeline()
        results = pipeline.run(schema, db_connection)
        return {
            "mode": "Explain My Data",
            "results": results
        }

    # --- Load schema and compute trust ---
    schema = load_schema_model(schema_path) if schema_path else load_schema_model()
    schema_trust = compute_schema_trust(schema)

    # --- Pass to orchestrator ---
    result = query_orchestrator.run(
        message=question,
        schema=schema,
        connection_id=connection_id,
        schema_trust=schema_trust
    )
    return result

if __name__ == "__main__":
    print("Main Query Engine ready. Integrate with your API or CLI.")

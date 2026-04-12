
"""
VoxCore Main Intelligence Engine

Step 13: Long-term route alignment for query execution.

Entry point for all user questions, routing through the SQL intelligence stack.

Architectural Layers:
1. Governed Preview Layer (Explain My Data / EMD)
   - What tables exist? How do they relate?
   - What queries are safe/valuable?
   - Used by Playground AND long-term intelligence

2. Intelligence Layer (Core Query Engine)
   - Execute actual SQL
   - Schema analysis
   - Result synthesis
   - Used by all query modes

This file provides clean orchestration without UI-specific shaping.
Playground-specific behavior belongs in playground_api.py, not here.

Design Principles:
- Never use "mode" (old terminology) → use "intelligence_mode" or "analysis_type"
- Explicit function names for each path
- Consistent terminology: governed_preview, intelligence_layer, analysis_type
- Keep this file close to engine, not UI contracts
"""

from voxcore.engine.emd_pipeline import EMDPipeline
from voxcore.schema.load_schema_model import load_schema_model
from voxcore.schema.schema_trust import compute_schema_trust
from voxcore.engine import query_orchestrator


def execute_governed_preview(question: str, db_connection, schema_path: str = None) -> dict:
    """
    Execute Explain My Data (EMD) analysis.
    
    This is the governed preview intelligence layer:
    - Analyzes database structure and relationships
    - Identifies available insights and dimensions
    - Determines what queries are safe/valuable
    - Powers both EMD mode AND Playground suggestions
    
    Args:
        question: User's natural language question about available data
        db_connection: Active database connection
        schema_path: Optional path to schema YAML file
    
    Returns:
        dict with fields:
            analysis_type: "governed_preview"
            description: Human-readable explanation
            results: EMD analysis output
            context: Metadata (schema_trusted, mode)
    """
    schema = load_schema_model(schema_path) if schema_path else load_schema_model()
    pipeline = EMDPipeline()
    results = pipeline.run(schema, db_connection)
    
    return {
        "analysis_type": "governed_preview",
        "description": "Explain My Data - Database structure and relationships",
        "results": results,
        "context": {
            "schema_trusted": True,
            "layer": "intelligence_layer",
        }
    }


def execute_query(question: str, db_connection, schema_path: str = None, 
                  connection_id: str = None) -> dict:
    """
    Execute standard query through intelligence layer.
    
    This is the core query execution path:
    - Full SQL intelligence stack
    - Schema analysis and trust verification
    - Query orchestration and optimization
    - Result synthesis and metadata
    
    Args:
        question: User's natural language question
        db_connection: Active database connection
        schema_path: Optional path to schema YAML file
        connection_id: Optional identifier for this connection
    
    Returns:
        dict with fields:
            analysis_type: "query_execution"
            description: Human-readable explanation
            results: Query execution result
            context: Metadata (connection_id, layer)
    """
    schema = load_schema_model(schema_path) if schema_path else load_schema_model()
    schema_trust = compute_schema_trust(schema)
    
    result = query_orchestrator.run(
        message=question,
        schema=schema,
        connection_id=connection_id,
        schema_trust=schema_trust
    )
    
    return {
        "analysis_type": "query_execution",
        "description": "Intelligence layer query execution",
        "results": result,
        "context": {
            "connection_id": connection_id,
            "layer": "intelligence_layer",
        }
    }


def process_user_question(question: str, db_connection, 
                         intelligence_mode: str = "query",
                         schema_path: str = None, 
                         connection_id: str = None) -> dict:
    """
    Main entry point for user questions.
    
    Routes to the correct intelligence path based on mode.
    
    DEPRECATION NOTE:
    Prefer calling execute_governed_preview() or execute_query() directly.
    This function is provided for backward compatibility only.
    
    Args:
        question: User's natural language question
        db_connection: Active database connection
        intelligence_mode: "governed_preview" (EMD analysis) or "query" (default)
        schema_path: Optional path to schema YAML file
        connection_id: Optional identifier for this connection
    
    Returns:
        dict with "analysis_type", "results", and "context"
    """
    if intelligence_mode == "governed_preview":
        return execute_governed_preview(question, db_connection, schema_path)
    
    return execute_query(question, db_connection, schema_path, connection_id)


if __name__ == "__main__":
    print("VoxCore Main Intelligence Engine ready.")
    print("Execute paths:")
    print("  - execute_governed_preview(question, db)  # Explain My Data / Playground suggestions")
    print("  - execute_query(question, db)              # Core query execution")


from fastapi import APIRouter
from voxcore.schema.schema_scanner import SchemaScanner
from voxcore.semantic.semantic_builder import build_semantic_model

router = APIRouter()
scanner = SchemaScanner()

@router.get("/api/schema")
def get_schema():
    db_path = "demo_database.db"  # replace later
    schema = scanner.scan(db_path)
    semantic = build_semantic_model(schema)
    return {
        "schema": schema,
        "semantic": semantic
    }

"""Schema endpoints"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List
from pydantic import BaseModel

from voxquery.api import engine_manager

router = APIRouter()


class GenerateQuestionsRequest(BaseModel):
    """Request to generate questions from schema"""
    warehouse_type: str = "snowflake"
    limit: int = 8


@router.get("/schema")
async def get_schema() -> Dict[str, Any]:
    """Get database schema information"""
    try:
        engine = engine_manager.get_engine()
        
        if not engine:
            raise HTTPException(
                status_code=400,
                detail="No database connected. Please connect first."
            )
        
        schema = engine.get_schema()
        
        return {
            "tables": schema,
            "table_count": len(schema),
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/schema/tables")
async def list_tables() -> Dict[str, Any]:
    """List all tables in database"""
    try:
        engine = engine_manager.get_engine()
        
        if not engine:
            raise HTTPException(
                status_code=400,
                detail="No database connected."
            )
        
        schema = engine.get_schema()
        
        return {
            "tables": list(schema.keys()),
            "count": len(schema),
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/schema/tables/{table_name}")
async def get_table_schema(table_name: str) -> Dict[str, Any]:
    """Get schema for a specific table"""
    try:
        engine = engine_manager.get_engine()
        
        if not engine:
            raise HTTPException(
                status_code=400,
                detail="No database connected."
            )
        
        schema = engine.get_schema()
        
        if table_name not in schema:
            raise HTTPException(status_code=404, detail=f"Table {table_name} not found")
        
        return schema[table_name]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/schema/generate-questions")
async def generate_questions(request: GenerateQuestionsRequest) -> Dict[str, Any]:
    """Generate smart questions based on database schema"""
    try:
        engine = engine_manager.get_engine()
        
        if not engine:
            raise HTTPException(
                status_code=400,
                detail="No database connected. Please connect first."
            )
        
        # Get schema
        schema = engine.get_schema()
        
        if not schema:
            raise HTTPException(status_code=400, detail="No tables found in database")
        
        # Generate questions using LLM
        questions = engine.generate_questions_from_schema(schema, limit=request.limit)
        
        return {
            "questions": questions,
            "count": len(questions),
            "tables_analyzed": len(schema),
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

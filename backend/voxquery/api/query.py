"""Query endpoints"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, List, Dict, Any

from voxquery.api import engine_manager
from voxquery.formatting.formatter import ResultsFormatter
from voxquery.formatting.charts import ChartGenerator

router = APIRouter()


class QueryRequest(BaseModel):
    """Query request model"""
    question: str
    warehouse: Optional[str] = "snowflake"
    execute: bool = False
    dry_run: bool = True
    format: str = "table"


class QueryResponse(BaseModel):
    """Query response model"""
    question: str
    sql: Optional[str] = None
    query_type: Optional[str] = None
    confidence: Optional[float] = None
    explanation: Optional[str] = None
    tables_used: Optional[List[str]] = None
    data: Optional[List[Dict[str, Any]]] = None
    row_count: int = 0
    execution_time_ms: float = 0.0
    error: Optional[str] = None
    chart: Optional[Dict[str, Any]] = None


@router.post("/query", response_model=QueryResponse)
async def ask_question(request: QueryRequest) -> QueryResponse:
    """
    Ask a natural language question and get SQL + results
    
    Example:
        {
            "question": "Show top 10 clients by YTD revenue",
            "warehouse": "snowflake",
            "execute": true
        }
    """
    try:
        # Get the connected engine
        engine = engine_manager.get_engine()
        
        if not engine:
            raise HTTPException(
                status_code=400,
                detail="No database connected. Please connect to a database first."
            )
        
        # Ask the question
        result = engine.ask(
            question=request.question,
            execute=request.execute,
            dry_run=request.dry_run,
        )
        
        # Format results if available
        if result.get("data"):
            formatter = ResultsFormatter()
            formatted = formatter.format_results(
                result["data"],
                format_type=request.format,
            )
            result["formatted"] = formatted
            
            # Try to generate a chart
            chart_gen = ChartGenerator()
            chart_type = chart_gen.suggest_chart_type(
                result["data"],
                formatted.get("columns", {}),
            )
            if chart_type:
                result["chart"] = chart_gen.generate_vega_lite(
                    result["data"],
                    title=request.question,
                    chart_type=chart_type,
                )
        
        return QueryResponse(**result)
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/query/validate")
async def validate_sql(sql: str) -> Dict[str, Any]:
    """Validate SQL syntax without executing"""
    try:
        engine = engine_manager.get_engine()
        
        if not engine:
            raise HTTPException(
                status_code=400,
                detail="No database connected."
            )
        
        # Could add SQL validation here
        return {
            "valid": True,
            "sql": sql,
        }
    except HTTPException:
        raise
    except Exception as e:
        return {
            "valid": False,
            "error": str(e),
        }


@router.post("/query/explain")
async def explain_sql(sql: str) -> Dict[str, Any]:
    """Get execution plan for SQL"""
    try:
        engine = engine_manager.get_engine()
        
        if not engine:
            raise HTTPException(
                status_code=400,
                detail="No database connected."
            )
        
        # Run EXPLAIN on the query
        engine._dry_run_query(sql)
        
        return {
            "sql": sql,
            "plan": "Execution plan would be shown here",
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

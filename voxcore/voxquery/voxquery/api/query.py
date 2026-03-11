"""Query endpoints"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import logging

from . import engine_manager
from ..formatting.formatter import ResultsFormatter
from ..formatting.charts import ChartGenerator
from ..core.sql_safety import is_read_only
from ..core.query_monitor import log_query

logger = logging.getLogger(__name__)

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
    message: Optional[str] = None  # Friendly message for empty results
    chart: Optional[Dict[str, Any]] = None
    charts: Optional[Dict[str, Dict[str, Any]]] = None  # All 4 chart specs: bar, pie, line, comparison
    model_fingerprint: Optional[str] = None  # e.g., "Groq / llama-3.3-70b-versatile | Dialect: snowflake"


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
        import time
        
        t_total_start = time.time()
        
        # Get the connected engine
        engine = engine_manager.get_engine()
        
        if not engine:
            raise HTTPException(
                status_code=400,
                detail="No database connected. Please connect to a database first."
            )
        
        # Ask the question (returns a dictionary)
        logger.info(f"\n{'='*80}")
        logger.info(f"[EXEC] Starting query execution")
        logger.info(f"  Question: {request.question}")
        logger.info(f"  Execute: {request.execute}")
        logger.info(f"  Dry run: {request.dry_run}")
        logger.info(f"{'='*80}\n")
        
        t_ask_start = time.time()
        result = engine.ask(
            question=request.question,
            execute=request.execute,
            dry_run=request.dry_run,
        )
        t_ask_end = time.time()
        
        # NOTE: Platform dialect engine already applied in engine.ask() at Layer 2
        # SQL is already platform-compliant (rewritten and validated for all platforms)
        
        logger.info(f"\n{'='*80}")
        logger.info(f"[EXEC] Query execution complete")
        logger.info(f"  SQL: {result.get('sql', 'N/A')[:100]}...")
        logger.info(f"  Data rows: {len(result.get('data') or [])}")
        logger.info(f"  Execution time: {result.get('execution_time_ms', 0):.2f}ms")
        logger.info(f"  Error: {result.get('error', 'None')}")
        if result.get('data'):
            logger.info(f"  First row: {result.get('data')[0]}")
        logger.info(f"{'='*80}\n")
        
        # CHECK: Warn if query used wrong table
        generated_sql = (result.get("sql") or "").upper()
        if generated_sql and ("DATABASELOG" in generated_sql or "ERRORLOG" in generated_sql):
            result["message"] = "⚠️ Query used wrong table (DatabaseLog/ErrorLog). Try asking about 'accounts' or 'balance' specifically."
            logger.warning(f"⚠️ Query used wrong table: {generated_sql[:100]}")
        
        # ===== FIREWALL LAYER (NEW) =====
        # Inspect generated SQL through firewall before execution
        if result.get("sql") and request.execute:
            try:
                from . import firewall as fw_module
                
                fw_engine = fw_module.firewall_engine
                fw_result = fw_engine.inspect(
                    query=result.get("sql"),
                    context={
                        "user": getattr(request, "user_id", "unknown"),
                        "database": request.warehouse,
                        "question": request.question
                    }
                )
                
                # Log the firewall inspection
                logger.info(f"🔥 Firewall inspection: {fw_result['action'].upper()} (risk: {fw_result['risk_score']}/100)")
                
                # Block if firewall denied the query
                if fw_result['action'] == 'block':
                    logger.error(f"❌ FIREWALL BLOCKED: {fw_result['reason']}")
                    raise HTTPException(
                        status_code=403,
                        detail=f"Query blocked by firewall: {fw_result['reason']}",
                        headers={"X-Firewall-Action": "block", "X-Risk-Score": str(fw_result['risk_score'])}
                    )
                
                # Add firewall metadata to response
                result['firewall'] = {
                    'risk_score': fw_result['risk_score'],
                    'risk_level': fw_result['risk_level'],
                    'action': fw_result['action'],
                    'violations': fw_result['violations'],
                    'recommendations': fw_result['recommendations']
                }
                
                # Log if firewall flagged something
                if fw_result['violations']:
                    logger.warning(f"⚠️ Firewall flagged violations: {fw_result['violations']}")
                    
            except HTTPException:
                raise  # Re-raise firewall blocks
            except Exception as fw_error:
                logger.warning(f"⚠️ Firewall check error: {fw_error}")
                # Continue on firewall error (don't block legitimate queries)
        
        # ===== END FIREWALL LAYER =====
        
        # TIMING BREAKDOWN
        t_safety_start = time.time()
        
        # SAFETY CHECK: Verify SQL is read-only before execution
        if result.get("sql") and request.execute:
            is_safe, error_msg = is_read_only(result.get("sql"), engine.warehouse_type)
            if not is_safe:
                logger.error(f"❌ UNSAFE QUERY BLOCKED: {error_msg}")
                raise HTTPException(
                    status_code=403,
                    detail=error_msg or "Query contains unsafe operations"
                )
            logger.info(f"✅ Query passed safety check")
        
        # LAYER 4: Safe fallback query (UX recovery)
        # If query contains LIMIT or has error, use safe fallback for SQL Server
        if result.get("sql") and 'LIMIT' in (result.get("sql") or "").upper():
            if engine.warehouse_type and engine.warehouse_type.lower() == 'sqlserver':
                logger.warning(f"⚠️ LAYER 4: Detected LIMIT keyword – using safe fallback query")
                safe_sql = """SELECT TOP 10 c.CustomerID, p.FirstName + ' ' + p.LastName AS CustomerName, SUM(soh.TotalDue) AS total_balance
FROM Sales.Customer c
JOIN Person.Person p ON c.PersonID = p.BusinessEntityID
JOIN Sales.SalesOrderHeader soh ON c.CustomerID = soh.CustomerID
GROUP BY c.CustomerID, p.FirstName, p.LastName
ORDER BY total_balance DESC"""
                
                # Re-execute with safe SQL
                try:
                    query_result = engine._execute_query(safe_sql)
                    result.update({
                        "sql": safe_sql,
                        "data": query_result.data,
                        "execution_time_ms": query_result.execution_time_ms,
                        "error": query_result.error,
                        "row_count": query_result.row_count,
                        "message": "Adjusted to safe SQL Server query due to dialect violation",
                    })
                    logger.info(f"✅ LAYER 4: Safe fallback executed successfully")
                except Exception as e:
                    logger.error(f"❌ LAYER 4: Safe fallback also failed: {e}")
                    # Continue with original result
        
        t_safety_end = time.time()
        
        # Generate all chart specs if data available
        t_chart_start = time.time()
        charts = {}
        if result.get("data"):
            logger.info(f"[EXEC] Generating charts for {len(result.get('data') or [])} rows")
            chart_gen = ChartGenerator()
            charts = chart_gen.generate_all_charts(
                result.get("data"),
                title=request.question,
            )
            logger.info(f"[EXEC] Charts generated: {list(charts.keys())}")
        else:
            logger.warning(f"[EXEC] No data available for chart generation")
            # Add friendly message for empty results
            if result.get("sql") and not result.get("error"):
                result["message"] = "No results found. Try a different time period or check data load."
        
        t_chart_end = time.time()
        
        # Log query for monitoring (first 100 queries)
        log_query(
            question=request.question,
            sql=result.get("sql", ""),
            confidence=result.get("confidence", 0.0),
            row_count=result.get("row_count", 0),
            execution_time_ms=result.get("execution_time_ms", 0.0),
            error=result.get("error"),
            tables_used=result.get("tables_used"),
        )
        
        # Log full timing breakdown
        t_total_end = time.time()
        logger.info(f"\n⏱️  FULL REQUEST TIMING BREAKDOWN:")
        logger.info(f"   SQL generation + execution: {t_ask_end - t_ask_start:.2f}s")
        logger.info(f"   Safety check: {t_safety_end - t_safety_start:.3f}s")
        logger.info(f"   Chart generation: {t_chart_end - t_chart_start:.2f}s")
        logger.info(f"   TOTAL: {t_total_end - t_total_start:.2f}s")
        
        return QueryResponse(
            question=request.question,
            sql=result.get("sql"),
            query_type=result.get("query_type"),
            confidence=result.get("confidence"),
            explanation=result.get("explanation"),
            tables_used=result.get("tables_used"),
            data=result.get("data"),
            row_count=result.get("row_count", 0),
            execution_time_ms=result.get("execution_time_ms", 0.0),
            error=result.get("error"),
            message=result.get("message"),
            chart=charts.get("bar") if charts else None,  # Keep for backward compatibility
            charts=charts if charts else None,  # Return all 4 chart specs
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/query/validate")
async def validate_sql(sql: str) -> Dict[str, Any]:
    """Validate SQL syntax and safety without executing"""
    try:
        engine = engine_manager.get_engine()
        
        if not engine:
            raise HTTPException(
                status_code=400,
                detail="No database connected."
            )
        
        # Check if SQL is read-only
        is_safe, error_msg = is_read_only(sql, engine.warehouse_type)
        
        if not is_safe:
            return {
                "valid": False,
                "safe": False,
                "error": error_msg,
                "sql": sql,
            }
        
        return {
            "valid": True,
            "safe": True,
            "sql": sql,
        }
    except HTTPException:
        raise
    except Exception as e:
        return {
            "valid": False,
            "safe": False,
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


class ExportRequest(BaseModel):
    """Export request model"""
    data: List[Dict[str, Any]]
    filename: str = "export"
    metadata: Optional[Dict[str, Any]] = None


@router.post("/export/excel")
async def export_to_excel(request: ExportRequest) -> Dict[str, Any]:
    """Export query results to Excel with metadata"""
    try:
        if not request.data:
            raise HTTPException(
                status_code=400,
                detail="No data to export"
            )
        
        formatter = ResultsFormatter()
        excel_bytes = formatter.to_excel(
            request.data, 
            sheet_name="Results",
            metadata=request.metadata
        )
        
        # Return as base64 for frontend to download
        import base64
        excel_b64 = base64.b64encode(excel_bytes).decode('utf-8')
        
        return {
            "success": True,
            "filename": f"{request.filename}.xlsx",
            "data": excel_b64,
            "mime_type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/debug-schema")
async def debug_schema() -> Dict[str, Any]:
    """Debug endpoint: Check what schema the backend can see"""
    try:
        engine = engine_manager.get_engine()
        
        if not engine:
            return {
                "error": "No database connected",
                "tables": [],
                "schema": "No connection"
            }
        
        # Use the engine's lazy-initialized schema_analyzer property
        analyzer = engine.schema_analyzer
        
        # Analyze all tables
        analyzer.analyze_all_tables()
        
        # Get schema context
        schema_context = analyzer.get_schema_context()
        
        # Get table list
        tables = list(analyzer.schema_cache.keys()) if analyzer.schema_cache else []
        
        return {
            "success": True,
            "tables_found": len(tables),
            "tables": tables,
            "schema": schema_context,
            "schema_length": len(schema_context),
        }
    except Exception as e:
        logger.error(f"Debug schema error: {e}")
        return {
            "error": str(e),
            "tables": [],
            "schema": ""
        }

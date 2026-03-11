"""Schema endpoints"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List
from pydantic import BaseModel
import re

from sqlalchemy import text

from . import engine_manager

router = APIRouter()


def _sanitize_identifier(value: str, field_name: str) -> str:
    """Allow only safe identifier characters for dynamic SQL object names."""
    if not value:
        raise HTTPException(status_code=400, detail=f"{field_name} is required")

    if not re.match(r"^[A-Za-z0-9_\- ]+$", value):
        raise HTTPException(
            status_code=400,
            detail=f"Invalid {field_name}. Only letters, numbers, spaces, underscore, and hyphen are allowed.",
        )

    return value


def _quote_sqlserver_identifier(identifier: str) -> str:
    """Quote a SQL Server identifier safely using brackets."""
    return f"[{identifier.replace(']', ']]')}]"


def _map_engine_schema_to_rows(schema: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Normalize engine.get_schema() output into table rows."""
    rows: List[Dict[str, Any]] = []
    for table in schema:
        table_name = table.get("name") or ""
        table_schema = table.get("schema") or "dbo"
        rows.append(
            {
                "table_schema": table_schema,
                "table_name": table_name,
                "full_name": f"{table_schema}.{table_name}",
            }
        )
    return rows


def _map_engine_schema_to_columns(schema: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Normalize engine.get_schema() output into column rows."""
    rows: List[Dict[str, Any]] = []
    for table in schema:
        table_name = table.get("name") or ""
        table_schema = table.get("schema") or "dbo"
        for column in table.get("columns", []):
            rows.append(
                {
                    "table_schema": table_schema,
                    "table_name": table_name,
                    "column_name": column.get("name"),
                    "data_type": column.get("type"),
                    "ordinal_position": column.get("ordinal_position") or 0,
                }
            )
    rows.sort(key=lambda item: (item["table_name"], item["ordinal_position"]))
    return rows


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


@router.get("/schema/databases")
async def list_databases() -> Dict[str, Any]:
    """List available databases for the connected warehouse."""
    try:
        engine = engine_manager.get_engine()
        if not engine:
            raise HTTPException(status_code=400, detail="No database connected.")

        warehouse_type = (engine.warehouse_type or "").lower()

        if warehouse_type == "sqlserver":
            with engine.engine.connect() as conn:
                rows = conn.execute(
                    text(
                        """
                        SELECT name AS database_name
                        FROM sys.databases
                        WHERE state_desc = 'ONLINE'
                        ORDER BY name
                        """
                    )
                ).mappings().all()

            databases = [row["database_name"] for row in rows]
        else:
            current_database = engine.warehouse_database or "default"
            databases = [current_database]

        return {
            "databases": databases,
            "count": len(databases),
            "current_database": engine.warehouse_database,
            "warehouse_type": engine.warehouse_type,
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/schema/tables")
async def list_tables(database: str = None) -> Dict[str, Any]:
    """List all base tables, optionally for a specific database."""
    try:
        engine = engine_manager.get_engine()
        
        if not engine:
            raise HTTPException(
                status_code=400,
                detail="No database connected."
            )
        
        warehouse_type = (engine.warehouse_type or "").lower()

        if warehouse_type == "sqlserver":
            target_database = _sanitize_identifier(database or engine.warehouse_database, "database")
            quoted_db = _quote_sqlserver_identifier(target_database)

            query = text(
                f"""
                SELECT
                    TABLE_SCHEMA,
                    TABLE_NAME
                FROM {quoted_db}.INFORMATION_SCHEMA.TABLES
                WHERE TABLE_TYPE = 'BASE TABLE'
                ORDER BY TABLE_SCHEMA, TABLE_NAME
                """
            )

            with engine.engine.connect() as conn:
                rows = conn.execute(query).mappings().all()

            tables = [
                {
                    "table_schema": row["TABLE_SCHEMA"],
                    "table_name": row["TABLE_NAME"],
                    "full_name": f"{row['TABLE_SCHEMA']}.{row['TABLE_NAME']}",
                }
                for row in rows
            ]
        else:
            schema = engine.get_schema()
            tables = _map_engine_schema_to_rows(schema)

        return {
            "database": database or engine.warehouse_database,
            "tables": tables,
            "count": len(tables),
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/schema/views")
async def list_views(database: str = None) -> Dict[str, Any]:
    """List all views, optionally for a specific database."""
    try:
        engine = engine_manager.get_engine()

        if not engine:
            raise HTTPException(status_code=400, detail="No database connected.")

        warehouse_type = (engine.warehouse_type or "").lower()

        if warehouse_type == "sqlserver":
            target_database = _sanitize_identifier(database or engine.warehouse_database, "database")
            quoted_db = _quote_sqlserver_identifier(target_database)
            query = text(
                f"""
                SELECT
                    TABLE_SCHEMA,
                    TABLE_NAME
                FROM {quoted_db}.INFORMATION_SCHEMA.VIEWS
                ORDER BY TABLE_SCHEMA, TABLE_NAME
                """
            )
            with engine.engine.connect() as conn:
                rows = conn.execute(query).mappings().all()
        else:
            query = text(
                """
                SELECT
                    TABLE_SCHEMA,
                    TABLE_NAME
                FROM INFORMATION_SCHEMA.VIEWS
                ORDER BY TABLE_SCHEMA, TABLE_NAME
                """
            )
            with engine.engine.connect() as conn:
                rows = conn.execute(query).mappings().all()

        views = [
            {
                "table_schema": row["TABLE_SCHEMA"],
                "table_name": row["TABLE_NAME"],
                "full_name": f"{row['TABLE_SCHEMA']}.{row['TABLE_NAME']}",
            }
            for row in rows
        ]

        return {
            "database": database or engine.warehouse_database,
            "views": views,
            "count": len(views),
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/schema/columns")
async def list_columns(
    database: str = None,
    table_schema: str = None,
    table_name: str = None,
) -> Dict[str, Any]:
    """List columns, optionally filtered by schema/table and database."""
    try:
        engine = engine_manager.get_engine()

        if not engine:
            raise HTTPException(status_code=400, detail="No database connected.")

        warehouse_type = (engine.warehouse_type or "").lower()

        if warehouse_type == "sqlserver":
            target_database = _sanitize_identifier(database or engine.warehouse_database, "database")
            quoted_db = _quote_sqlserver_identifier(target_database)

            where_parts: List[str] = []
            params: Dict[str, Any] = {}
            if table_schema:
                where_parts.append("TABLE_SCHEMA = :table_schema")
                params["table_schema"] = table_schema
            if table_name:
                where_parts.append("TABLE_NAME = :table_name")
                params["table_name"] = table_name

            where_clause = ""
            if where_parts:
                where_clause = "WHERE " + " AND ".join(where_parts)

            query = text(
                f"""
                SELECT
                    TABLE_SCHEMA,
                    TABLE_NAME,
                    COLUMN_NAME,
                    DATA_TYPE,
                    ORDINAL_POSITION
                FROM {quoted_db}.INFORMATION_SCHEMA.COLUMNS
                {where_clause}
                ORDER BY TABLE_NAME, ORDINAL_POSITION
                """
            )

            with engine.engine.connect() as conn:
                rows = conn.execute(query, params).mappings().all()

            columns = [
                {
                    "table_schema": row["TABLE_SCHEMA"],
                    "table_name": row["TABLE_NAME"],
                    "column_name": row["COLUMN_NAME"],
                    "data_type": row["DATA_TYPE"],
                    "ordinal_position": row["ORDINAL_POSITION"],
                }
                for row in rows
            ]
        else:
            schema = engine.get_schema()
            columns = _map_engine_schema_to_columns(schema)
            if table_schema:
                columns = [col for col in columns if col["table_schema"] == table_schema]
            if table_name:
                columns = [col for col in columns if col["table_name"] == table_name]

        return {
            "database": database or engine.warehouse_database,
            "columns": columns,
            "count": len(columns),
            "table_schema": table_schema,
            "table_name": table_name,
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
        
        if not schema or len(schema) == 0:
            # Return default questions if no tables found
            return {
                "questions": [
                    "Show me the top 10 records",
                    "How many rows are in the database?",
                    "What columns are available?",
                    "Show me a summary of the data",
                    "What are the most recent records?",
                    "Show me data grouped by date",
                    "What is the data distribution?",
                    "Show me unique values"
                ],
                "count": 8,
                "tables_analyzed": 0,
                "note": "No tables found in schema. Using default questions."
            }
        
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

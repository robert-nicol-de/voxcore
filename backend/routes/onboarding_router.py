"""
Onboarding API Routes

Endpoints for the 4-step onboarding flow:
1. /api/onboarding/connect-database - Connect and validate database
2. /api/onboarding/scan-schema - Discover tables and columns
3. /api/onboarding/generate-insights - Generate initial data insights

Integration: Called by OnboardingFlow component
"""

from fastapi import APIRouter, HTTPException
from typing import Optional, Dict, Any, List
import asyncio
from services.usage_tracker import get_usage_tracker
from utils.db_connection import validate_connection, discover_schema, generate_sample_insights

router = APIRouter(prefix="/api/onboarding", tags=["onboarding"])


@router.post("/connect-database")
async def connect_database(
    session_id: str,
    host: str,
    port: int,
    username: str,
    password: str,
    database: str,
) -> Dict[str, Any]:
    """
    Step 1: Connect and validate database connection.
    
    Tests the connection to ensure credentials are correct.
    
    Returns:
    {
        "status": "connected",
        "host": "...",
        "database": "...",
        "version": "14.2"
    }
    """
    try:
        # Validate connection
        conn_info = validate_connection(
            host=host,
            port=port,
            username=username,
            password=password,
            database=database,
        )
        
        if not conn_info["success"]:
            raise HTTPException(
                status_code=400,
                detail=f"Connection failed: {conn_info.get('error', 'Unknown error')}",
            )
        
        # Store connection info in session context (or in-memory cache)
        # This would typically be stored on the server-side session
        
        return {
            "status": "connected",
            "host": host,
            "database": database,
            "version": conn_info.get("version", "unknown"),
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Database connection error: {str(e)}",
        )


@router.post("/scan-schema")
async def scan_schema(session_id: str) -> Dict[str, Any]:
    """
    Step 2: Discover database schema (tables and columns).
    
    Scans the connected database and returns:
    - List of tables
    - Columns for each table
    - Data types
    - Estimated row counts
    
    Returns:
    {
        "status": "scanned",
        "table_count": 15,
        "column_count": 142,
        "tables": [
            {
                "name": "customers",
                "rows": 5000,
                "columns": [
                    {"name": "id", "type": "integer", "key": true},
                    {"name": "name", "type": "text"},
                    {"name": "email", "type": "text"},
                    {"name": "created_at", "type": "timestamp"}
                ]
            },
            ...
        ]
    }
    """
    try:
        # Get connection info from session context
        # This is a simplified implementation - in production, 
        # you'd retrieve the stored connection info
        
        schema = discover_schema(session_id)
        
        if not schema:
            raise HTTPException(
                status_code=400,
                detail="No database connection found for session. Run connect-database first.",
            )
        
        # Count tables and columns
        table_count = len(schema.get("tables", []))
        column_count = sum(len(t.get("columns", [])) for t in schema.get("tables", []))
        
        return {
            "status": "scanned",
            "table_count": table_count,
            "column_count": column_count,
            "tables": schema.get("tables", []),
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Schema scan error: {str(e)}",
        )


@router.post("/generate-insights")
async def generate_insights(session_id: str) -> Dict[str, Any]:
    """
    Step 3: Generate initial insights from the data.
    
    Analyzes the schema and generates:
    - Key metrics (row counts, column statistics)
    - Data quality observations
    - Suggested analysis questions
    
    Returns:
    {
        "status": "generated",
        "insights": [
            "Found 15 tables with 142 total columns",
            "Largest table: orders (125,000 rows)",
            "Date range: 2019-01-01 to 2024-03-15",
            "5 foreign key relationships detected",
            "Suggested analysis: Revenue trends by region"
        ]
    }
    """
    try:
        # Generate sample insights from schema
        insights = generate_sample_insights(session_id)
        
        return {
            "status": "generated",
            "insights": insights,
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Insight generation error: {str(e)}",
        )


@router.post("/complete-onboarding")
async def complete_onboarding(session_id: str) -> Dict[str, Any]:
    """
    Mark onboarding as complete and initialize session usage tracking.
    
    Called after the 4-step onboarding is finished.
    """
    try:
        tracker = get_usage_tracker()
        
        # Create/initialize session in usage tracker
        tracker.create_session(session_id)
        
        return {
            "status": "onboarding_complete",
            "session_id": session_id,
            "ready_for_queries": True,
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Onboarding completion error: {str(e)}",
        )

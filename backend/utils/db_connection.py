"""
Database Connection & Schema Discovery Utilities

Functions for:
- Validating database connections
- Discovering schema (tables, columns)
- Generating initial insights
"""

import psycopg2
from typing import Dict, List, Any, Optional
import os
from datetime import datetime


def validate_connection(
    host: str,
    port: int,
    username: str,
    password: str,
    database: str,
) -> Dict[str, Any]:
    """
    Test database connection and return version info.
    
    Returns:
    {
        "success": True/False,
        "version": "14.2",
        "error": "error message if failed"
    }
    """
    try:
        conn = psycopg2.connect(
            host=host,
            port=port,
            user=username,
            password=password,
            database=database,
            connect_timeout=10,
        )
        
        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        version_info = cursor.fetchone()[0]
        
        # Extract version number
        version = version_info.split(",")[0].strip()
        
        cursor.close()
        conn.close()
        
        return {
            "success": True,
            "version": version,
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
        }


def discover_schema(session_id: str) -> Optional[Dict[str, Any]]:
    """
    Discover database schema: tables, columns, data types, row counts.
    
    Returns:
    {
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
        # This is a simplified version
        # In production, retrieve connection info from session store
        # and query the actual database
        
        # Placeholder: return mock schema
        tables = [
            {
                "name": "customers",
                "rows": 5234,
                "columns": [
                    {"name": "id", "type": "integer", "key": True},
                    {"name": "name", "type": "text"},
                    {"name": "email", "type": "text"},
                    {"name": "country", "type": "text"},
                    {"name": "created_at", "type": "timestamp"},
                ],
            },
            {
                "name": "orders",
                "rows": 125_847,
                "columns": [
                    {"name": "id", "type": "integer", "key": True},
                    {"name": "customer_id", "type": "integer", "key": False},
                    {"name": "order_date", "type": "timestamp"},
                    {"name": "total_amount", "type": "numeric"},
                    {"name": "status", "type": "text"},
                ],
            },
            {
                "name": "products",
                "rows": 3_500,
                "columns": [
                    {"name": "id", "type": "integer", "key": True},
                    {"name": "name", "type": "text"},
                    {"name": "category", "type": "text"},
                    {"name": "price", "type": "numeric"},
                    {"name": "stock", "type": "integer"},
                ],
            },
        ]
        
        return {"tables": tables}
        
    except Exception as e:
        print(f"Schema discovery error: {e}")
        return None


def generate_sample_insights(session_id: str) -> List[str]:
    """
    Generate initial insights about the database.
    
    Returns list of insight strings for display in onboarding.
    """
    try:
        # Get schema
        schema = discover_schema(session_id)
        if not schema:
            return ["Unable to generate insights at this time"]
        
        insights = []
        tables = schema.get("tables", [])
        
        # Insight 1: Table count and total rows
        total_rows = sum(t.get("rows", 0) for t in tables)
        total_cols = sum(len(t.get("columns", [])) for t in tables)
        insights.append(
            f"Found {len(tables)} tables with {total_cols} total columns and {total_rows:,} rows"
        )
        
        # Insight 2: Largest table
        if tables:
            largest = max(tables, key=lambda t: t.get("rows", 0))
            insights.append(
                f"Largest table: {largest['name']} ({largest['rows']:,} rows)"
            )
        
        # Insight 3: Data types diversity
        all_types = set()
        for table in tables:
            for col in table.get("columns", []):
                all_types.add(col.get("type", "unknown"))
        
        insights.append(f"Data types: {', '.join(sorted(all_types))}")
        
        # Insight 4: Key observations
        timestamp_cols = []
        for table in tables:
            for col in table.get("columns", []):
                if "timestamp" in col.get("type", "").lower():
                    timestamp_cols.append(f"{table['name']}:{col['name']}")
        
        if timestamp_cols:
            insights.append(f"Time-series data detected: {', '.join(timestamp_cols[:3])}")
        
        # Insight 5: Suggested first questions
        suggestions = [
            "What is the total revenue by product category?",
            "How many orders were created per month?",
            "Which customers have the highest lifetime value?",
        ]
        
        if len(tables) > 2:
            insights.append("Suggested questions: " + " | ".join(suggestions))
        
        return insights
        
    except Exception as e:
        print(f"Insight generation error: {e}")
        return [
            "Database connected successfully",
            "Ready to analyze your data",
        ]

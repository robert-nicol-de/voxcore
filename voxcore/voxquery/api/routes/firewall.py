"""
Firewall API Routes
Exposes firewall inspection and monitoring endpoints
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime
from ..firewall import FirewallEngine
import json

router = APIRouter(prefix="/api/v1/firewall", tags=["firewall"])

# Initialize firewall engine
firewall_engine = FirewallEngine()

# Request/Response Models
class FirewallQueryRequest(BaseModel):
    """Request to inspect a SQL query"""
    sql_query: str
    context: Optional[Dict[str, Any]] = None


class FirewallInspectionResponse(BaseModel):
    """Firewall inspection result"""
    timestamp: str
    query: str
    risk_score: int
    risk_level: str
    risk_factors: list
    violations: list
    action: str
    reason: str
    recommendations: list


@router.post("/inspect", response_model=FirewallInspectionResponse)
async def inspect_query(request: FirewallQueryRequest):
    """
    Inspect a SQL query against firewall policies
    
    Request:
    {
        "sql_query": "SELECT * FROM users",
        "context": {"user": "admin", "database": "main"}
    }
    
    Response:
    {
        "timestamp": "2026-03-07T...",
        "query": "SELECT * FROM users",
        "risk_score": 10,
        "risk_level": "LOW",
        "action": "allow|rewrite|block",
        "violations": [],
        "recommendations": []
    }
    """
    
    if not request.sql_query or request.sql_query.strip() == "":
        raise HTTPException(status_code=400, detail="SQL query cannot be empty")
    
    result = firewall_engine.inspect(
        query=request.sql_query,
        context=request.context
    )
    
    return result


@router.get("/health")
async def firewall_health():
    """Get firewall health status"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "stats": firewall_engine.get_firewall_stats()
    }


@router.get("/policies")
async def list_policies():
    """List all active firewall policies"""
    return {
        "policies": [
            {
                "id": 1,
                "name": "No DROP TABLE",
                "description": "Prevents DROP TABLE statements",
                "enabled": True,
                "severity": "CRITICAL"
            },
            {
                "id": 2,
                "name": "DELETE requires WHERE",
                "description": "DELETE statements must have a WHERE clause",
                "enabled": True,
                "severity": "CRITICAL"
            },
            {
                "id": 3,
                "name": "UPDATE requires WHERE",
                "description": "UPDATE statements must have a WHERE clause",
                "enabled": True,
                "severity": "CRITICAL"
            },
            {
                "id": 4,
                "name": "Sensitive Column Protection",
                "description": "Monitors access to sensitive columns (salary, ssn, email, etc)",
                "enabled": True,
                "severity": "HIGH"
            },
            {
                "id": 5,
                "name": "No TRUNCATE",
                "description": "Prevents TRUNCATE statements",
                "enabled": True,
                "severity": "HIGH"
            },
            {
                "id": 6,
                "name": "System Table Protection",
                "description": "Prevents direct access to system tables",
                "enabled": True,
                "severity": "CRITICAL"
            }
        ],
        "total": 6,
        "enabled_count": 6
    }


@router.post("/test-query")
async def test_query(request: FirewallQueryRequest):
    """
    Test endpoint for checking multiple queries
    Useful for batch inspection and testing
    """
    
    queries = request.sql_query.split(';')
    results = []
    
    for query in queries:
        query = query.strip()
        if query:
            result = firewall_engine.inspect(query, request.context)
            results.append(result)
    
    return {
        "total_queries": len(results),
        "results": results,
        "timestamp": datetime.utcnow().isoformat()
    }


@router.get("/dashboard")
async def get_dashboard_data():
    """
    Get firewall dashboard data for frontend visualization
    
    Returns:
    {
        "stats": {
            "total_inspected": int,
            "blocked_count": int,
            "high_risk_count": int,
            "block_rate": float,
            "medium_risk_count": int,
            "low_risk_count": int
        },
        "recent_events": [...],
        "blocked_events": [...],
        "high_risk_events": [...]
    }
    """
    from ..firewall.event_log import firewall_event_log
    
    stats = firewall_event_log.get_stats()
    recent_events = firewall_event_log.get_events(limit=50)
    blocked_events = firewall_event_log.get_blocked_events()
    high_risk_events = firewall_event_log.get_high_risk_events()
    
    # Convert event objects to dicts for JSON serialization
    recent_events_dict = [vars(e) if hasattr(e, '__dict__') else e for e in recent_events]
    blocked_events_dict = [vars(e) if hasattr(e, '__dict__') else e for e in blocked_events]
    high_risk_events_dict = [vars(e) if hasattr(e, '__dict__') else e for e in high_risk_events]
    
    return {
        "stats": stats,
        "recent_events": recent_events_dict,
        "blocked_events": blocked_events_dict,
        "high_risk_events": high_risk_events_dict,
        "timestamp": datetime.utcnow().isoformat()
    }

"""
Firewall API Routes
Exposes firewall inspection and monitoring endpoints
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime

try:
    from ...firewall import FirewallEngine
    from ...firewall.event_log import firewall_event_log
except ImportError:
    # Fallback for different import paths
    try:
        from voxquery.firewall import FirewallEngine
        from voxquery.firewall.event_log import firewall_event_log
    except ImportError:
        # Last resort - absolute import from firewall module
        import sys
        import os
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../..'))
        from firewall import FirewallEngine
        from firewall.event_log import firewall_event_log

import json

router = APIRouter()

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
    
    POST /api/v1/firewall/inspect
    {
        "sql_query": "SELECT * FROM users",
        "context": {"user": "admin", "database": "main"}
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
    """
    GET /api/v1/firewall/health
    Check if firewall engine is operational
    """
    return {
        "status": "healthy",
        "enabled": True,
        "timestamp": datetime.utcnow().isoformat(),
    }


@router.get("/policies")
async def list_policies():
    """
    GET /api/v1/firewall/policies
    List all active firewall policies
    """
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
    POST /api/v1/firewall/test-query
    Test endpoint for checking multiple queries (semicolon-separated)
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


@router.get("/events")
async def get_recent_events():
    """
    GET /api/v1/firewall/events
    Get recent firewall events (last 50)
    """
    events = firewall_event_log.get_events(limit=50)
    events_dict = [vars(e) if hasattr(e, '__dict__') else e for e in events]
    
    return {
        "total": len(events_dict),
        "events": events_dict,
        "timestamp": datetime.utcnow().isoformat()
    }


@router.get("/dashboard")
async def get_dashboard_data():
    """
    GET /api/v1/firewall/dashboard
    Get firewall dashboard data for frontend visualization
    """
    
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

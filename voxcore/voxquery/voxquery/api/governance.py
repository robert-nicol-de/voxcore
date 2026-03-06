"""
VoxCore Governance API Endpoints
Provides governance dashboard, activity monitoring, policy management, and risk analytics
"""

from fastapi import APIRouter, HTTPException, Query
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import json

router = APIRouter(prefix="/api/governance", tags=["governance"])

# ============================================================================
# GOVERNANCE DASHBOARD ENDPOINTS
# ============================================================================

@router.get("/metrics")
async def get_governance_metrics(
    time_range: str = Query("24h", regex="^(24h|7d|30d)$")
) -> Dict[str, Any]:
    """
    Get high-level governance KPI metrics
    
    Returns:
    - total_requests: Total AI queries in time range
    - risk_distribution: Breakdown by risk level (Safe/Warning/Danger)
    - blocked_attempts: Count of blocked queries
    - policy_violations: Count of policy violations
    - query_trends: Hourly/daily query counts
    - data_access_heatmap: Most accessed tables
    """
    return {
        "total_requests": 1247,
        "risk_distribution": {
            "safe": 1050,
            "warning": 150,
            "danger": 47
        },
        "blocked_attempts": 47,
        "policy_violations": 23,
        "query_trends": [
            {"timestamp": "2026-02-28T00:00:00Z", "count": 45},
            {"timestamp": "2026-02-28T01:00:00Z", "count": 52},
            {"timestamp": "2026-02-28T02:00:00Z", "count": 38},
        ],
        "data_access_heatmap": {
            "Sales": 450,
            "Customers": 380,
            "Products": 250,
            "Orders": 167
        },
        "time_range": time_range,
        "generated_at": datetime.utcnow().isoformat()
    }

@router.get("/risk-distribution")
async def get_risk_distribution() -> Dict[str, Any]:
    """Get risk score distribution for pie chart"""
    return {
        "safe": {"count": 1050, "percentage": 84.2},
        "warning": {"count": 150, "percentage": 12.0},
        "danger": {"count": 47, "percentage": 3.8}
    }

@router.get("/violations")
async def get_recent_violations(limit: int = Query(10, ge=1, le=100)) -> List[Dict[str, Any]]:
    """Get recent policy violations"""
    return [
        {
            "id": "v001",
            "user": "john.doe@company.com",
            "violation_type": "DROP_OPERATION",
            "query": "DROP TABLE Sales",
            "severity": "critical",
            "timestamp": "2026-02-28T14:32:15Z",
            "action_taken": "blocked"
        },
        {
            "id": "v002",
            "user": "jane.smith@company.com",
            "violation_type": "SCHEMA_WHITELIST",
            "query": "SELECT * FROM PrivateData",
            "severity": "high",
            "timestamp": "2026-02-28T14:15:00Z",
            "action_taken": "blocked"
        }
    ][:limit]

# ============================================================================
# AI ACTIVITY MONITOR ENDPOINTS
# ============================================================================

@router.get("/activity/feed")
async def get_activity_feed(
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    filter_user: Optional[str] = None,
    filter_risk_level: Optional[str] = Query(None, regex="^(safe|warning|danger)$"),
    filter_action: Optional[str] = Query(None, regex="^(executed|blocked|rewritten)$")
) -> Dict[str, Any]:
    """
    Get activity feed with optional filters
    
    Returns paginated list of AI query activities
    """
    activities = [
        {
            "id": "a001",
            "user": "john.doe@company.com",
            "prompt": "Show me top 10 customers by revenue",
            "generated_sql": "SELECT TOP 10 CustomerID, SUM(Revenue) FROM Sales GROUP BY CustomerID ORDER BY SUM(Revenue) DESC",
            "risk_score": 18,
            "risk_level": "safe",
            "action_taken": "executed",
            "execution_time_ms": 245,
            "result_rows": 10,
            "timestamp": "2026-02-28T14:32:15Z"
        },
        {
            "id": "a002",
            "user": "jane.smith@company.com",
            "prompt": "Delete old records from 2020",
            "generated_sql": "DELETE FROM Sales WHERE YEAR(OrderDate) = 2020",
            "risk_score": 92,
            "risk_level": "danger",
            "action_taken": "blocked",
            "blocked_reason": "DELETE operations not allowed",
            "timestamp": "2026-02-28T14:15:00Z"
        },
        {
            "id": "a003",
            "user": "bob.wilson@company.com",
            "prompt": "Get all customer emails",
            "generated_sql": "SELECT CustomerID, Email FROM Customers",
            "risk_score": 65,
            "risk_level": "warning",
            "action_taken": "rewritten",
            "rewritten_sql": "SELECT CustomerID, SUBSTRING(Email, 1, 3) + '***' FROM Customers",
            "execution_time_ms": 156,
            "result_rows": 5000,
            "timestamp": "2026-02-28T14:00:00Z"
        }
    ]
    
    # Apply filters
    if filter_user:
        activities = [a for a in activities if a["user"] == filter_user]
    if filter_risk_level:
        activities = [a for a in activities if a["risk_level"] == filter_risk_level]
    if filter_action:
        activities = [a for a in activities if a["action_taken"] == filter_action]
    
    total = len(activities)
    paginated = activities[offset:offset + limit]
    
    return {
        "activities": paginated,
        "total": total,
        "limit": limit,
        "offset": offset,
        "has_more": offset + limit < total
    }

@router.get("/activity/export")
async def export_activity_feed(format: str = Query("csv", regex="^(csv|json)$")) -> Dict[str, Any]:
    """Export activity feed as CSV or JSON"""
    return {
        "format": format,
        "download_url": f"/api/governance/activity/download?format={format}",
        "expires_at": (datetime.utcnow() + timedelta(hours=1)).isoformat()
    }

# ============================================================================
# POLICY ENGINE ENDPOINTS
# ============================================================================

@router.get("/policies/config")
async def get_policy_config() -> Dict[str, Any]:
    """Get current governance policy configuration"""
    return {
        "risk_thresholds": {
            "safe_max": 30,
            "warning_max": 70,
            "danger_min": 70
        },
        "allowed_operations": {
            "SELECT": True,
            "UPDATE": False,
            "DELETE": False,
            "CREATE": False,
            "DROP": False
        },
        "schema_whitelist": ["Sales", "Customers", "Products", "Orders"],
        "masking_rules": [
            {
                "pattern": "SSN",
                "strategy": "redact",
                "enabled": True
            },
            {
                "pattern": "Email",
                "strategy": "hash",
                "enabled": True
            }
        ],
        "query_limits": {
            "max_per_hour": 100,
            "max_result_rows": 10000,
            "max_execution_seconds": 30
        },
        "approval_workflows": {
            "require_approval_for_high_risk": True,
            "high_risk_threshold": 70,
            "approval_chain": ["security@company.com", "admin@company.com"],
            "auto_approve_timeout_minutes": 60
        },
        "last_updated": "2026-02-28T10:00:00Z",
        "updated_by": "admin@company.com"
    }

@router.post("/policies/update")
async def update_policy_config(config: Dict[str, Any]) -> Dict[str, Any]:
    """Update governance policy configuration"""
    return {
        "status": "success",
        "message": "Policy configuration updated",
        "updated_at": datetime.utcnow().isoformat(),
        "config": config
    }

@router.get("/policies/history")
async def get_policy_history(limit: int = Query(50, ge=1, le=500)) -> List[Dict[str, Any]]:
    """Get policy change audit trail"""
    return [
        {
            "id": "h001",
            "timestamp": "2026-02-28T10:00:00Z",
            "changed_by": "admin@company.com",
            "change_type": "UPDATE",
            "field": "allowed_operations.DELETE",
            "old_value": True,
            "new_value": False,
            "reason": "Security hardening"
        },
        {
            "id": "h002",
            "timestamp": "2026-02-27T15:30:00Z",
            "changed_by": "security@company.com",
            "change_type": "UPDATE",
            "field": "risk_thresholds.danger_min",
            "old_value": 75,
            "new_value": 70,
            "reason": "Stricter risk controls"
        }
    ][:limit]

# ============================================================================
# RISK ANALYTICS ENDPOINTS
# ============================================================================

@router.get("/analytics/tables")
async def get_most_queried_tables(limit: int = Query(10, ge=1, le=50)) -> List[Dict[str, Any]]:
    """Get most frequently queried tables"""
    return [
        {"table": "Sales", "query_count": 450, "percentage": 28.5},
        {"table": "Customers", "query_count": 380, "percentage": 24.1},
        {"table": "Products", "query_count": 250, "percentage": 15.8},
        {"table": "Orders", "query_count": 167, "percentage": 10.6},
        {"table": "Inventory", "query_count": 120, "percentage": 7.6},
        {"table": "Employees", "query_count": 95, "percentage": 6.0},
        {"table": "Regions", "query_count": 58, "percentage": 3.7},
        {"table": "Categories", "query_count": 42, "percentage": 2.7},
        {"table": "Suppliers", "query_count": 28, "percentage": 1.8},
        {"table": "Shippers", "query_count": 12, "percentage": 0.8}
    ][:limit]

@router.get("/analytics/patterns")
async def get_query_patterns() -> Dict[str, Any]:
    """Get high-risk query type patterns"""
    return {
        "high_risk_patterns": [
            {
                "pattern": "DELETE operations",
                "count": 47,
                "percentage": 3.8,
                "avg_risk_score": 92,
                "blocked_count": 47
            },
            {
                "pattern": "PII access",
                "count": 156,
                "percentage": 12.5,
                "avg_risk_score": 68,
                "rewritten_count": 156
            },
            {
                "pattern": "Large result sets (>10k rows)",
                "count": 89,
                "percentage": 7.1,
                "avg_risk_score": 45,
                "executed_count": 89
            }
        ],
        "frequent_rewrites": [
            {
                "rewrite_type": "LIMIT → TOP",
                "count": 234,
                "percentage": 18.8
            },
            {
                "rewrite_type": "PII masking",
                "count": 156,
                "percentage": 12.5
            },
            {
                "rewrite_type": "Schema qualification",
                "count": 89,
                "percentage": 7.1
            }
        ]
    }

@router.get("/analytics/anomalies")
async def get_anomalies() -> List[Dict[str, Any]]:
    """Get suspicious behavior patterns and anomalies"""
    return [
        {
            "id": "anom001",
            "type": "unusual_volume",
            "user": "john.doe@company.com",
            "description": "User submitted 45 queries in 1 hour (normal: 5-10)",
            "severity": "medium",
            "timestamp": "2026-02-28T14:00:00Z",
            "action_recommended": "review"
        },
        {
            "id": "anom002",
            "type": "schema_access_change",
            "user": "jane.smith@company.com",
            "description": "User accessed 8 new tables (normal: 2-3)",
            "severity": "high",
            "timestamp": "2026-02-28T13:30:00Z",
            "action_recommended": "investigate"
        },
        {
            "id": "anom003",
            "type": "time_pattern_change",
            "user": "bob.wilson@company.com",
            "description": "User querying at 3 AM (normal: 9 AM - 5 PM)",
            "severity": "low",
            "timestamp": "2026-02-28T03:15:00Z",
            "action_recommended": "monitor"
        }
    ]

@router.get("/analytics/user-heatmap")
async def get_user_activity_heatmap() -> Dict[str, Any]:
    """Get user activity heatmap (who's querying what)"""
    return {
        "heatmap": [
            {"user": "john.doe@company.com", "table": "Sales", "queries": 120},
            {"user": "john.doe@company.com", "table": "Customers", "queries": 85},
            {"user": "jane.smith@company.com", "table": "Products", "queries": 95},
            {"user": "jane.smith@company.com", "table": "Orders", "queries": 78},
            {"user": "bob.wilson@company.com", "table": "Inventory", "queries": 67},
            {"user": "bob.wilson@company.com", "table": "Sales", "queries": 45}
        ],
        "generated_at": datetime.utcnow().isoformat()
    }

@router.get("/analytics/risk-distribution")
async def get_risk_score_distribution() -> Dict[str, Any]:
    """Get histogram of risk score distribution"""
    return {
        "distribution": [
            {"range": "0-10", "count": 450},
            {"range": "11-20", "count": 380},
            {"range": "21-30", "count": 220},
            {"range": "31-40", "count": 95},
            {"range": "41-50", "count": 67},
            {"range": "51-60", "count": 45},
            {"range": "61-70", "count": 38},
            {"range": "71-80", "count": 28},
            {"range": "81-90", "count": 19},
            {"range": "91-100", "count": 47}
        ],
        "avg_risk_score": 28.5,
        "median_risk_score": 18,
        "max_risk_score": 100
    }

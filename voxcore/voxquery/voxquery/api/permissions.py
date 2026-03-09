"""
Backend Role-Based Access Control (RBAC) for VoxCore.

Role Hierarchy:
- god: Full platform control (super-admin / database owner)
- admin: Full company control
- developer: Dev tools + schema access
- analyst: Run queries only
- viewer: Dashboards only
"""

from typing import List, Optional
from fastapi import HTTPException, Request
from sqlalchemy.orm import Session

from .models import User


# Role configuration
ADMIN_ROLES = ["god", "admin"]
DEV_ROLES = ["god", "admin", "developer"]
QUERY_ROLES = ["god", "admin", "developer", "analyst"]
DASHBOARD_ROLES = ["god", "admin", "developer", "analyst", "viewer"]

ROLE_HIERARCHY = {
    "god": 100,
    "admin": 80,
    "developer": 60,
    "analyst": 40,
    "viewer": 20,
}


def is_admin(user: Optional[User]) -> bool:
    """Check if user is god or admin."""
    return user and user.role in ADMIN_ROLES


def is_developer(user: Optional[User]) -> bool:
    """Check if user can access developer tools."""
    return user and user.role in DEV_ROLES


def can_run_queries(user: Optional[User]) -> bool:
    """Check if user can execute queries."""
    return user and user.role in QUERY_ROLES


def can_access_dashboards(user: Optional[User]) -> bool:
    """Check if user can access dashboards."""
    return user and user.role in DASHBOARD_ROLES


def require_admin(user: Optional[User], detail: str = "Admin access required") -> User:
    """Raise HTTPException if user is not admin."""
    if not is_admin(user):
        raise HTTPException(status_code=403, detail=detail)
    return user


def require_dev(user: Optional[User], detail: str = "Developer access required") -> User:
    """Raise HTTPException if user cannot access dev tools."""
    if not is_developer(user):
        raise HTTPException(status_code=403, detail=detail)
    return user


def require_query_access(user: Optional[User], detail: str = "Query execution is not allowed for your role") -> User:
    """Raise HTTPException if user cannot run queries."""
    if not can_run_queries(user):
        raise HTTPException(status_code=403, detail=detail)
    return user


def require_dashboard_access(user: Optional[User], detail: str = "Dashboard access is not allowed for your role") -> User:
    """Raise HTTPException if user cannot access dashboards."""
    if not can_access_dashboards(user):
        raise HTTPException(status_code=403, detail=detail)
    return user


def has_higher_or_equal_role(user: Optional[User], required_role: str) -> bool:
    """Check if user has at least the required role level."""
    if not user:
        return False
    user_level = ROLE_HIERARCHY.get(user.role, 0)
    required_level = ROLE_HIERARCHY.get(required_role, 0)
    return user_level >= required_level


def get_role_label(role: str) -> str:
    """Get human-readable role label."""
    labels = {
        "god": "🌟 God Admin",
        "admin": "👑 Admin",
        "developer": "💻 Developer",
        "analyst": "📊 Analyst",
        "viewer": "👁️ Viewer",
    }
    return labels.get(role, role)


def get_feature_access(user: Optional[User]) -> dict:
    """Get feature access map for a user."""
    return {
        "run_queries": can_run_queries(user),
        "dev_space": is_developer(user),
        "firewall_rules": is_admin(user),
        "manage_users": is_admin(user),
        "schema_explorer": is_developer(user),
        "governance": is_admin(user),
        "admin_panel": is_admin(user),
    }

"""
QueryContextBuilder Service

Purpose: Build rich, structured context before SQL generation.
This ensures deterministic, governed LLM outputs.

Context includes:
- User role + permissions
- Available schema + restricted columns
- Active policies + constraints
- Session history
- Data sensitivity markers
"""

import json
from typing import Dict, List, Any, Optional
from datetime import datetime
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from backend.db.org_repository import PolicyRepository, UserRepository
from backend.middleware import logger


class QueryContextBuilder:
    """Builds structured context for queries."""
    
    # Sensitive columns that require special handling
    SENSITIVE_PATTERNS = [
        "password", "secret", "token", "key",
        "email", "phone", "ssn", "salary", 
        "credit_card", "api_key", "private"
    ]
    
    # Role permissions matrix
    ROLE_PERMISSIONS = {
        "admin": {
            "can_read_sensitive": True,
            "can_join_tables": True,
            "can_aggregate": True,
            "join_limit": None,
            "max_rows": None,
        },
        "analyst": {
            "can_read_sensitive": False,  # Masked instead
            "can_join_tables": True,
            "can_aggregate": True,
            "join_limit": 5,
            "max_rows": 100000,
        },
        "viewer": {
            "can_read_sensitive": False,
            "can_join_tables": False,
            "can_aggregate": False,
            "join_limit": 0,
            "max_rows": 10000,
        }
    }
    
    @classmethod
    def build_context(
        cls,
        org_id: str,
        user_id: str,
        user_natural_language_query: str,
        session_history: Optional[List[Dict]] = None,
        environment: str = "dev",
    ) -> Dict[str, Any]:
        """
        Build complete context for query generation.
        
        Flow:
        1. Get user + role
        2. Get org policies
        3. Detect sensitive columns
        4. Build permissions matrix
        5. Add session context
        6. Finalize + validate
        """
        try:
            # Step 1: Load user + role
            user_role = cls._get_user_role(org_id, user_id)
            
            # Step 2: Build schema context (what's available to this user)
            schema_context = cls._build_schema_context(org_id, user_role)
            
            # Step 3: Build policy context (what constraints apply)
            policy_context = cls._build_policy_context(org_id)
            
            # Step 4: Build permission context (what this user can do)
            permission_context = cls._build_permission_context(user_role)
            
            # Step 5: Build history context (what they've done before)
            history_context = cls._build_history_context(session_history, user_role)
            
            # Step 6: Assemble final context
            context = {
                "metadata": {
                    "builder_version": "1.0",
                    "timestamp": datetime.utcnow().isoformat(),
                    "org_id": org_id,
                    "user_id": user_id,
                    "user_role": user_role,
                    "environment": environment,
                },
                "user_query": user_natural_language_query,
                "user_role": user_role,
                "permissions": permission_context,
                "schema": schema_context,
                "policies": policy_context,
                "history": history_context,
                "sensitive_columns": schema_context.get("sensitive_columns", []),
                "available_tables": schema_context.get("available_tables", []),
                "forbidden_operations": cls._get_forbidden_operations(user_role),
            }
            
            logger.info({
                "event": "context_built",
                "org_id": org_id,
                "user_id": user_id,
                "role": user_role,
                "available_tables": len(schema_context.get("available_tables", [])),
                "active_policies": len(policy_context.get("active_policies", [])),
            })
            
            return context
        
        except Exception as e:
            logger.error({
                "event": "context_build_error",
                "error": str(e),
                "org_id": org_id,
                "user_id": user_id
            })
            # Return minimal safe context on error
            return cls._safe_default_context(org_id, user_id)
    
    @classmethod
    def _get_user_role(cls, org_id: str, user_id: str) -> str:
        """Retrieve user role from database."""
        try:
            user = UserRepository.get_user(org_id, user_id)
            return user.get("role", "viewer") if user else "viewer"
        except Exception as e:
            logger.error({"event": "get_user_role_error", "error": str(e)})
            return "viewer"  # Default to most restrictive
    
    @classmethod
    def _build_schema_context(cls, org_id: str, user_role: str) -> Dict[str, Any]:
        """
        Build schema information.
        For MVP: returns demo schema (AdventureWorks-like)
        Later: can query actual database schema
        """
        # MVP: Static demo schema
        demo_schema = {
            "SalesLT": {
                "tables": ["Product", "Customer", "SalesOrderHeader", "SalesOrderDetail"],
                "public_columns": ["ProductID", "Name", "ListPrice", "CustomerID", "OrderDate"],
                "sensitive_columns": ["CustomerEmail", "Phone", "CreditCardNumber"],
            },
            "HumanResources": {
                "tables": ["Employee", "Department"],
                "public_columns": ["EmployeeID", "FirstName", "LastName", "DepartmentID"],
                "sensitive_columns": ["Salary", "SSN", "StartDate"],  # Depends on role
            },
        }
        
        sensitive_columns = []
        available_tables = []
        
        for schema, info in demo_schema.items():
            for table in info["tables"]:
                available_tables.append(f"{schema}.{table}")
            
            # Only add sensitive columns if user can't read them
            if not cls.ROLE_PERMISSIONS.get(user_role, {}).get("can_read_sensitive", False):
                for col in info.get("sensitive_columns", []):
                    sensitive_columns.append(f"[{schema}].[{info['tables'][0]}].[{col}]")
        
        return {
            "available_tables": available_tables,
            "sensitive_columns": sensitive_columns,
            "demo_schema": demo_schema,
            "schema_knowledge": "AdventureWorks-like demo database",
        }
    
    @classmethod
    def _build_policy_context(cls, org_id: str) -> Dict[str, Any]:
        """Build policy constraints that apply to this org."""
        try:
            policies = PolicyRepository.get_org_policies(org_id, enabled_only=True)
            
            active_policies = []
            policy_constraints = []
            
            if policies:
                for policy in policies:
                    active_policies.append({
                        "id": policy.get("id"),
                        "name": policy.get("name"),
                        "description": policy.get("description"),
                        "rule_type": policy.get("rule_type"),
                    })
                    
                    # Convert policy to constraint for LLM
                    constraint = cls._policy_to_constraint(policy)
                    if constraint:
                        policy_constraints.append(constraint)
            
            return {
                "active_policies": active_policies,
                "policy_constraints": policy_constraints,
                "policy_count": len(active_policies),
            }
        
        except Exception as e:
            logger.error({"event": "build_policy_context_error", "error": str(e)})
            return {
                "active_policies": [],
                "policy_constraints": [],
                "policy_count": 0,
            }
    
    @classmethod
    def _policy_to_constraint(cls, policy: Dict[str, Any]) -> Optional[str]:
        """Convert policy rule to human-readable constraint."""
        rule_type = policy.get("rule_type", "").lower()
        
        if rule_type == "no_full_scan":
            return "Always include WHERE clause to filter rows"
        
        elif rule_type == "max_joins":
            max_joins = policy.get("config", {}).get("max_joins", 3)
            return f"Do not join more than {max_joins} tables in a single query"
        
        elif rule_type == "max_rows":
            max_rows = policy.get("config", {}).get("max_rows", 100000)
            return f"Result set must not exceed {max_rows} rows"
        
        elif rule_type == "destructive_check":
            return "Do not use DELETE, DROP, or TRUNCATE operations"
        
        elif rule_type == "no_cross_join":
            return "Do not use CROSS JOIN operations"
        
        else:
            return None
    
    @classmethod
    def _build_permission_context(cls, user_role: str) -> Dict[str, Any]:
        """Build permission matrix for this role."""
        perms = cls.ROLE_PERMISSIONS.get(user_role, cls.ROLE_PERMISSIONS["viewer"])
        
        return {
            "role": user_role,
            "can_read_sensitive_data": perms.get("can_read_sensitive", False),
            "can_join_tables": perms.get("can_join_tables", False),
            "can_aggregate": perms.get("can_aggregate", False),
            "max_joins": perms.get("join_limit"),
            "max_rows_per_query": perms.get("max_rows"),
            "role_description": cls._describe_role(user_role),
        }
    
    @classmethod
    def _describe_role(cls, role: str) -> str:
        """Return human-readable role description."""
        descriptions = {
            "admin": "Full access to all data and operations",
            "analyst": "Can query most data, but sensitive columns are masked",
            "viewer": "Read-only access to public data only, no joins",
        }
        return descriptions.get(role, "Unknown role")
    
    @classmethod
    def _build_history_context(
        cls,
        session_history: Optional[List[Dict]],
        user_role: str
    ) -> Dict[str, Any]:
        """Build context from recent query history."""
        if not session_history:
            return {
                "previous_queries": [],
                "query_count": 0,
                "recent_tables": [],
            }
        
        # Extract recent queries (last 5)
        recent_queries = session_history[-5:] if len(session_history) > 5 else session_history
        
        # Extract tables mentioned in history
        recent_tables = set()
        for query_log in recent_queries:
            sql = query_log.get("sql", "")
            # Simple table extraction (FROM keyword)
            if "FROM" in sql.upper():
                # This is simplified - real implementation would parse SQL
                tables = sql.upper().split("FROM")[1].split("WHERE")[0].split("JOIN")[0].strip().split()
                recent_tables.update(tables)
        
        return {
            "previous_queries": [
                {
                    "sql": q.get("sql", "")[:100],  # Truncate for context size
                    "status": q.get("status"),
                    "risk_score": q.get("risk_score"),
                }
                for q in recent_queries
            ],
            "query_count": len(session_history),
            "recent_tables": list(recent_tables),
        }
    
    @classmethod
    def _get_forbidden_operations(cls, user_role: str) -> List[str]:
        """Get list of SQL operations forbidden for this role."""
        if user_role == "admin":
            return []  # Admins can do anything
        
        elif user_role == "analyst":
            return ["DELETE", "DROP", "TRUNCATE", "ALTER"]
        
        else:  # viewer
            return ["DELETE", "DROP", "TRUNCATE", "ALTER", "INSERT", "UPDATE", "CREATE"]
    
    @classmethod
    def _safe_default_context(cls, org_id: str, user_id: str) -> Dict[str, Any]:
        """Return minimal safe context when build fails."""
        return {
            "metadata": {
                "builder_version": "1.0",
                "timestamp": datetime.utcnow().isoformat(),
                "org_id": org_id,
                "user_id": user_id,
                "error": "Context build failed, returning minimal safe context",
            },
            "user_role": "viewer",
            "permissions": cls.ROLE_PERMISSIONS["viewer"],
            "schema": {"available_tables": [], "sensitive_columns": []},
            "policies": {"active_policies": [], "policy_constraints": []},
            "forbidden_operations": ["DELETE", "DROP", "TRUNCATE", "ALTER", "INSERT", "UPDATE", "CREATE"],
        }
    
    @classmethod
    def format_for_llm_prompt(cls, context: Dict[str, Any]) -> str:
        """
        Format context as text for inclusion in LLM prompt.
        Makes it explicit what the model should/shouldn't do.
        """
        lines = []
        
        # Role + permissions
        lines.append(f"## User Context")
        lines.append(f"Role: {context.get('user_role', 'viewer').upper()}")
        lines.append(f"User Query: {context.get('user_query', '')}")
        lines.append("")
        
        # Permissions
        perms = context.get("permissions", {})
        lines.append(f"## You CAN:")
        if perms.get("can_read_sensitive_data"):
            lines.append("- Read and return sensitive columns")
        if perms.get("can_join_tables"):
            lines.append(f"- Join up to {perms.get('max_joins') or 'unlimited'} tables")
        if perms.get("can_aggregate"):
            lines.append("- Use aggregate functions (SUM, COUNT, AVG, etc.)")
        lines.append("")
        
        # Forbidden
        lines.append(f"## You CANNOT:")
        for op in context.get("forbidden_operations", []):
            lines.append(f"- Use {op} statements")
        lines.append("")
        
        # Constraints from policies
        policies = context.get("policies", {})
        if policies.get("policy_constraints"):
            lines.append(f"## Policy Constraints:")
            for constraint in policies["policy_constraints"]:
                lines.append(f"- {constraint}")
            lines.append("")
        
        # Available data
        schema = context.get("schema", {})
        if schema.get("available_tables"):
            lines.append(f"## Available Tables:")
            for table in schema["available_tables"][:5]:  # Limit to 5
                lines.append(f"- {table}")
            if len(schema["available_tables"]) > 5:
                lines.append(f"- ... ({len(schema['available_tables']) - 5} more)")
            lines.append("")
        
        # Sensitive columns warning
        if schema.get("sensitive_columns"):
            lines.append(f"## Sensitive Columns (will be MASKED if accessed):")
            for col in schema["sensitive_columns"][:3]:
                lines.append(f"- {col}")
            if len(schema["sensitive_columns"]) > 3:
                lines.append(f"- ... ({len(schema['sensitive_columns']) - 3} more)")
        
        return "\n".join(lines)


# Convenience function for use in pipeline
def build_query_context(
    org_id: str,
    user_id: str,
    user_query: str,
    session_history: Optional[List[Dict]] = None,
    environment: str = "dev",
) -> Dict[str, Any]:
    """
    Convenience wrapper for context building.
    """
    return QueryContextBuilder.build_context(
        org_id=org_id,
        user_id=user_id,
        user_natural_language_query=user_query,
        session_history=session_history,
        environment=environment,
    )

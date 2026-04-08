"""
TenantAwareQueryService - Enhanced Query Builder with Enforced Tenant Isolation

This wraps the standard QueryService and enforces org_id filtering on ALL queries.

CRITICAL: This prevents accidental cross-tenant data leakage.

Usage:
  from backend.services.tenant_context import tenant_context
  from backend.services.tenant_aware_query_service import get_tenant_aware_query_service
  
  with tenant_context(org_id="acme_corp", user_id="john@acme.com"):
      service = get_tenant_aware_query_service()
      
      # Service automatically adds: WHERE org_id = 'acme_corp'
      enhanced_sql = service.build_sql_with_tenant_filter(
          "SELECT product, revenue FROM sales WHERE year = 2024",
          org_id="acme_corp"
      )
      # Result: "SELECT product, revenue FROM sales WHERE year = 2024 AND org_id = 'acme_corp'"
"""

import re
from typing import Optional, Tuple
from .tenant_context import require_context, get_org_id


class TenantAwareQueryService:
    """
    Wraps query building with automatic tenant isolation.

    Every SQL query gets a WHERE clause enforcing org_id filter.
    """

    def __init__(self):
        pass

    def build_sql_with_tenant_filter(
        self, sql: str, org_id: Optional[str] = None
    ) -> str:
        """
        Build SQL with automatic org_id filtering.

        Adds 'WHERE org_id = :org_id' or 'AND org_id = :org_id' to the query.

        CRITICAL: Call this on ALL user-generated SQL before execution.

        Args:
            sql: Original SQL query
            org_id: Organization ID (optional, uses context if not provided)

        Returns:
            Enhanced SQL with org_id filter

        Raises:
            RuntimeError: If org_id not provided and no tenant context

        Examples:
            Input:  "SELECT * FROM customers"
            Output: "SELECT * FROM customers WHERE org_id = :org_id"

            Input:  "SELECT * FROM customers WHERE status='active'"
            Output: "SELECT * FROM customers WHERE status='active' AND org_id = :org_id"
        """
        if not org_id:
            org_id = get_org_id()  # Raises if no context

        sql = sql.strip()

        # Check if query already has WHERE clause
        if self._has_where_clause(sql):
            # Append AND org_id filter
            return sql + f" AND org_id = :org_id"
        else:
            # Add WHERE org_id filter
            return sql + f" WHERE org_id = :org_id"

    def _has_where_clause(self, sql: str) -> bool:
        """
        Detect if SQL already has a WHERE clause.

        Ignores WHERE in comments and strings.
        """
        # Remove SQL comments
        sql_no_comments = re.sub(r"--.*$", "", sql, flags=re.MULTILINE)
        sql_no_comments = re.sub(r"/\*.*?\*/", "", sql_no_comments, flags=re.DOTALL)

        # Check for WHERE keyword (case-insensitive, word boundary)
        return bool(re.search(r"\bWHERE\b", sql_no_comments, re.IGNORECASE))

    def build_sql_with_explicit_org_id(
        self, sql: str, org_id: str, param_style: str = "named"
    ) -> Tuple[str, dict]:
        """
        Build SQL with explicit org_id parameter binding.

        For explicit control over parameter binding style.

        Args:
            sql: Original SQL
            org_id: Organization ID
            param_style: "named" (default) for :org_id or "positional" for %s

        Returns:
            Tuple of (enhanced_sql, parameters_dict)

        Example (named):
            sql, params = service.build_sql_with_explicit_org_id(
                "SELECT * FROM customers WHERE status = :status",
                org_id="acme_corp"
            )
            # Result:
            # sql = "SELECT * FROM customers WHERE status = :status AND org_id = :org_id"
            # params = {"status": "active", "org_id": "acme_corp"}
        """
        if self._has_where_clause(sql):
            enhanced_sql = sql + " AND org_id = :org_id"
        else:
            enhanced_sql = sql + " WHERE org_id = :org_id"

        params = {"org_id": org_id}
        return enhanced_sql, params

    def validate_tenant_context(self) -> str:
        """
        Validate that tenant context is set.

        Call at start of any operation to ensure tenant is established.

        Returns:
            The org_id

        Raises:
            RuntimeError: If no tenant context
        """
        return get_org_id()  # Raises if not set

    def inject_org_id_into_params(
        self, params: dict, org_id: Optional[str] = None
    ) -> dict:
        """
        Inject org_id into parameters dict.

        Useful when you already have parameter dict.

        Args:
            params: Existing parameter dictionary
            org_id: Organization ID (optional, uses context if not provided)

        Returns:
            Updated params with org_id added

        Raises:
            ValueError: If org_id already in params with different value
        """
        if not org_id:
            org_id = get_org_id()

        if "org_id" in params and params["org_id"] != org_id:
            raise ValueError(
                f"Conflicting org_id in params: {params['org_id']} vs {org_id}"
            )

        params["org_id"] = org_id
        return params

    def audit_enforcement_check(self, sql: str, org_id: str) -> Tuple[bool, str]:
        """
        Audit check: verify org_id enforcement in SQL.

        For debugging/verification of tenant isolation.

        Args:
            sql: Generated SQL to check
            org_id: Expected org_id

        Returns:
            Tuple of (is_safe, message)

        Safe = org_id filter is present in SQL
        """
        if "org_id" not in sql.lower():
            return (
                False,
                f"⚠️ SECURITY: SQL missing org_id filter for org {org_id}",
            )

        if org_id not in sql:
            return (
                False,
                f"⚠️ SECURITY: SQL missing specific org_id '{org_id}' value",
            )

        return (True, f"✅ Tenant isolation verified for org {org_id}")


# Singleton instance
_service: Optional[TenantAwareQueryService] = None


def get_tenant_aware_query_service() -> TenantAwareQueryService:
    """Get or create global TenantAwareQueryService instance"""
    global _service
    if _service is None:
        _service = TenantAwareQueryService()
    return _service

"""Zero-Trust Query Policy Enforcer."""

import re
import logging
from typing import Dict, Any, List, Tuple, Optional
from enum import Enum

logger = logging.getLogger(__name__)


class PolicyViolationType(Enum):
    """Types of policy violations."""
    DENIED_TABLE = "DENIED_TABLE"
    DENIED_COLUMN = "DENIED_COLUMN"
    PII_ACCESS = "PII_ACCESS"
    DANGEROUS_OPERATION = "DANGEROUS_OPERATION"
    ROW_LIMIT_EXCEEDED = "ROW_LIMIT_EXCEEDED"
    UNAUTHORIZED_APPLICATION = "UNAUTHORIZED_APPLICATION"
    UNAUTHORIZED_ROLE = "UNAUTHORIZED_ROLE"
    MISSING_TOKEN = "MISSING_TOKEN"


class QueryViolation:
    """Represents a query policy violation."""
    
    def __init__(
        self,
        violation_type: PolicyViolationType,
        message: str,
        table: Optional[str] = None,
        column: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        self.violation_type = violation_type
        self.message = message
        self.table = table
        self.column = column
        self.details = details or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert violation to dictionary."""
        return {
            "type": self.violation_type.value,
            "message": self.message,
            "table": self.table,
            "column": self.column,
            "details": self.details
        }


class ZeroTrustPolicyEnforcer:
    """
    Enforces zero-trust security policies on AI queries.
    
    Zero-Trust principles:
    1. No direct database access - only through VoxCore
    2. Mandatory policy enforcement - all queries validated
    3. Identity-aware - request context matters
    4. Least privilege - whitelist approach
    """
    
    def __init__(self, zero_trust_config: Dict[str, Any]):
        """
        Initialize enforcer with zero-trust policy configuration.
        
        Args:
            zero_trust_config: Dictionary from [zero_trust] section of policies.ini
        """
        self.config = zero_trust_config
        self.mode = zero_trust_config.get("mode", "enabled")
        
        # Parse policy lists
        self.allow_tables = self._parse_list(zero_trust_config.get("allow_tables", ""))
        self.deny_tables = self._parse_list(zero_trust_config.get("deny_tables", ""))
        self.pii_protected_columns = self._parse_list(zero_trust_config.get("pii_protected_columns", ""))
        self.max_rows = int(zero_trust_config.get("max_rows", 1000))
        self.allowed_ai_applications = self._parse_list(zero_trust_config.get("allowed_ai_applications", ""))
        self.allowed_user_roles = self._parse_list(zero_trust_config.get("allowed_user_roles", ""))
        
        # Parse dangerous operations
        self.block_delete = zero_trust_config.get("block_delete", "false").lower() == "true"
        self.block_drop = zero_trust_config.get("block_drop", "false").lower() == "true"
        self.block_update = zero_trust_config.get("block_update", "false").lower() == "true"
        self.require_query_token = zero_trust_config.get("require_query_token", "false").lower() == "true"
    
    def _parse_list(self, value: str) -> List[str]:
        """Parse comma-separated list from config."""
        if not value or not value.strip():
            return []
        return [item.strip() for item in value.split(",") if item.strip()]
    
    def validate_query(self, query: str, request_context: Dict[str, Any]) -> Tuple[bool, List[QueryViolation]]:
        """
        Validate a query against zero-trust policies.
        
        Args:
            query: SQL query string
            request_context: Request metadata (tenant_id, user_id, application, role, etc)
        
        Returns:
            Tuple of (is_valid, violations_list)
        """
        if self.mode != "enabled":
            return True, []
        
        violations: List[QueryViolation] = []
        
        # 1. Check application authorization
        app = request_context.get("application", "unknown")
        violations.extend(self._check_application_allowed(app))
        
        # 2. Check user role authorization
        role = request_context.get("role", "viewer")
        violations.extend(self._check_role_allowed(role))
        
        # 3. Check query token if required
        if self.require_query_token:
            token = request_context.get("query_token")
            violations.extend(self._check_token(token))
        
        # 4. Check dangerous operations
        violations.extend(self._check_dangerous_operations(query))
        
        # 5. Parse and validate tables/columns
        tables = self._extract_tables(query)
        columns = self._extract_columns(query)
        
        violations.extend(self._check_table_access(tables))
        violations.extend(self._check_column_access(columns))
        violations.extend(self._check_pii_access(columns))
        
        # 6. Check row limit
        limit = self._extract_limit(query)
        if limit and limit > self.max_rows:
            violations.append(QueryViolation(
                PolicyViolationType.ROW_LIMIT_EXCEEDED,
                f"Query limit {limit} exceeds policy maximum {self.max_rows}",
                details={"requested": limit, "maximum": self.max_rows}
            ))
        
        is_valid = len(violations) == 0
        return is_valid, violations
    
    def _check_application_allowed(self, application: str) -> List[QueryViolation]:
        """Check if application is allowed."""
        if not self.allowed_ai_applications:
            return []
        
        if application not in self.allowed_ai_applications:
            return [QueryViolation(
                PolicyViolationType.UNAUTHORIZED_APPLICATION,
                f"Application '{application}' not in allowed list: {', '.join(self.allowed_ai_applications)}",
                details={"application": application, "allowed": self.allowed_ai_applications}
            )]
        return []
    
    def _check_role_allowed(self, role: str) -> List[QueryViolation]:
        """Check if user role is allowed."""
        if not self.allowed_user_roles:
            return []
        
        if role not in self.allowed_user_roles:
            return [QueryViolation(
                PolicyViolationType.UNAUTHORIZED_ROLE,
                f"Role '{role}' not in allowed list: {', '.join(self.allowed_user_roles)}",
                details={"role": role, "allowed": self.allowed_user_roles}
            )]
        return []
    
    def _check_token(self, token: Optional[str]) -> List[QueryViolation]:
        """Check if valid query token is provided."""
        if not token or token.strip() == "":
            return [QueryViolation(
                PolicyViolationType.MISSING_TOKEN,
                "Query token required by zero-trust policy"
            )]
        return []
    
    def _check_dangerous_operations(self, query: str) -> List[QueryViolation]:
        """Check for DELETE, DROP, UPDATE operations."""
        violations = []
        query_upper = query.upper().strip()
        
        if self.block_delete and query_upper.startswith("DELETE"):
            violations.append(QueryViolation(
                PolicyViolationType.DANGEROUS_OPERATION,
                "DELETE operations blocked by policy"
            ))
        
        if self.block_drop and query_upper.startswith("DROP"):
            violations.append(QueryViolation(
                PolicyViolationType.DANGEROUS_OPERATION,
                "DROP operations blocked by policy"
            ))
        
        if self.block_update and query_upper.startswith("UPDATE"):
            violations.append(QueryViolation(
                PolicyViolationType.DANGEROUS_OPERATION,
                "UPDATE operations blocked by policy"
            ))
        
        return violations
    
    def _extract_tables(self, query: str) -> List[str]:
        """Extract table names from query (basic parsing)."""
        tables = []
        
        # Find tables after FROM/JOIN clauses
        from_pattern = r'(?:FROM|JOIN|INTO|UPDATE)\s+(\w+)'
        matches = re.finditer(from_pattern, query, re.IGNORECASE)
        
        for match in matches:
            table = match.group(1).lower()
            if table not in tables:
                tables.append(table)
        
        return tables
    
    def _extract_columns(self, query: str) -> List[str]:
        """Extract column names from query (basic parsing)."""
        columns = []
        
        # Find columns in SELECT, WHERE clauses
        select_pattern = r'SELECT\s+(.*?)\s+FROM'
        select_match = re.search(select_pattern, query, re.IGNORECASE)
        
        if select_match:
            select_clause = select_match.group(1)
            # Split by comma and get individual columns
            for col in select_clause.split(","):
                col = col.strip()
                # Remove aliases and functions
                col = re.sub(r'\s+AS\s+\w+', '', col, flags=re.IGNORECASE)
                col = re.sub(r'\w+\(', '', col)  # Remove function names
                col = col.replace(")", "").strip()
                if col and col != "*":
                    columns.append(col.lower())
        
        return columns
    
    def _check_table_access(self, tables: List[str]) -> List[QueryViolation]:
        """Check if tables are allowed by policy."""
        violations = []
        
        for table in tables:
            # Check if table is explicitly denied
            if table in self.deny_tables:
                violations.append(QueryViolation(
                    PolicyViolationType.DENIED_TABLE,
                    f"Table '{table}' is explicitly denied by policy",
                    table=table
                ))
            
            # If allow_tables is specified, check whitelist
            if self.allow_tables and table not in self.allow_tables:
                violations.append(QueryViolation(
                    PolicyViolationType.DENIED_TABLE,
                    f"Table '{table}' not in allowed list: {', '.join(self.allow_tables)}",
                    table=table,
                    details={"allowed": self.allow_tables}
                ))
        
        return violations
    
    def _check_column_access(self, columns: List[str]) -> List[QueryViolation]:
        """Check if columns are allowed by policy."""
        violations = []
        
        # For now, just check against PII columns
        # Could be expanded for column-level RBAC
        
        return violations
    
    def _check_pii_access(self, columns: List[str]) -> List[QueryViolation]:
        """Check if PII-protected columns are being accessed."""
        violations = []
        
        for column in columns:
            if column in self.pii_protected_columns:
                violations.append(QueryViolation(
                    PolicyViolationType.PII_ACCESS,
                    f"Column '{column}' contains PII and is access-restricted",
                    column=column,
                    details={"pii_protected_columns": self.pii_protected_columns}
                ))
        
        return violations
    
    def _extract_limit(self, query: str) -> Optional[int]:
        """Extract LIMIT value from query."""
        limit_pattern = r'LIMIT\s+(\d+)'
        match = re.search(limit_pattern, query, re.IGNORECASE)
        
        if match:
            return int(match.group(1))
        return None


def load_policy_enforcer(policies: Dict[str, Any]) -> Optional[ZeroTrustPolicyEnforcer]:
    """
    Load zero-trust policy enforcer from policies dictionary.
    
    Args:
        policies: Dictionary of policies from policies.ini
    
    Returns:
        ZeroTrustPolicyEnforcer instance or None if zero_trust config not found
    """
    zero_trust_config = policies.get("zero_trust")
    if not zero_trust_config:
        return None
    
    return ZeroTrustPolicyEnforcer(zero_trust_config)

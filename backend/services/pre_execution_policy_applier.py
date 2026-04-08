"""
Pre-Execution Policy Applier: Transforms SQL before execution

Applies FILTER and AGGREGATE_ONLY policies to SQL queries before they execute.
This is the first line of defense - limiting what data the query can access.

Examples:
- FILTER policy: "sales sees only their region" → adds WHERE region = 'us_west'
- AGGREGATE_ONLY policy: "analytics team sees only aggregates" → rewrites SELECT with GROUP BY
"""

import re
from typing import Dict, List, Optional, Any, Tuple
from backend.services.policy_definition import PolicyDefinition, PolicyType


class PreExecutionPolicyApplier:
    """
    Applies policies to SQL before execution.
    Modifies queries to enforce access restrictions at execution time.
    """
    
    def __init__(self):
        self.aggregate_functions = {'COUNT', 'SUM', 'AVG', 'MIN', 'MAX', 'GROUP_CONCAT', 'STRING_AGG'}
    
    def apply_policies(
        self,
        sql: str,
        policies: List[PolicyDefinition]
    ) -> Tuple[str, List[str]]:
        """
        Apply all applicable policies to SQL.
        
        Returns:
            (transformed_sql, effects_applied)
        
        Raises:
            RuntimeError: If BLOCK policy applies
        """
        effects = []
        current_sql = sql
        
        # Check for BLOCK policies first
        for policy in policies:
            if policy.type == PolicyType.BLOCK and policy.action.deny_access:
                raise RuntimeError(f"Access denied: {policy.action.deny_reason}")
        
        # Apply AGGREGATE_ONLY policies (must enable aggregation)
        aggregate_policies = [p for p in policies if p.type == PolicyType.AGGREGATE_ONLY]
        if aggregate_policies:
            current_sql = self._apply_aggregate_only(current_sql, aggregate_policies)
            effects.append("aggregate_only_enforced")
        
        # Apply FILTER policies (add WHERE clauses)
        filter_policies = [p for p in policies if p.type == PolicyType.FILTER]
        if filter_policies:
            where_clauses = [p.action.where_clause for p in filter_policies if p.action.where_clause]
            if where_clauses:
                current_sql = self._add_where_clauses(current_sql, where_clauses)
                effects.append(f"filters_applied:{len(where_clauses)}")
        
        return current_sql, effects
    
    def _add_where_clauses(self, sql: str, where_clauses: List[str]) -> str:
        """
        Add WHERE clauses to SQL query.
        Handles existing WHERE clauses by using AND.
        """
        if not where_clauses:
            return sql
        
        combined_where = " AND ".join(f"({clause})" for clause in where_clauses)
        
        # Check if query already has WHERE
        where_match = re.search(
            r'WHERE\s+(.+?)(?:\s+GROUP\s+BY|\s+ORDER\s+BY|\s+LIMIT|\s+;|$)',
            sql,
            re.IGNORECASE | re.DOTALL
        )
        
        if where_match:
            # Query has WHERE - add AND
            existing_where = where_match.group(1).rstrip()
            # Find the position to insert
            where_start = where_match.start()
            where_end = where_match.start() + len("WHERE") + len(where_match.group(0)) - len(where_match.group(1))
            
            # Build new query with additional WHERE clause
            before_where = sql[:where_start + 5]  # Include "WHERE"
            after_where = sql[where_start + 5:]
            
            new_sql = before_where + f" ({existing_where}) AND {combined_where}" + after_where
            return new_sql
        else:
            # No WHERE - add one
            # Find insertion point (after FROM clause)
            from_match = re.search(
                r'FROM\s+.+?(?=\s+GROUP\s+BY|\s+ORDER\s+BY|\s+LIMIT|\s+;|$)',
                sql,
                re.IGNORECASE | re.DOTALL
            )
            
            if from_match:
                insert_pos = from_match.end()
                return sql[:insert_pos] + f" WHERE {combined_where}" + sql[insert_pos:]
            else:
                # Couldn't find FROM - append WHERE at end
                if sql.rstrip().endswith(';'):
                    return sql.rstrip()[:-1] + f" WHERE {combined_where};"
                else:
                    return sql.rstrip() + f" WHERE {combined_where}"
    
    def _apply_aggregate_only(
        self,
        sql: str,
        policies: List[PolicyDefinition]
    ) -> str:
        """
        Transform query to use only allowed aggregates.
        
        Converts SELECT col1, col2 to SELECT COUNT(*) or similar,
        forcing aggregation instead of row-level access.
        """
        # Check if query is already aggregated
        if self._has_aggregate_function(sql):
            return sql  # Already aggregated
        
        # Get allowed aggregates from first policy
        allowed = policies[0].action.allowed_aggregates if policies[0].action.allowed_aggregates else ['COUNT']
        
        # Simple rewrite: replace SELECT clause with COUNT(*)
        # For now, enforce COUNT(*) which is safest
        select_match = re.search(
            r'SELECT\s+(DISTINCT\s+)?(.+?)\s+FROM',
            sql,
            re.IGNORECASE | re.DOTALL
        )
        
        if select_match:
            distinct = select_match.group(1) or ''
            before_select = sql[:select_match.start()]
            from_pos = sql.find('FROM', select_match.start())
            after_select = sql[from_pos:]
            
            # Rewrite with COUNT(*)
            rewritten = f"{before_select}SELECT {distinct}COUNT(*) FROM {after_select[5:]}"
            return rewritten
        
        return sql
    
    def _has_aggregate_function(self, sql: str) -> bool:
        """Check if SQL already contains aggregate functions"""
        sql_clean = re.sub(r'--.*$', '', sql, flags=re.MULTILINE)
        sql_clean = re.sub(r'/\*.*?\*/', '', sql_clean, flags=re.DOTALL)
        
        for agg in self.aggregate_functions:
            if re.search(rf'\b{agg}\s*\(', sql_clean, re.IGNORECASE):
                return True
        return False
    
    def validate_query_allowed(
        self,
        sql: str,
        policies: List[PolicyDefinition]
    ) -> Tuple[bool, Optional[str]]:
        """
        Check if query is completely allowed before transformation.
        
        Returns:
            (is_allowed, reason_if_denied)
        """
        for policy in policies:
            if policy.type == PolicyType.BLOCK and policy.action.deny_access:
                return False, policy.action.deny_reason
        
        return True, None

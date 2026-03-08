"""
Policy Enforcement Engine
Checks SQL queries against organizational policies
"""

from typing import Dict, List, Any


class PolicyChecker:
    """Enforces security and governance policies on SQL queries"""
    
    def __init__(self):
        self.violations = []
        self.blocked = False
        self.recommendations = []
    
    def check(self, query: str) -> Dict[str, Any]:
        """
        Check SQL query against policies
        
        Args:
            query: SQL query string
            
        Returns:
            {
                "violations": [],
                "blocked": bool,
                "recommendations": []
            }
        """
        self.violations = []
        self.blocked = False
        self.recommendations = []
        
        query_upper = query.upper()
        
        # Policy 1: Prevent DROP TABLE
        if self._check_drop_policy(query_upper):
            self.violations.append("DROP TABLE not permitted")
            self.blocked = True
            self.recommendations.append("Use DELETE with WHERE clause instead")
        
        # Policy 2: Prevent DELETE without WHERE
        if self._check_delete_without_where(query_upper):
            self.violations.append("DELETE without WHERE clause not permitted")
            self.blocked = True
            self.recommendations.append("Add WHERE clause to limit affected rows")
        
        # Policy 3: Prevent UPDATE without WHERE
        if self._check_update_without_where(query_upper):
            self.violations.append("UPDATE without WHERE clause not permitted")
            self.blocked = True
            self.recommendations.append("Add WHERE clause to limit affected rows")
        
        # Policy 4: Prevent access to sensitive columns
        if self._check_sensitive_column_access(query_upper):
            self.violations.append("Access to sensitive columns requires authorization")
            self.recommendations.append("Use field-level security or request authorization")
        
        # Policy 5: Prevent TRUNCATE
        if self._check_truncate(query_upper):
            self.violations.append("TRUNCATE not permitted")
            self.blocked = True
            self.recommendations.append("Use DELETE instead")
        
        # Policy 6: Prevent direct system table access
        if self._check_system_tables(query_upper):
            self.violations.append("Direct system table access not permitted")
            self.blocked = True
        
        return {
            "violations": self.violations,
            "blocked": self.blocked,
            "recommendations": self.recommendations
        }
    
    @staticmethod
    def _check_drop_policy(query_upper: str) -> bool:
        """Check DROP TABLE policy"""
        return 'DROP' in query_upper and 'TABLE' in query_upper
    
    @staticmethod
    def _check_delete_without_where(query_upper: str) -> bool:
        """Check DELETE without WHERE clause"""
        if 'DELETE' not in query_upper:
            return False
        
        # Simple check: if DELETE exists but no WHERE, it's risky
        delete_match = query_upper.find('DELETE')
        where_match = query_upper.find('WHERE', delete_match)
        
        return where_match == -1
    
    @staticmethod
    def _check_update_without_where(query_upper: str) -> bool:
        """Check UPDATE without WHERE clause"""
        if 'UPDATE' not in query_upper:
            return False
        
        # Simple check: if UPDATE exists but no WHERE, it's risky
        update_match = query_upper.find('UPDATE')
        where_match = query_upper.find('WHERE', update_match)
        
        return where_match == -1
    
    @staticmethod
    def _check_sensitive_column_access(query_upper: str) -> bool:
        """Check access to sensitive columns"""
        sensitive_columns = {
            'SALARY', 'EMAIL', 'SSN', 'PASSWORD', 'CREDIT_CARD',
            'PHONE', 'PRIVATE_KEY', 'API_KEY', 'TOKEN'
        }
        
        return any(col in query_upper for col in sensitive_columns)
    
    @staticmethod
    def _check_truncate(query_upper: str) -> bool:
        """Check TRUNCATE policy"""
        return 'TRUNCATE' in query_upper
    
    @staticmethod
    def _check_system_tables(query_upper: str) -> bool:
        """Check access to system tables"""
        system_patterns = ['SYS.', 'INFORMATION_SCHEMA', 'SYSOBJECTS', 'SYSCOLUMNS']
        return any(pattern in query_upper for pattern in system_patterns)

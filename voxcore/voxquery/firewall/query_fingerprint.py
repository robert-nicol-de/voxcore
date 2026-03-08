"""
Query Fingerprinting for Governance
Creates normalized query patterns to detect repeated risky behaviors
"""

import re
import hashlib
from typing import Dict, Any


class QueryFingerprinter:
    """
    Creates query fingerprints for governance analytics
    
    Example:
        Original: SELECT * FROM customers WHERE id = 123
        Fingerprint: SELECT * FROM customers WHERE id = ?
        Hash: a3f5c8d2e1b9f4c6a2d8e5f1b3c6d8e0
        
    This allows tracking:
    - Repeated risky patterns
    - AI model behavior
    - Frequently blocked operations
    """
    
    def fingerprint(self, query: str) -> Dict[str, Any]:
        """
        Create a fingerprint of a SQL query for pattern matching
        
        Returns:
            {
                "fingerprint": normalized query pattern,
                "hash": SHA256 hash,
                "operations": ["SELECT", "FROM", "WHERE"],
                "tables": ["customers"],
                "sensitive_columns": ["email"],
                "literals_count": 1
            }
        """
        
        # Normalize the query
        normalized = self._normalize_query(query)
        
        # Extract operation types
        operations = self._extract_operations(query)
        
        # Extract table names
        tables = self._extract_tables(query)
        
        # Extract sensitive column access
        sensitive_columns = self._detect_sensitive_columns(query)
        
        # Count literals (numbers, strings)
        literals_count = len(re.findall(r"'[^']*'|\b\d+\b", query))
        
        # Create hash
        fingerprint_hash = hashlib.sha256(normalized.encode()).hexdigest()
        
        return {
            "fingerprint": normalized,
            "hash": fingerprint_hash,
            "operations": operations,
            "tables": tables,
            "sensitive_columns": sensitive_columns,
            "literals_count": literals_count
        }
    
    @staticmethod
    def _normalize_query(query: str) -> str:
        """
        Normalize SQL query for pattern matching
        
        Examples:
            "SELECT id FROM users WHERE id = 123" → "SELECT id FROM users WHERE id = ?"
            "DrOp TABLE users" → "DROP TABLE users" (SQL injection attempt)
        """
        
        # CRITICAL: Normalize case to catch bypass attempts
        normalized = query.upper()
        
        # Replace string literals with ?
        normalized = re.sub(r"'[^']*'", "?", normalized)
        
        # Replace numbers with ?
        normalized = re.sub(r"\b\d+\b", "?", normalized)
        
        # Normalize whitespace
        normalized = re.sub(r"\s+", " ", normalized).strip()
        
        # Normalize common SQL variations
        normalized = normalized.replace("!=", "<>")
        normalized = normalized.replace(" = NULL", " IS NULL")
        
        return normalized
    
    @staticmethod
    def _extract_operations(query: str) -> list:
        """Extract SQL operation types (SELECT, INSERT, UPDATE, DELETE, DROP, etc.)"""
        operations = []
        sql_upper = query.upper()
        
        operation_keywords = [
            'SELECT', 'INSERT', 'UPDATE', 'DELETE', 'DROP', 'CREATE', 
            'ALTER', 'TRUNCATE', 'EXEC', 'EXECUTE', 'GRANT', 'REVOKE'
        ]
        
        for op in operation_keywords:
            if f" {op} " in f" {sql_upper} ":
                operations.append(op)
        
        return operations
    
    @staticmethod
    def _extract_tables(query: str) -> list:
        """Extract table names from query"""
        tables = []
        sql_upper = query.upper()
        
        # Extract FROM clause tables
        from_match = re.search(r'FROM\s+([^\s,;]+)', sql_upper)
        if from_match:
            tables.append(from_match.group(1).lower())
        
        # Extract JOIN clause tables
        join_matches = re.findall(r'JOIN\s+([^\s,;]+)', sql_upper)
        tables.extend([t.lower() for t in join_matches])
        
        # Extract INTO clause tables (INSERT)
        into_match = re.search(r'INTO\s+([^\s,;(]+)', sql_upper)
        if into_match:
            tables.append(into_match.group(1).lower())
        
        # Remove duplicates while preserving order
        seen = set()
        unique_tables = []
        for t in tables:
            if t not in seen:
                seen.add(t)
                unique_tables.append(t)
        
        return unique_tables
    
    @staticmethod
    def _detect_sensitive_columns(query: str) -> list:
        """
        Detect access to sensitive columns
        Triggers governance alerts for PII/security-sensitive data
        """
        sensitive_patterns = {
            'email': r'\bemail\b|\bemails\b',
            'password': r'\bpassword\b|\bpasswords\b',
            'ssn': r'\bssn\b|\bsocial_security\b',
            'salary': r'\bsalary\b|\bsalaries\b|\bpay\b',
            'phone': r'\bphone\b|\bphone_number\b',
            'credit_card': r'\bcredit_card\b|\bcc_number\b',
            'token': r'\btoken\b|\bauth_token\b|\brefresh_token\b',
            'secret': r'\bsecret\b|\bapi_secret\b',
            'api_key': r'\bapi_key\b|\bapikey\b'
        }
        
        detected = []
        sql_upper = query.upper()
        
        for column_type, pattern in sensitive_patterns.items():
            if re.search(pattern, sql_upper, re.IGNORECASE):
                detected.append(column_type)
        
        return detected


# Global fingerprinter instance
query_fingerprinter = QueryFingerprinter()

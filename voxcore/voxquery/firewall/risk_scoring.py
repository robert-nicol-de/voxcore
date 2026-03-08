"""
Risk Scoring Engine for SQL Query Analysis
Analyzes generated SQL queries and assigns risk scores
"""

import re
from typing import Dict, Any


class RiskScorer:
    """Analyzes SQL queries and assigns risk scores (0-100)"""
    
    # High-risk keywords
    HIGH_RISK_KEYWORDS = {'DROP', 'DELETE', 'UPDATE', 'TRUNCATE', 'ALTER', 'EXEC', 'EXECUTE'}
    
    # Medium-risk patterns
    MEDIUM_RISK_PATTERNS = {
        'SELECT *': 2,  # Wildcard selection
        'UNION': 3,      # Potential injection
        'CROSS JOIN': 2, # Performance risk
    }
    
    # Sensitive columns that should be protected
    SENSITIVE_COLUMNS = {
        'password', 'salt', 'token', 'secret', 'ssn', 'salary', 
        'email', 'phone', 'credit_card', 'cvv', 'pin', 'api_key',
        'access_token', 'refresh_token', 'private_key'
    }
    
    def __init__(self):
        self.risk_score = 0
        self.risk_factors = []
    
    def score(self, query: str) -> Dict[str, Any]:
        """
        Analyze SQL query and return risk score
        
        Args:
            query: SQL query string
            
        Returns:
            {
                "risk_score": int (0-100),
                "risk_level": "LOW" | "MEDIUM" | "HIGH",
                "risk_factors": []
            }
        """
        self.risk_score = 0
        self.risk_factors = []
        
        query_upper = query.upper()
        
        # Check for destructive operations (enterprise risk scoring)
        if 'DROP' in query_upper or 'TRUNCATE' in query_upper:
            self.risk_score += 95
            self.risk_factors.append("CRITICAL: DROP/TRUNCATE operation detected")
        elif 'DELETE' in query_upper:
            self.risk_score += 85
            self.risk_factors.append("HIGH: DELETE operation detected")
        elif 'UPDATE' in query_upper:
            self.risk_score += 75
            self.risk_factors.append("HIGH: UPDATE operation detected")
        elif 'ALTER' in query_upper or 'EXEC' in query_upper or 'EXECUTE' in query_upper:
            self.risk_score += 80
            self.risk_factors.append("CRITICAL: ALTER/EXEC operation detected")
        
        # Check for suspicious patterns
        if self._has_suspicious_patterns(query_upper):
            self.risk_score += 15
        
        # Check for sensitive column access
        if self._accesses_sensitive_columns(query_upper):
            self.risk_score += 25
            self.risk_factors.append("Access to sensitive columns detected")
        
        # Check for potential SQL injection patterns
        if self._has_injection_indicators(query):
            self.risk_score += 20
            self.risk_factors.append("Potential SQL injection pattern detected")
        
        # Check for wildcard selections
        if 'SELECT *' in query_upper:
            self.risk_score += 10
            self.risk_factors.append("Wildcard column selection (SELECT *)")
        
        # Cap at 100
        self.risk_score = min(100, self.risk_score)
        
        risk_level = self._get_risk_level(self.risk_score)
        
        return {
            "risk_score": self.risk_score,
            "risk_level": risk_level,
            "risk_factors": self.risk_factors
        }
    
    def _has_destructive_keywords(self, query_upper: str) -> bool:
        """Check for destructive SQL keywords"""
        return any(keyword in query_upper for keyword in self.HIGH_RISK_KEYWORDS)
    
    def _has_suspicious_patterns(self, query_upper: str) -> bool:
        """Check for suspicious patterns"""
        for pattern in self.MEDIUM_RISK_PATTERNS.keys():
            if pattern in query_upper:
                self.risk_factors.append(f"Suspicious pattern detected: {pattern}")
                return True
        return False
    
    def _accesses_sensitive_columns(self, query_upper: str) -> bool:
        """Check if query accesses sensitive columns"""
        for sensitive in self.SENSITIVE_COLUMNS:
            if sensitive.upper() in query_upper or f'`{sensitive}`' in query_upper.lower():
                self.risk_factors.append(f"Sensitive column access: {sensitive}")
                return True
        return False
    
    def _has_injection_indicators(self, query: str) -> bool:
        """Check for common SQL injection patterns"""
        injection_patterns = [
            r"'\s*OR\s*'",
            r"--\s*$",
            r"/\*.*\*/",
            r"xp_",
            r"sp_",
        ]
        
        for pattern in injection_patterns:
            if re.search(pattern, query, re.IGNORECASE):
                return True
        return False
    
    @staticmethod
    def _get_risk_level(score: int) -> str:
        """Convert numeric score to risk level"""
        if score < 30:
            return "LOW"
        elif score < 70:
            return "MEDIUM"
        else:
            return "HIGH"

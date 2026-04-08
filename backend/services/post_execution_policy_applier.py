"""
Post-Execution Policy Applier: Masks and redacts results after execution

Applies MASK and REDACT policies to query results.
This is the final defense - hiding sensitive data in the result set.

Examples:
- MASK policy: salary column shows "***" instead of actual values
- REDACT policy: ssn column is completely removed from results
"""

from typing import Dict, List, Any, Optional, Tuple, Set
from backend.services.policy_definition import PolicyDefinition, PolicyType


class PostExecutionPolicyApplier:
    """
    Applies policies to query results after execution.
    Masks sensitive columns, redacts forbidden columns, etc.
    """
    
    def apply_policies(
        self,
        results: List[Dict[str, Any]],
        policies: List[PolicyDefinition]
    ) -> Tuple[List[Dict[str, Any]], List[str]]:
        """
        Apply all applicable post-execution policies to results.
        
        Args:
            results: Query result rows as list of dicts
            policies: Applicable policies
        
        Returns:
            (transformed_results, effects_applied)
        """
        if not results:
            return results, []
        
        effects = []
        current_results = results
        
        # Get columns to redact (completely remove)
        redacted_columns = set()
        for policy in policies:
            if policy.type == PolicyType.REDACT and policy.action.redact:
                if policy.condition.column:
                    redacted_columns.add(policy.condition.column)
        
        if redacted_columns:
            current_results = self._redact_columns(current_results, redacted_columns)
            effects.append(f"redacted_columns:{len(redacted_columns)}")
        
        # Get columns to mask (replace with ***)
        masked_columns = {}
        for policy in policies:
            if policy.type == PolicyType.MASK and policy.action.mask:
                if policy.condition.column:
                    masked_columns[policy.condition.column] = (
                        policy.action.mask_char,
                        policy.action.mask_length
                    )
        
        if masked_columns:
            current_results = self._mask_columns(current_results, masked_columns)
            effects.append(f"masked_columns:{len(masked_columns)}")
        
        return current_results, effects
    
    def _redact_columns(
        self,
        results: List[Dict[str, Any]],
        columns_to_redact: Set[str]
    ) -> List[Dict[str, Any]]:
        """
        Remove specified columns from all result rows.
        
        Args:
            results: Query results
            columns_to_redact: Set of column names to completely remove
        
        Returns:
            Results with specified columns removed
        """
        redacted_results = []
        
        for row in results:
            redacted_row = {}
            for key, value in row.items():
                if key.lower() not in {c.lower() for c in columns_to_redact}:
                    redacted_row[key] = value
            redacted_results.append(redacted_row)
        
        return redacted_results
    
    def _mask_columns(
        self,
        results: List[Dict[str, Any]],
        columns_to_mask: Dict[str, Tuple[str, int]]
    ) -> List[Dict[str, Any]]:
        """
        Mask specified columns with replacement characters.
        
        Args:
            results: Query results
            columns_to_mask: Dict of column_name -> (mask_char, length)
                           e.g., {"salary": ("*", 3)} → "***"
        
        Returns:
            Results with specified columns masked
        """
        masked_results = []
        
        # Build case-insensitive lookup
        mask_lookup = {k.lower(): v for k, v in columns_to_mask.items()}
        
        for row in results:
            masked_row = {}
            for key, value in row.items():
                if key.lower() in mask_lookup:
                    char, length = mask_lookup[key.lower()]
                    masked_row[key] = self._create_mask(char, length)
                else:
                    masked_row[key] = value
            masked_results.append(masked_row)
        
        return masked_results
    
    @staticmethod
    def _create_mask(mask_char: str = "*", length: int = 3) -> str:
        """Create mask string"""
        return mask_char * length
    
    def mask_value(self, value: Any, mask_char: str = "*", mask_length: int = 3) -> str:
        """Mask a single value"""
        return mask_char * mask_length
    
    def apply_column_level_policies(
        self,
        results: List[Dict[str, Any]],
        column_policies: Dict[str, List[PolicyDefinition]]
    ) -> List[Dict[str, Any]]:
        """
        Apply policies at column level.
        
        Args:
            results: Query results
            column_policies: Dict of column_name -> [policies]
        
        Returns:
            Masked/redacted results
        """
        if not column_policies:
            return results
        
        masked_results = []
        
        for row in results:
            masked_row = dict(row)
            
            for column, policies in column_policies.items():
                if column not in masked_row:
                    continue
                
                for policy in policies:
                    if policy.type == PolicyType.REDACT and policy.action.redact:
                        # Remove column
                        masked_row.pop(column, None)
                        break
                    elif policy.type == PolicyType.MASK and policy.action.mask:
                        # Mask value
                        masked_row[column] = self._create_mask(
                            policy.action.mask_char,
                            policy.action.mask_length
                        )
            
            masked_results.append(masked_row)
        
        return masked_results
    
    def redact_all_sensitive_columns(
        self,
        results: List[Dict[str, Any]],
        sensitive_columns: Set[str]
    ) -> List[Dict[str, Any]]:
        """
        Redact all sensitive columns (complete removal).
        
        Useful for "safe mode" where all PII/sensitive data is removed.
        """
        return self._redact_columns(results, sensitive_columns)
    
    def mask_all_sensitive_columns(
        self,
        results: List[Dict[str, Any]],
        sensitive_columns: Set[str],
        mask_char: str = "*",
        mask_length: int = 3
    ) -> List[Dict[str, Any]]:
        """
        Mask all sensitive columns.
        
        Useful for "blurred mode" where sensitive data is visible but obscured.
        """
        mask_dict = {col: (mask_char, mask_length) for col in sensitive_columns}
        return self._mask_columns(results, mask_dict)
    
    def get_safe_columns(
        self,
        results: List[Dict[str, Any]],
        redacted_columns: Set[str],
        masked_columns: Set[str]
    ) -> List[str]:
        """
        Get list of columns that are fully visible (not masked/redacted).
        
        Useful for client-side rendering decisions.
        """
        if not results:
            return []
        
        first_row = results[0]
        safe_columns = []
        
        for column in first_row.keys():
            col_lower = column.lower()
            if col_lower not in {c.lower() for c in redacted_columns}:
                if col_lower not in {c.lower() for c in masked_columns}:
                    safe_columns.append(column)
        
        return safe_columns


class ResultMetadata:
    """
    Metadata about applied policies for client awareness.
    Helps client understand which columns are masked/redacted.
    """
    
    def __init__(self):
        self.masked_columns: Dict[str, str] = {}  # column -> mask_char
        self.redacted_columns: Set[str] = set()
        self.policies_applied: List[str] = []
        self.warnings: List[str] = []
    
    def add_mask(self, column: str, mask_char: str) -> None:
        """Record that column was masked"""
        self.masked_columns[column] = mask_char
    
    def add_redact(self, column: str) -> None:
        """Record that column was redacted"""
        self.redacted_columns.add(column)
    
    def add_policy(self, policy_name: str) -> None:
        """Record that policy was applied"""
        self.policies_applied.append(policy_name)
    
    def add_warning(self, warning: str) -> None:
        """Add warning message"""
        self.warnings.append(warning)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dict for API response"""
        return {
            "masked_columns": self.masked_columns,
            "redacted_columns": list(self.redacted_columns),
            "policies_applied": self.policies_applied,
            "warnings": self.warnings
        }

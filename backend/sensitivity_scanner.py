"""
Data Sensitivity Scanner for VoxCore

Automatically detects sensitive columns in database schemas and categorizes them
for policy generation and data protection.

Author: VoxCore
Date: March 2026
"""

import re
from typing import Dict, List, Set
from dataclasses import dataclass, asdict
from datetime import datetime


@dataclass
class SensitiveColumn:
    """Represents a detected sensitive column"""
    table_name: str
    column_name: str
    sensitivity_type: str  # pii, secret, financial, health, public
    confidence: float  # 0.0 to 1.0
    detected_patterns: List[str]  # Patterns that matched

    def to_dict(self):
        return asdict(self)


class SensitivityScanner:
    """
    Detects sensitive data columns in database schemas.
    
    Sensitivity categories:
    - SECRET: Passwords, API keys, tokens
    - PII: Personally Identifiable Information
    - FINANCIAL: Credit cards, bank accounts, transactions
    - HEALTH: Medical records, health conditions
    - PUBLIC: Non-sensitive public data
    """

    # Pattern definitions for column name matching
    SENSITIVE_PATTERNS = {
        # SECRETS
        "password": ("secret", 0.95),
        "passwd": ("secret", 0.95),
        "pwd": ("secret", 0.90),
        "token": ("secret", 0.85),
        "api.key": ("secret", 0.95),
        "apikey": ("secret", 0.95),
        "api_key": ("secret", 0.95),
        "secret": ("secret", 0.95),
        "access_token": ("secret", 0.95),
        "refresh_token": ("secret", 0.95),
        "auth_token": ("secret", 0.95),
        "private_key": ("secret", 0.95),
        "encryption_key": ("secret", 0.90),
        "client_secret": ("secret", 0.95),

        # PII
        "email": ("pii", 0.95),
        "phone": ("pii", 0.90),
        "phone_number": ("pii", 0.95),
        "telephone": ("pii", 0.90),
        "ssn": ("pii", 0.95),
        "social_security": ("pii", 0.95),
        "social_security_number": ("pii", 0.95),
        "license": ("pii", 0.85),
        "driver_license": ("pii", 0.95),
        "passport": ("pii", 0.90),
        "date_of_birth": ("pii", 0.95),
        "dob": ("pii", 0.90),
        "birthdate": ("pii", 0.90),
        "gender": ("pii", 0.70),
        "address_line": ("pii", 0.90),
        "address": ("pii", 0.85),
        "city": ("pii", 0.70),
        "state": ("pii", 0.70),
        "postal_code": ("pii", 0.80),
        "zip_code": ("pii", 0.85),
        "zip": ("pii", 0.80),
        "country": ("pii", 0.60),

        # FINANCIAL
        "card_number": ("financial", 0.95),
        "card_no": ("financial", 0.95),
        "cardno": ("financial", 0.95),
        "credit_card": ("financial", 0.95),
        "creditcard": ("financial", 0.95),
        "cc_number": ("financial", 0.95),
        "ccn": ("financial", 0.95),
        "cvv": ("financial", 0.95),
        "cvc": ("financial", 0.90),
        "expiry_date": ("financial", 0.85),
        "expiration_date": ("financial", 0.90),
        "bank_account": ("financial", 0.95),
        "account_number": ("financial", 0.95),
        "account_no": ("financial", 0.90),
        "routing_number": ("financial", 0.95),
        "iban": ("financial", 0.95),
        "swift": ("financial", 0.85),
        "bic": ("financial", 0.85),
        "balance": ("financial", 0.75),
        "transaction": ("financial", 0.70),

        # HEALTH
        "health_condition": ("health", 0.95),
        "medical_record": ("health", 0.95),
        "health_data": ("health", 0.95),
        "prescription": ("health", 0.95),
        "medication": ("health", 0.90),
        "diagnosis": ("health", 0.95),
        "allergy": ("health", 0.90),
        "blood_type": ("health", 0.85),
        "vaccine": ("health", 0.85),
    }

    # Table name patterns that suggest sensitive data
    SENSITIVE_TABLE_PATTERNS = {
        "password": ("secret", 0.95),
        "token": ("secret", 0.90),
        "secret": ("secret", 0.95),
        "credential": ("secret", 0.90),
        "auth": ("secret", 0.80),
        "user": ("pii", 0.70),  # Often contains PII
        "profile": ("pii", 0.70),
        "contact": ("pii", 0.80),
        "address": ("pii", 0.80),
        "payment": ("financial", 0.85),
        "transaction": ("financial", 0.80),
        "invoice": ("financial", 0.75),
        "health": ("health", 0.90),
        "medical": ("health", 0.90),
        "patient": ("health", 0.80),
    }

    def __init__(self):
        """Initialize the scanner"""
        self.findings: List[SensitiveColumn] = []
        self.scan_timestamp = None

    def scan_schema(self, schema_info: List[Dict]) -> Dict:
        """
        Scan a database schema for sensitive data.
        
        Args:
            schema_info: List of dicts with 'table_name' and 'columns' keys
                        Example: [{"table_name": "users", "columns": ["id", "email", "password"]}, ...]
        
        Returns:
            Dictionary with scan results organized by sensitivity type
        """
        self.findings = []
        self.scan_timestamp = datetime.utcnow().isoformat()

        for table_info in schema_info:
            table_name = table_info.get("table_name", "")
            columns = table_info.get("columns", [])

            for column_name in columns:
                self._analyze_column(table_name, column_name)

        return self._compile_report()

    def _analyze_column(self, table_name: str, column_name: str) -> None:
        """
        Analyze a single column for sensitivity indicators.
        
        Args:
            table_name: Name of the table
            column_name: Name of the column
        """
        column_lower = column_name.lower()
        table_lower = table_name.lower()

        # Check column name patterns
        column_matches = self._match_patterns(column_lower, self.SENSITIVE_PATTERNS)

        # Check table name patterns
        table_matches = self._match_patterns(table_lower, self.SENSITIVE_TABLE_PATTERNS)

        # Combine findings
        all_matches = {}
        for sensitivity_type, (category, confidence) in column_matches.items():
            all_matches[sensitivity_type] = (category, confidence)

        for sensitivity_type, (category, confidence) in table_matches.items():
            # Team table patterns are weighted less with column patterns
            if sensitivity_type not in all_matches:
                all_matches[sensitivity_type] = (category, confidence * 0.6)

        # Create findings for detected sensitivities
        if all_matches:
            for sensitivity_type, (category, confidence) in all_matches.items():
                patterns = [k for k in self.SENSITIVE_PATTERNS if k in column_lower]
                patterns.extend([k for k in self.SENSITIVE_TABLE_PATTERNS if k in table_lower])

                finding = SensitiveColumn(
                    table_name=table_name,
                    column_name=column_name,
                    sensitivity_type=category,
                    confidence=min(confidence, 1.0),
                    detected_patterns=list(set(patterns)),
                )
                self.findings.append(finding)

    def _match_patterns(
        self, text: str, patterns: Dict[str, tuple]
    ) -> Dict[str, tuple]:
        """
        Match text against pattern dictionary.
        
        Args:
            text: Text to match against
            patterns: Dictionary of {pattern: (category, confidence)}
        
        Returns:
            Dictionary of matched patterns with their categories and confidences
        """
        matches = {}

        for pattern, (category, confidence) in patterns.items():
            if self._pattern_matches(pattern, text):
                if category not in matches:
                    matches[category] = (category, 0.0)
                # Use the highest confidence for each category
                _, existing_conf = matches[category]
                if confidence > existing_conf:
                    matches[category] = (category, confidence)

        return matches

    def _pattern_matches(self, pattern: str, text: str) -> bool:
        """
        Check if pattern matches text (word-boundary aware).
        
        Args:
            pattern: Pattern to match
            text: Text to search in
        
        Returns:
            True if pattern matches as a whole word
        """
        # Match as whole word or with underscores/lowercase boundaries
        regex = rf"(?:^|[_]){re.escape(pattern)}(?:[_]|$)"
        return bool(re.search(regex, text))

    def _compile_report(self) -> Dict:
        """
        Compile findings into a structured report.
        
        Returns:
            Dictionary organized by sensitivity type
        """
        report = {
            "timestamp": self.scan_timestamp,
            "total_findings": len(self.findings),
            "by_type": {
                "secret": [],
                "pii": [],
                "financial": [],
                "health": [],
            },
            "by_table": {},
            "risk_summary": {
                "critical": 0,  # SECRET columns
                "high": 0,  # PII + FINANCIAL
                "medium": 0,  # HEALTH
            },
        }

        for finding in self.findings:
            # Organize by type
            sensitivity_type = finding.sensitivity_type
            if sensitivity_type in report["by_type"]:
                report["by_type"][sensitivity_type].append(finding.to_dict())

            # Organize by table
            if finding.table_name not in report["by_table"]:
                report["by_table"][finding.table_name] = []
            report["by_table"][finding.table_name].append(finding.to_dict())

            # Risk summary
            if sensitivity_type == "secret":
                report["risk_summary"]["critical"] += 1
            elif sensitivity_type in ("pii", "financial"):
                report["risk_summary"]["high"] += 1
            elif sensitivity_type == "health":
                report["risk_summary"]["medium"] += 1

        # Sort by confidence (highest first)
        for sensitivity_type in report["by_type"]:
            report["by_type"][sensitivity_type].sort(
                key=lambda x: x["confidence"], reverse=True
            )

        for table_name in report["by_table"]:
            report["by_table"][table_name].sort(
                key=lambda x: x["confidence"], reverse=True
            )

        return report

    def get_high_confidence_findings(self, min_confidence: float = 0.80) -> List[SensitiveColumn]:
        """
        Get findings with high confidence (>= min_confidence).
        
        Args:
            min_confidence: Minimum confidence threshold (0.0 to 1.0)
        
        Returns:
            List of high-confidence findings
        """
        return [f for f in self.findings if f.confidence >= min_confidence]

    def get_findings_by_type(self, sensitivity_type: str) -> List[SensitiveColumn]:
        """
        Get all findings of a specific sensitivity type.
        
        Args:
            sensitivity_type: Type of sensitivity (secret, pii, financial, health)
        
        Returns:
            List of findings matching the type
        """
        return [f for f in self.findings if f.sensitivity_type == sensitivity_type]

    def get_findings_by_table(self, table_name: str) -> List[SensitiveColumn]:
        """
        Get all findings for a specific table.
        
        Args:
            table_name: Name of the table
        
        Returns:
            List of findings for the table
        """
        return [f for f in self.findings if f.table_name == table_name]

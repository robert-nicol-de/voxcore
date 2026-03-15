# Query Guardian: SQL Safety and Governance Layer for VoxCore
import re

DANGEROUS_SQL_PATTERNS = [
    r"\\bDROP\\b",
    r"\\bDELETE\\b",
    r"\\bTRUNCATE\\b",
    r"\\bALTER\\b",
]

class QueryGuardian:
    @staticmethod
    def validate(sql: str) -> bool:
        """Return True if SQL is safe, False if blocked."""
        for pattern in DANGEROUS_SQL_PATTERNS:
            if re.search(pattern, sql, re.IGNORECASE):
                return False
        # Add more checks: unfiltered scans, huge result sets, etc.
        return True

    @staticmethod
    def explain_block(sql: str) -> str:
        for pattern in DANGEROUS_SQL_PATTERNS:
            if re.search(pattern, sql, re.IGNORECASE):
                return f"Blocked dangerous SQL pattern: {pattern}"
        return "Query blocked for safety."

from enum import Enum
from typing import Any, Dict, Optional
from pydantic import BaseModel

class ErrorType(str, Enum):
    SQL_SYNTAX_ERROR = "SQL_SYNTAX_ERROR"
    MISSING_TABLE = "MISSING_TABLE"
    MISSING_COLUMN = "MISSING_COLUMN"
    SEMANTIC_MISMATCH = "SEMANTIC_MISMATCH"
    EMPTY_RESULT = "EMPTY_RESULT"
    TIMEOUT = "TIMEOUT"
    HIGH_COST = "HIGH_COST"
    HALLUCINATED_FIELD = "HALLUCINATED_FIELD"

class SuggestedAction(str, Enum):
    RETRY = "RETRY"
    CLARIFY = "CLARIFY"
    FALLBACK = "FALLBACK"
    BLOCK = "BLOCK"

class ErrorDetectionInput(BaseModel):
    query: str
    semantic_plan: Dict[str, Any]
    result: Optional[Any] = None
    execution_metadata: Optional[Dict[str, Any]] = None

class ErrorDetectionOutput(BaseModel):
    error_detected: bool
    error_type: Optional[ErrorType] = None
    error_details: Optional[Dict[str, Any]] = None
    suggested_action: Optional[SuggestedAction] = None
    raw_error: Optional[str] = None

class ErrorDetectionLayer:
    def detect(self, input: ErrorDetectionInput) -> ErrorDetectionOutput:
        """
        Basic error detection logic for demonstration.
        Detects SQL syntax errors, missing tables/columns, and empty results.
        """
        sql = input.query or ""
        plan = input.semantic_plan or {}
        # Simulate detection
        if not sql.strip():
            return ErrorDetectionOutput(
                error_detected=True,
                error_type=ErrorType.SQL_SYNTAX_ERROR,
                error_details={"reason": "Empty SQL"},
                suggested_action=SuggestedAction.RETRY,
                raw_error="SQL is empty."
            )
        if "SELECT" not in sql.upper():
            return ErrorDetectionOutput(
                error_detected=True,
                error_type=ErrorType.SQL_SYNTAX_ERROR,
                error_details={"reason": "No SELECT statement"},
                suggested_action=SuggestedAction.RETRY,
                raw_error="No SELECT in SQL."
            )
        if "nonexistent_table" in sql:
            return ErrorDetectionOutput(
                error_detected=True,
                error_type=ErrorType.MISSING_TABLE,
                error_details={"table": "nonexistent_table"},
                suggested_action=SuggestedAction.CLARIFY,
                raw_error="Table does not exist."
            )
        # Simulate empty result
        if input.result == []:
            return ErrorDetectionOutput(
                error_detected=True,
                error_type=ErrorType.EMPTY_RESULT,
                error_details={"reason": "No data returned"},
                suggested_action=SuggestedAction.FALLBACK,
                raw_error="Empty result set."
            )
        # No error detected
        return ErrorDetectionOutput(error_detected=False)
        raise NotImplementedError

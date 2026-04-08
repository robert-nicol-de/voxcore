from enum import Enum
from typing import Any, Dict, Optional
from pydantic import BaseModel

class FallbackMode(str, Enum):
    FULL_ANSWER = "full_answer"
    PARTIAL_ANSWER = "partial_answer"
    SUMMARY = "summary"
    EXPLANATION = "explanation"

class FallbackInput(BaseModel):
    semantic_plan: Dict[str, Any]
    error_report: Dict[str, Any]
    retry_context: Optional[Dict[str, Any]] = None
    clarification_context: Optional[Dict[str, Any]] = None

class FallbackOutput(BaseModel):
    fallback_mode: FallbackMode
    fallback_result: Any
    fallback_details: Optional[Dict[str, Any]] = None
    log_entry: Optional[Dict[str, Any]] = None

class FallbackManager:
    def fallback(self, input: FallbackInput) -> FallbackOutput:
        """
        Basic fallback: if empty result, return summary message.
        """
        error_type = input.error_report.get("error_type")
        if error_type == "EMPTY_RESULT":
            return FallbackOutput(
                fallback_mode=FallbackMode.SUMMARY,
                fallback_result="No data available for your query. Showing summary only.",
                fallback_details={"reason": "empty_result"},
                log_entry={"fallback": "summary"}
            )
        return FallbackOutput(
            fallback_mode=FallbackMode.EXPLANATION,
            fallback_result="Unable to provide a result due to an unknown error.",
            fallback_details={"reason": "unknown"},
            log_entry={"fallback": "explanation"}
        )

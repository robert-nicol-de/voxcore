from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel

class ClarificationType(str, Enum):
    MISSING_FILTER = "missing_filter"
    AMBIGUOUS_INTENT = "ambiguous_intent"
    CONFLICTING_INTENT = "conflicting_intent"
    OTHER = "other"

class ClarificationContext(BaseModel):
    previous_clarifications: Optional[List[Dict[str, Any]]] = None
    user_profile: Optional[Dict[str, Any]] = None

class ClarificationInput(BaseModel):
    semantic_plan: Dict[str, Any]
    error_report: Dict[str, Any]
    clarification_context: Optional[ClarificationContext] = None

class ClarificationOutput(BaseModel):
    clarification_needed: bool
    clarification_prompt: Optional[str] = None
    clarification_type: Optional[ClarificationType] = None
    clarification_options: Optional[List[str]] = None
    updated_semantic_plan: Optional[Dict[str, Any]] = None
    log_entry: Optional[Dict[str, Any]] = None

class ClarificationSystem:
    def clarify(self, input: ClarificationInput) -> ClarificationOutput:
        """
        Basic clarification: if missing table, ask user to clarify table.
        """
        error_type = input.error_report.get("error_type")
        if error_type == "MISSING_TABLE":
            return ClarificationOutput(
                clarification_needed=True,
                clarification_prompt="The table referenced does not exist. Please select a valid table.",
                clarification_type=ClarificationType.MISSING_FILTER,
                clarification_options=["customers", "orders", "products"],
                log_entry={"clarification": "missing_table"}
            )
        return ClarificationOutput(clarification_needed=False)

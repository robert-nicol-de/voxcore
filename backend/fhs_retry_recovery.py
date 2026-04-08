from enum import Enum
from typing import Any, Dict, Optional
from pydantic import BaseModel

class RecoveryStrategy(str, Enum):
    REGENERATE = "regenerate"
    SIMPLIFY = "simplify"
    SWITCH_METRIC = "switch_metric"
    USE_FALLBACK = "use_fallback"
    SAFE_DEFAULT = "safe_default"

class RetryContext(BaseModel):
    attempts: int = 0
    previous_queries: Optional[list] = None
    previous_strategies: Optional[list] = None
    last_error: Optional[Dict[str, Any]] = None

class RetryRecoveryInput(BaseModel):
    original_query: str
    semantic_plan: Dict[str, Any]
    error_report: Dict[str, Any]
    retry_context: Optional[RetryContext] = None

class RetryRecoveryOutput(BaseModel):
    recovered: bool
    final_query: Optional[str] = None
    recovery_strategy: Optional[RecoveryStrategy] = None
    recovery_details: Optional[Dict[str, Any]] = None
    escalate: bool = False
    log_entry: Optional[Dict[str, Any]] = None

class RetryRecoveryEngine:
    def recover(self, input: RetryRecoveryInput) -> RetryRecoveryOutput:
        """
        Basic retry logic: if SQL error, try to add SELECT * FROM fallback.
        """
        attempts = input.retry_context.attempts if input.retry_context else 1
        if attempts == 1 and input.error_report.get("error_type") == "SQL_SYNTAX_ERROR":
            # Simulate retry by returning a valid SQL
            return RetryRecoveryOutput(
                recovered=True,
                final_query="SELECT * FROM fallback_table LIMIT 1",
                recovery_strategy=RecoveryStrategy.REGENERATE,
                recovery_details={"note": "Fallback to default table."},
                escalate=False,
                log_entry={"attempts": attempts}
            )
        return RetryRecoveryOutput(
            recovered=False,
            recovery_strategy=RecoveryStrategy.SAFE_DEFAULT,
            escalate=True,
            log_entry={"attempts": attempts}
        )

"""
STEP 10 — Observability: Structured Logging System

JSON-based logging with context propagation and correlation IDs.
Every query, error, and event is logged with full metadata for debugging and auditing.
"""

import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional
from contextvars import ContextVar
import traceback
import sys


# Context variables for request/query correlation
correlation_id: ContextVar[str] = ContextVar("correlation_id", default="")
org_id_ctx: ContextVar[str] = ContextVar("org_id", default="")
user_id_ctx: ContextVar[str] = ContextVar("user_id", default="")
session_id_ctx: ContextVar[str] = ContextVar("session_id", default="")


class StructuredLogger:
    """
    JSON-based structured logging with context propagation.
    
    Each log entry includes:
    - timestamp: ISO 8601 timestamp
    - level: DEBUG, INFO, WARNING, ERROR, CRITICAL
    - message: Human-readable message
    - correlation_id: Unique ID for tracing requests
    - org_id: Organization ID (multi-tenant)
    - user_id: User ID (audit trail)
    - session_id: Session ID (conversation context)
    - metadata: Additional structured data
    - stack_trace: (for errors)
    """
    
    def __init__(self, name: str, level: str = "INFO"):
        self.name = name
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)
        
        # JSON formatter
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(JSONFormatter())
        self.logger.addHandler(handler)
    
    def _get_context(self) -> Dict[str, Any]:
        """Get current context (correlation ID, org, user, session)"""
        return {
            "correlation_id": correlation_id.get(),
            "org_id": org_id_ctx.get(),
            "user_id": user_id_ctx.get(),
            "session_id": session_id_ctx.get()
        }
    
    def _build_log_entry(
        self,
        level: str,
        message: str,
        metadata: Optional[Dict[str, Any]] = None,
        exception: Optional[Exception] = None
    ) -> Dict[str, Any]:
        """Build structured log entry"""
        entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": level,
            "logger": self.name,
            "message": message,
            **self._get_context(),
            "metadata": metadata or {},
        }
        
        # Add exception details if present
        if exception:
            entry["exception"] = {
                "type": type(exception).__name__,
                "message": str(exception),
                "traceback": traceback.format_exc()
            }
        
        return entry
    
    def debug(self, message: str, **metadata):
        """Log debug message"""
        entry = self._build_log_entry("DEBUG", message, metadata)
        self.logger.debug(json.dumps(entry))
    
    def info(self, message: str, **metadata):
        """Log info message"""
        entry = self._build_log_entry("INFO", message, metadata)
        self.logger.info(json.dumps(entry))
    
    def warning(self, message: str, **metadata):
        """Log warning message"""
        entry = self._build_log_entry("WARNING", message, metadata)
        self.logger.warning(json.dumps(entry))
    
    def error(self, message: str, exception: Optional[Exception] = None, **metadata):
        """Log error message"""
        entry = self._build_log_entry("ERROR", message, metadata, exception)
        self.logger.error(json.dumps(entry))
    
    def critical(self, message: str, exception: Optional[Exception] = None, **metadata):
        """Log critical message"""
        entry = self._build_log_entry("CRITICAL", message, metadata, exception)
        self.logger.critical(json.dumps(entry))


class JSONFormatter(logging.Formatter):
    """
    Formatter that outputs JSON.
    Used by StructuredLogger for consistent formatting.
    """
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON string"""
        # The message is already JSON from StructuredLogger
        return record.getMessage()


class QueryLogger(StructuredLogger):
    """
    Specialized logger for query execution events.
    Tracks query lifecycle: submission → execution → results → completion/error.
    """
    
    def __init__(self):
        super().__init__("query")
    
    def query_submitted(
        self,
        query_id: str,
        sql: str,
        org_id: str,
        user_id: str,
        user_role: str,
        **metadata
    ):
        """Log when query is submitted"""
        self.info(
            "Query submitted",
            query_id=query_id,
            sql=sql[:100],  # First 100 chars
            org_id=org_id,
            user_id=user_id,
            user_role=user_role,
            **metadata
        )
    
    def query_started_execution(
        self,
        query_id: str,
        sql: str,
        **metadata
    ):
        """Log when query execution starts"""
        self.info(
            "Query execution started",
            query_id=query_id,
            sql=sql[:100],
            **metadata
        )
    
    def query_completed(
        self,
        query_id: str,
        execution_time_ms: float,
        rows_returned: int,
        cost_score: float,
        **metadata
    ):
        """Log when query completes successfully"""
        self.info(
            "Query completed",
            query_id=query_id,
            execution_time_ms=execution_time_ms,
            rows_returned=rows_returned,
            cost_score=cost_score,
            **metadata
        )
    
    def query_failed(
        self,
        query_id: str,
        execution_time_ms: float,
        error: Exception,
        error_message: str,
        **metadata
    ):
        """Log when query fails"""
        self.error(
            "Query execution failed",
            exception=error,
            query_id=query_id,
            execution_time_ms=execution_time_ms,
            error_message=error_message,
            **metadata
        )
    
    def query_cached(
        self,
        query_id: str,
        cache_hit_time_ms: float,
        rows_returned: int,
        cache_key: str,
        **metadata
    ):
        """Log cache hit"""
        self.info(
            "Query served from cache",
            query_id=query_id,
            cache_hit_time_ms=cache_hit_time_ms,
            rows_returned=rows_returned,
            cache_key=cache_key,
            **metadata
        )


class PolicyLogger(StructuredLogger):
    """Specialized logger for policy enforcement events"""
    
    def __init__(self):
        super().__init__("policy")
    
    def policy_evaluated(
        self,
        query_id: str,
        policies_count: int,
        user_role: str,
        **metadata
    ):
        """Log policy evaluation"""
        self.info(
            "Policies evaluated",
            query_id=query_id,
            policies_count=policies_count,
            user_role=user_role,
            **metadata
        )
    
    def policy_applied(
        self,
        query_id: str,
        policy_name: str,
        policy_type: str,
        effect: str,
        **metadata
    ):
        """Log individual policy application"""
        self.info(
            "Policy applied",
            query_id=query_id,
            policy_name=policy_name,
            policy_type=policy_type,
            effect=effect,
            **metadata
        )
    
    def policy_blocked_access(
        self,
        query_id: str,
        user_id: str,
        policy_name: str,
        reason: str,
        **metadata
    ):
        """Log when policy blocks access"""
        self.warning(
            "Access blocked by policy",
            query_id=query_id,
            user_id=user_id,
            policy_name=policy_name,
            reason=reason,
            **metadata
        )


class PerformanceLogger(StructuredLogger):
    """Specialized logger for performance events"""
    
    def __init__(self):
        super().__init__("performance")
    
    def slow_query(
        self,
        query_id: str,
        execution_time_ms: float,
        threshold_ms: float,
        sql: str,
        **metadata
    ):
        """Log slow queries (over threshold)"""
        self.warning(
            "Slow query detected",
            query_id=query_id,
            execution_time_ms=execution_time_ms,
            threshold_ms=threshold_ms,
            sql=sql[:100],
            **metadata
        )
    
    def high_cost_query(
        self,
        query_id: str,
        cost_score: float,
        threshold: float,
        **metadata
    ):
        """Log high-cost queries"""
        self.warning(
            "High cost query detected",
            query_id=query_id,
            cost_score=cost_score,
            threshold=threshold,
            **metadata
        )
    
    def cache_miss(
        self,
        query_id: str,
        cache_key: str,
        **metadata
    ):
        """Log cache misses for analysis"""
        self.debug(
            "Cache miss",
            query_id=query_id,
            cache_key=cache_key,
            **metadata
        )
    
    def cache_hit(
        self,
        query_id: str,
        cache_key: str,
        age_seconds: int,
        **metadata
    ):
        """Log cache hits"""
        self.debug(
            "Cache hit",
            query_id=query_id,
            cache_key=cache_key,
            age_seconds=age_seconds,
            **metadata
        )


class ErrorLogger(StructuredLogger):
    """Specialized logger for error tracking"""
    
    def __init__(self):
        super().__init__("error")
    
    def database_error(
        self,
        query_id: str,
        error: Exception,
        error_message: str,
        sql: str = "",
        **metadata
    ):
        """Log database errors"""
        self.error(
            "Database error",
            exception=error,
            query_id=query_id,
            error_message=error_message,
            sql=sql[:100] if sql else "",
            **metadata
        )
    
    def llm_error(
        self,
        query_id: str,
        error: Exception,
        error_message: str,
        model: str = "",
        **metadata
    ):
        """Log LLM errors"""
        self.error(
            "LLM error",
            exception=error,
            query_id=query_id,
            error_message=error_message,
            model=model,
            **metadata
        )
    
    def validation_error(
        self,
        query_id: str,
        error_message: str,
        validation_type: str,
        **metadata
    ):
        """Log validation errors"""
        self.error(
            "Validation error",
            query_id=query_id,
            error_message=error_message,
            validation_type=validation_type,
            **metadata
        )


# Global logger instances
query_logger = QueryLogger()
policy_logger = PolicyLogger()
performance_logger = PerformanceLogger()
error_logger = ErrorLogger()


def set_correlation_id(corr_id: str):
    """Set correlation ID for current request"""
    correlation_id.set(corr_id)


def set_request_context(org_id: str, user_id: str, session_id: str = ""):
    """Set request context (org, user, session)"""
    org_id_ctx.set(org_id)
    user_id_ctx.set(user_id)
    if session_id:
        session_id_ctx.set(session_id)


def clear_context():
    """Clear context (call at end of request)"""
    correlation_id.set("")
    org_id_ctx.set("")
    user_id_ctx.set("")
    session_id_ctx.set("")

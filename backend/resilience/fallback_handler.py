"""
Fallback Handler — Graceful degradation when services fail

Provides:
- Fallback responses for different failure types
- Fallback chains (try primary, then secondary, etc.)
- LLM fallback messages
- Database fallback responses
- Progressive degradation
"""

from typing import Callable, Any, Optional, List
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class FailureType(Enum):
    """Types of failures"""
    LLM_FAILURE = "llm_failure"
    DATABASE_FAILURE = "database_failure"
    CACHE_FAILURE = "cache_failure"
    TIMEOUT = "timeout"
    RATE_LIMIT = "rate_limit"
    UNKNOWN = "unknown"


class FallbackResponse:
    """A fallback response for when primary operation fails"""
    
    def __init__(
        self,
        type: FailureType,
        message: str,
        data: Optional[Any] = None,
        can_retry: bool = False,
        is_degraded: bool = True
    ):
        self.type = type
        self.message = message
        self.data = data
        self.can_retry = can_retry
        self.is_degraded = is_degraded
    
    def to_dict(self) -> dict:
        """Convert to response dictionary"""
        return {
            "status": "degraded" if self.is_degraded else "error",
            "message": self.message,
            "data": self.data,
            "can_retry": self.can_retry,
            "failure_type": self.type.value
        }


class FallbackHandler:
    """Handle failures with graceful degradation"""
    
    # Default fallback messages
    DEFAULT_MESSAGES = {
        FailureType.LLM_FAILURE: (
            "I couldn't process that safely right now. "
            "The AI service is temporarily unavailable. "
            "Try rephrasing your question or contact support."
        ),
        FailureType.DATABASE_FAILURE: (
            "Database temporarily unavailable. "
            "Please try again in a moment."
        ),
        FailureType.CACHE_FAILURE: (
            "Cache service unavailable. "
            "Queries may be slower than usual."
        ),
        FailureType.TIMEOUT: (
            "Request timed out. "
            "Try with a simpler query or check system status."
        ),
        FailureType.RATE_LIMIT: (
            "Rate limit exceeded. "
            "Please wait a moment before trying again."
        ),
        FailureType.UNKNOWN: (
            "An unexpected error occurred. "
            "Please try again or contact support."
        )
    }
    
    def __init__(self):
        self.custom_messages: dict[FailureType, str] = {}
    
    def set_fallback_message(self, failure_type: FailureType, message: str):
        """Set custom fallback message for failure type"""
        self.custom_messages[failure_type] = message
        logger.info(f"Set fallback message for {failure_type.value}")
    
    def get_fallback_message(self, failure_type: FailureType) -> str:
        """Get fallback message for failure type"""
        if failure_type in self.custom_messages:
            return self.custom_messages[failure_type]
        return self.DEFAULT_MESSAGES.get(failure_type, self.DEFAULT_MESSAGES[FailureType.UNKNOWN])
    
    def create_llm_fallback(self) -> FallbackResponse:
        """Create fallback for LLM failure"""
        return FallbackResponse(
            type=FailureType.LLM_FAILURE,
            message=self.get_fallback_message(FailureType.LLM_FAILURE),
            can_retry=True,
            is_degraded=True
        )
    
    def create_database_fallback(self) -> FallbackResponse:
        """Create fallback for database failure"""
        return FallbackResponse(
            type=FailureType.DATABASE_FAILURE,
            message=self.get_fallback_message(FailureType.DATABASE_FAILURE),
            can_retry=True,
            is_degraded=True
        )
    
    def create_cache_fallback(self) -> FallbackResponse:
        """Create fallback for cache failure"""
        return FallbackResponse(
            type=FailureType.CACHE_FAILURE,
            message=self.get_fallback_message(FailureType.CACHE_FAILURE),
            can_retry=False,
            is_degraded=True
        )
    
    def create_timeout_fallback(self) -> FallbackResponse:
        """Create fallback for timeout"""
        return FallbackResponse(
            type=FailureType.TIMEOUT,
            message=self.get_fallback_message(FailureType.TIMEOUT),
            can_retry=True,
            is_degraded=True
        )
    
    def create_rate_limit_fallback(self) -> FallbackResponse:
        """Create fallback for rate limiting"""
        return FallbackResponse(
            type=FailureType.RATE_LIMIT,
            message=self.get_fallback_message(FailureType.RATE_LIMIT),
            can_retry=True,
            is_degraded=True
        )
    
    def create_error_fallback(
        self,
        error: Exception,
        failure_type: Optional[FailureType] = None
    ) -> FallbackResponse:
        """Create fallback for exception"""
        
        # Determine failure type from exception type
        if failure_type is None:
            failure_type = self._classify_error(error)
        
        return FallbackResponse(
            type=failure_type,
            message=self.get_fallback_message(failure_type),
            can_retry=self._is_retryable(failure_type),
            is_degraded=True
        )
    
    def _classify_error(self, error: Exception) -> FailureType:
        """Classify error type from exception"""
        error_str = str(error).lower()
        error_type = type(error).__name__.lower()
        
        if "timeout" in error_str or "timeout" in error_type:
            return FailureType.TIMEOUT
        elif "rate" in error_str or "quota" in error_str:
            return FailureType.RATE_LIMIT
        elif "database" in error_str or "connection" in error_str or "sql" in error_str:
            return FailureType.DATABASE_FAILURE
        elif "llm" in error_str or "groq" in error_str or "api" in error_str:
            return FailureType.LLM_FAILURE
        elif "cache" in error_str or "redis" in error_str:
            return FailureType.CACHE_FAILURE
        
        return FailureType.UNKNOWN
    
    def _is_retryable(self, failure_type: FailureType) -> bool:
        """Check if failure is retryable"""
        return failure_type in [
            FailureType.TIMEOUT,
            FailureType.RATE_LIMIT,
            FailureType.LLM_FAILURE,
            FailureType.DATABASE_FAILURE
        ]


class FallbackChain:
    """Chain multiple fallback strategies"""
    
    def __init__(self, fallbacks: List[Callable[[], Any]]):
        """
        Args:
            fallbacks: List of fallback functions, tried in order
        """
        self.fallbacks = fallbacks
        self.attempts = []
    
    def execute(self) -> Any:
        """Try fallbacks in order until one succeeds"""
        
        for i, fallback in enumerate(self.fallbacks):
            try:
                logger.info(f"Trying fallback {i + 1}/{len(self.fallbacks)}")
                result = fallback()
                logger.info(f"Fallback {i + 1} succeeded")
                return result
            
            except Exception as e:
                logger.warning(
                    f"Fallback {i + 1} failed: {str(e)}. "
                    f"Trying next fallback..."
                )
                self.attempts.append({
                    "fallback_index": i,
                    "error": str(e)
                })
        
        # All fallbacks exhausted
        logger.error("All fallbacks exhausted")
        raise RuntimeError("All fallback strategies failed")
    
    async def execute_async(self) -> Any:
        """Try async fallbacks in order until one succeeds"""
        
        for i, fallback in enumerate(self.fallbacks):
            try:
                logger.info(f"Trying fallback {i + 1}/{len(self.fallbacks)}")
                
                import asyncio
                if asyncio.iscoroutinefunction(fallback):
                    result = await fallback()
                else:
                    result = fallback()
                
                logger.info(f"Fallback {i + 1} succeeded")
                return result
            
            except Exception as e:
                logger.warning(
                    f"Fallback {i + 1} failed: {str(e)}. "
                    f"Trying next fallback..."
                )
                self.attempts.append({
                    "fallback_index": i,
                    "error": str(e)
                })
        
        # All fallbacks exhausted
        logger.error("All fallbacks exhausted")
        raise RuntimeError("All fallback strategies failed")


# Global fallback handler
_fallback_handler = FallbackHandler()


def get_fallback_handler() -> FallbackHandler:
    """Get global fallback handler"""
    return _fallback_handler


def set_custom_fallback_message(failure_type: FailureType, message: str):
    """Set custom fallback message"""
    _fallback_handler.set_fallback_message(failure_type, message)

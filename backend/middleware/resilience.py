"""
Resilience Middleware — Integrate retry, circuit breaker, and fallback into FastAPI

Provides:
- Automatic retry on transient failures
- Circuit breaker protection for downstream services
- Graceful fallback responses
- Error aggregation and monitoring
"""

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from datetime import datetime
import logging
from typing import Callable, Optional

from backend.resilience.retry_handler import AsyncRetryHandler, RetryConfig
from backend.resilience.circuit_breaker import get_registry, CircuitBreakerOpenError
from backend.resilience.fallback_handler import (
    get_fallback_handler, FailureType, FallbackResponse
)
from backend.observability.structured_logger import error_logger

logger = logging.getLogger(__name__)


class ResilienceContext:
    """Context for tracking resilience during request"""
    
    def __init__(self, request_id: str):
        self.request_id = request_id
        self.retries_attempted = 0
        self.circuit_breaker_triggered = False
        self.fallback_used = False
        self.errors = []
        self.start_time = datetime.utcnow()
    
    def add_error(self, error: Exception, context: str = ""):
        """Track error"""
        self.errors.append({
            "error": str(error),
            "type": type(error).__name__,
            "context": context,
            "timestamp": datetime.utcnow().isoformat()
        })


class ResilienceMiddleware(BaseHTTPMiddleware):
    """Middleware for resilience pattern application"""
    
    def __init__(self, app, enable_retry: bool = True, enable_circuit_breaker: bool = True):
        super().__init__(app)
        self.enable_retry = enable_retry
        self.enable_circuit_breaker = enable_circuit_breaker
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request with resilience patterns"""
        
        request_id = request.headers.get("x-request-id", "unknown")
        context = ResilienceContext(request_id)
        
        try:
            # Check circuit breakers
            if self.enable_circuit_breaker:
                self._check_circuit_breakers()
            
            # Execute with retry if enabled
            if self.enable_retry:
                response = await self._execute_with_retry(call_next, request, context)
            else:
                response = await call_next(request)
            
            return response
        
        except CircuitBreakerOpenError as e:
            context.circuit_breaker_triggered = True
            logger.warning(f"Circuit breaker open: {str(e)}")
            return self._create_degraded_response(context, e)
        
        except Exception as e:
            logger.error(f"Request failed: {str(e)}", exc_info=True)
            context.add_error(e, "request_processing")
            return self._create_error_response(context, e)
    
    async def _execute_with_retry(
        self,
        call_next: Callable,
        request: Request,
        context: ResilienceContext
    ) -> Response:
        """Execute request with retry logic"""
        
        retry_config = RetryConfig(
            max_attempts=3,
            initial_delay_ms=100,
            jitter=True,
            retryable_exceptions=(Exception,)
        )
        handler = AsyncRetryHandler(retry_config)
        
        async def execute():
            return await call_next(request)
        
        try:
            response = await handler.execute(execute)
            context.retries_attempted = len(handler.attempts)
            return response
        
        except Exception as e:
            context.retries_attempted = len(handler.attempts)
            raise
    
    def _check_circuit_breakers(self):
        """Check if any critical circuit breakers are open"""
        registry = get_registry()
        
        # Check if database circuit breaker is open
        db_breaker = registry.get("database")
        if db_breaker and db_breaker.is_open():
            raise CircuitBreakerOpenError("Database circuit breaker is open")
        
        # Check if LLM circuit breaker is open
        llm_breaker = registry.get("llm")
        if llm_breaker and llm_breaker.is_open():
            # LLM failure is not critical, just log it
            logger.warning("LLM circuit breaker is open")
    
    def _create_degraded_response(
        self,
        context: ResilienceContext,
        error: Exception
    ) -> Response:
        """Create degraded response"""
        
        fallback_handler = get_fallback_handler()
        fallback = fallback_handler.create_database_fallback()
        
        context.fallback_used = True
        
        return Response(
            content=fallback.to_dict(),
            status_code=503,  # Service Unavailable
            media_type="application/json"
        )
    
    def _create_error_response(
        self,
        context: ResilienceContext,
        error: Exception
    ) -> Response:
        """Create error response"""
        
        fallback_handler = get_fallback_handler()
        fallback = fallback_handler.create_error_fallback(error)
        
        context.fallback_used = True
        
        return Response(
            content=fallback.to_dict(),
            status_code=500,
            media_type="application/json"
        )


class QueryResilienceHandler:
    """Handles resilience for query execution"""
    
    def __init__(self):
        self.retry_handler = AsyncRetryHandler(RetryConfig(
            max_attempts=3,
            initial_delay_ms=100,
            max_delay_ms=2000
        ))
        self.fallback_handler = get_fallback_handler()
    
    async def execute_query_with_resilience(
        self,
        query_func,
        query_id: str,
        org_id: str,
        user_id: str,
        *args,
        **kwargs
    ):
        """Execute query with full resilience protection"""
        
        from backend.resilience.circuit_breaker import get_database_breaker
        
        db_breaker = get_database_breaker()
        
        try:
            # Check if database is available
            if db_breaker.is_open():
                raise CircuitBreakerOpenError("Database circuit breaker is open")
            
            # Try to execute with retries
            result = await self.retry_handler.execute(
                query_func,
                query_id=query_id,
                org_id=org_id,
                user_id=user_id,
                *args,
                **kwargs
            )
            
            # Record success
            db_breaker.record_success()
            return result
        
        except CircuitBreakerOpenError:
            db_breaker.record_failure()
            logger.error(f"Database circuit breaker open for query {query_id}")
            
            # Return fallback
            fallback = self.fallback_handler.create_database_fallback()
            return {
                "status": "degraded",
                "message": fallback.message,
                "query_id": query_id,
                "can_retry": fallback.can_retry
            }
        
        except Exception as e:
            db_breaker.record_failure()
            logger.error(f"Query {query_id} failed: {str(e)}", exc_info=True)
            
            # Log error
            error_logger.database_error(query_id, e, str(e))
            
            # Return fallback
            fallback = self.fallback_handler.create_error_fallback(e)
            return {
                "status": "error",
                "message": fallback.message,
                "query_id": query_id,
                "can_retry": fallback.can_retry
            }


class LLMResilienceHandler:
    """Handles resilience for LLM execution"""
    
    def __init__(self):
        self.retry_handler = AsyncRetryHandler(RetryConfig(
            max_attempts=3,
            initial_delay_ms=200,
            max_delay_ms=3000
        ))
        self.fallback_handler = get_fallback_handler()
    
    async def execute_llm_with_resilience(
        self,
        llm_func,
        query_id: str,
        org_id: str,
        user_id: str,
        *args,
        **kwargs
    ):
        """Execute LLM call with full resilience protection"""
        
        from backend.resilience.circuit_breaker import get_llm_breaker
        
        llm_breaker = get_llm_breaker()
        
        try:
            # Check if LLM is available
            if llm_breaker.is_open():
                # LLM failure is not critical, return fallback
                logger.warning(f"LLM circuit breaker open, using fallback")
                fallback = self.fallback_handler.create_llm_fallback()
                return {
                    "status": "degraded",
                    "message": fallback.message,
                    "query_id": query_id,
                    "is_fallback": True
                }
            
            # Try to execute with retries
            result = await self.retry_handler.execute(
                llm_func,
                query_id=query_id,
                org_id=org_id,
                user_id=user_id,
                *args,
                **kwargs
            )
            
            # Record success
            llm_breaker.record_success()
            return result
        
        except Exception as e:
            llm_breaker.record_failure()
            logger.warning(f"LLM execution failed for query {query_id}: {str(e)}")
            
            # Log error
            error_logger.llm_error(query_id, e, str(e))
            
            # Return fallback (graceful degradation)
            fallback = self.fallback_handler.create_llm_fallback()
            return {
                "status": "degraded",
                "message": fallback.message,
                "query_id": query_id,
                "is_fallback": True,
                "can_retry": fallback.can_retry
            }


# Global instances
_query_resilience = QueryResilienceHandler()
_llm_resilience = LLMResilienceHandler()


def get_query_resilience_handler() -> QueryResilienceHandler:
    """Get query resilience handler"""
    return _query_resilience


def get_llm_resilience_handler() -> LLMResilienceHandler:
    """Get LLM resilience handler"""
    return _llm_resilience

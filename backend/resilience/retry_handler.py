"""
Retry Handler — Exponential backoff retry logic

Provides:
- Exponential backoff with jitter
- Configurable max attempts
- Custom retry conditions
- Automatic retry on transient failures
"""

import asyncio
import random
from typing import Callable, Any, Optional, Type
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class RetryConfig:
    """Configuration for retry behavior"""
    
    def __init__(
        self,
        max_attempts: int = 3,
        initial_delay_ms: float = 100,
        max_delay_ms: float = 5000,
        exponential_base: float = 2.0,
        jitter: bool = True,
        retryable_exceptions: tuple = (Exception,)
    ):
        self.max_attempts = max_attempts
        self.initial_delay_ms = initial_delay_ms
        self.max_delay_ms = max_delay_ms
        self.exponential_base = exponential_base
        self.jitter = jitter
        self.retryable_exceptions = retryable_exceptions
    
    def get_delay_ms(self, attempt: int) -> float:
        """Calculate delay for attempt (exponential backoff with jitter)"""
        delay = min(
            self.initial_delay_ms * (self.exponential_base ** attempt),
            self.max_delay_ms
        )
        
        if self.jitter:
            # Add random jitter (±20%)
            jitter_amount = delay * 0.2
            delay = delay + random.uniform(-jitter_amount, jitter_amount)
        
        return max(delay, 0)


class RetryAttempt:
    """Information about a retry attempt"""
    
    def __init__(self, attempt_number: int, error: Exception, delay_ms: float):
        self.attempt_number = attempt_number
        self.error = error
        self.delay_ms = delay_ms
        self.timestamp = datetime.utcnow()


class RetryHandler:
    """Synchronous retry handler with exponential backoff"""
    
    def __init__(self, config: Optional[RetryConfig] = None):
        self.config = config or RetryConfig()
        self.attempts: list[RetryAttempt] = []
    
    def execute(
        self,
        func: Callable,
        *args,
        **kwargs
    ) -> Any:
        """Execute function with retries"""
        
        last_error = None
        
        for attempt_num in range(self.config.max_attempts):
            try:
                logger.info(f"Attempt {attempt_num + 1} of {self.config.max_attempts}")
                result = func(*args, **kwargs)
                return result
                
            except Exception as e:
                last_error = e
                is_retryable = isinstance(e, self.config.retryable_exceptions)
                
                if not is_retryable or attempt_num == self.config.max_attempts - 1:
                    # Not retryable or last attempt
                    logger.error(
                        f"Failed after {attempt_num + 1} attempts: {str(e)}",
                        exc_info=True
                    )
                    raise
                
                # Calculate delay
                delay_ms = self.config.get_delay_ms(attempt_num)
                attempt_info = RetryAttempt(attempt_num + 1, e, delay_ms)
                self.attempts.append(attempt_info)
                
                logger.warning(
                    f"Attempt {attempt_num + 1} failed: {str(e)}. "
                    f"Retrying in {delay_ms:.0f}ms..."
                )
                
                # Wait before retry
                asyncio.run(asyncio.sleep(delay_ms / 1000))
        
        # Should not reach here
        raise last_error


class AsyncRetryHandler:
    """Asynchronous retry handler with exponential backoff"""
    
    def __init__(self, config: Optional[RetryConfig] = None):
        self.config = config or RetryConfig()
        self.attempts: list[RetryAttempt] = []
    
    async def execute(
        self,
        func: Callable,
        *args,
        **kwargs
    ) -> Any:
        """Execute async function with retries"""
        
        last_error = None
        
        for attempt_num in range(self.config.max_attempts):
            try:
                logger.info(f"Attempt {attempt_num + 1} of {self.config.max_attempts}")
                
                # Handle both async and sync functions
                if asyncio.iscoroutinefunction(func):
                    result = await func(*args, **kwargs)
                else:
                    result = func(*args, **kwargs)
                
                return result
                
            except Exception as e:
                last_error = e
                is_retryable = isinstance(e, self.config.retryable_exceptions)
                
                if not is_retryable or attempt_num == self.config.max_attempts - 1:
                    # Not retryable or last attempt
                    logger.error(
                        f"Failed after {attempt_num + 1} attempts: {str(e)}",
                        exc_info=True
                    )
                    raise
                
                # Calculate delay
                delay_ms = self.config.get_delay_ms(attempt_num)
                attempt_info = RetryAttempt(attempt_num + 1, e, delay_ms)
                self.attempts.append(attempt_info)
                
                logger.warning(
                    f"Attempt {attempt_num + 1} failed: {str(e)}. "
                    f"Retrying in {delay_ms:.0f}ms..."
                )
                
                # Wait before retry
                await asyncio.sleep(delay_ms / 1000)
        
        # Should not reach here
        raise last_error
    
    def get_retry_history(self) -> list[dict]:
        """Get history of retry attempts"""
        return [
            {
                "attempt": attempt.attempt_number,
                "error": str(attempt.error),
                "delay_ms": attempt.delay_ms,
                "timestamp": attempt.timestamp.isoformat()
            }
            for attempt in self.attempts
        ]


# Decorator for automatic retry
def with_retries(config: Optional[RetryConfig] = None):
    """Decorator for automatic retry with exponential backoff"""
    
    retry_config = config or RetryConfig()
    
    def decorator(func):
        async def async_wrapper(*args, **kwargs):
            handler = AsyncRetryHandler(retry_config)
            return await handler.execute(func, *args, **kwargs)
        
        def sync_wrapper(*args, **kwargs):
            handler = RetryHandler(retry_config)
            return handler.execute(func, *args, **kwargs)
        
        # Return appropriate wrapper
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator


# Predefined configurations
DATABASE_RETRY_CONFIG = RetryConfig(
    max_attempts=3,
    initial_delay_ms=50,
    max_delay_ms=2000,
    retryable_exceptions=(Exception,)  # Retry all DB errors
)

LLM_RETRY_CONFIG = RetryConfig(
    max_attempts=3,
    initial_delay_ms=100,
    max_delay_ms=3000,
    retryable_exceptions=(Exception,)  # Retry on timeout, rate limit
)

API_RETRY_CONFIG = RetryConfig(
    max_attempts=3,
    initial_delay_ms=200,
    max_delay_ms=5000,
    retryable_exceptions=(Exception,)
)

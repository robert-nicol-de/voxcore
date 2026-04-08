"""
Tests for STEP 11 — Failure & Resilience
"""

import pytest
import asyncio
from datetime import datetime, timedelta

from backend.resilience.retry_handler import (
    RetryHandler, AsyncRetryHandler, RetryConfig,
    DATABASE_RETRY_CONFIG, LLM_RETRY_CONFIG
)
from backend.resilience.circuit_breaker import (
    CircuitBreaker, CircuitBreakerConfig, CircuitBreakerState,
    CircuitBreakerOpenError, CircuitBreakerRegistry,
    get_database_breaker, get_llm_breaker, get_registry
)
from backend.resilience.fallback_handler import (
    FallbackHandler, FallbackResponse, FailureType, FallbackChain,
    get_fallback_handler
)


# ===== RETRY HANDLER TESTS =====

class TestRetryConfig:
    """Test retry configuration"""
    
    def test_exponential_backoff(self):
        """Test exponential backoff calculation"""
        config = RetryConfig(
            initial_delay_ms=100,
            exponential_base=2.0,
            jitter=False
        )
        
        # Delays should double: 100ms, 200ms, 400ms
        assert config.get_delay_ms(0) == 100
        assert config.get_delay_ms(1) == 200
        assert config.get_delay_ms(2) == 400
    
    def test_max_delay(self):
        """Test max delay cap"""
        config = RetryConfig(
            initial_delay_ms=100,
            exponential_base=2.0,
            max_delay_ms=500,
            jitter=False
        )
        
        # Should cap at 500ms
        assert config.get_delay_ms(10) == 500
    
    def test_jitter(self):
        """Test jitter randomization"""
        config = RetryConfig(
            initial_delay_ms=100,
            exponential_base=2.0,
            max_delay_ms=1000,
            jitter=True
        )
        
        # Get multiple delays and verify they have variation
        delays = [config.get_delay_ms(0) for _ in range(10)]
        
        # Should have some variation due to jitter
        assert len(set(delays)) > 1


class TestRetryHandler:
    """Test synchronous retry handler"""
    
    def test_success_on_first_attempt(self):
        """Test successful execution on first attempt"""
        handler = RetryHandler(RetryConfig(max_attempts=3))
        
        def success_func():
            return "success"
        
        result = handler.execute(success_func)
        assert result == "success"
        assert len(handler.attempts) == 0
    
    def test_retry_on_failure(self):
        """Test retry on transient failure"""
        handler = RetryHandler(RetryConfig(max_attempts=3, jitter=False))
        
        attempt_count = 0
        
        def failing_func():
            nonlocal attempt_count
            attempt_count += 1
            if attempt_count < 3:
                raise Exception("Temporary failure")
            return "success"
        
        result = handler.execute(failing_func)
        assert result == "success"
        assert attempt_count == 3
    
    def test_max_attempts_exceeded(self):
        """Test failure after max attempts"""
        handler = RetryHandler(RetryConfig(max_attempts=3, jitter=False))
        
        def always_failing():
            raise ValueError("Permanent failure")
        
        with pytest.raises(ValueError):
            handler.execute(always_failing)
    
    def test_retry_with_args(self):
        """Test retry with function arguments"""
        handler = RetryHandler(RetryConfig(max_attempts=2, jitter=False))
        
        def add(a, b):
            return a + b
        
        result = handler.execute(add, 5, 3)
        assert result == 8


class TestAsyncRetryHandler:
    """Test asynchronous retry handler"""
    
    @pytest.mark.asyncio
    async def test_async_success(self):
        """Test successful async execution"""
        handler = AsyncRetryHandler(RetryConfig(max_attempts=3))
        
        async def success_func():
            return "async_success"
        
        result = await handler.execute(success_func)
        assert result == "async_success"
    
    @pytest.mark.asyncio
    async def test_async_retry(self):
        """Test async retry on failure"""
        handler = AsyncRetryHandler(RetryConfig(max_attempts=3, jitter=False))
        
        attempt_count = 0
        
        async def failing_func():
            nonlocal attempt_count
            attempt_count += 1
            if attempt_count < 2:
                raise Exception("Temporary failure")
            return "async_success"
        
        result = await handler.execute(failing_func)
        assert result == "async_success"
        assert attempt_count == 2


# ===== CIRCUIT BREAKER TESTS =====

class TestCircuitBreaker:
    """Test circuit breaker pattern"""
    
    def test_closed_state_normal_operation(self):
        """Test circuit breaker in CLOSED state (normal operation)"""
        config = CircuitBreakerConfig(failure_threshold=3)
        breaker = CircuitBreaker(config)
        
        assert breaker.state == CircuitBreakerState.CLOSED
        assert not breaker.is_open()
    
    def test_transitions_to_open_on_failures(self):
        """Test transition from CLOSED to OPEN"""
        config = CircuitBreakerConfig(failure_threshold=3)
        breaker = CircuitBreaker(config)
        
        # Record failures
        breaker.record_failure()
        assert breaker.state == CircuitBreakerState.CLOSED
        
        breaker.record_failure()
        assert breaker.state == CircuitBreakerState.CLOSED
        
        breaker.record_failure()
        assert breaker.state == CircuitBreakerState.OPEN
    
    def test_open_state_rejects_requests(self):
        """Test that OPEN state rejects all requests"""
        config = CircuitBreakerConfig(failure_threshold=1)
        breaker = CircuitBreaker(config)
        
        # Force open
        breaker.record_failure()
        assert breaker.state == CircuitBreakerState.OPEN
        
        # Try to execute
        def dummy_func():
            return "success"
        
        with pytest.raises(CircuitBreakerOpenError):
            breaker.execute(dummy_func)
    
    def test_half_open_transitions_to_closed(self):
        """Test HALF_OPEN → CLOSED transition"""
        config = CircuitBreakerConfig(
            failure_threshold=1,
            success_threshold=2,
            timeout_seconds=0  # Instant timeout for testing
        )
        breaker = CircuitBreaker(config)
        
        # Force open
        breaker.record_failure()
        assert breaker.state == CircuitBreakerState.OPEN
        
        # Wait for timeout
        breaker.opened_at = datetime.utcnow() - timedelta(seconds=1)
        
        # Next call should check timeout
        assert not breaker.is_open()
        assert breaker.state == CircuitBreakerState.HALF_OPEN
        
        # Record successes to close
        breaker.record_success()
        assert breaker.state == CircuitBreakerState.HALF_OPEN
        
        breaker.record_success()
        assert breaker.state == CircuitBreakerState.CLOSED
    
    def test_half_open_reopens_on_failure(self):
        """Test HALF_OPEN → OPEN transition"""
        config = CircuitBreakerConfig(
            failure_threshold=1,
            timeout_seconds=0
        )
        breaker = CircuitBreaker(config)
        
        # Force open
        breaker.record_failure()
        
        # Move to half-open
        breaker.opened_at = datetime.utcnow() - timedelta(seconds=1)
        assert not breaker.is_open()
        assert breaker.state == CircuitBreakerState.HALF_OPEN
        
        # Failure should immediately re-open
        breaker.record_failure()
        assert breaker.state == CircuitBreakerState.OPEN
    
    def test_get_status(self):
        """Test getting circuit breaker status"""
        config = CircuitBreakerConfig(failure_threshold=3, name="test_breaker")
        breaker = CircuitBreaker(config)
        
        breaker.record_failure()
        
        status = breaker.get_status()
        
        assert status["name"] == "test_breaker"
        assert status["state"] == "closed"
        assert status["failure_count"] == 1
        assert status["is_available"] is True


class TestCircuitBreakerRegistry:
    """Test circuit breaker registry"""
    
    def test_register_breaker(self):
        """Test registering circuit breaker"""
        registry = CircuitBreakerRegistry()
        config = CircuitBreakerConfig(name="test_service")
        
        breaker = registry.register("test_service", config)
        
        assert registry.get("test_service") == breaker
    
    def test_get_all_status(self):
        """Test getting all breaker statuses"""
        registry = CircuitBreakerRegistry()
        
        config1 = CircuitBreakerConfig(name="service1")
        config2 = CircuitBreakerConfig(name="service2")
        
        registry.register("service1", config1)
        registry.register("service2", config2)
        
        status = registry.get_all_status()
        
        assert "service1" in status
        assert "service2" in status
    
    def test_get_unhealthy_breakers(self):
        """Test getting unhealthy circuit breakers"""
        registry = CircuitBreakerRegistry()
        
        config = CircuitBreakerConfig(failure_threshold=1, name="failing_service")
        breaker = registry.register("failing_service", config)
        
        # Force failure
        breaker.record_failure()
        
        unhealthy = registry.get_unhealthy()
        assert len(unhealthy) == 1
        assert unhealthy[0]["name"] == "failing_service"


# ===== FALLBACK HANDLER TESTS =====

class TestFallbackResponse:
    """Test fallback response"""
    
    def test_fallback_response_creation(self):
        """Test creating fallback response"""
        response = FallbackResponse(
            type=FailureType.LLM_FAILURE,
            message="LLM failed",
            can_retry=True
        )
        
        assert response.type == FailureType.LLM_FAILURE
        assert response.can_retry is True
    
    def test_fallback_response_dict(self):
        """Test converting fallback to dict"""
        response = FallbackResponse(
            type=FailureType.DATABASE_FAILURE,
            message="Database unavailable",
            can_retry=True,
            is_degraded=True
        )
        
        data = response.to_dict()
        
        assert data["status"] == "degraded"
        assert data["message"] == "Database unavailable"
        assert data["can_retry"] is True


class TestFallbackHandler:
    """Test fallback handler"""
    
    def test_llm_fallback(self):
        """Test LLM fallback response"""
        handler = FallbackHandler()
        fallback = handler.create_llm_fallback()
        
        assert fallback.type == FailureType.LLM_FAILURE
        assert "safely" in fallback.message
        assert fallback.can_retry is True
    
    def test_database_fallback(self):
        """Test database fallback response"""
        handler = FallbackHandler()
        fallback = handler.create_database_fallback()
        
        assert fallback.type == FailureType.DATABASE_FAILURE
        assert "temporarily unavailable" in fallback.message.lower()
    
    def test_custom_fallback_message(self):
        """Test setting custom fallback message"""
        handler = FallbackHandler()
        
        custom_msg = "Custom LLM failure message"
        handler.set_fallback_message(FailureType.LLM_FAILURE, custom_msg)
        
        fallback = handler.create_llm_fallback()
        assert fallback.message == custom_msg
    
    def test_error_classification(self):
        """Test error type classification"""
        handler = FallbackHandler()
        
        # Test timeout classification
        timeout_error = TimeoutError("Request timed out")
        classified = handler._classify_error(timeout_error)
        assert classified == FailureType.TIMEOUT
        
        # Test database classification
        db_error = Exception("Database connection failed")
        classified = handler._classify_error(db_error)
        assert classified == FailureType.DATABASE_FAILURE


class TestFallbackChain:
    """Test fallback chain"""
    
    def test_fallback_chain_first_success(self):
        """Test fallback chain succeeds on first fallback"""
        fallback1 = lambda: "fallback1_result"
        fallback2 = lambda: "fallback2_result"
        
        chain = FallbackChain([fallback1, fallback2])
        result = chain.execute()
        
        assert result == "fallback1_result"
    
    def test_fallback_chain_second_success(self):
        """Test fallback chain uses second fallback"""
        def failing_fallback():
            raise Exception("First fallback failed")
        
        fallback2 = lambda: "fallback2_result"
        
        chain = FallbackChain([failing_fallback, fallback2])
        result = chain.execute()
        
        assert result == "fallback2_result"
    
    def test_fallback_chain_all_exhausted(self):
        """Test fallback chain failure when all exhausted"""
        def failing1():
            raise Exception("First failed")
        
        def failing2():
            raise Exception("Second failed")
        
        chain = FallbackChain([failing1, failing2])
        
        with pytest.raises(RuntimeError):
            chain.execute()


# ===== INTEGRATION TESTS =====

class TestResilienceIntegration:
    """End-to-end resilience integration tests"""
    
    def test_retry_then_fallback(self):
        """Test retry mechanism followed by fallback"""
        # This simulates: try query 3 times, then fall back
        
        retries_remaining = 3
        
        def query_with_retry():
            nonlocal retries_remaining
            retries_remaining -= 1
            if retries_remaining > 0:
                raise Exception("Temporary failure")
            return "success"
        
        handler = RetryHandler(RetryConfig(max_attempts=3, jitter=False))
        result = handler.execute(query_with_retry)
        
        assert result == "success"
        assert retries_remaining == 0
    
    def test_circuit_breaker_fallback_integration(self):
        """Test circuit breaker with fallback"""
        config = CircuitBreakerConfig(failure_threshold=2)
        breaker = CircuitBreaker(config)
        
        def failing_service():
            raise Exception("Service failed")
        
        def fallback_service():
            return "fallback_result"
        
        # Try primary service twice (will fail twice)
        for _ in range(2):
            try:
                breaker.execute(failing_service)
            except:
                breaker.record_failure()
        
        # Circuit should now be open
        assert breaker.state == CircuitBreakerState.OPEN
        
        # Use fallback instead
        if breaker.is_open():
            result = fallback_service()
            assert result == "fallback_result"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

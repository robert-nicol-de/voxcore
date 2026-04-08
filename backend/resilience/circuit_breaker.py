"""
Circuit Breaker Pattern — Prevents cascading failures

States:
- CLOSED: Normal operation, all requests pass through
- OPEN: Service failed too many times, all requests fail immediately
- HALF_OPEN: Testing if service recovered, limited requests allowed

Transitions:
CLOSED → OPEN (on failure threshold) → HALF_OPEN → CLOSED/OPEN
"""

from enum import Enum
from datetime import datetime, timedelta
import logging
from typing import Optional, Callable, Any

logger = logging.getLogger(__name__)


class CircuitBreakerState(Enum):
    """Circuit breaker states"""
    CLOSED = "closed"        # Normal operation
    OPEN = "open"           # Service failed, reject requests
    HALF_OPEN = "half_open" # Testing if service recovered


class CircuitBreakerConfig:
    """Configuration for circuit breaker"""
    
    def __init__(
        self,
        failure_threshold: int = 5,
        success_threshold: int = 2,
        timeout_seconds: int = 60,
        name: str = "circuit_breaker"
    ):
        """
        Args:
            failure_threshold: # failures to trip (CLOSED → OPEN)
            success_threshold: # successes to close (HALF_OPEN → CLOSED)
            timeout_seconds: Time to wait before OPEN → HALF_OPEN
            name: Circuit breaker identifier
        """
        self.failure_threshold = failure_threshold
        self.success_threshold = success_threshold
        self.timeout_seconds = timeout_seconds
        self.name = name


class CircuitBreaker:
    """Circuit breaker implementation"""
    
    def __init__(self, config: CircuitBreakerConfig):
        self.config = config
        self.state = CircuitBreakerState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time: Optional[datetime] = None
        self.opened_at: Optional[datetime] = None
    
    def is_open(self) -> bool:
        """Check if circuit is open"""
        if self.state == CircuitBreakerState.OPEN:
            # Check if timeout expired
            if self.opened_at:
                elapsed = (datetime.utcnow() - self.opened_at).total_seconds()
                if elapsed >= self.config.timeout_seconds:
                    logger.info(
                        f"Circuit '{self.config.name}': "
                        f"Timeout expired, moving to HALF_OPEN"
                    )
                    self.state = CircuitBreakerState.HALF_OPEN
                    self.success_count = 0
                    return False
                return True
        
        return False
    
    def record_success(self):
        """Record a successful call"""
        self.failure_count = 0
        
        if self.state == CircuitBreakerState.HALF_OPEN:
            self.success_count += 1
            logger.debug(
                f"Circuit '{self.config.name}': "
                f"Half-open success: {self.success_count}/{self.config.success_threshold}"
            )
            
            if self.success_count >= self.config.success_threshold:
                self.state = CircuitBreakerState.CLOSED
                self.success_count = 0
                logger.info(
                    f"Circuit '{self.config.name}': "
                    f"Recovered! Moving to CLOSED"
                )
        
        elif self.state == CircuitBreakerState.CLOSED:
            # Normal operation
            pass
    
    def record_failure(self):
        """Record a failed call"""
        self.failure_count += 1
        self.last_failure_time = datetime.utcnow()
        self.success_count = 0
        
        logger.warning(
            f"Circuit '{self.config.name}': "
            f"Failure recorded: {self.failure_count}/{self.config.failure_threshold}"
        )
        
        if self.failure_count >= self.config.failure_threshold:
            if self.state != CircuitBreakerState.OPEN:
                self.state = CircuitBreakerState.OPEN
                self.opened_at = datetime.utcnow()
                logger.error(
                    f"Circuit '{self.config.name}': "
                    f"OPENED! Too many failures. Will retry in {self.config.timeout_seconds}s"
                )
    
    def execute(
        self,
        func: Callable,
        *args,
        **kwargs
    ) -> Any:
        """Execute function with circuit breaker protection"""
        
        if self.is_open():
            raise CircuitBreakerOpenError(
                f"Circuit '{self.config.name}' is OPEN. "
                f"Service unavailable, will retry later."
            )
        
        try:
            result = func(*args, **kwargs)
            self.record_success()
            return result
        
        except Exception as e:
            self.record_failure()
            raise
    
    async def execute_async(
        self,
        func: Callable,
        *args,
        **kwargs
    ) -> Any:
        """Execute async function with circuit breaker protection"""
        
        if self.is_open():
            raise CircuitBreakerOpenError(
                f"Circuit '{self.config.name}' is OPEN. "
                f"Service unavailable, will retry later."
            )
        
        try:
            result = await func(*args, **kwargs)
            self.record_success()
            return result
        
        except Exception as e:
            self.record_failure()
            raise
    
    def get_status(self) -> dict:
        """Get current circuit breaker status"""
        return {
            "name": self.config.name,
            "state": self.state.value,
            "failure_count": self.failure_count,
            "success_count": self.success_count,
            "last_failure_time": self.last_failure_time.isoformat() if self.last_failure_time else None,
            "opened_at": self.opened_at.isoformat() if self.opened_at else None,
            "is_available": not self.is_open()
        }


class CircuitBreakerOpenError(Exception):
    """Raised when circuit breaker is open"""
    pass


class CircuitBreakerRegistry:
    """Manages multiple circuit breakers"""
    
    def __init__(self):
        self.breakers: dict[str, CircuitBreaker] = {}
    
    def register(self, name: str, config: CircuitBreakerConfig) -> CircuitBreaker:
        """Register a new circuit breaker"""
        breaker = CircuitBreaker(config)
        self.breakers[name] = breaker
        logger.info(f"Registered circuit breaker: {name}")
        return breaker
    
    def get(self, name: str) -> Optional[CircuitBreaker]:
        """Get circuit breaker by name"""
        return self.breakers.get(name)
    
    def get_all_status(self) -> dict:
        """Get status of all circuit breakers"""
        return {
            name: breaker.get_status()
            for name, breaker in self.breakers.items()
        }
    
    def get_unhealthy(self) -> list[dict]:
        """Get all open/half-open breakers"""
        return [
            breaker.get_status()
            for breaker in self.breakers.values()
            if breaker.state != CircuitBreakerState.CLOSED
        ]


# Global registry
_circuit_breaker_registry = CircuitBreakerRegistry()


# Predefined circuit breakers
def get_database_breaker() -> CircuitBreaker:
    """Get or create database circuit breaker"""
    if "database" not in _circuit_breaker_registry.breakers:
        config = CircuitBreakerConfig(
            failure_threshold=5,
            success_threshold=2,
            timeout_seconds=30,
            name="database"
        )
        _circuit_breaker_registry.register("database", config)
    return _circuit_breaker_registry.get("database")


def get_llm_breaker() -> CircuitBreaker:
    """Get or create LLM circuit breaker"""
    if "llm" not in _circuit_breaker_registry.breakers:
        config = CircuitBreakerConfig(
            failure_threshold=3,
            success_threshold=2,
            timeout_seconds=60,
            name="llm"
        )
        _circuit_breaker_registry.register("llm", config)
    return _circuit_breaker_registry.get("llm")


def get_cache_breaker() -> CircuitBreaker:
    """Get or create cache circuit breaker"""
    if "cache" not in _circuit_breaker_registry.breakers:
        config = CircuitBreakerConfig(
            failure_threshold=10,
            success_threshold=5,
            timeout_seconds=20,
            name="cache"
        )
        _circuit_breaker_registry.register("cache", config)
    return _circuit_breaker_registry.get("cache")


def get_registry() -> CircuitBreakerRegistry:
    """Get global circuit breaker registry"""
    return _circuit_breaker_registry

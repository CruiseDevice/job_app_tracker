"""
Circuit breaker pattern implementation.

Prevents cascading failures by:
- Monitoring failure rates
- Opening circuit after threshold
- Allowing periodic retries
- Auto-recovery when service recovers
"""

import logging
import time
import asyncio
from typing import Callable, Any, Optional
from enum import Enum
from dataclasses import dataclass
from functools import wraps

logger = logging.getLogger(__name__)


class CircuitState(str, Enum):
    """States of a circuit breaker."""
    CLOSED = "closed"  # Normal operation
    OPEN = "open"  # Failing, rejecting requests
    HALF_OPEN = "half_open"  # Testing if service recovered


@dataclass
class CircuitBreakerConfig:
    """Configuration for circuit breaker."""
    failure_threshold: int = 5  # Failures before opening circuit
    success_threshold: int = 2  # Successes needed to close circuit from half-open
    timeout: float = 60.0  # Seconds before trying half-open state
    expected_exception: type = Exception  # Exception type to catch


class CircuitBreakerError(Exception):
    """Raised when circuit breaker is open."""
    pass


class CircuitBreaker:
    """
    Circuit breaker for preventing cascading failures.

    Features:
    - Three-state circuit (closed, open, half-open)
    - Automatic recovery testing
    - Failure rate monitoring
    - Configurable thresholds
    """

    def __init__(self, name: str, config: Optional[CircuitBreakerConfig] = None):
        """
        Initialize circuit breaker.

        Args:
            name: Name of the circuit
            config: Circuit breaker configuration
        """
        self.name = name
        self.config = config or CircuitBreakerConfig()
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time = None
        self.last_state_change = time.time()

        logger.info(f"🔌 Circuit Breaker '{name}' initialized")

    def _should_attempt_reset(self) -> bool:
        """Check if enough time has passed to try resetting."""
        if self.last_failure_time is None:
            return False

        time_since_failure = time.time() - self.last_failure_time
        return time_since_failure >= self.config.timeout

    def _on_success(self) -> None:
        """Handle successful execution."""
        if self.state == CircuitState.HALF_OPEN:
            self.success_count += 1
            logger.info(
                f"✅ Circuit '{self.name}' half-open success "
                f"({self.success_count}/{self.config.success_threshold})"
            )

            if self.success_count >= self.config.success_threshold:
                self._close_circuit()
        elif self.state == CircuitState.CLOSED:
            self.failure_count = 0

    def _on_failure(self, exception: Exception) -> None:
        """Handle failed execution."""
        self.last_failure_time = time.time()

        if self.state == CircuitState.HALF_OPEN:
            self._open_circuit()
        elif self.state == CircuitState.CLOSED:
            self.failure_count += 1
            logger.warning(
                f"⚠️ Circuit '{self.name}' failure "
                f"({self.failure_count}/{self.config.failure_threshold})"
            )

            if self.failure_count >= self.config.failure_threshold:
                self._open_circuit()

    def _open_circuit(self) -> None:
        """Open the circuit."""
        self.state = CircuitState.OPEN
        self.last_state_change = time.time()
        self.success_count = 0
        logger.error(
            f"🔴 Circuit '{self.name}' OPENED after {self.failure_count} failures"
        )

    def _close_circuit(self) -> None:
        """Close the circuit."""
        self.state = CircuitState.CLOSED
        self.last_state_change = time.time()
        self.failure_count = 0
        self.success_count = 0
        logger.info(f"🟢 Circuit '{self.name}' CLOSED - service recovered")

    def _half_open_circuit(self) -> None:
        """Move to half-open state to test recovery."""
        self.state = CircuitState.HALF_OPEN
        self.last_state_change = time.time()
        self.success_count = 0
        logger.info(f"🟡 Circuit '{self.name}' HALF-OPEN - testing recovery")

    async def execute_async(self, func: Callable, *args, **kwargs) -> Any:
        """
        Execute async function with circuit breaker.

        Args:
            func: Async function to execute
            *args: Positional arguments
            **kwargs: Keyword arguments

        Returns:
            Function result

        Raises:
            CircuitBreakerError: If circuit is open
        """
        # Check if we should attempt reset
        if self.state == CircuitState.OPEN and self._should_attempt_reset():
            self._half_open_circuit()

        # Reject if circuit is open
        if self.state == CircuitState.OPEN:
            raise CircuitBreakerError(
                f"Circuit '{self.name}' is OPEN. "
                f"Service unavailable for {self.config.timeout}s after failure."
            )

        try:
            result = await func(*args, **kwargs)
            self._on_success()
            return result

        except self.config.expected_exception as e:
            self._on_failure(e)
            raise

    def execute_sync(self, func: Callable, *args, **kwargs) -> Any:
        """
        Execute synchronous function with circuit breaker.

        Args:
            func: Function to execute
            *args: Positional arguments
            **kwargs: Keyword arguments

        Returns:
            Function result

        Raises:
            CircuitBreakerError: If circuit is open
        """
        # Check if we should attempt reset
        if self.state == CircuitState.OPEN and self._should_attempt_reset():
            self._half_open_circuit()

        # Reject if circuit is open
        if self.state == CircuitState.OPEN:
            raise CircuitBreakerError(
                f"Circuit '{self.name}' is OPEN. "
                f"Service unavailable for {self.config.timeout}s after failure."
            )

        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result

        except self.config.expected_exception as e:
            self._on_failure(e)
            raise

    def get_state(self) -> CircuitState:
        """Get current circuit state."""
        return self.state

    def get_stats(self) -> dict:
        """Get circuit breaker statistics."""
        return {
            'name': self.name,
            'state': self.state.value,
            'failure_count': self.failure_count,
            'success_count': self.success_count,
            'last_failure_time': self.last_failure_time,
            'last_state_change': self.last_state_change,
            'time_since_state_change': time.time() - self.last_state_change
        }

    def reset(self) -> None:
        """Manually reset the circuit breaker."""
        self._close_circuit()
        logger.info(f"🔄 Circuit '{self.name}' manually reset")


def with_circuit_breaker(
    name: str,
    config: Optional[CircuitBreakerConfig] = None
):
    """
    Decorator for adding circuit breaker to functions.

    Args:
        name: Circuit breaker name
        config: Circuit breaker configuration

    Example:
        @with_circuit_breaker("api_service")
        async def call_api():
            # Function that calls external API
            pass
    """
    circuit_breaker = CircuitBreaker(name, config)

    def decorator(func: Callable) -> Callable:
        if asyncio.iscoroutinefunction(func):
            @wraps(func)
            async def async_wrapper(*args, **kwargs):
                return await circuit_breaker.execute_async(func, *args, **kwargs)
            return async_wrapper
        else:
            @wraps(func)
            def sync_wrapper(*args, **kwargs):
                return circuit_breaker.execute_sync(func, *args, **kwargs)
            return sync_wrapper

    return decorator


# Global circuit breaker registry
_circuit_breakers = {}


def get_circuit_breaker(
    name: str,
    config: Optional[CircuitBreakerConfig] = None
) -> CircuitBreaker:
    """
    Get or create a circuit breaker.

    Args:
        name: Circuit breaker name
        config: Circuit breaker configuration

    Returns:
        CircuitBreaker instance
    """
    if name not in _circuit_breakers:
        _circuit_breakers[name] = CircuitBreaker(name, config)
    return _circuit_breakers[name]


def get_all_circuit_breakers() -> dict:
    """Get statistics for all circuit breakers."""
    return {
        name: cb.get_stats()
        for name, cb in _circuit_breakers.items()
    }

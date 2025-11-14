"""
Retry handler with exponential backoff and jitter.

Provides robust retry mechanisms for:
- API calls
- Tool executions
- Agent operations
- Database operations
"""

import logging
import asyncio
import time
import random
from typing import Callable, Optional, Any, List, Type
from dataclasses import dataclass
from enum import Enum
from functools import wraps

logger = logging.getLogger(__name__)


class BackoffStrategy(str, Enum):
    """Backoff strategies for retries."""
    EXPONENTIAL = "exponential"
    LINEAR = "linear"
    FIXED = "fixed"
    EXPONENTIAL_JITTER = "exponential_jitter"


@dataclass
class RetryPolicy:
    """Configuration for retry behavior."""
    max_retries: int = 3
    initial_delay: float = 1.0  # seconds
    max_delay: float = 60.0  # seconds
    backoff_strategy: BackoffStrategy = BackoffStrategy.EXPONENTIAL_JITTER
    backoff_multiplier: float = 2.0
    jitter: bool = True
    retry_on_exceptions: List[Type[Exception]] = None  # None means retry on all exceptions

    def __post_init__(self):
        if self.retry_on_exceptions is None:
            self.retry_on_exceptions = [Exception]


class RetryHandler:
    """
    Handler for retrying operations with various backoff strategies.

    Features:
    - Multiple backoff strategies
    - Configurable retry policies
    - Exception filtering
    - Timeout support
    - Retry statistics tracking
    """

    def __init__(self, policy: Optional[RetryPolicy] = None):
        """
        Initialize retry handler.

        Args:
            policy: Retry policy (uses defaults if not provided)
        """
        self.policy = policy or RetryPolicy()
        self.retry_stats = {
            'total_retries': 0,
            'successful_retries': 0,
            'failed_retries': 0
        }
        logger.info(f"🔄 Retry Handler initialized with {self.policy.max_retries} max retries")

    def _calculate_delay(self, attempt: int) -> float:
        """
        Calculate delay for next retry based on strategy.

        Args:
            attempt: Current attempt number (0-indexed)

        Returns:
            Delay in seconds
        """
        if self.policy.backoff_strategy == BackoffStrategy.FIXED:
            delay = self.policy.initial_delay

        elif self.policy.backoff_strategy == BackoffStrategy.LINEAR:
            delay = self.policy.initial_delay * (attempt + 1)

        elif self.policy.backoff_strategy == BackoffStrategy.EXPONENTIAL:
            delay = self.policy.initial_delay * (self.policy.backoff_multiplier ** attempt)

        elif self.policy.backoff_strategy == BackoffStrategy.EXPONENTIAL_JITTER:
            base_delay = self.policy.initial_delay * (self.policy.backoff_multiplier ** attempt)
            # Add random jitter (±20%)
            jitter_range = base_delay * 0.2
            delay = base_delay + random.uniform(-jitter_range, jitter_range)

        else:
            delay = self.policy.initial_delay

        # Cap at max delay
        delay = min(delay, self.policy.max_delay)

        return delay

    def _should_retry(self, exception: Exception) -> bool:
        """
        Determine if exception should trigger a retry.

        Args:
            exception: Exception that occurred

        Returns:
            True if should retry
        """
        if not self.policy.retry_on_exceptions:
            return True

        for exc_type in self.policy.retry_on_exceptions:
            if isinstance(exception, exc_type):
                return True

        return False

    async def execute_async(
        self,
        func: Callable,
        *args,
        **kwargs
    ) -> Any:
        """
        Execute async function with retry logic.

        Args:
            func: Async function to execute
            *args: Positional arguments
            **kwargs: Keyword arguments

        Returns:
            Function result

        Raises:
            Exception: If all retries are exhausted
        """
        last_exception = None

        for attempt in range(self.policy.max_retries + 1):
            try:
                logger.debug(f"Attempt {attempt + 1}/{self.policy.max_retries + 1}")
                result = await func(*args, **kwargs)

                if attempt > 0:
                    self.retry_stats['successful_retries'] += 1
                    logger.info(f"✅ Retry successful after {attempt} attempts")

                return result

            except Exception as e:
                last_exception = e
                self.retry_stats['total_retries'] += 1

                if not self._should_retry(e):
                    logger.warning(f"⚠️ Exception {type(e).__name__} not configured for retry")
                    raise

                if attempt < self.policy.max_retries:
                    delay = self._calculate_delay(attempt)
                    logger.warning(
                        f"⚠️ Attempt {attempt + 1} failed: {e}. "
                        f"Retrying in {delay:.2f}s..."
                    )
                    await asyncio.sleep(delay)
                else:
                    self.retry_stats['failed_retries'] += 1
                    logger.error(
                        f"❌ All {self.policy.max_retries + 1} attempts failed. "
                        f"Last error: {e}"
                    )

        raise last_exception

    def execute_sync(
        self,
        func: Callable,
        *args,
        **kwargs
    ) -> Any:
        """
        Execute synchronous function with retry logic.

        Args:
            func: Function to execute
            *args: Positional arguments
            **kwargs: Keyword arguments

        Returns:
            Function result

        Raises:
            Exception: If all retries are exhausted
        """
        last_exception = None

        for attempt in range(self.policy.max_retries + 1):
            try:
                logger.debug(f"Attempt {attempt + 1}/{self.policy.max_retries + 1}")
                result = func(*args, **kwargs)

                if attempt > 0:
                    self.retry_stats['successful_retries'] += 1
                    logger.info(f"✅ Retry successful after {attempt} attempts")

                return result

            except Exception as e:
                last_exception = e
                self.retry_stats['total_retries'] += 1

                if not self._should_retry(e):
                    logger.warning(f"⚠️ Exception {type(e).__name__} not configured for retry")
                    raise

                if attempt < self.policy.max_retries:
                    delay = self._calculate_delay(attempt)
                    logger.warning(
                        f"⚠️ Attempt {attempt + 1} failed: {e}. "
                        f"Retrying in {delay:.2f}s..."
                    )
                    time.sleep(delay)
                else:
                    self.retry_stats['failed_retries'] += 1
                    logger.error(
                        f"❌ All {self.policy.max_retries + 1} attempts failed. "
                        f"Last error: {e}"
                    )

        raise last_exception

    def get_stats(self) -> dict:
        """Get retry statistics."""
        return self.retry_stats.copy()


def with_retry(policy: Optional[RetryPolicy] = None):
    """
    Decorator for adding retry logic to functions.

    Args:
        policy: Retry policy

    Example:
        @with_retry(RetryPolicy(max_retries=5))
        async def my_function():
            # Function that might fail
            pass
    """
    def decorator(func: Callable) -> Callable:
        retry_handler = RetryHandler(policy)

        if asyncio.iscoroutinefunction(func):
            @wraps(func)
            async def async_wrapper(*args, **kwargs):
                return await retry_handler.execute_async(func, *args, **kwargs)
            return async_wrapper
        else:
            @wraps(func)
            def sync_wrapper(*args, **kwargs):
                return retry_handler.execute_sync(func, *args, **kwargs)
            return sync_wrapper

    return decorator


# Global retry handler with default policy
global_retry_handler = RetryHandler()

"""
Comprehensive error handling system for agents.

Provides:
- Error classification
- Recovery strategies
- Graceful degradation
- Error reporting
- Automatic error recovery
"""

import logging
import traceback
from typing import Optional, Callable, Any, Dict, List
from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime
import json

logger = logging.getLogger(__name__)


class ErrorSeverity(str, Enum):
    """Severity levels for errors."""
    LOW = "low"  # Minor issues, can continue
    MEDIUM = "medium"  # Significant issues, degraded operation
    HIGH = "high"  # Major issues, limited functionality
    CRITICAL = "critical"  # System failure, cannot continue


class ErrorCategory(str, Enum):
    """Categories of errors."""
    NETWORK = "network"
    TIMEOUT = "timeout"
    RATE_LIMIT = "rate_limit"
    AUTHENTICATION = "authentication"
    VALIDATION = "validation"
    RESOURCE = "resource"
    CONFIGURATION = "configuration"
    EXTERNAL_SERVICE = "external_service"
    INTERNAL = "internal"
    UNKNOWN = "unknown"


class ErrorRecoveryStrategy(str, Enum):
    """Recovery strategies for errors."""
    RETRY = "retry"  # Retry the operation
    FALLBACK = "fallback"  # Use fallback/default value
    SKIP = "skip"  # Skip and continue
    ESCALATE = "escalate"  # Escalate to human/admin
    FAIL_FAST = "fail_fast"  # Fail immediately
    GRACEFUL_DEGRADATION = "graceful_degradation"  # Continue with reduced functionality


@dataclass
class ErrorInfo:
    """Information about an error."""
    error_id: str
    timestamp: datetime
    exception: Exception
    exception_type: str
    message: str
    severity: ErrorSeverity
    category: ErrorCategory
    context: Dict[str, Any] = field(default_factory=dict)
    stack_trace: str = ""
    recovery_strategy: Optional[ErrorRecoveryStrategy] = None
    recovered: bool = False
    recovery_details: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'error_id': self.error_id,
            'timestamp': self.timestamp.isoformat(),
            'exception_type': self.exception_type,
            'message': self.message,
            'severity': self.severity.value,
            'category': self.category.value,
            'context': self.context,
            'stack_trace': self.stack_trace,
            'recovery_strategy': self.recovery_strategy.value if self.recovery_strategy else None,
            'recovered': self.recovered,
            'recovery_details': self.recovery_details
        }


class ErrorHandler:
    """
    Comprehensive error handling system.

    Features:
    - Error classification
    - Severity assessment
    - Recovery strategy selection
    - Error logging and tracking
    - Graceful degradation
    """

    def __init__(self):
        """Initialize error handler."""
        self.error_history: List[ErrorInfo] = []
        self.max_history = 1000
        self.error_count_by_category: Dict[ErrorCategory, int] = {}
        logger.info("🛡️ Error Handler initialized")

    def classify_error(self, exception: Exception) -> ErrorCategory:
        """
        Classify an exception into a category.

        Args:
            exception: The exception to classify

        Returns:
            ErrorCategory
        """
        exception_name = type(exception).__name__.lower()
        message = str(exception).lower()

        # Network errors
        if any(term in exception_name for term in ['connection', 'network', 'socket']):
            return ErrorCategory.NETWORK

        # Timeout errors
        if 'timeout' in exception_name or 'timeout' in message:
            return ErrorCategory.TIMEOUT

        # Rate limit errors
        if any(term in message for term in ['rate limit', 'too many requests', '429']):
            return ErrorCategory.RATE_LIMIT

        # Authentication errors
        if any(term in exception_name for term in ['auth', 'credential', 'permission']):
            return ErrorCategory.AUTHENTICATION

        # Validation errors
        if any(term in exception_name for term in ['validation', 'value', 'type']):
            return ErrorCategory.VALIDATION

        # Resource errors
        if any(term in exception_name for term in ['memory', 'resource', 'quota']):
            return ErrorCategory.RESOURCE

        # Configuration errors
        if any(term in exception_name for term in ['config', 'setting', 'environment']):
            return ErrorCategory.CONFIGURATION

        # External service errors
        if any(term in message for term in ['api', 'service', 'external', 'openai']):
            return ErrorCategory.EXTERNAL_SERVICE

        return ErrorCategory.UNKNOWN

    def assess_severity(
        self,
        exception: Exception,
        category: ErrorCategory
    ) -> ErrorSeverity:
        """
        Assess the severity of an error.

        Args:
            exception: The exception
            category: Error category

        Returns:
            ErrorSeverity
        """
        # Critical errors
        if category in [ErrorCategory.AUTHENTICATION, ErrorCategory.CONFIGURATION]:
            return ErrorSeverity.CRITICAL

        # High severity
        if category in [ErrorCategory.RESOURCE]:
            return ErrorSeverity.HIGH

        # Medium severity
        if category in [ErrorCategory.RATE_LIMIT, ErrorCategory.EXTERNAL_SERVICE]:
            return ErrorSeverity.MEDIUM

        # Low severity
        if category in [ErrorCategory.VALIDATION, ErrorCategory.TIMEOUT]:
            return ErrorSeverity.LOW

        # Default to medium for unknown
        return ErrorSeverity.MEDIUM

    def determine_recovery_strategy(
        self,
        category: ErrorCategory,
        severity: ErrorSeverity
    ) -> ErrorRecoveryStrategy:
        """
        Determine appropriate recovery strategy.

        Args:
            category: Error category
            severity: Error severity

        Returns:
            ErrorRecoveryStrategy
        """
        # Critical errors - fail fast or escalate
        if severity == ErrorSeverity.CRITICAL:
            return ErrorRecoveryStrategy.ESCALATE

        # Category-specific strategies
        if category == ErrorCategory.RATE_LIMIT:
            return ErrorRecoveryStrategy.RETRY  # Retry with backoff

        if category == ErrorCategory.TIMEOUT:
            return ErrorRecoveryStrategy.RETRY

        if category == ErrorCategory.NETWORK:
            return ErrorRecoveryStrategy.RETRY

        if category == ErrorCategory.EXTERNAL_SERVICE:
            return ErrorRecoveryStrategy.FALLBACK

        if category == ErrorCategory.VALIDATION:
            return ErrorRecoveryStrategy.SKIP

        # Default strategy based on severity
        if severity == ErrorSeverity.HIGH:
            return ErrorRecoveryStrategy.GRACEFUL_DEGRADATION
        elif severity == ErrorSeverity.MEDIUM:
            return ErrorRecoveryStrategy.FALLBACK
        else:
            return ErrorRecoveryStrategy.RETRY

    def handle_error(
        self,
        exception: Exception,
        context: Optional[Dict[str, Any]] = None,
        custom_recovery: Optional[Callable] = None
    ) -> ErrorInfo:
        """
        Handle an error with appropriate strategy.

        Args:
            exception: The exception that occurred
            context: Additional context information
            custom_recovery: Optional custom recovery function

        Returns:
            ErrorInfo object
        """
        import uuid

        # Classify and assess error
        category = self.classify_error(exception)
        severity = self.assess_severity(exception, category)
        recovery_strategy = self.determine_recovery_strategy(category, severity)

        # Create error info
        error_info = ErrorInfo(
            error_id=str(uuid.uuid4()),
            timestamp=datetime.now(),
            exception=exception,
            exception_type=type(exception).__name__,
            message=str(exception),
            severity=severity,
            category=category,
            context=context or {},
            stack_trace=traceback.format_exc(),
            recovery_strategy=recovery_strategy
        )

        # Log error
        log_level = {
            ErrorSeverity.LOW: logging.WARNING,
            ErrorSeverity.MEDIUM: logging.ERROR,
            ErrorSeverity.HIGH: logging.ERROR,
            ErrorSeverity.CRITICAL: logging.CRITICAL
        }[severity]

        logger.log(
            log_level,
            f"{'🔴' if severity == ErrorSeverity.CRITICAL else '⚠️'} "
            f"[{category.value}] {severity.value.upper()}: {exception}",
            exc_info=True
        )

        # Attempt recovery
        if custom_recovery:
            try:
                custom_recovery(error_info)
                error_info.recovered = True
                error_info.recovery_details = "Custom recovery successful"
                logger.info(f"✅ Error {error_info.error_id} recovered using custom strategy")
            except Exception as recovery_error:
                error_info.recovery_details = f"Custom recovery failed: {recovery_error}"
                logger.error(f"❌ Custom recovery failed: {recovery_error}")

        # Store in history
        self.error_history.append(error_info)
        if len(self.error_history) > self.max_history:
            self.error_history = self.error_history[-self.max_history:]

        # Update category counts
        self.error_count_by_category[category] = \
            self.error_count_by_category.get(category, 0) + 1

        return error_info

    def get_error_stats(self) -> Dict[str, Any]:
        """Get error statistics."""
        total_errors = len(self.error_history)
        if total_errors == 0:
            return {
                'total_errors': 0,
                'errors_by_category': {},
                'errors_by_severity': {},
                'recovery_rate': 0.0
            }

        errors_by_severity = {}
        recovered_count = 0

        for error in self.error_history:
            # Count by severity
            severity = error.severity.value
            errors_by_severity[severity] = errors_by_severity.get(severity, 0) + 1

            # Count recoveries
            if error.recovered:
                recovered_count += 1

        return {
            'total_errors': total_errors,
            'errors_by_category': {
                cat.value: count
                for cat, count in self.error_count_by_category.items()
            },
            'errors_by_severity': errors_by_severity,
            'recovery_rate': (recovered_count / total_errors) * 100,
            'recent_errors': [
                {
                    'error_id': e.error_id,
                    'category': e.category.value,
                    'severity': e.severity.value,
                    'message': e.message,
                    'timestamp': e.timestamp.isoformat()
                }
                for e in self.error_history[-10:]
            ]
        }

    def get_error_by_id(self, error_id: str) -> Optional[ErrorInfo]:
        """Get error information by ID."""
        for error in self.error_history:
            if error.error_id == error_id:
                return error
        return None

    def export_errors(self, filepath: Optional[str] = None) -> str:
        """
        Export error history as JSON.

        Args:
            filepath: Optional file path to save

        Returns:
            JSON string
        """
        data = {
            'exported_at': datetime.now().isoformat(),
            'total_errors': len(self.error_history),
            'stats': self.get_error_stats(),
            'errors': [error.to_dict() for error in self.error_history]
        }

        json_data = json.dumps(data, indent=2, default=str)

        if filepath:
            with open(filepath, 'w') as f:
                f.write(json_data)
            logger.info(f"📁 Errors exported to {filepath}")

        return json_data

    def clear_history(self) -> None:
        """Clear error history."""
        self.error_history.clear()
        self.error_count_by_category.clear()
        logger.info("🗑️ Error history cleared")


# Global error handler instance
global_error_handler = ErrorHandler()

"""
Structured logging system for agents.

Provides enhanced logging with:
- Structured JSON logs
- Request ID tracking
- Context propagation
- Log correlation
- Performance logging
"""

import logging
import json
import uuid
from datetime import datetime
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict
from contextvars import ContextVar
from enum import Enum

# Context variable for request tracking
request_context: ContextVar[Optional[Dict[str, Any]]] = ContextVar('request_context', default=None)


class LogLevel(str, Enum):
    """Log levels."""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


@dataclass
class LogContext:
    """Context information for structured logging."""
    request_id: str
    agent_name: Optional[str] = None
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    correlation_id: Optional[str] = None
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

    def to_dict(self) -> Dict[str, Any]:
        """Convert context to dictionary."""
        return {k: v for k, v in asdict(self).items() if v is not None}


class StructuredLogger:
    """
    Structured logger with enhanced context and correlation.

    Features:
    - JSON formatted logs
    - Automatic request ID tracking
    - Context propagation
    - Performance metrics
    - Error tracking
    """

    def __init__(self, name: str):
        """
        Initialize structured logger.

        Args:
            name: Logger name (typically __name__)
        """
        self.logger = logging.getLogger(name)
        self.name = name

    def _format_log(
        self,
        level: str,
        message: str,
        context: Optional[LogContext] = None,
        extra: Optional[Dict[str, Any]] = None,
        error: Optional[Exception] = None
    ) -> Dict[str, Any]:
        """
        Format log entry as structured JSON.

        Args:
            level: Log level
            message: Log message
            context: Log context
            extra: Additional fields
            error: Exception if applicable

        Returns:
            Dictionary with structured log data
        """
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'level': level,
            'logger': self.name,
            'message': message,
        }

        # Add context if available
        if context:
            log_entry['context'] = context.to_dict()
        else:
            # Try to get context from context var
            ctx = request_context.get()
            if ctx:
                log_entry['context'] = ctx

        # Add extra fields
        if extra:
            log_entry['extra'] = extra

        # Add error information
        if error:
            log_entry['error'] = {
                'type': type(error).__name__,
                'message': str(error),
                'module': error.__class__.__module__
            }

        return log_entry

    def _log(
        self,
        level: LogLevel,
        message: str,
        context: Optional[LogContext] = None,
        extra: Optional[Dict[str, Any]] = None,
        error: Optional[Exception] = None
    ) -> None:
        """
        Internal log method.

        Args:
            level: Log level
            message: Log message
            context: Log context
            extra: Additional fields
            error: Exception if applicable
        """
        log_entry = self._format_log(level.value, message, context, extra, error)
        log_str = json.dumps(log_entry)

        # Log using appropriate level
        if level == LogLevel.DEBUG:
            self.logger.debug(log_str)
        elif level == LogLevel.INFO:
            self.logger.info(log_str)
        elif level == LogLevel.WARNING:
            self.logger.warning(log_str)
        elif level == LogLevel.ERROR:
            self.logger.error(log_str, exc_info=error is not None)
        elif level == LogLevel.CRITICAL:
            self.logger.critical(log_str, exc_info=error is not None)

    def debug(self, message: str, context: Optional[LogContext] = None, **kwargs) -> None:
        """Log debug message."""
        self._log(LogLevel.DEBUG, message, context, kwargs)

    def info(self, message: str, context: Optional[LogContext] = None, **kwargs) -> None:
        """Log info message."""
        self._log(LogLevel.INFO, message, context, kwargs)

    def warning(self, message: str, context: Optional[LogContext] = None, **kwargs) -> None:
        """Log warning message."""
        self._log(LogLevel.WARNING, message, context, kwargs)

    def error(
        self,
        message: str,
        error: Optional[Exception] = None,
        context: Optional[LogContext] = None,
        **kwargs
    ) -> None:
        """Log error message."""
        self._log(LogLevel.ERROR, message, context, kwargs, error)

    def critical(
        self,
        message: str,
        error: Optional[Exception] = None,
        context: Optional[LogContext] = None,
        **kwargs
    ) -> None:
        """Log critical message."""
        self._log(LogLevel.CRITICAL, message, context, kwargs, error)

    def log_agent_execution(
        self,
        agent_name: str,
        action: str,
        success: bool,
        duration: Optional[float] = None,
        context: Optional[LogContext] = None,
        **kwargs
    ) -> None:
        """
        Log agent execution event.

        Args:
            agent_name: Name of the agent
            action: Action being performed
            success: Whether action was successful
            duration: Execution duration in seconds
            context: Log context
            **kwargs: Additional fields
        """
        status = "✅ SUCCESS" if success else "❌ FAILED"
        message = f"Agent {agent_name}: {action} - {status}"

        extra = {
            'agent_name': agent_name,
            'action': action,
            'success': success,
            **kwargs
        }

        if duration is not None:
            extra['duration_seconds'] = duration
            message += f" ({duration:.2f}s)"

        self._log(LogLevel.INFO, message, context, extra)

    def log_api_call(
        self,
        method: str,
        endpoint: str,
        status_code: int,
        duration: float,
        context: Optional[LogContext] = None,
        **kwargs
    ) -> None:
        """
        Log API call.

        Args:
            method: HTTP method
            endpoint: API endpoint
            status_code: Response status code
            duration: Request duration in seconds
            context: Log context
            **kwargs: Additional fields
        """
        message = f"API {method} {endpoint} - {status_code} ({duration:.3f}s)"

        extra = {
            'http_method': method,
            'endpoint': endpoint,
            'status_code': status_code,
            'duration_seconds': duration,
            **kwargs
        }

        level = LogLevel.INFO if 200 <= status_code < 400 else LogLevel.WARNING
        self._log(level, message, context, extra)

    def log_tool_call(
        self,
        tool_name: str,
        success: bool,
        duration: Optional[float] = None,
        context: Optional[LogContext] = None,
        **kwargs
    ) -> None:
        """
        Log tool execution.

        Args:
            tool_name: Name of the tool
            success: Whether tool call was successful
            duration: Execution duration
            context: Log context
            **kwargs: Additional fields
        """
        status = "✅" if success else "❌"
        message = f"{status} Tool: {tool_name}"

        extra = {
            'tool_name': tool_name,
            'success': success,
            **kwargs
        }

        if duration is not None:
            extra['duration_seconds'] = duration
            message += f" ({duration:.2f}s)"

        self._log(LogLevel.INFO, message, context, extra)


def create_log_context(
    agent_name: Optional[str] = None,
    user_id: Optional[str] = None,
    session_id: Optional[str] = None,
    correlation_id: Optional[str] = None,
    **metadata
) -> LogContext:
    """
    Create a new log context with generated request ID.

    Args:
        agent_name: Name of the agent
        user_id: User identifier
        session_id: Session identifier
        correlation_id: Correlation identifier for tracking related requests
        **metadata: Additional metadata

    Returns:
        LogContext object
    """
    return LogContext(
        request_id=str(uuid.uuid4()),
        agent_name=agent_name,
        user_id=user_id,
        session_id=session_id,
        correlation_id=correlation_id,
        metadata=metadata
    )


def set_request_context(context: LogContext) -> None:
    """
    Set the current request context.

    Args:
        context: LogContext to set
    """
    request_context.set(context.to_dict())


def get_request_context() -> Optional[Dict[str, Any]]:
    """
    Get the current request context.

    Returns:
        Current context dictionary or None
    """
    return request_context.get()


def clear_request_context() -> None:
    """Clear the current request context."""
    request_context.set(None)


# Configure JSON formatter for standard logging
class JSONFormatter(logging.Formatter):
    """Custom formatter for JSON logs."""

    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON."""
        log_data = {
            'timestamp': datetime.fromtimestamp(record.created).isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
        }

        # Add exception info if present
        if record.exc_info:
            log_data['exception'] = self.formatException(record.exc_info)

        # Add extra fields
        if hasattr(record, 'extra'):
            log_data['extra'] = record.extra

        return json.dumps(log_data)


def configure_structured_logging(level: str = "INFO", use_json: bool = False) -> None:
    """
    Configure structured logging for the application.

    Args:
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        use_json: Whether to use JSON formatter
    """
    root_logger = logging.getLogger()
    root_logger.setLevel(level)

    # Remove existing handlers
    root_logger.handlers.clear()

    # Create console handler
    handler = logging.StreamHandler()
    handler.setLevel(level)

    # Set formatter
    if use_json:
        formatter = JSONFormatter()
    else:
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )

    handler.setFormatter(formatter)
    root_logger.addHandler(handler)

    logging.info(f"🔧 Structured logging configured (level={level}, json={use_json})")

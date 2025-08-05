"""Utility functions for modular logging system."""

import inspect
import re
import traceback
from pathlib import Path
from typing import Any

from loguru import logger


def get_caller_info(skip_frames: int = 1) -> dict[str, Any]:
    """Get information about the calling function.

    Args:
        skip_frames: Number of frames to skip in the call stack

    Returns:
        Dictionary with caller information (function, module, line)
    """
    try:
        frame = inspect.currentframe()
        for _ in range(skip_frames + 1):  # +1 to skip this function
            frame = frame.f_back if frame else None

        if frame:
            return {
                "function": frame.f_code.co_name,
                "module": Path(frame.f_code.co_filename).stem,
                "line": frame.f_lineno,
                "file": frame.f_code.co_filename,
            }
    except Exception:
        pass

    return {
        "function": "unknown",
        "module": "unknown",
        "line": 0,
        "file": "unknown",
    }


def log_error(
    error: Exception,
    message: str = "An error occurred",
    include_traceback: bool = True,
    extra_context: dict[str, Any] | None = None,
) -> None:
    """Log an error with enhanced context information.

    Args:
        error: The exception that occurred
        message: Custom message to log
        include_traceback: Whether to include full traceback
        extra_context: Additional context to include in log
    """
    caller_info = get_caller_info(skip_frames=1)

    context = {
        "error_type": type(error).__name__,
        "error_message": str(error),
        "caller": caller_info,
    }

    if extra_context:
        context.update(extra_context)

    if include_traceback:
        context["traceback"] = traceback.format_exc()

    logger.bind(**context).error(f"{message}: {error}")


def log_performance(
    operation: str,
    duration_ms: float,
    threshold_ms: float = 1000.0,
    extra_context: dict[str, Any] | None = None,
) -> None:
    """Log performance metrics for operations.

    Args:
        operation: Name of the operation
        duration_ms: Duration in milliseconds
        threshold_ms: Threshold above which to log as warning
        extra_context: Additional context to include
    """
    caller_info = get_caller_info(skip_frames=1)

    context = {
        "operation": operation,
        "duration_ms": duration_ms,
        "caller": caller_info,
    }

    if extra_context:
        context.update(extra_context)

    if duration_ms > threshold_ms:
        logger.bind(**context).warning(
            f"Slow operation '{operation}' took {duration_ms:.2f}ms"
        )
    else:
        logger.bind(**context).info(
            f"Operation '{operation}' completed in {duration_ms:.2f}ms"
        )


def sanitize_log_message(
    message: str, sensitive_patterns: list[str] | None = None
) -> str:
    """Sanitize log message by removing sensitive information.

    Args:
        message: Original log message
        sensitive_patterns: List of sensitive patterns to redact

    Returns:
        Sanitized message with sensitive data redacted
    """
    if sensitive_patterns is None:
        sensitive_patterns = ["password", "token", "secret", "apikey", "jwt"]

    sanitized = message
    for pattern in sensitive_patterns:
        # Simple case-insensitive replacement

        sanitized = re.sub(
            rf"\b{re.escape(pattern)}\s*[:=]\s*\S+",
            f"{pattern}=[REDACTED]",
            sanitized,
            flags=re.IGNORECASE,
        )

    return sanitized


def create_structured_log(
    level: str,
    message: str,
    component: str | None = None,
    operation: str | None = None,
    user_id: str | None = None,
    request_id: str | None = None,
    extra_fields: dict[str, Any] | None = None,
) -> None:
    """Create a structured log entry with consistent fields.

    Args:
        level: Log level (INFO, WARNING, ERROR, etc.)
        message: Log message
        component: Component/module name
        operation: Operation being performed
        user_id: User identifier
        request_id: Request identifier for tracing
        extra_fields: Additional fields to include
    """
    caller_info = get_caller_info(skip_frames=1)

    context = {
        "component": component or caller_info["module"],
        "operation": operation,
        "user_id": user_id,
        "request_id": request_id,
        "caller": caller_info,
    }

    # Remove None values
    context = {k: v for k, v in context.items() if v is not None}

    if extra_fields:
        context.update(extra_fields)

    # Get the appropriate logger method
    log_method = getattr(logger.bind(**context), level.lower(), logger.info)
    log_method(message)


def format_file_size(size_bytes: int) -> str:
    """Format file size in human-readable format.

    Args:
        size_bytes: Size in bytes

    Returns:
        Formatted size string (e.g., "1.5 MB")
    """
    size = float(size_bytes)
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if size < 1024.0:
            return f"{size:.1f} {unit}"
        size /= 1024.0
    return f"{size:.1f} PB"


def validate_log_level(level: str) -> str:
    """Validate and normalize log level.

    Args:
        level: Log level string

    Returns:
        Normalized log level

    Raises:
        ValueError: If level is invalid
    """
    valid_levels = ["TRACE", "DEBUG", "INFO", "SUCCESS", "WARNING", "ERROR", "CRITICAL"]
    normalized = level.upper().strip()

    if normalized not in valid_levels:
        raise ValueError(f"Invalid log level: {level}. Valid levels: {valid_levels}")

    return normalized


def extract_exception_info(exc: Exception) -> dict[str, Any]:
    """Extract comprehensive information from an exception.

    Args:
        exc: Exception instance

    Returns:
        Dictionary with exception details
    """
    return {
        "type": type(exc).__name__,
        "message": str(exc),
        "module": getattr(exc, "__module__", "unknown"),
        "args": exc.args if hasattr(exc, "args") else [],
        "traceback": traceback.format_exc(),
        "cause": str(exc.__cause__) if exc.__cause__ else None,
        "context": str(exc.__context__) if exc.__context__ else None,
    }

"""Core logging functionality for modular mlogger system.

This module contains the main LoggerManager class that handles
sophisticated Loguru setup using the configuration from config.py.
"""

import contextlib
import sys
import warnings
from collections.abc import Callable
from pathlib import Path
from typing import Any

from loguru import logger

from src.mlogger.config import MLogConfig


class LoggerManager:
    """Central logger management for sophisticated modular logging.

    Features:
    - Configuration-driven setup
    - Separate terminal and file handlers
    - Dynamic level-based file rotation
    - Sensitive data filtering
    - Custom formatter support
    """

    def __init__(self, config: MLogConfig | None = None):
        """Initialize LoggerManager with configuration."""
        self.config = config or MLogConfig()
        self._handlers: list[int] = []
        self._is_setup = False

    def setup(self) -> None:
        """Set up logging handlers based on configuration."""
        if self._is_setup:
            warnings.warn("Logger already setup. Skipping.", stacklevel=2)
            return

        # Remove default handler
        logger.remove()

        # Setup terminal handler
        if self.config.terminal.enabled:
            self._setup_terminal_handler()

        # Setup file handlers
        if self.config.file.enabled:
            self._setup_file_handlers()

        # Configure global settings
        self._configure_global_settings()

        self._is_setup = True
        logger.info("MLogger system initialized successfully")

    def _setup_terminal_handler(self) -> None:
        """Configure terminal (console) output handler."""
        terminal_config = self.config.terminal

        handler_id = logger.add(
            sys.stderr,
            level=terminal_config.level,
            format=self.config.get_terminal_format(),
            colorize=terminal_config.colorize,
            diagnose=terminal_config.diagnose,
            enqueue=terminal_config.enqueue,
            filter=self._create_filter(),
        )

        self._handlers.append(handler_id)
        logger.debug(f"Terminal handler setup with level: {terminal_config.level}")

    def _setup_file_handlers(self) -> None:
        """Configure file output handlers with rotation and filtering."""
        file_config = self.config.file

        # Create base logs directory
        base_path = Path(file_config.base_path)
        base_path.mkdir(parents=True, exist_ok=True)

        # Info level file handler
        if file_config.levels.info:
            info_file = base_path / f"{file_config.name_prefix}_info.log"
            self._add_file_handler(
                file_path=str(info_file),
                level="INFO",
                filter_func=lambda record: record["level"].name in ["INFO", "DEBUG"],
            )

        # Error level file handler
        if file_config.levels.error:
            error_file = base_path / f"{file_config.name_prefix}_error.log"
            self._add_file_handler(
                file_path=str(error_file),
                level="WARNING",
                filter_func=lambda record: record["level"].name
                in ["WARNING", "ERROR", "CRITICAL"],
            )

        # Debug level file handler
        if file_config.levels.debug:
            debug_file = base_path / f"{file_config.name_prefix}_debug.log"
            self._add_file_handler(
                file_path=str(debug_file),
                level="DEBUG",
                filter_func=lambda record: record["level"].name == "DEBUG",
            )

        # Warning level file handler
        if file_config.levels.warning:
            warning_file = base_path / f"{file_config.name_prefix}_warning.log"
            self._add_file_handler(
                file_path=str(warning_file),
                level="WARNING",
                filter_func=lambda record: record["level"].name == "WARNING",
            )

    def _add_file_handler(
        self,
        file_path: str,
        level: str,
        filter_func: Callable[[Any], bool] | None = None,
    ) -> None:
        """Add individual file handler with rotation."""
        file_config = self.config.file

        # Ensure directory exists
        Path(file_path).parent.mkdir(parents=True, exist_ok=True)

        # Combine filters
        combined_filter = self._combine_filters(filter_func)

        handler_id = logger.add(
            file_path,
            level=level,
            format=self.config.get_file_format(),
            rotation=f"{file_config.rotation_mb} MB",
            retention=f"{file_config.retention_days} days",
            compression="zip",
            serialize=False,
            backtrace=True,
            diagnose=file_config.diagnose,
            enqueue=file_config.enqueue,
            filter=combined_filter,
        )

        self._handlers.append(handler_id)
        logger.debug(f"File handler added: {file_path} (level: {level})")

    def _combine_filters(
        self, level_filter: Callable[[Any], bool] | None = None
    ) -> Callable[[Any], bool] | None:
        """Combine level filter with sensitive data filter."""
        sensitivity_filter = self._create_filter()

        if level_filter and sensitivity_filter:
            return lambda record: level_filter(record) and sensitivity_filter(record)
        elif level_filter:
            return level_filter
        elif sensitivity_filter:
            return sensitivity_filter
        else:
            return None

    def _create_filter(self) -> Callable[[Any], bool]:
        """Create filter function for sensitive data."""
        filters_config = self.config.filters

        def filter_sensitive(record: Any) -> bool:
            """Filter function to mask sensitive information."""
            # Get the message
            message = str(record.get("message", ""))

            # Check for sensitive fields
            for sensitive_keyword in filters_config.sensitive_keywords:
                if sensitive_keyword.lower() in message.lower():
                    # Replace sensitive content
                    record["message"] = message.replace(
                        sensitive_keyword, filters_config.redact_replacement
                    )

            return True

        return filter_sensitive

    def _configure_global_settings(self) -> None:
        """Configure global Loguru settings."""
        # Set up exception handling
        if self.config.exception_hooks:
            logger.opt(exception=True)

        # Note: bind_context is applied per logger instance in get_logger()

    def shutdown(self) -> None:
        """Clean shutdown of all handlers."""
        for handler_id in self._handlers:
            with contextlib.suppress(ValueError):
                logger.remove(handler_id)

        self._handlers.clear()
        self._is_setup = False
        logger.info("MLogger system shutdown complete")

    def get_logger(self, name: str | None = None) -> Any:
        """Get a logger instance with optional name binding."""
        if not self._is_setup:
            self.setup()

        # Create logger with bound context
        bound_logger = logger

        # Apply global bind context if configured
        if self.config.bind_context:
            bound_logger = bound_logger.bind(**self.config.bind_context)

        # Add logger name if provided
        if name:
            bound_logger = bound_logger.bind(logger_name=name)

        return bound_logger

    @classmethod
    def from_toml(cls, config_path: str | Path = "log_config.toml") -> "LoggerManager":
        """Create LoggerManager from TOML configuration file."""
        config = MLogConfig.from_toml_file(config_path)
        return cls(config)


# Global logger manager instance
_global_manager: LoggerManager | None = None
_setup_lock = False


def get_logger_manager() -> LoggerManager:
    """Get or create global logger manager instance."""
    global _global_manager
    if _global_manager is None:
        # Auto-setup on first access
        setup_logging_from_toml()

    # At this point _global_manager should be set by setup_logging_from_toml
    if _global_manager is None:
        raise RuntimeError("Failed to initialize logger manager")

    return _global_manager


def setup_logging_from_toml(config_path: str | Path = "log_config.toml") -> None:
    """Setup logging system from TOML configuration file."""
    global _global_manager, _setup_lock

    # Prevent multiple setups in the same process
    if _setup_lock:
        return

    _setup_lock = True

    try:
        manager = LoggerManager.from_toml(config_path)
        manager.setup()
        _global_manager = manager
    except Exception:
        _setup_lock = False  # Reset on error
        raise


def get_logger(name: str | None = None) -> Any:
    """Get a logger instance using the global manager."""
    manager = get_logger_manager()
    return manager.get_logger(name)


def shutdown_logging() -> None:
    """Shutdown the global logging system."""
    global _global_manager
    if _global_manager:
        _global_manager.shutdown()
        _global_manager = None

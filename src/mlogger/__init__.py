"""Modern Modular Loguru Logger System.

A sophisticated, modular logging system built on top of Loguru with:
- TOML-based configuration with advanced sections
- Separate terminal and file handlers
- Custom formatters and filters
- Performance monitoring and sampling
- Future-ready extensibility

Example:
    >>> from mlogger import setup_logging_from_toml, get_logger
    >>> setup_logging_from_toml()  # Load from log_config.toml
    >>> logger = get_logger(__name__)
    >>> logger.info("Ready to log!")
"""

# Core functionality
# Configuration classes

from src.mlogger.config import (
    FileConfig,
    FileLevelsConfig,
    FiltersConfig,
    MLogConfig,
    TerminalConfig,
)
from src.mlogger.core import (
    LoggerManager,
    get_logger,
    get_logger_manager,
    setup_logging_from_toml,
    shutdown_logging,
)

# Utility functions
from src.mlogger.utils import (
    create_structured_log,
    extract_exception_info,
    format_file_size,
    get_caller_info,
    log_error,
    log_performance,
    sanitize_log_message,
    validate_log_level,
)

__version__ = "2.0.0"
__author__ = "Maki & ChatGPT"

# Ensure logging is set up on import (optional, or call setup explicitly elsewhere)
setup_logging_from_toml()

# Expose the global logger
logger = get_logger()  # This will include bind_context and default context

__all__ = [
    "FileConfig",
    "FileLevelsConfig",
    "FiltersConfig",
    "LoggerManager",
    "MLogConfig",
    "TerminalConfig",
    "create_structured_log",
    "extract_exception_info",
    "format_file_size",
    "get_caller_info",
    "get_logger",
    "get_logger_manager",
    "log_error",
    "log_performance",
    "sanitize_log_message",
    "setup_logging_from_toml",
    "shutdown_logging",
    "validate_log_level",
]

# from src.mlogger import get_logger
# mylog = get_logger("custom_name")
# mylog.info("With custom logger_name")

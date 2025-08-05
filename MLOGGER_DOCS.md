# Modular Logging System (mlogger) - Documentation

## Overview

We have successfully refactored the monolithic logging system into a sophisticated modular architecture with the following structure:

```
src/mlogger/
├── __init__.py      # Package entry point with exports
├── config.py        # Configuration management with dataclasses
├── core.py          # Logger management and setup
└── utils.py         # Utility functions for enhanced logging
```

## Key Features

### 1. **Configuration Management (config.py)**

- **TOML Configuration Support**: Load settings from `log_config.toml` with fallback to defaults
- **Dataclass Architecture**: Type-safe configuration with `MLogConfig`, `TerminalConfig`, `FileConfig`, etc.
- **Sophisticated Parsing**: Nested configuration sections for terminal/file handlers, filters, and formatters
- **Validation**: Built-in validation and error handling for configuration values

### 2. **Core Logger Management (core.py)**

- **LoggerManager Class**: Central management of all logging handlers
- **Multiple Handler Support**: Separate terminal and file handlers with independent configuration
- **Dynamic File Handlers**: Level-based file routing (info, error, debug, warning)
- **Filtering System**: Built-in sensitive data filtering and redaction
- **Global Management**: Singleton pattern for application-wide logger management

### 3. **Utility Functions (utils.py)**

- **Caller Information**: `get_caller_info()` for context tracking
- **Error Logging**: Enhanced `log_error()` with exception details and context
- **Performance Monitoring**: `log_performance()` for operation timing
- **Structured Logging**: `create_structured_log()` for consistent log entries
- **Data Sanitization**: `sanitize_log_message()` for sensitive data protection

## Configuration Structure

The system now supports sophisticated TOML configuration:

```toml
[mlog]
level = "INFO"
intercept = true
exception_hooks = true

[mlog.terminal]
enabled = true
level = "DEBUG"
format = "simple"
colorize = true

[mlog.file]
enabled = true
base_path = "logs"
name_prefix = "app"
rotation_mb = 10
retention_days = 7

[mlog.file.levels]
info = true
error = true
debug = false
warning = false

[mlog.filters]
sensitive_keywords = ["password", "token", "secret"]
redact_replacement = "[REDACTED]"

[mlog.formatters]
simple = "<level>{level.name}</level>: <magenta>{name}:{function}:{line}</magenta> | {message}"
full = "<level>{level.name}</level>: {time:YYYY-MM-DD HH:mm:ss} | <cyan>{process.name}:{thread.name}</cyan> | <magenta>{name}:{function}:{line}</magenta> | <level>{message}</level>"
```

## Usage Examples

### Basic Setup

```python
from src.mlogger import setup_logging_from_toml, get_logger

# Setup from TOML config
setup_logging_from_toml("log_config.toml")

# Get logger instance
logger = get_logger(__name__)
logger.info("Application started")
```

### Advanced Usage

```python
from src.mlogger import (
    LoggerManager,
    MLogConfig,
    log_error,
    log_performance,
    get_caller_info
)

# Custom configuration
config = MLogConfig(
    level="DEBUG",
    terminal=TerminalConfig(colorize=True),
    file=FileConfig(rotation_mb=50)
)

# Create manager with custom config
manager = LoggerManager(config)
manager.setup()

# Enhanced logging
log_performance("database_query", 234.5)
try:
    # ... some operation
    pass
except Exception as e:
    log_error(e, "Database operation failed")
```

## Benefits Achieved

1. **Modularity**: Separated concerns into dedicated modules
2. **Type Safety**: Full dataclass support with type hints
3. **Flexibility**: Easy to extend and customize
4. **Maintainability**: Clean, well-documented code structure
5. **Performance**: Efficient filtering and handling
6. **Robustness**: Comprehensive error handling and fallbacks

## Migration from Old System

The old monolithic `src/utils/mlogger.py` remains functional for backward compatibility, but new development should use the modular system:

```python
# Old way (still works)
from src.utils.mlogger import setup_logging_from_toml

# New way (recommended)
from src.mlogger import setup_logging_from_toml
```

## Testing Results

✅ **TOML Configuration Loading**: Successfully loads and parses complex configuration
✅ **Multiple Handlers**: Terminal and file handlers work independently
✅ **Sensitive Data Filtering**: Properly redacts passwords, tokens, etc.
✅ **Performance Logging**: Tracks operation timing with thresholds
✅ **Error Context**: Enhanced error logging with caller information
✅ **File Rotation**: Automatic log file rotation and retention
✅ **Structured Output**: Consistent JSON formatting for file logs
✅ **Lint Compliance**: All code passes ruff formatting and linting

## Next Steps

The modular logging system is now ready for production use and can be easily extended with additional features like:

- Custom log processors
- Remote log shipping
- Advanced filtering rules
- Metrics collection
- Log aggregation

The architecture supports future enhancements while maintaining backward compatibility.

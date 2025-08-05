# --- ADVANCED LOGURU RECIPES (DISABLED, UNCOMMENT TO USE) ---
#
# # 1. Dynamic filter per handler (e.g. only WARNING and above)
# def warn_only_filter(record):
#     return record["level"].no >= loguru_logger.level("WARNING").no
# # Example usage:
# # loguru_logger.add(sys.stderr, filter=warn_only_filter, level="DEBUG")
#
# # 2. Custom formatter with dynamic color
# # def color_formatter(record):
# #     return f"<cyan>{record['name']}</cyan>: {record['message']}"
# # loguru_logger.add(sys.stderr, format=color_formatter)
#
# # 3. Capture warnings as loguru WARNING
# # import warnings
# # showwarning_ = warnings.showwarning
# # def showwarning(message, *args, **kwargs):
# #     loguru_logger.opt(depth=2).warning(message)
# #     showwarning_(message, *args, **kwargs)
# # warnings.showwarning = showwarning
#
# # 4. Custom log level
# # from functools import partialmethod
# # loguru_logger.level("SECURITY", no=35, color="<red>")
# # loguru_logger.__class__.security = partialmethod(loguru_logger.__class__.log, "SECURITY")
# # loguru_logger.security("This is a security log!")
#
# # 5. Split log per task using bind and filter
# # loguru_logger.add("file_A.log", filter=lambda r: r["extra"].get("task") == "A")
# # loguru_logger.add("file_B.log", filter=lambda r: r["extra"].get("task") == "B")
# # loguru_logger.bind(task="A").info("Log for task A")
# # loguru_logger.bind(task="B").info("Log for task B")
#
# # 6. Custom serialization (if needed)
# # import json
# # def serialize(record):
# #     subset = {"timestamp": record["time"].timestamp(), "message": record["message"]}
# #     return json.dumps(subset)
# # def sink(message):
# #     serialized = serialize(message.record)
# #     print(serialized)
# # loguru_logger.add(sink)
#
# # 7. Patch logger to always colorize
# # from functools import partial
# # logger_colored = loguru_logger.opt(colors=True)
# # logger_colored.opt = partial(loguru_logger.opt, colors=True)
# # logger_colored.info("It <green>works</>!")
#
# --- END ADVANCED LOGURU RECIPES ---
"""Custom Loguru Logger Setup (OOP Refactor).

==========================================

Modul ini menyederhanakan integrasi Loguru ke dalam aplikasi Python,
baik synchronous maupun asynchronous. Dirancang agar mudah di-setup,
siap pakai di aplikasi FastAPI, testing (pytest), maupun script CLI.

Fitur:
- Logging ke terminal & file (rotasi size + daily)
- Intercept logging bawaan Python (`logging`, `uvicorn`, dll)
- Decorator `@timer`, `@logger_wraps`, context `log_block`, `LogContext`
- Stacktrace logging untuk debugging mendalam
- Siap pakai di `conftest.py`, support format simple/full
- Support unhandled exception handler untuk sync & async
- Support default `logger.bind()` context
- Konfigurasi via TOML file dengan fallback ke default values

TOML Configuration Support:
- Buat file `log_config.toml` di root project
- Semua setting opsional, akan fallback ke default jika tidak ada
- Contoh usage:
  ```python
  from utils.mlogger import setup_logging_from_toml, logger

  setup_logging_from_toml()  # Load dari log_config.toml
  logger.info("Ready to log!")
  ```

Quick Setup:
  ```python
  from utils.mlogger import setup_logging, logger

  setup_logging(level="DEBUG", to_file=True)
  logger.debug("Quick setup done!")
  ```

Author: Maki & ChatGPT
"""

import asyncio
import functools
import inspect
import logging
import os
import sys
import time
import uuid
from collections.abc import Callable, Iterator
from contextlib import AbstractContextManager, contextmanager
from dataclasses import dataclass
from pathlib import Path
from types import TracebackType
from typing import Any, Literal, ParamSpec, TypeVar

from loguru import logger as loguru_logger

# TOML support - try built-in first (Python 3.11+), then fallback to tomli
try:
    import tomllib
except ImportError:
    try:
        import tomli as tomllib
    except ImportError:
        tomllib = None


# =====================
# Formatter Presets
class LogFormatters:
    """Preset log formatters for Loguru sinks (compatible signature)."""

    @staticmethod
    def simple(record: Any) -> str:
        # Fields are already sanitized by _filter_sensitive
        return f"<level>{record['level'].name}</level>: <magenta>{record['name']}:{record['function']}:{record['line']}</magenta> | {record['message']} | {record['extra']}"

    @staticmethod
    def full(record: Any) -> str:
        # Fields are already sanitized by _filter_sensitive
        return (
            f"<level>{record['level'].name}</level>: {record['time']:YYYY-MM-DD HH:mm:ss} | "
            f"<cyan>{record['process'].name}:{record['thread'].name}</cyan> | "
            f"<magenta>{record['name']}:{record['function']}:{record['line']}</magenta> | "
            f"<level>{record['message']}</level> | {record['extra']}"
        )

    @staticmethod
    def progress(record: Any) -> str:
        end = record["extra"].get("end", "\n")
        return f"[{record['time']:%H:%M:%S}] {record['message']}" + end + "{exception}"


Level = Literal["TRACE", "DEBUG", "INFO", "SUCCESS", "WARNING", "ERROR", "CRITICAL"]


# ============================================Block Kode Konfigurasi Logging
def _load_toml_file(file_path: Path) -> dict[str, Any]:
    """Load TOML file and return parsed data."""
    if not file_path.exists():
        return {}

    if tomllib is None:
        return {}

    try:
        with open(file_path, "rb") as f:
            return tomllib.load(f)
    except Exception:
        return {}


def _extract_logging_config(toml_data: dict[str, Any]) -> dict[str, Any]:
    """Extract and validate logging configuration from TOML data."""
    config_dict = {}

    if "logging" not in toml_data:
        return config_dict

    logging_config = toml_data["logging"]

    # Map TOML keys to LogConfig fields
    valid_fields = {
        "level",
        "to_terminal",
        "to_file",
        "diagnose",
        "enqueue",
        "log_path",
        "name_prefix",
        "size_mb",
        "retention_days",
        "override_stdout",
        "enable_exception_hooks",
        "intercept",
    }

    for key, value in logging_config.items():
        if key in valid_fields:
            config_dict[key] = value
        elif key == "bind_context" and isinstance(value, dict):
            config_dict["bind_context"] = value

    # Handle bind_context from separate section
    if (
        "bind_context" not in config_dict
        and "bind_context" in logging_config
        and isinstance(logging_config["bind_context"], dict)
        and logging_config["bind_context"]
    ):
        config_dict["bind_context"] = logging_config["bind_context"]

    return config_dict


def _validate_log_level(config_dict: dict[str, Any]) -> None:
    """Validate and fix log level in config dictionary."""
    if "level" not in config_dict:
        return

    level = str(config_dict["level"]).upper()
    valid_levels = {"TRACE", "DEBUG", "INFO", "SUCCESS", "WARNING", "ERROR", "CRITICAL"}

    if level not in valid_levels:
        config_dict["level"] = "INFO"
    else:
        config_dict["level"] = level


@dataclass
class LogConfig:
    level: Level = "INFO"
    to_terminal: bool = True
    to_file: bool = False
    diagnose: bool = False
    enqueue: bool = True
    log_path: str = "logs"
    name_prefix: str = "app"
    size_mb: int = 10
    retention_days: int = 7
    override_stdout: bool = False
    formatter_terminal: Any = None  # string/fungsi/callable
    formatter_file: Any = None  # string/fungsi/callable
    bind_context: dict[str, Any] | None = None
    enable_exception_hooks: bool = True
    intercept: bool = True  # intercept std logging/uvicorn

    @classmethod
    def from_toml_file(cls, file_path: str | Path = "log_config.toml") -> "LogConfig":
        """Load configuration from TOML file with fallback to defaults.

        Args:
            file_path: Path to TOML configuration file

        Returns:
            LogConfig instance with settings from file or defaults

        Example:
            >>> config = LogConfig.from_toml_file("log_config.toml")
            >>> config = LogConfig.from_toml_file()  # Uses default path
        """
        file_path = Path(file_path)
        toml_data = _load_toml_file(file_path)
        config_dict = _extract_logging_config(toml_data)
        _validate_log_level(config_dict)

        return cls(**config_dict)

    @classmethod
    def from_toml_string(cls, toml_string: str) -> "LogConfig":
        """Load configuration from TOML string with fallback to defaults.

        Args:
            toml_string: TOML configuration as string

        Returns:
            LogConfig instance with settings from string or defaults
        """
        if tomllib is None:
            return cls()

        try:
            toml_data = tomllib.loads(toml_string)
            config_dict = _extract_logging_config(toml_data)
            _validate_log_level(config_dict)
            return cls(**config_dict)
        except Exception:
            return cls()


class LoggerManager:
    class _InterceptHandler(logging.Handler):
        def emit(self, record: logging.LogRecord) -> None:
            # Get corresponding Loguru level if it exists.
            level: str | int
            try:
                level = logger.level(record.levelname).name
            except ValueError:
                level = record.levelno

            # Find caller from where originated the logged message.
            frame, depth = inspect.currentframe(), 0
            while frame and (
                depth == 0 or frame.f_code.co_filename == logging.__file__
            ):
                frame = frame.f_back
                depth += 1

            logger.opt(depth=depth, exception=record.exc_info).log(
                level, record.getMessage()
            )

    def __init__(self, config: LogConfig):
        self.config = config

    def setup(self):
        # Set log level color and completely remove all existing handlers
        loguru_logger.level("INFO", color="<cyan>")
        loguru_logger.remove()

        Path(self.config.log_path).mkdir(parents=True, exist_ok=True)

        # Setup intercept handler for stdlib logging if enabled
        if getattr(self.config, "intercept", False):
            logging.basicConfig(
                handlers=[self._InterceptHandler()], level=0, force=True
            )

        # Apply patch for sensitive data filtering
        loguru_logger.patch(self._filter_sensitive)

        # --- Terminal sink ---
        if self.config.to_terminal:
            # Use a safe format that won't cause issues
            terminal_format = (
                "<level>{level.name}</level>: "
                "<magenta>{name}:{function}:{line}</magenta> | "
                "{message}"
            )

            loguru_logger.add(
                sink=sys.stderr,
                level=self.config.level,
                format=terminal_format,
                backtrace=True,
                diagnose=self.config.diagnose,
                enqueue=self.config.enqueue,
                serialize=False,
                colorize=True,
            )

        # --- File sink ---
        if self.config.to_file:
            file_format = (
                "{level.name}: {time:YYYY-MM-DD HH:mm:ss} | "
                "{process.name}:{thread.name} | "
                "{name}:{function}:{line} | "
                "{message}"
            )

            for level in ("INFO", "ERROR"):
                loguru_logger.add(
                    sink=f"{self.config.log_path}/{self.config.name_prefix}_{level.lower()}.log",
                    level=level,
                    format=file_format,
                    diagnose=self.config.diagnose,
                    backtrace=True,
                    enqueue=self.config.enqueue,
                    serialize=True,
                    rotation=f"{self.config.size_mb} MB",
                    retention=f"{self.config.retention_days} days",
                    opener=LoggerManager._opener,
                    colorize=False,
                )

        if self.config.override_stdout:
            self._patch_stdout()
        if self.config.enable_exception_hooks:
            self._setup_exception_hooks()

        # Bind context if provided
        if self.config.bind_context:
            global logger
            logger = loguru_logger.bind(**self.config.bind_context)

        loguru_logger.info("Logging initialized")

    @staticmethod
    def _filter_sensitive(record: Any) -> None:
        msg = str(record["message"]).lower()
        if any(
            word in msg
            for word in ["password", "token", "secret", "apikey", "authorization"]
        ):
            record["message"] = "[REDACTED]"

        # Sanitize function and name fields to prevent color directive conflicts
        if record.get("function"):
            record["function"] = (
                str(record["function"]).replace("<", "\\<").replace(">", "\\>")
            )
        if record.get("name"):
            record["name"] = str(record["name"]).replace("<", "\\<").replace(">", "\\>")

        return None

    def _patch_stdout(self) -> None:
        class StreamToLogger:
            def __init__(self, level: Level = "INFO"):
                self.level = level

            def write(self, buffer: str) -> None:
                for line in buffer.rstrip().splitlines():
                    loguru_logger.log(self.level, line.rstrip())

            def flush(self) -> None:
                # Required by stream interface but no action needed for loguru
                pass

        sys.stdout = StreamToLogger("INFO")
        sys.stderr = StreamToLogger("ERROR")

    def _setup_exception_hooks(self) -> None:
        def global_exception_hook(
            exc_type: type, exc_value: Exception, exc_traceback: TracebackType
        ):
            if issubclass(exc_type, KeyboardInterrupt):
                sys.__excepthook__(exc_type, exc_value, exc_traceback)
                return
            loguru_logger.opt(exception=exc_value).critical("Unhandled exception")

        def handle_async_exception(
            loop: asyncio.AbstractEventLoop,
            context: dict[str, Any],
        ):
            _ = loop  # Mark as intentionally unused (required by asyncio interface)
            msg = context.get("message", "Async exception")
            exception = context.get("exception")
            loguru_logger.opt(exception=exception).error(f"Async exception: {msg}")

        sys.excepthook = global_exception_hook
        try:
            loop = asyncio.get_event_loop()
            loop.set_exception_handler(handle_async_exception)
        except RuntimeError:
            pass

    @staticmethod
    def _opener(file: str, flags: int) -> int:
        return os.open(file, flags, 0o600)

    # ==============================================================End Block Setup

    @staticmethod
    def log_traced(
        *,
        level: Level = "DEBUG",
        entry: bool = True,
        exit: bool = True,
        timing: bool = True,
    ) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
        """Decorator: Log entry, exit, arguments, result, error, dan durasi eksekusi fungsi.

        Cocok untuk tracing dan profiling fungsi logika bisnis, service, dsb.

        Args:
            level: Level loguru (default: DEBUG)
            entry: Log entry dan argumen fungsi (default: True)
            exit: Log hasil return fungsi (default: True)
            timing: Log durasi eksekusi fungsi (default: True)

        Example:
            >>> @LoggerManager.log_traced(level="INFO")
            ... def foo(x, y):
            ...     return x + y
            >>> foo(1, 2)
            # INFO: → foo | args=(1, 2), kwargs={}
            # INFO: [foo] Starting...
            # INFO: [foo] Done in 0.123s
            # INFO: ← foo | result=3

        """
        function_params = ParamSpec("function_params")
        function_return = TypeVar("function_return")

        def decorator(
            func: Callable[function_params, function_return],
        ) -> Callable[function_params, function_return]:
            @functools.wraps(func)
            def wrapper(
                *args: function_params.args, **kwargs: function_params.kwargs
            ) -> function_return:
                op = func.__name__
                if entry:
                    loguru_logger.log(level, f"→ {op} | args={args}, kwargs={kwargs}")
                start = time.perf_counter() if timing else None
                try:
                    if timing:
                        loguru_logger.log(level, f"[{op}] Starting...")
                    result = func(*args, **kwargs)
                    if timing and start is not None:
                        loguru_logger.log(
                            level, f"[{op}] Done in {time.perf_counter() - start:.3f}s"
                        )
                except Exception as e:
                    loguru_logger.exception(f"Exception in function {op}: {e}")
                    raise
                if exit:
                    loguru_logger.log(level, f"← {op} | result={result}")
                return result

            return wrapper

        return decorator

    @staticmethod
    def log_block(
        operation: str, level: Level = "INFO"
    ) -> AbstractContextManager[None]:
        """Context manager: Log waktu mulai, selesai, dan durasi blok kode.

        Use case:
            - Profiling/monitoring blok kode
        Args:
            operation (str): Nama operasi yang sedang dijalankan.
            level (Level, optional): Level logging. Defaults to "INFO".


        Returns:
            AbstractContextManager[None]: Context manager untuk logging blok kode.

        Example:
            >>> with LoggerManager.log_block("proses data"):
            ...     # kode yang ingin dilog
            ...     pass

        """

        @contextmanager
        def _block() -> Iterator[None]:
            start = time.perf_counter()
            loguru_logger.log(level, f"[{operation}] Starting...")
            try:
                yield
                loguru_logger.log(
                    level, f"[{operation}] Done in {time.perf_counter() - start:.3f}s"
                )
            except Exception as e:
                loguru_logger.exception(f"[{operation}] Failed: {e}")
                raise

        return _block()

    class LogContext:
        """Context manager (OOP): Log waktu mulai, selesai, dan durasi blok kode, bisa di-extend.

        Untuk 90% kasus, log_block sudah cukup dan sangat praktis.
        Pakai LogContext jika Anda butuh OOP-style, custom behavior, atau ingin context manager yang bisa di-extend.

        Use case:
            - Profiling/monitoring blok kode dengan kebutuhan OOP atau custom state
            - Extend class ini untuk menambah perilaku logging

        Example:
            >>> with LoggerManager.LogContext("proses data"):
            ...     ...
            # INFO: [proses data] Starting...
            # INFO: [proses data] Done in 0.789s
        """

        def __init__(self, operation: str, level: Level = "INFO"):
            self.operation = operation
            self.level = level
            self.start_time = None
            self._time = time

        def __enter__(self):
            self.start_time = self._time.perf_counter()
            loguru_logger.log(self.level, f"[{self.operation}] Starting...")
            return self

        def __exit__(
            self,
            exc_type: type | None,
            exc_val: Exception | None,
            exc_tb: TracebackType | None,
        ) -> None:
            if self.start_time is not None:
                duration = self._time.perf_counter() - self.start_time
            else:
                duration = 0.0
            if exc_type:
                loguru_logger.error(
                    f"[{self.operation}] Failed after {duration:.3f}s: {exc_val}"
                )
            else:
                loguru_logger.log(
                    self.level, f"[{self.operation}] Done in {duration:.3f}s"
                )


# --- Logger khusus progress/debug (log di satu baris) ---


# --- Progress formatter (preset) ---
def _progress_formatter(record: Any) -> str:
    """Format log record for progress logging (single line, Loguru compatible)."""
    return LogFormatters.progress(record)


logger_progress = loguru_logger.bind()
_progress_handler_id = logger_progress.add(
    sys.stderr, format=_progress_formatter, level="DEBUG"
)


logger = loguru_logger


def caller_info():
    """Get the caller's information for logging context.

    This function retrieves the filename, function name, and line number of the caller.

    Returns:
        str: Caller information in the format "filename:function:line_number"
    """
    frame = inspect.currentframe()
    # Go back two frames: caller_info -> log_exception_with_caller -> actual caller
    if (
        frame is not None
        and frame.f_back is not None
        and frame.f_back.f_back is not None
    ):
        outer_frame = frame.f_back.f_back
        info = inspect.getframeinfo(outer_frame)
        return f"{info.filename}:{info.function}:{info.lineno}"
    return "unknown"


def log_exception_with_caller(exc: Exception):
    """Log exception with caller information.

    This function logs the exception with the caller's filename, function name, and line number.

    Args:
        exc (Exception): The exception to log.

    Example:
        >>> try:
        ...     1 / 0
        ... except Exception as e:
        ...     log_exception_with_caller(e)
    """
    logger.bind(caller=caller_info()).opt(exception=exc).error(
        "Unhandled exception in service"
    )


def log_error(exc: Exception, msg: str = ""):
    """Log error with exception traceback.

    Example:
        >>> from utils.mlogger import log_error
        >>> try:
        ...     1 / 0
        ... except Exception as e:
        ...     log_error(e, "Division error")
    """
    loguru_logger.opt(exception=exc).error(msg or str(exc))


def request_id() -> str:
    """Generate a unique request ID (UUID).

    Example:
        >>> from utils.mlogger import request_id
        >>> rid = request_id()
        >>> print(rid)
    """
    return str(uuid.uuid4())


def parse_log_level(level: str) -> Level:
    """Parse log level string to Loguru Level."""
    allowed = {"TRACE", "DEBUG", "INFO", "SUCCESS", "WARNING", "ERROR", "CRITICAL"}
    lvl = str(level).upper()
    return lvl if lvl in allowed else "INFO"  # type: ignore


def setup_logging_from_toml(
    config_file: str | Path = "log_config.toml",
) -> LoggerManager:
    """Convenience function to setup logging from TOML configuration file.

    This is the easiest way to setup logging in your application:

    Example:
        >>> from utils.mlogger import setup_logging_from_toml, logger
        >>> setup_logging_from_toml("log_config.toml")
        >>> logger.info("Logging is ready!")

    Args:
        config_file: Path to TOML configuration file (default: "log_config.toml")

    Returns:
        LoggerManager instance for further customization if needed
    """
    config = LogConfig.from_toml_file(config_file)
    manager = LoggerManager(config)
    manager.setup()
    return manager


def setup_logging(
    level: Level = "INFO",
    to_terminal: bool = True,
    to_file: bool = False,
    log_path: str = "logs",
    **kwargs,
) -> LoggerManager:
    """Convenience function to setup logging with direct parameters.

    Example:
        >>> from utils.mlogger import setup_logging, logger
        >>> setup_logging(level="DEBUG", to_file=True)
        >>> logger.debug("Debug logging enabled!")

    Args:
        level: Log level
        to_terminal: Enable terminal logging
        to_file: Enable file logging
        log_path: Directory for log files
        **kwargs: Additional LogConfig parameters

    Returns:
        LoggerManager instance
    """
    config = LogConfig(
        level=level,
        to_terminal=to_terminal,
        to_file=to_file,
        log_path=log_path,
        **kwargs,
    )
    manager = LoggerManager(config)
    manager.setup()
    return manager


__all__ = [
    "LogConfig",
    "LoggerManager",
    "caller_info",
    "log_error",
    "log_exception_with_caller",
    "logger",
    "logger_progress",
    "parse_log_level",
    "request_id",
    "setup_logging",
    "setup_logging_from_toml",
]

"""Configuration management for modular logging system."""

import warnings
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Literal

# TOML support
try:
    import tomllib
except ImportError:
    try:
        import tomli as tomllib
    except ImportError:
        tomllib = None

Level = Literal["TRACE", "DEBUG", "INFO", "SUCCESS", "WARNING", "ERROR", "CRITICAL"]


@dataclass
class TerminalConfig:
    """Configuration for terminal/console output."""

    enabled: bool = True
    level: Level = "INFO"
    format: str = "simple"
    colorize: bool = True
    diagnose: bool = False
    enqueue: bool = True


@dataclass
class FileLevelsConfig:
    """Configuration for level-based file handlers."""

    info: bool = True
    error: bool = True
    debug: bool = False
    warning: bool = False


@dataclass
class FileConfig:
    """Configuration for file logging."""

    enabled: bool = True
    base_path: str = "logs"
    name_prefix: str = "app"
    rotation_mb: int = 10
    retention_days: int = 7
    enqueue: bool = True
    diagnose: bool = False
    levels: FileLevelsConfig = field(default_factory=FileLevelsConfig)


@dataclass
class FiltersConfig:
    """Configuration for content filtering and redaction."""

    sensitive_keywords: list[str] = field(
        default_factory=lambda: [
            "password",
            "token",
            "secret",
            "apikey",
            "authorization",
            "jwt",
        ]
    )
    redact_replacement: str = "[REDACTED]"
    exclude_modules: list[str] = field(default_factory=list)
    include_only: list[str] = field(default_factory=list)


@dataclass
class MLogConfig:
    """Main configuration class for modular logging system."""

    # Global settings
    level: Level = "INFO"
    intercept: bool = True
    exception_hooks: bool = True

    # Handler configurations
    terminal: TerminalConfig = field(default_factory=TerminalConfig)
    file: FileConfig = field(default_factory=FileConfig)

    # Advanced features
    filters: FiltersConfig = field(default_factory=FiltersConfig)
    custom_formatters: dict[str, str] = field(default_factory=dict)
    bind_context: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Initialize default formatters if not provided."""
        if not self.custom_formatters:
            self.custom_formatters = {
                "simple": "<level>{level.name}</level>: <magenta>{name}:{function}:{line}</magenta> | {message}",
                "full": "<level>{level.name}</level>: {time:YYYY-MM-DD HH:mm:ss} | <cyan>{process.name}:{thread.name}</cyan> | <magenta>{name}:{function}:{line}</magenta> | <level>{message}</level> | {extra}",
                "minimal": "{level.name}: {message}",
                "json": '{"timestamp": "{time:YYYY-MM-DD HH:mm:ss}", "level": "{level.name}", "message": "{message}", "module": "{name}", "function": "{function}", "line": {line}}',
            }

    @classmethod
    def from_toml_file(cls, file_path: str | Path = "log_config.toml") -> "MLogConfig":
        """Load configuration from TOML file with sophisticated parsing."""
        file_path = Path(file_path)

        if not file_path.exists():
            warnings.warn(
                f"Config file {file_path} not found. Using defaults.", stacklevel=2
            )
            return cls()

        if tomllib is None:
            warnings.warn("TOML library not available. Using defaults.", stacklevel=2)
            return cls()

        try:
            with open(file_path, "rb") as f:
                data = tomllib.load(f)

            if "mlog" not in data:
                warnings.warn(
                    "No [mlog] section found in config. Using defaults.", stacklevel=2
                )
                return cls()

            return cls._from_mlog_section(data["mlog"])

        except Exception as e:
            warnings.warn(f"Error loading config: {e}. Using defaults.", stacklevel=2)
            return cls()

    @classmethod
    def _from_mlog_section(cls, mlog_data: dict[str, Any]) -> "MLogConfig":
        """Parse [mlog] section and create config instance."""
        config_kwargs = {}

        # Global settings
        for key in ["level", "intercept", "exception_hooks"]:
            if key in mlog_data:
                config_kwargs[key] = mlog_data[key]

        # Terminal configuration
        if "terminal" in mlog_data:
            terminal_data = mlog_data["terminal"]
            config_kwargs["terminal"] = TerminalConfig(**{
                k: v
                for k, v in terminal_data.items()
                if k in TerminalConfig.__dataclass_fields__
            })

        # File configuration
        if "file" in mlog_data:
            file_data = mlog_data["file"]
            levels_data = file_data.pop("levels", {})

            file_config = FileConfig(**{
                k: v
                for k, v in file_data.items()
                if k in FileConfig.__dataclass_fields__ and k != "levels"
            })

            if levels_data:
                file_config.levels = FileLevelsConfig(**{
                    k: v
                    for k, v in levels_data.items()
                    if k in FileLevelsConfig.__dataclass_fields__
                })

            config_kwargs["file"] = file_config

        # Filters configuration
        if "filters" in mlog_data:
            filters_data = mlog_data["filters"]
            config_kwargs["filters"] = FiltersConfig(**{
                k: v
                for k, v in filters_data.items()
                if k in FiltersConfig.__dataclass_fields__
            })

        # Other sections
        if "formatters" in mlog_data:
            config_kwargs["custom_formatters"] = mlog_data["formatters"]

        if "bind_context" in mlog_data:
            config_kwargs["bind_context"] = mlog_data["bind_context"]

        return cls(**config_kwargs)

    def get_terminal_format(self) -> str:
        """Get formatter string for terminal output."""
        format_name = self.terminal.format
        return self.custom_formatters.get(format_name, self.custom_formatters["simple"])

    def get_file_format(self) -> str:
        """Get formatter string for file output."""
        # For files, prefer full format by default
        return self.custom_formatters.get("full", self.custom_formatters["simple"])

    def should_create_level_file(self, level: str) -> bool:
        """Check if a specific level file should be created."""
        level_lower = level.lower()
        return getattr(self.file.levels, level_lower, False)

    def get_enabled_file_levels(self) -> list[str]:
        """Get list of enabled file level handlers."""
        enabled_levels = [
            level_name.upper()
            for level_name in ["info", "error", "debug", "warning"]
            if getattr(self.file.levels, level_name, False)
        ]
        return enabled_levels

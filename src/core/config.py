"""core configuration Module Will Use Pydantic-settings for configuration management."""

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from src._version import __version__ as version


class ServerSettings(BaseSettings):
    """Settings related to the server (Uvicorn)."""

    host: str = Field("0.0.0.0", alias="UVICORN_HOST")
    port: int = Field(8000, alias="UVICORN_PORT")
    reload: bool = Field(True, alias="UVICORN_RELOAD")
    workers: int = Field(1, alias="UVICORN_WORKERS")
    log_level: str = Field("info", alias="UVICORN_LOG_LEVEL")
    timeout_keep_alive: int = Field(5, alias="UVICORN_TIMEOUT_KEEP_ALIVE")
    timeout_graceful_shutdown: int = Field(5, alias="UVICORN_TIMEOUT_GRACEFUL_SHUTDOWN")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


class AppSettings(BaseSettings):
    """Settings related to the application secrets."""

    decrypt_key: str = Field(..., alias="APP_DECRYPT_KEY")
    secret_key: str = Field(..., alias="APP_SECRET_KEY")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


class Config(BaseSettings):
    """Core configuration settings for the application."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",  # Ignore extra fields not defined in the model
        case_sensitive=False,  # Environment variables are case-insensitive by default
        env_nested_delimiter="__",  # Support nested env vars like SERVER__HOST
        nested_model_default_partial_update=True,  # Allow partial updates for nested models
    )

    service: str = "mod-apiparser"
    version: str = version
    environment: str = "development"

    server: ServerSettings = ServerSettings()  # type: ignore
    app: AppSettings = AppSettings()  # type: ignore

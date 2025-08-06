from enum import StrEnum  # Python 3.11+

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from src._version import __version__ as version


class EnvironmentEnum(StrEnum):
    """Enum for different environments."""

    DEVELOPMENT = "development"
    PRODUCTION = "production"
    TESTING = "testing"


class Settings(BaseSettings):
    """Core configuration settings for the application (flat structure)."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="forbid",
        case_sensitive=False,
    )

    service: str = "mod-apiparser"
    version: str = version
    username: str = Field(..., alias="ADMIN_USERNAME")
    password: str = Field(..., alias="ADMIN_PASSWORD")
    decrypt_key: str = Field(..., alias="KEY_DECRYPT")
    secret_key: str = Field(..., alias="KEY_SECRET")
    algorithm: str = Field(..., alias="KEY_ALGORITHM")
    debug: bool = Field(False, alias="APP_DEBUG")
    environment: EnvironmentEnum = Field(
        default=EnvironmentEnum.PRODUCTION, alias="APP_ENV"
    )
    path_accounts: str = Field("accounts.yaml", alias="PATH_ACCOUNTS")

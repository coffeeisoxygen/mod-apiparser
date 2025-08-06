from functools import lru_cache
from typing import Annotated

from fastapi import Depends
from pydantic import BaseModel

from src.config.settings import EnvironmentEnum, Settings


@lru_cache
def get_settings() -> Settings:
    """Just a cache for settings, so we don't create new instance every time.

    Use This In Service Or Everywhere you need settings.

    Environment files loaded based on APP_ENV:
    - Base: .env (always loaded)
    - development: .env.dev overrides .env values
    - production: .env.prod overrides .env values
    - testing: .env.test overrides .env values
    """
    # Simply create Settings() - env_file loading is handled in model_config
    # The dynamic loading is controlled by the SettingsConfigDict.env_file tuple
    return Settings()


class EnvInfoModel(BaseModel):
    """Model for environment information."""

    service: str
    version: str
    debug: bool
    environment: EnvironmentEnum


def get_env_settings() -> EnvInfoModel:
    """Returns environment settings."""
    settings: Settings = get_settings()
    return EnvInfoModel(
        service=settings.service,
        version=settings.version,
        debug=settings.debug,
        environment=settings.environment,
    )


# Sample Call With Annotated Dependency
EnvInfo = Annotated[EnvInfoModel, Depends(get_env_settings)]

from functools import lru_cache
from typing import Annotated

from fastapi import Depends
from pydantic import BaseModel

from src.config.settings import EnvironmentEnum, Settings


@lru_cache
def get_settings() -> Settings:
    """Just a cache for settings, so we don't create new instance every time.

    Use This In Service Or Everywhere you need settings.
    """
    return Settings()  # type: ignore


class EnvInfoModel(BaseModel):
    """Model for environment information."""

    services: str
    version: str
    debug: bool
    environment: EnvironmentEnum


def get_env_settings() -> EnvInfoModel:
    """Returns environment settings."""
    settings: Settings = get_settings()
    return EnvInfoModel(
        services=settings.service,
        version=settings.version,
        debug=settings.debug,
        environment=settings.environment,
    )


# Sample Call With Anotated Dependency
EnvInfo = Annotated[EnvInfoModel, Depends(get_env_settings)]

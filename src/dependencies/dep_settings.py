import os
from functools import lru_cache
from typing import Annotated

from fastapi import Depends
from pydantic import BaseModel

from src.config.settings import EnvironmentEnum, Settings


@lru_cache
def get_settings() -> Settings:
    """Dynamic environment loading using _env_file parameter."""
    app_env = os.getenv("APP_ENV", "development").lower()
    env_files = [".env"]  # Base file always loaded first

    if app_env == "production":
        env_files.append(".env.prod")
    elif app_env == "testing":
        env_files.append(".env.test")
    else:  # development (default)
        env_files.append(".env.dev")

    # Using Pydantic Settings _env_file parameter for runtime loading
    return Settings(_env_file=env_files)  # type: ignore


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

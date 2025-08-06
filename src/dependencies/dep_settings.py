import os
from functools import lru_cache
from typing import Annotated

from fastapi import Depends

from src.config.settings import (
    AppConfig,
    JWTConfig,
    PathConfig,
    SecurityConfig,
    Settings,
)


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


def get_app_config() -> AppConfig:
    """Returns app configuration from settings."""
    settings: Settings = get_settings()
    return settings.app


def get_jwt_config() -> JWTConfig:
    """Returns JWT configuration from settings."""
    settings: Settings = get_settings()
    return settings.jwt


def get_security_config() -> SecurityConfig:
    """Returns security configuration from settings."""
    settings: Settings = get_settings()
    return settings.security


def get_path_config() -> PathConfig:
    """Returns path configuration from settings."""
    settings: Settings = get_settings()
    return settings.paths


# FastAPI Dependencies
AppConfigDep = Annotated[AppConfig, Depends(get_app_config)]
JWTConfigDep = Annotated[JWTConfig, Depends(get_jwt_config)]
SecurityConfigDep = Annotated[SecurityConfig, Depends(get_security_config)]
PathConfigDep = Annotated[PathConfig, Depends(get_path_config)]
SettingsDep = Annotated[Settings, Depends(get_settings)]

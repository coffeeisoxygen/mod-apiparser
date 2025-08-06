from enum import StrEnum
from pathlib import Path

from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from src._version import __version__ as version


class EnvironmentEnum(StrEnum):
    """Environment types."""

    DEVELOPMENT = "development"
    PRODUCTION = "production"
    TESTING = "testing"


class AppConfig(BaseModel):
    """Application configuration."""

    debug: bool
    env: EnvironmentEnum
    service: str
    version: str


class SecurityConfig(BaseModel):
    """Security and encryption configuration."""

    secret_key: str
    algorithm: str


class JWTConfig(BaseModel):
    """JWT token configuration."""

    algorithm: str
    secret_key: str
    access_token_expire_minutes: int
    refresh_token_expire_days: int
    issuer: str
    audience: str
    private_key_path: str
    public_key_path: str
    key_size: int
    verify_signature: bool
    verify_audience: bool
    verify_issuer: bool
    verify_expiration: bool
    blacklist_enabled: bool
    blacklist_token_checks: bool
    require_https: bool
    cookie_secure: bool
    cookie_samesite: str

    @property
    def key_file_path(self) -> Path:
        """Get JWT key file path as Path object."""
        return Path(self.private_key_path).parent / "jwt_key"


class PathConfig(BaseModel):
    """File paths configuration."""

    users: str
    modules: str
    keys: str


class Settings(BaseSettings):
    """Application settings with nested configuration."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="allow",
    )

    # Application Settings
    app_debug: bool = Field(default=False, alias="APP_DEBUG")
    app_env: EnvironmentEnum = Field(
        default=EnvironmentEnum.DEVELOPMENT, alias="APP_ENV"
    )
    app_service: str = Field(default="mod-apiparser", alias="APP_SERVICE")
    app_version: str = Field(default=version, alias="APP_VERSION")

    # Security Settings
    security_secret_key: str = Field(
        default="default-secret-key", alias="SECURITY_SECRET_KEY"
    )
    security_algorithm: str = Field(default="HS256", alias="SECURITY_ALGORITHM")

    # JWT Settings
    jwt_algorithm: str = Field(default="HS256", alias="JWT_ALGORITHM")
    jwt_secret_key: str = Field(
        default="default-jwt-secret-key", alias="JWT_SECRET_KEY"
    )
    jwt_access_token_expire_minutes: int = Field(
        default=30, alias="JWT_ACCESS_TOKEN_EXPIRE_MINUTES"
    )
    jwt_refresh_token_expire_days: int = Field(
        default=7, alias="JWT_REFRESH_TOKEN_EXPIRE_DAYS"
    )
    jwt_issuer: str = Field(default="otomax-api", alias="JWT_ISSUER")
    jwt_audience: str = Field(default="otomax-client", alias="JWT_AUDIENCE")
    jwt_private_key_path: str = Field(
        default="secrets/keys/jwt_private.pem", alias="JWT_PRIVATE_KEY_PATH"
    )
    jwt_public_key_path: str = Field(
        default="secrets/keys/jwt_public.pem", alias="JWT_PUBLIC_KEY_PATH"
    )
    jwt_key_size: int = Field(default=2048, alias="JWT_KEY_SIZE")
    jwt_verify_signature: bool = Field(default=True, alias="JWT_VERIFY_SIGNATURE")
    jwt_verify_audience: bool = Field(default=True, alias="JWT_VERIFY_AUDIENCE")
    jwt_verify_issuer: bool = Field(default=True, alias="JWT_VERIFY_ISSUER")
    jwt_verify_expiration: bool = Field(default=True, alias="JWT_VERIFY_EXPIRATION")
    jwt_blacklist_enabled: bool = Field(default=True, alias="JWT_BLACKLIST_ENABLED")
    jwt_blacklist_token_checks: bool = Field(
        default=True, alias="JWT_BLACKLIST_TOKEN_CHECKS"
    )
    jwt_require_https: bool = Field(default=False, alias="JWT_REQUIRE_HTTPS")
    jwt_cookie_secure: bool = Field(default=False, alias="JWT_COOKIE_SECURE")
    jwt_cookie_samesite: str = Field(default="lax", alias="JWT_COOKIE_SAMESITE")

    # Path Settings
    path_users: str = Field(default="secrets/users.yaml", alias="PATH_USERS")
    path_modules: str = Field(default="secrets/modules.yaml", alias="PATH_MODULES")
    path_keys: str = Field(default="secrets/keys", alias="PATH_KEYS")

    @property
    def app(self) -> AppConfig:
        """Get app configuration."""
        return AppConfig(
            debug=self.app_debug,
            env=self.app_env,
            service=self.app_service,
            version=self.app_version,
        )

    @property
    def security(self) -> SecurityConfig:
        """Get security configuration."""
        return SecurityConfig(
            secret_key=self.security_secret_key, algorithm=self.security_algorithm
        )

    @property
    def jwt(self) -> JWTConfig:
        """Get JWT configuration."""
        return JWTConfig(
            algorithm=self.jwt_algorithm,
            secret_key=self.jwt_secret_key,
            access_token_expire_minutes=self.jwt_access_token_expire_minutes,
            refresh_token_expire_days=self.jwt_refresh_token_expire_days,
            issuer=self.jwt_issuer,
            audience=self.jwt_audience,
            private_key_path=self.jwt_private_key_path,
            public_key_path=self.jwt_public_key_path,
            key_size=self.jwt_key_size,
            verify_signature=self.jwt_verify_signature,
            verify_audience=self.jwt_verify_audience,
            verify_issuer=self.jwt_verify_issuer,
            verify_expiration=self.jwt_verify_expiration,
            blacklist_enabled=self.jwt_blacklist_enabled,
            blacklist_token_checks=self.jwt_blacklist_token_checks,
            require_https=self.jwt_require_https,
            cookie_secure=self.jwt_cookie_secure,
            cookie_samesite=self.jwt_cookie_samesite,
        )

    @property
    def paths(self) -> PathConfig:
        """Get paths configuration."""
        return PathConfig(
            users=self.path_users, modules=self.path_modules, keys=self.path_keys
        )

    @property
    def jwt_key_file_path(self) -> Path:
        """Get JWT key file path as Path object."""
        return Path(self.jwt_private_key_path).parent / "jwt_key"

    @property
    def is_production(self) -> bool:
        """Check if running in production."""
        return self.app_env == EnvironmentEnum.PRODUCTION

    @property
    def is_development(self) -> bool:
        """Check if running in development."""
        return self.app_env == EnvironmentEnum.DEVELOPMENT

    @property
    def debug(self) -> bool:
        """Get debug flag."""
        return self.app_debug

    @property
    def environment(self) -> EnvironmentEnum:
        """Get environment."""
        return self.app_env

    @property
    def service(self) -> str:
        """Get service name."""
        return self.app_service

    @property
    def version(self) -> str:
        """Get version."""
        return self.app_version

# """core configuration Module Will Use Pydantic-settings for configuration management."""

# from pydantic import Field
# from pydantic_settings import BaseSettings, SettingsConfigDict

# from src._version import __version__ as version


# class KeysSettings(BaseSettings):
#     """Settings related to the application secrets."""

#     decrypt_key: str = Field(..., alias="APP_DECRYPT_KEY")
#     secret_key: str = Field(..., alias="APP_SECRET_KEY")

#     model_config = SettingsConfigDict(
#         env_file=".env",
#         env_file_encoding="utf-8",
#         extra="ignore",
#     )


# class AdminSettings(BaseSettings):
#     """Settings related to the admin user."""

#     username: str = Field(..., alias="APP_ADMIN_USERNAME")
#     password: str = Field(..., alias="APP_ADMIN_PASSWORD")

#     model_config = SettingsConfigDict(
#         env_file=".env",
#         env_file_encoding="utf-8",
#         extra="ignore",
#     )


# class HashSettings(BaseSettings):
#     """Settings related to hashing algorithm."""

#     algorithm: str = Field(..., alias="APP_HASH_ALGORITHM")

#     model_config = SettingsConfigDict(
#         env_file=".env",
#         env_file_encoding="utf-8",
#         extra="ignore",
#     )


# class Config(BaseSettings):
#     """Core configuration settings for the application."""

#     model_config = SettingsConfigDict(
#         env_file=".env",
#         env_file_encoding="utf-8",
#         extra="ignore",  # Ignore extra fields not defined in the model
#         case_sensitive=False,  # Environment variables are case-insensitive by default
#         env_nested_delimiter="__",  # Support nested env vars like SERVER__HOST
#         nested_model_default_partial_update=True,  # Allow partial updates for nested models
#     )

#     service: str = "mod-apiparser"
#     version: str = version
#     environment: str = "development"

#     key: KeysSettings = KeysSettings()  # type: ignore
#     admin: AdminSettings = AdminSettings()  # type: ignore
#     hash: HashSettings = HashSettings()  # type: ignore

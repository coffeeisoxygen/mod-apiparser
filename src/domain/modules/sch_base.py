"""schemas untuk module configuration."""

from functools import lru_cache

from pydantic import BaseModel
from pydantic_settings import (
    BaseSettings,
    PydanticBaseSettingsSource,
    SettingsConfigDict,
    TomlConfigSettingsSource,
)


class RequestConfig(BaseModel):
    method: str
    timeout: int
    max_retries: int
    seconds_between_retries: int


class ResponseConfig(BaseModel):
    min_inbound_characters: int


# Dynamic response config per provider
class ProviderResponseConfig(BaseModel):
    type: str
    list_regex_replacement: list[str]
    list_product_prefixes: list[str]


class ResponsesConfig(BaseModel):
    items: list[ProviderResponseConfig]


class Account(BaseModel):
    type: str
    username: str
    password: str
    pin: str
    msisdn: str
    is_aktif: bool
    base_url: str | None = None


class AccountsConfig(BaseModel):
    default_account: str
    accounts: list[Account]


class Settings(BaseSettings):
    request: RequestConfig
    response: ResponseConfig
    responses: ResponsesConfig
    accounts: AccountsConfig
    model_config = SettingsConfigDict(toml_file="config.toml")

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,  # noqa: ARG003
        env_settings: PydanticBaseSettingsSource,  # noqa: ARG003
        dotenv_settings: PydanticBaseSettingsSource,  # noqa: ARG003
        file_secret_settings: PydanticBaseSettingsSource,  # noqa: ARG003
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        return (TomlConfigSettingsSource(settings_cls),)


@lru_cache
def get_settings() -> Settings:
    """Get the application settings.

    Returns:
        An instance of Settings containing the configuration.
    """
    return Settings()  # type: ignore

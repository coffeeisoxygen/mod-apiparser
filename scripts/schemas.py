from pydantic import BaseModel, Field


class AppSettings(BaseModel):
    debug: bool = Field(..., alias="APP_DEBUG")
    env: str = Field(..., alias="APP_ENV")
    hash_algorithm: str = Field(..., alias="APP_HASH_ALGORITHM")


class KeysSettings(BaseModel):
    decrypt_key: str = Field(..., alias="APP_DECRYPT_KEY")
    secret_key: str = Field(..., alias="APP_SECRET_KEY")


class AdminSettings(BaseModel):
    username: str = Field(..., alias="APP_ADMIN_USERNAME")
    password: str = Field(..., alias="APP_ADMIN_PASSWORD")


class UvicornSettings(BaseModel):
    host: str = Field(..., alias="UVICORN_HOST")
    port: int = Field(..., alias="UVICORN_PORT")
    reload: bool = Field(..., alias="UVICORN_RELOAD")
    log_level: str = Field(..., alias="UVICORN_LOG_LEVEL")
    timeout_keep_alive: int = Field(..., alias="UVICORN_TIMEOUT_KEEP_ALIVE")
    timeout_graceful_shutdown: int = Field(
        ..., alias="UVICORN_TIMEOUT_GRACEFUL_SHUTDOWN"
    )

"""schemas Untuk Modules, supported many API providers."""

import re
from datetime import datetime
from enum import StrEnum

from pydantic import (
    AnyHttpUrl,
    BaseModel,
    ConfigDict,
    EmailStr,
    Field,
    SecretStr,
    field_validator,
)


class EnumAPIProvider(StrEnum):
    DIGIPOS = "digipos"
    ISIMPLE = "isimple"
    MYIM3 = "myim3"
    SIDOMPUL = "sidompul"
    RITA = "rita"
    EXAMPLE = "example"


# REGEX For AccountID (alphanumeric + underscore, 1-10 chars)
VALID_MODULEID_REGEX = re.compile(r"^\w{1,10}$")


class ModuleConfig(BaseModel):
    """schemas base yg akan di inherit oleh schemas lain."""

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        extra="forbid",
    )


class ModuleCredential(ModuleConfig):
    """schemas untuk credential module."""

    moduleid: str = Field(
        description="ini adalah id unik yg akan di hit oleh client (alphanumeric/underscore, 1-10 karakter)",
        examples=["module1", "module2", "module3"],
        frozen=True,  # immutable field klo mau ganti better hapus module ini dan buat baru
        json_schema_extra={"example": "module1"},
    )

    username: SecretStr = Field(
        description="ini adalah username untuk login di api provider",
        json_schema_extra={"example": "WIR6289504"},
    )
    pin: SecretStr = Field(
        description="ini adalah pin untuk login di api provider",
        json_schema_extra={"example": "123456"},
    )
    password: SecretStr = Field(
        description="ini adalah password untuk login di api provider",
        json_schema_extra={"example": "password123"},
    )
    msisdn: str = Field(
        description="ini adalah nomor handphone untuk login di api provider",
        examples=["08123456789", "08234567890"],
        json_schema_extra={"example": "08123456789"},
    )
    email: EmailStr = Field(
        description="ini adalah email untuk login di api provider",
        examples=["user@example.com"],
        json_schema_extra={"example": "user@example.com"},
    )
    base_url: AnyHttpUrl = Field(
        description="Masukan Url Tempat Api Provider Anda Berada",
        json_schema_extra={"example": "http://10.0.0.3:10003/"},
    )

    @field_validator("moduleid")
    @classmethod
    def validate_moduleid(cls, v: str) -> str:
        """Validasi moduleid harus sesuai regex."""
        if not VALID_MODULEID_REGEX.match(v):
            raise ValueError("moduleid harus alphanumeric/underscore, 1-10 karakter")
        return v


class ModuleCreate(ModuleCredential):
    """schemas untuk membuat module baru."""

    provider: EnumAPIProvider = Field(
        description="ini adalah provider api yang digunakan",
        examples=[e.value for e in EnumAPIProvider],
        json_schema_extra={"example": EnumAPIProvider.EXAMPLE.value},
    )

    is_active: bool = Field(
        description="ini adalah status aktif module",
        json_schema_extra={"example": True},
    )
    # Optional Sections /Fields Metadata
    name: str | None = Field(
        description="ini masukan nama asli module pada account api provider anda.",
        examples=["AFCell", "AFCel2", "AFCel3"],
    )

    description: str | None = Field(
        description="ini adalah metada data atau deskripsi module",
        json_schema_extra={
            "example": "ini adalah module utama transaksi, dan lain lain"
        },
    )

    @field_validator("provider", mode="before")
    @classmethod
    def validate_provider(cls, v: EnumAPIProvider) -> EnumAPIProvider:
        """Validasi provider harus sesuai enum."""
        if not isinstance(v, EnumAPIProvider):
            raise ValueError("provider harus salah satu dari EnumAPIProvider")  # noqa: TRY004
        return v

    @field_validator("is_active", mode="before")
    @classmethod
    def validate_is_active(cls, v: bool | str | None) -> bool:
        """Accepts bool, "true", "false", "", or None.

        Converts to bool: "" or None -> False, "true"/True -> True, "false"/False -> False.
        """
        if v is True or v is False:
            return v
        if not v:
            return False
        if isinstance(v, str):
            if v.lower() == "true":
                return True
            if v.lower() == "false":
                return False
        return bool(v)


class ModuleRead(ModuleCreate):
    pass


class ModuleList(BaseModel):
    """schemas untuk list module."""

    modules: list[ModuleRead] = Field(
        description="ini adalah list module yang tersedia",
        json_schema_extra={
            "example": [{"moduleid": "module1"}, {"moduleid": "module2"}]
        },
    )


class ModuleInDB(ModuleCreate):
    created_at: datetime = Field(
        description="Waktu pembuatan module dalam format datetime",
        json_schema_extra={"example": "2023-01-01T00:00:00Z"},
    )

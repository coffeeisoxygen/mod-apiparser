"""schemas Untuk Accounts, supported many API providers."""

import re
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
VALID_ACCOUNTID_REGEX = re.compile(r"^\w{1,10}$")


class AccountConfig(BaseModel):
    """schemas base yg akan di inherit oleh schemas lain."""

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        extra="forbid",
    )


class AccountCredential(AccountConfig):
    """schemas untuk credential akun."""

    accountid: str = Field(
        description="ini adalah id unik yg akan di hit oleh client (alphanumeric/underscore, 1-10 karakter)",
        examples=["account1", "account2", "account3"],
        frozen=True,  # immutable field klo mau ganti better hapus account ini dan buat baru
        json_schema_extra={"example": "account1"},
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

    @field_validator("accountid")
    @classmethod
    def validate_accountid(cls, v: str) -> str:
        """Validasi accountid harus sesuai regex."""
        if not VALID_ACCOUNTID_REGEX.match(v):
            raise ValueError("accountid harus alphanumeric/underscore, 1-10 karakter")
        return v


class AccountCreate(AccountCredential):
    """schemas untuk membuat akun baru."""

    provider: EnumAPIProvider = Field(
        description="ini adalah provider api yang digunakan",
        examples=[e.value for e in EnumAPIProvider],
        json_schema_extra={"example": EnumAPIProvider.EXAMPLE.value},
    )

    is_active: bool = Field(
        description="ini adalah status aktif akun", json_schema_extra={"example": True}
    )
    # Optional Sections /Fields Metadata
    name: str | None = Field(
        description="ini masukan nama asli akun pada account api provider anda.",
        examples=["AFCell", "AFCel2", "AFCel3"],
    )

    description: str | None = Field(
        description="ini adalah metada data atau deskripsi akun",
        json_schema_extra={"example": "ini adalah akun utama transaksi, dan lain lain"},
    )

    @field_validator("provider", mode="before")
    @classmethod
    def validate_provider(cls, v: EnumAPIProvider) -> EnumAPIProvider:
        """Validasi provider harus sesuai enum."""
        if not isinstance(v, EnumAPIProvider):
            raise ValueError("provider harus salah satu dari EnumAPIProvider")  # noqa: TRY004
        return v


class AccountRead(AccountCreate):
    pass


class AccountList(BaseModel):
    """schemas untuk list akun."""

    accounts: list[AccountRead] = Field(
        description="ini adalah list akun yang tersedia",
        json_schema_extra={
            "example": [{"accountid": "account1"}, {"accountid": "account2"}]
        },
    )

"""schemas untuk membuat token."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class TokenPayload(BaseModel):
    """Schema untuk payload JWT token."""

    # Standard JWT Claims (RFC 7519)
    sub: str = Field(..., description="Subject - User ID atau identifier")
    iss: str = Field(..., description="Issuer - Siapa yang mengeluarkan token")
    aud: str = Field(..., description="Audience - Untuk siapa token ini")
    exp: int = Field(..., description="Expiration time - Unix timestamp")
    iat: int = Field(..., description="Issued at - Unix timestamp")
    nbf: int | None = Field(None, description="Not before - Unix timestamp")
    jti: str | None = Field(None, description="JWT ID - Unique identifier")

    # Custom Claims untuk aplikasi
    user_id: str | UUID = Field(..., description="ID user yang login")
    username: str = Field(..., description="Username user tersebut")
    is_superuser: bool = Field(
        default=False, description="Apakah user adalah superuser"
    )
    token_type: str = Field(..., description="access_token atau refresh_token")

    model_config = ConfigDict(json_encoders={UUID: str})


class TokenCreate(BaseModel):
    """Schema untuk membuat token baru."""

    user_id: str | UUID = Field(..., description="ID user")
    username: str = Field(..., description="Username user")
    is_superuser: bool = Field(default=False, description="Status superuser")
    token_type: str = Field(default="access_token", description="Tipe token yg dibuat")

    model_config = ConfigDict(json_encoders={UUID: str})


class TokenResponse(BaseModel):
    """Schema untuk response token."""

    access_token: str = Field(..., description="JWT access token")
    refresh_token: str = Field(..., description="JWT refresh token")
    token_type: str = Field(default="bearer", description="Tipe token (bearer)")
    expires_in: int = Field(..., description="Waktu expired dalam detik")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVaCJ9...",
                "refresh_token": "eyJhbGciOiJIUzI1NiIssInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
                "expires_in": 1800,
            }
        }
    )


class TokenData(BaseModel):
    """Schema untuk data token yang sudah di-decode."""

    user_id: str | UUID = Field(..., description="ID user")
    username: str = Field(..., description="Username user")
    is_superuser: bool = Field(default=False, description="Status superuser")
    token_type: str = Field(..., description="Tipe token (access_token/refresh_token)")
    exp: datetime = Field(..., description="Waktu expired")
    iat: datetime = Field(..., description="Waktu issued")

    model_config = ConfigDict(
        json_encoders={UUID: str, datetime: lambda v: v.isoformat()}
    )


class TokenRefresh(BaseModel):
    """Schema untuk refresh token request."""

    refresh_token: str = Field(..., description="Refresh token yang valid")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {"refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."}
        }
    )


class TokenValidation(BaseModel):
    """Schema untuk validasi token."""

    token: str = Field(..., description="Token yang akan divalidasi")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {"token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."}
        }
    )


class TokenBlacklist(BaseModel):
    """Schema untuk blacklist token."""

    jti: str = Field(..., description="JWT ID dari token")
    user_id: str | UUID = Field(..., description="ID user pemilik token")
    token_type: str = Field(..., description="Tipe token")
    blacklisted_at: datetime = Field(
        default_factory=datetime.now, description="Waktu diblacklist"
    )
    reason: str | None = Field(None, description="Alasan diblacklist")

    model_config = ConfigDict(
        json_encoders={UUID: str, datetime: lambda v: v.isoformat()}
    )


class TokenIntrospection(BaseModel):
    """Schema untuk introspeksi token (RFC 7662)."""

    active: bool = Field(..., description="Apakah token masih aktif")
    scope: str | None = Field(None, description="Scope token")
    client_id: str | None = Field(None, description="Client ID")
    username: str | None = Field(None, description="Username")
    token_type: str | None = Field(None, description="Tipe token")
    exp: int | None = Field(None, description="Expiration time")
    iat: int | None = Field(None, description="Issued at")
    nbf: int | None = Field(None, description="Not before")
    sub: str | None = Field(None, description="Subject")
    aud: str | None = Field(None, description="Audience")
    iss: str | None = Field(None, description="Issuer")
    jti: str | None = Field(None, description="JWT ID")


class TokenError(BaseModel):
    """Schema untuk error response token."""

    error: str = Field(..., description="Kode error")
    error_description: str = Field(..., description="Deskripsi error")
    error_uri: str | None = Field(None, description="URI untuk info lebih lanjut")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "error": "invalid_token",
                "error_description": "Token telah expired atau tidak valid",
                "error_uri": None,
            }
        }
    )

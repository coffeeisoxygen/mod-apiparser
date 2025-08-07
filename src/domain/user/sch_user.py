"""schemas user."""

from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field

# TODO : nanti perketatt validasi Disini , sementara hanay defining Model aja.


class UserInDB(BaseModel):
    """User seeding schema."""

    id: str | UUID = Field(..., description="ID user")
    username: str = Field(..., min_length=3, max_length=50, description="Username user")
    email: EmailStr = Field(..., description="Email user")
    name: str = Field(
        ..., min_length=3, max_length=100, description="Nama lengkap user"
    )
    password: str = Field(
        ..., min_length=6, max_length=100, description="Password user (hashed)"
    )
    is_active: bool = Field(default=True, description="Status aktif user")
    is_superuser: bool = Field(
        default=False, description="Apakah user adalah superuser"
    )

    model_config = ConfigDict(
        json_encoders={UUID: str},
        json_schema_extra={
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "username": "admin",
                "email": "admin@example.com",
                "name": "Administrator",
                "password": "$argon2id$v=19$m=65536,t=3,p=4$...",
                "is_active": True,
                "is_superuser": False,
            }
        },
    )


class UserRead(BaseModel):
    """User read schema (untuk response API)."""

    id: str | UUID = Field(..., description="ID user")
    username: str = Field(..., description="Username user")
    email: EmailStr = Field(..., description="Email user")
    name: str = Field(..., description="Nama lengkap user")
    is_active: bool = Field(..., description="Status aktif user")
    is_superuser: bool = Field(..., description="Apakah user adalah superuser")

    model_config = ConfigDict(
        json_encoders={UUID: str},
        json_schema_extra={
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "username": "admin",
                "email": "admin@example.com",
                "name": "Administrator",
                "is_active": True,
                "is_superuser": False,
            }
        },
    )


class UserReadList(BaseModel):
    """User read list schema (untuk response API list)."""

    users: list[UserRead] = Field(..., description="Daftar users")
    total: int = Field(..., description="Total jumlah users")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "users": [
                    {
                        "id": "123e4567-e89b-12d3-a456-426614174000",
                        "username": "admin",
                        "email": "admin@example.com",
                        "name": "Administrator",
                        "is_active": True,
                        "is_superuser": False,
                    }
                ],
                "total": 1,
            }
        }
    )


class UserLogin(BaseModel):
    """User login schema."""

    username: str = Field(..., min_length=3, max_length=50, description="Username user")
    password: str = Field(
        ..., min_length=6, max_length=100, description="Password user"
    )

    model_config = ConfigDict(
        json_schema_extra={"example": {"username": "admin", "password": "password123"}}
    )


class UserCreate(BaseModel):
    """Schema untuk membuat user baru."""

    username: str = Field(..., min_length=3, max_length=50, description="Username user")
    email: EmailStr = Field(..., description="Email user")
    name: str = Field(
        ..., min_length=3, max_length=100, description="Nama lengkap user"
    )
    password: str = Field(
        ..., min_length=6, max_length=100, description="Password user"
    )
    is_active: bool = Field(default=True, description="Status aktif user")
    is_superuser: bool = Field(
        default=False, description="Apakah user adalah superuser"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "username": "newuser",
                "email": "newuser@example.com",
                "name": "New User",
                "password": "password123",
                "is_active": True,
                "is_superuser": False,
            }
        }
    )


class UserUpdate(BaseModel):
    """Schema untuk update user."""

    username: str | None = Field(
        None, min_length=3, max_length=50, description="Username user"
    )
    email: EmailStr | None = Field(None, description="Email user")
    name: str | None = Field(
        None, min_length=3, max_length=100, description="Nama lengkap user"
    )
    password: str | None = Field(
        None, min_length=6, max_length=100, description="Password user baru"
    )
    is_active: bool | None = Field(None, description="Status aktif user")
    is_superuser: bool | None = Field(None, description="Apakah user adalah superuser")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "username": "updateduser",
                "email": "updated@example.com",
                "name": "Updated Name",
                "is_active": True,
                "is_superuser": False,
            }
        }
    )


# UserInDB      # Untuk seeding & database storage
# UserRead      # Untuk response API (tanpa password)
# UserReadList  # Untuk list response dengan pagination info
# UserLogin     # Untuk login request
# UserCreate    # Untuk create user request
# UserUpdate    # Untuk update user request (partial)

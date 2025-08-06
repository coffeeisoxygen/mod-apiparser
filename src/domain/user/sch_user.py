"""schemas user."""

from pydantic import BaseModel, EmailStr, Field

# TODO : nanti perketatt validasi Disini , sementara hanay defining Model aja.


class UserInDB(BaseModel):
    """User seeding schema."""

    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    name: str = Field(..., min_length=3, max_length=100)
    password: str = Field(..., min_length=6, max_length=100)
    is_active: bool = Field(default=True)
    is_superuser: bool = Field(default=True)


class UserRead(BaseModel):
    """User read schema (untuk response API)."""

    username: str
    email: EmailStr
    name: str
    is_active: bool
    is_superuser: bool
    # id: int  # Uncomment jika ada field id di model/database


class UserReadList(BaseModel):
    """User read list schema (untuk response API list)."""

    users: list[UserRead]


class UserLogin(BaseModel):
    """User login schema."""

    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6, max_length=100)

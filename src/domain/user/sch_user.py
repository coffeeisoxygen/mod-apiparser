"""schemas user."""

from pydantic import BaseModel, EmailStr, Field

# TODO : nanti perketatt validasi Disini , sementara hanay defining Model aja.


class UserSeeding(BaseModel):
    """User seeding schema."""

    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    name: str = Field(..., min_length=3, max_length=100)
    password: str = Field(..., min_length=6, max_length=100)
    is_active: bool = Field(default=True)
    is_superuser: bool = Field(default=True)

"""dependencies untuk admin."""

from fastapi import Request
from fastapi.security import OAuth2PasswordBearer

from src.repos.rep_user import UserRepository

# Skema keamanan dasar, bisa disesuaikan
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def get_user_repo(request: Request) -> UserRepository:
    """Dependency injection untuk User Repository."""
    return request.app.state.user_repo

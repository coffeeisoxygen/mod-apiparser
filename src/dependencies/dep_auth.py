"""dependencies untuk admin."""
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from src.repos.rep_user import UserRepository
from src.domain.user.sch_user import UserInDB

# Skema keamanan dasar, bisa disesuaikan
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def get_user_repo(request: Request) -> UserRepository:
    """Dependency injection untuk User Repository."""
    return request.app.state.user_repo


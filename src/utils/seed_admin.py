import pathlib

import yaml

from src.dependencies.dep_settings import get_settings
from src.utils.hasher_service import HasherService

DEFAULT_USERS = [
    {
        "username": "admin",
        "password": "admin123",
        "email": "admin@example.com",
        "is_active": True,
        "is_superuser": True,
    },
    {
        "username": "user1",
        "password": "user123",
        "email": "user1@example.com",
        "is_active": True,
        "is_superuser": True,
    },
]


class SeederService:
    def __init__(self):
        self.path_users = pathlib.Path(get_settings().path_users)

    def seed(self):
        """Seed users file with default admin if not exists or empty."""
        if not self.path_users.exists() or self.path_users.stat().st_size == 0:
            users = []
            for user in DEFAULT_USERS:
                user_copy = user.copy()
                user_copy["password"] = HasherService.hash_password(
                    user_copy["password"]
                )
                users.append(user_copy)
            with open(self.path_users, "w", encoding="utf-8") as f:
                yaml.dump(
                    {"users": users}, f, sort_keys=False, default_flow_style=False
                )

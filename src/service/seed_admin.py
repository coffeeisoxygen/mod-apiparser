import pathlib

import yaml

from src.dependencies.dep_settings import get_settings
from src.domain.user.sch_user import UserSeeding
from src.utils.hasher_service import HasherService

DEFAULT_USERS = [
    {
        "username": "admin",
        "password": "admin123",
        "name": "Administrator",
        "email": "admin@example.com",
        "is_active": True,
        "is_superuser": True,
    },
    {
        "username": "user1",
        "password": "user123",
        "name": "User One",
        "email": "user1@example.com",
        "is_active": True,
        "is_superuser": True,
    },
]

DEFAULT_MODULES = [
    {
        "name": "module1",
        "description": "This is module 1",
        "is_active": True,
    },
    {
        "name": "module2",
        "description": "This is module 2",
        "is_active": True,
    },
]


class SeederService:
    def __init__(self):
        self.path_users = pathlib.Path(get_settings().path_users)

    def seed(self):
        """Seed users file with default admin if not exists or empty."""
        if not self.path_users.exists() or self.path_users.stat().st_size == 0:
            # check if directory exists, if not create it
            self.path_users.parent.mkdir(parents=True, exist_ok=True)
            users = []
            for user in DEFAULT_USERS:
                # Validasi dan normalisasi dengan schema
                user_obj = UserSeeding(**user)
                user_dict = user_obj.model_dump()
                user_dict["password"] = HasherService.hash_password(
                    user_dict["password"]
                )
                users.append(user_dict)
            with open(self.path_users, "w", encoding="utf-8") as f:
                yaml.dump(
                    {"users": users}, f, sort_keys=False, default_flow_style=False
                )

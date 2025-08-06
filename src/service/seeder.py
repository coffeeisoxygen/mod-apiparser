import pathlib

import yaml

from src.dependencies.dep_settings import get_settings
from src.domain.user.sch_user import UserInDB
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
        "provider": "",
        "accountid": "",
        "username": "",
        "pin": "",
        "password": "",
        "msisdn": "",
        "email": "",
        "base_url": "",
        "is_active": "",
        "name": "",
        "description": "",
    }
]


class SeederService:
    def __init__(self):
        settings = get_settings()
        self.path_users = pathlib.Path(settings.path_users)
        self.path_modules = pathlib.Path(settings.path_modules)

    def seed(self):
        self.create_default_users()
        self.create_default_modules()

    @staticmethod
    def _ensure_parent_dir(path: pathlib.Path) -> None:
        if not path.parent.exists():
            path.parent.mkdir(parents=True, exist_ok=True)

    def create_default_users(self):
        """Seed users file with default admin if not exists or empty."""
        path = self.path_users
        if not path.exists() or path.stat().st_size == 0:
            self._ensure_parent_dir(path)
            users = []
            for user in DEFAULT_USERS:
                user_obj = UserInDB(**user)
                user_dict = user_obj.model_dump()
                user_dict["password"] = HasherService.hash_password(
                    user_dict["password"]
                )
                users.append(user_dict)
            with open(path, "w", encoding="utf-8") as f:
                yaml.dump(
                    {"users": users}, f, sort_keys=False, default_flow_style=False
                )

    def create_default_modules(self):
        """Seed modules file with default modules if not exists or empty."""
        path = self.path_modules
        if not path.exists() or path.stat().st_size == 0:
            self._ensure_parent_dir(path)
            with open(path, "w", encoding="utf-8") as f:
                yaml.dump(
                    {"modules": DEFAULT_MODULES},
                    f,
                    sort_keys=False,
                    default_flow_style=False,
                )

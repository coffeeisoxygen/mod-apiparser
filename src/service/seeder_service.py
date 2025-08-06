import pathlib

import yaml

from src.dependencies.dep_settings import get_settings
from src.domain.user.sch_user import UserInDB
from src.mlogger import logger
from src.mlogger.utils import log_error
from src.service.hasher_service import HasherService

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
        log = logger.bind(operation="ensure_parent_dir", path=str(path))
        if not path.parent.exists():
            try:
                log.info("Creating parent directory: {}", path.parent)
                path.parent.mkdir(parents=True, exist_ok=True)
                log.success("Parent directory created successfully")
            except Exception as e:
                log_error(
                    error=e,
                    message="Failed to create parent directory",
                    extra_context={"path": str(path), "parent": str(path.parent)},
                )
                raise
        else:
            log.debug("Parent directory already exists")

    def create_default_users(self):
        """Seed users file with default admin if not exists or empty."""
        path = self.path_users
        log = logger.bind(operation="seed_users", path=str(path))
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
            try:
                with open(path, "w", encoding="utf-8") as f:
                    yaml.dump(
                        {"users": users}, f, sort_keys=False, default_flow_style=False
                    )
                log.success("Seeded users file successfully")
            except Exception as e:
                log_error(
                    error=e,
                    message="Failed to write users file",
                    extra_context={"path": str(path)},
                )
                raise
        else:
            log.debug("Users file already exists and is not empty")

    def create_default_modules(self):
        """Seed modules file with default modules if not exists or empty."""
        path = self.path_modules
        log = logger.bind(operation="seed_modules", path=str(path))
        if not path.exists() or path.stat().st_size == 0:
            self._ensure_parent_dir(path)
            try:
                with open(path, "w", encoding="utf-8") as f:
                    yaml.dump(
                        {"modules": DEFAULT_MODULES},
                        f,
                        sort_keys=False,
                        default_flow_style=False,
                    )
                log.success("Seeded modules file successfully")
            except Exception as e:
                log_error(
                    error=e,
                    message="Failed to write modules file",
                    extra_context={"path": str(path)},
                )
                raise
        else:
            log.debug("Modules file already exists and is not empty")

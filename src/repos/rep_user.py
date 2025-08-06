from typing import Any

import yaml
from pydantic import ValidationError

from mlogger import logger
from src.dependencies.dep_settings import get_settings
from src.domain.user.sch_user import UserInDB
from src.exceptions.app_exceptions import AppException


class UserRepository:
    def __init__(self):
        # Ambil path dari settings yang sudah di-cache
        settings = get_settings()
        self.file_path = settings.path_users
        self._users: list[UserInDB] = []
        self._load_users()

    def _load_users(self):
        """Memuat data dari file YAML dan memvalidasinya dengan skema UserInDB."""
        # Tambahkan bind untuk melacak operasi ini
        operation_logger = logger.bind(operation="load_users_from_yaml")

        try:
            with open(self.file_path) as file:
                data: dict[str, list[dict[str, Any]]] = yaml.safe_load(file)
                if data and "users" in data:
                    self._users = [UserInDB(**user_data) for user_data in data["users"]]
                    operation_logger.info(
                        f"Berhasil memuat {len(self._users)} user dari file.",
                        users_loaded=len(self._users),
                    )
                else:
                    operation_logger.warning(
                        "File users.yaml kosong atau tidak memiliki kunci 'users'."
                    )
        except FileNotFoundError as e:
            operation_logger.error(
                "File users.yaml tidak ditemukan. Jalankan seeder terlebih dahulu.",
                file=self.file_path,
            )
            self._users = []
            raise AppException.FileNotFoundError(
                message="File users.yaml tidak ditemukan. Jalankan seeder terlebih dahulu.",
                context={"file": self.file_path},
            ) from e
        except ValidationError as e:
            operation_logger.error(
                "Error validasi Pydantic saat memuat user.", error_details=e.errors()
            )
            self._users = []
            raise AppException.UserActionError(
                message="Error validasi Pydantic saat memuat user.",
                context={"error_details": e.errors()},
            ) from e
        except Exception as e:
            operation_logger.critical(
                "Error tak terduga saat memuat data user.", exception=e
            )
            self._users = []
            raise AppException.UserActionError(
                message="Error tak terduga saat memuat data user.",
                context={"exception": str(e)},
            ) from e

    def get_user_by_username(self, username: str) -> UserInDB | None:
        """Mencari user di memori berdasarkan username."""
        for user in self._users:
            if user.username == username:
                logger.debug("User ditemukan.", user=username)
                return user
        logger.warning("User tidak ditemukan.", user=username)
        return None

    def get_all_users(self) -> list[UserInDB]:
        """Mengembalikan semua user yang ada."""
        return self._users

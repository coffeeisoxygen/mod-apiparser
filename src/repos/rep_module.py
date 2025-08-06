from typing import Any

import yaml
from pydantic import ValidationError

from mlogger import logger
from src.dependencies.dep_settings import get_settings
from src.domain.module.sch_module import ModuleInDB
from src.exceptions.app_exceptions import AppException


class ModuleRepository:
    def __init__(self):
        settings = get_settings()
        self.file_path = settings.path_modules
        self._modules: list[ModuleInDB] = []
        self.reload()

    def _load_data_from_file(self) -> list[ModuleInDB]:
        """Memuat data dari file modules.yaml dan memvalidasinya.

        Mengembalikan list objek ModuleInDB atau list kosong jika file kosong.
        """
        operation_logger = logger.bind(operation="load_modules_from_yaml")

        try:
            with open(self.file_path) as file:
                data: dict[str, list[dict[str, Any]]] = yaml.safe_load(file)
                if not data or "modules" not in data:
                    operation_logger.warning(
                        "File modules.yaml kosong atau tidak memiliki kunci 'modules'."
                    )
                    return []

                # Memvalidasi setiap item dengan skema ModuleInDB
                modules_list = [
                    ModuleInDB(**module_data) for module_data in data["modules"]
                ]
                operation_logger.debug(
                    f"Berhasil memuat {len(modules_list)} modul dari file.",
                    modules_loaded=len(modules_list),
                )
                return modules_list
        except (ValidationError, Exception) as e:
            operation_logger.error(
                "Gagal memuat atau memvalidasi file YAML.",
                file=self.file_path,
                exception=e,
            )
            # Melempar satu custom exception yang spesifik
            raise AppException.YamlReloadExceptionError(
                message="Terjadi kesalahan saat memuat atau memvalidasi file YAML.",
                context={"error_details": str(e)},
            ) from e

    def reload(self):
        """Memuat ulang semua data dari file dan memperbarui state internal."""
        logger.info("Memulai proses reload ModuleRepository.")
        try:
            self._modules = self._load_data_from_file()
            logger.info("ModuleRepository berhasil dimuat ulang.")
        except AppException.YamlReloadExceptionError as e:
            # Jika terjadi error saat memuat ulang, log tapi biarkan data lama tetap ada
            logger.bind(error=e.message, context=e.context).error(
                "Gagal memuat ulang data, menggunakan data lama."
            )
        except Exception as e:
            # Blok fallback untuk error tak terduga
            logger.bind(exception=str(e)).error(
                "Gagal memuat ulang data karena error tak terduga, menggunakan data lama."
            )

    def get_module_by_id(self, module_id: str) -> ModuleInDB | None:
        """Mencari modul di memori berdasarkan module_id (moduleid)."""
        for module in self._modules:
            if module.moduleid == module_id:
                logger.debug("Modul ditemukan.", module_id=module_id)
                return module
        logger.warning("Modul tidak ditemukan.", module_id=module_id)
        return None

    def get_all_modules(self) -> list[ModuleInDB]:
        """Mengembalikan semua modul yang ada."""
        return self._modules

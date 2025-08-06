"""lifespan setup For FastAPi."""

from contextlib import asynccontextmanager

from src.mlogger import shutdown_logging
from src.repos.rep_user import UserRepository
from src.service.seeder_service import SeederService


@asynccontextmanager
async def lifespan(app):  # noqa: ANN001, RUF029
    """Event yang dijalankan saat aplikasi dimulai dan dihentikan."""
    # --- Startup Logic ---
    # 1. Jalankan seeder untuk memastikan file data ada.
    SeederService().seed()

    # 2. Inisialisasi repositories dan simpan di app.state
    app.state.user_repo = UserRepository()
    # Anda bisa menambahkan repository lain di sini, contoh:
    # app.state.module_repo = ModuleRepository()

    yield  # Aplikasi siap menerima permintaan

    # --- Shutdown Logic ---
    # 1. Bersihkan sumber daya jika diperlukan.
    # 2. Matikan sistem logging.
    shutdown_logging()

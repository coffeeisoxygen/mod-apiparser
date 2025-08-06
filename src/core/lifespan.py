"""lifespan setup For FastAPi."""

import pathlib
from contextlib import asynccontextmanager

from src.dependencies.dep_settings import get_settings
from src.mlogger import shutdown_logging
from src.repos.rep_user import UserRepository
from src.service.seeder_service import SeederService
from src.service.watcher import FileWatcher


@asynccontextmanager
async def lifespan(app):
    settings = get_settings()

    # --- Startup Logic ---
    # 1. Jalankan seeder untuk memastikan file data ada.
    SeederService().seed()

    # 2. Inisialisasi UserRepository dan simpan di app.state
    user_repo = UserRepository()
    app.state.user_repo = user_repo

    # 3. Inisialisasi dan jalankan watcher service
    user_file_path = pathlib.Path(settings.path_users)
    watcher = FileWatcher(file_path=user_file_path, callback=user_repo.reload)
    watcher.start()
    app.state.watcher = watcher

    yield  # Aplikasi siap menerima permintaan

    # --- Shutdown Logic ---
    app.state.watcher.stop()
    shutdown_logging()

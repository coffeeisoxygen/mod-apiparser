"""lifespan setup For FastAPi."""

import pathlib
from contextlib import asynccontextmanager

from src.dependencies.dep_settings import get_settings
from src.mlogger import shutdown_logging
from src.repos import ModuleRepository, UserRepository
from src.service.seeder_service import SeederService
from src.service.watcher import FileWatcher


@asynccontextmanager
async def lifespan(app):  # noqa: ANN001, RUF029
    """Manages the lifespan of the FastAPI application.

    This includes startup and shutdown logic, such as initializing
    repositories and starting background tasks.

    Args:
        app (_type_): The FastAPI application instance.

    Yields:
        _type_: Yields control back to the application after startup logic is complete.
    """
    settings = get_settings()

    # --- Startup Logic ---
    # 1. Jalankan seeder untuk memastikan file data ada.
    SeederService().seed()

    # 2. Inisialisasi UserRepository dan simpan di app.state
    user_repo = UserRepository()
    app.state.user_repo = user_repo
    module_repo = ModuleRepository()
    app.state.module_repo = module_repo

    # 3. Inisialisasi dan jalankan watcher service
    user_file_path = pathlib.Path(settings.path_data) / "users.yaml"
    module_file_path = pathlib.Path(settings.path_data) / "modules.yaml"
    user_watcher = FileWatcher(file_path=user_file_path, callback=user_repo.reload)
    module_watcher = FileWatcher(
        file_path=module_file_path, callback=module_repo.reload
    )
    user_watcher.start()
    module_watcher.start()
    app.state.user_watcher = user_watcher
    app.state.module_watcher = module_watcher

    yield  # Aplikasi siap menerima permintaan

    # --- Shutdown Logic ---
    app.state.watcher.stop()
    shutdown_logging()

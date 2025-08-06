"""lifespan setup For FastAPi."""

from contextlib import asynccontextmanager

from src.dependencies.dep_settings import get_settings
from src.mlogger import shutdown_logging
from src.utils.path_resolver import ensure_all_files

PATHUSERS = get_settings().path_users
PATHMODULES = get_settings().path_modules


@asynccontextmanager
async def lifespan(app):  # noqa: ANN001, ARG001, D103, RUF029
    ensure_all_files([(PATHUSERS, "users:"), (PATHMODULES, "modules:")])
    yield

    # Properly shutdown logging system
    shutdown_logging()

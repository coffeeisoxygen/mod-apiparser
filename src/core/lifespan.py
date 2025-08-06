"""lifespan setup For FastAPi."""

from contextlib import asynccontextmanager

from src.mlogger import shutdown_logging
from src.service.seed_admin import SeederService


@asynccontextmanager
async def lifespan(app):  # noqa: ANN001, ARG001, D103, RUF029
    SeederService().seed()
    yield

    # Properly shutdown logging system
    shutdown_logging()

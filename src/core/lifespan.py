"""lifespan setup For FastAPi."""

from contextlib import asynccontextmanager

from src.mlogger import get_logger, shutdown_logging


@asynccontextmanager
async def lifespan(app):  # noqa: ANN001, ARG001, D103, RUF029
    lifespan_logging = get_logger("lifespan")

    lifespan_logging.info("app is starting")
    yield
    lifespan_logging.info("app stopped")

    # Properly shutdown logging system
    shutdown_logging()

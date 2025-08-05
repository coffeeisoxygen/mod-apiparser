"""lifespan setup For FastAPi."""

from contextlib import asynccontextmanager

from src.mlogger import get_logger, shutdown_logging


@asynccontextmanager
async def lifespan(app):  # noqa: ANN001, ARG001, D103, RUF029
    # Get logger (setup happens automatically on first call)
    logger = get_logger(__name__)

    logger.info("app is starting")
    yield
    logger.info("app stopped")

    # Properly shutdown logging system
    shutdown_logging()

"""lifespan setup For FastAPi."""

from contextlib import asynccontextmanager

from utils.mlogger import logger


@asynccontextmanager
async def lifespan(app):  # noqa: ANN001, ARG001, D103, RUF029
    logger.info("app is starting")
    yield
    logger.info("app stopped")

"""Test script to demonstrate the complete logging lifecycle with shutdown."""

import asyncio
from contextlib import asynccontextmanager

from src.mlogger import get_logger, shutdown_logging


@asynccontextmanager
async def test_lifespan():
    """Simulate FastAPI lifespan for testing."""
    # Startup
    logger = get_logger(__name__)
    logger.info("Test application starting up")
    
    # Simulate some work
    logger.info("Application is running...")
    logger.debug("Debug message during runtime")
    logger.warning("Warning message during runtime")
    
    yield
    
    # Shutdown
    logger.info("Test application shutting down")
    shutdown_logging()
    print("✓ Shutdown logging called successfully")


async def main():
    """Run the lifecycle test."""
    async with test_lifespan():
        # Simulate application runtime
        logger = get_logger("test_runtime")
        logger.info("Application is processing requests...")
        await asyncio.sleep(0.1)  # Simulate some async work
        
    print("✓ Test completed - check logs for shutdown message")


if __name__ == "__main__":
    asyncio.run(main())

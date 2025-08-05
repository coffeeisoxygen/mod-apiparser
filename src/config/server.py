"""setup uvicorn server for FastAPI application."""

import os
from multiprocessing import cpu_count

from dotenv import load_dotenv


class ServerConfig:
    """Configuration for the FastAPI server."""

    def __init__(self):
        load_dotenv()  # Load environment variables from .env file
        self.host = os.getenv("UVICORN_HOST", "0.0.0.0")
        self.port = int(os.getenv("UVICORN_PORT", 8000))
        self.reload = os.getenv("UVICORN_RELOAD", "true").lower() in (
            "true",
            "1",
            "yes",
        )
        self.workers = int(os.getenv("UVICORN_WORKERS", cpu_count()))
        self.log_level = os.getenv("UVICORN_LOG_LEVEL", "info")
        self.timeout_keep_alive = int(os.getenv("UVICORN_TIMEOUT_KEEP_ALIVE", 5))
        self.timeout_graceful_shutdown = int(
            os.getenv("UVICORN_TIMEOUT_GRACEFUL_SHUTDOWN", 5)
        )

"""setup uvicorn server for FastAPI application."""

import os
from dataclasses import asdict, dataclass
from multiprocessing import cpu_count


@dataclass
class ServerConfig:
    host: str = os.getenv("UVICORN_HOST", "0.0.0.0")
    port: int = int(os.getenv("UVICORN_PORT", 8000))
    reload: bool = os.getenv("UVICORN_RELOAD", "true").lower() in ("true", "1", "yes")
    workers: int = int(os.getenv("UVICORN_WORKERS", cpu_count()))
    log_level: str = os.getenv("UVICORN_LOG_LEVEL", "info")
    timeout_keep_alive: int = int(os.getenv("UVICORN_TIMEOUT_KEEP_ALIVE", 5))
    timeout_graceful_shutdown: int = int(
        os.getenv("UVICORN_TIMEOUT_GRACEFUL_SHUTDOWN", 5)
    )

    def get_config(self) -> dict:
        """Get the server configuration as a dictionary."""
        return asdict(self)

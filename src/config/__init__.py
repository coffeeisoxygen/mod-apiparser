from src.config.lifespan import lifespan
from src.config.middleware import setup_middlewares

# from src.config.router import api_router
from src.config.server import ServerConfig

__all__ = ["ServerConfig", "api_router", "lifespan", "setup_middlewares"]

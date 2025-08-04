from .lifespan import lifespan
from .middleware import setup_middlewares
from .router import api_router

__all__ = ["api_router", "lifespan", "setup_middlewares"]

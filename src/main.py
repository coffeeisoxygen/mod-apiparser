from functools import lru_cache

import uvicorn
from fastapi import FastAPI

from src._version import version
from src.config.base import Settings
from src.core.lifespan import lifespan
from src.core.middleware import setup_middlewares


@lru_cache
def get_settings():
    return Settings()  # type: ignore


app = FastAPI(
    lifespan=lifespan,
    title="modkit-parser",
    description="dari pada ribet parsing json panjang, pake ini aja biar tenang",
    version=version,
    summary="middleware service antara otomax client dan APi Provider.",
)
setup_middlewares(app=app)
# app.include_router(api_router)


@app.get("/")
async def root():
    """Root endpoint for health check."""
    return {"message": "OK"}


@app.get("/info")
async def info():
    """Endpoint for retrieving information."""
    return {
        "service": get_settings().service,
        "version": get_settings().version,
        "environment": get_settings().environment.value,
    }


if __name__ == "__main__":
    # development server
    uvicorn.run(
        app="src.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
        timeout_keep_alive=5,
        timeout_graceful_shutdown=5,
    )

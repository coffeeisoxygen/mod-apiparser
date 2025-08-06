import uvicorn
from fastapi import FastAPI

from src._version import version
from src.core.lifespan import lifespan
from src.core.middleware import setup_middlewares
from src.dependencies.dep_settings import EnvInfo

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
async def info(env_parameters: EnvInfo) -> EnvInfo:
    """Get information about the current environment.

    This endpoint provides details about the current environment settings.

    Args:
        env_parameters (EnvInfo): The environment settings.

    Returns:
        EnvInfo: The environment settings.
    """
    return env_parameters


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

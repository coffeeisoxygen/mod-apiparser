import uvicorn
from fastapi import FastAPI

from src._version import version
from src.core.config import Config
from src.core.lifespan import lifespan
from src.core.middleware import setup_middlewares
from src.mlogger import logger

config = Config()
uvc = config.server


app = FastAPI(
    lifespan=lifespan,
    title="modkit-parser",
    description="dari pada ribet parsing json panjang, pake ini aja biar tenang",
    version=version,
    summary="middleware service antara otomax client dan APi Provider.",
)
setup_middlewares(app)
# app.include_router(api_router)


@app.get("/")
async def root():
    """Root endpoint for health check."""
    return {"message": "OK"}


if __name__ == "__main__":
    logger.bind(
        server="uvicorn",
        host=uvc.host,
        port=uvc.port,
        reload=uvc.reload,
        workers=uvc.workers,
        log_level=uvc.log_level,
    ).info(f"Starting Uvicorn server with config: {uvc}")
    uvicorn.run(
        app="main:app",
        host=uvc.host,
        port=uvc.port,
        reload=uvc.reload,
        workers=uvc.workers,
        log_level=uvc.log_level,
        timeout_keep_alive=uvc.timeout_keep_alive,
        timeout_graceful_shutdown=uvc.timeout_graceful_shutdown,
    )
else:
    logger.bind(server="uvicorn").info(
        "Not running in main block, use 'uvicorn main:app' to start"
    )

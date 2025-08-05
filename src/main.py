import uvicorn
from fastapi import FastAPI

from src._version import version
from src.config import ServerConfig, lifespan, setup_middlewares
from src.mlogger import get_logger

# Get logger (setup will happen in lifespan)
logger = get_logger(__name__)


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
    return {"message": "OK"}


if __name__ == "__main__":
    uvc_config = ServerConfig().get_config()
    logger.bind(
        server="uvicorn",
        host=uvc_config["host"],
        port=uvc_config["port"],
        reload=uvc_config["reload"],
        workers=uvc_config["workers"],
        log_level=uvc_config["log_level"],
    ).info(f"Starting Uvicorn server with config: {uvc_config}")
    uvicorn.run(
        app="main:app",
        host=uvc_config["host"],
        port=uvc_config["port"],
        reload=uvc_config["reload"],
        workers=uvc_config["workers"],
        log_level=uvc_config["log_level"],
        timeout_keep_alive=uvc_config["timeout_keep_alive"],
        timeout_graceful_shutdown=uvc_config["timeout_graceful_shutdown"],
    )
else:
    logger.bind(server="uvicorn").info(
        "Not running in main block, use 'uvicorn main:app' to start"
    )

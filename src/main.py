import uvicorn
from fastapi import FastAPI

from config import api_router, lifespan, setup_middlewares
from src._version import version
from utils.mlogger import LogConfig, LoggerManager, logger

log_config = LogConfig(
    level="DEBUG",
    to_file=False,
    to_terminal=True,
    serialize=False,
    diagnose=True,
    enqueue=True,
    format_style="simple",
)

LoggerManager(log_config).setup()
logger.debug("Logger initialized with config", log_config=log_config)


app = FastAPI(
    lifespan=lifespan,
    title="modkit-parser",
    description="dari pada ribet parsing json panjang, pake ini aja biar tenang",
    version=version,
    summary="middleware service antara otomax client dan APi Provider.",
)
setup_middlewares(app)
app.include_router(api_router)


@app.get("/")
async def root():
    return {"message": "OK"}


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

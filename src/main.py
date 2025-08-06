import uvicorn
from fastapi import FastAPI

from src._version import version
from src.core.config import Config
from src.core.lifespan import lifespan
from src.core.middleware import setup_middlewares

config = Config()


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


if __name__ == "__main__":
    uvicorn.run(
        app="src.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
        timeout_keep_alive=5,
        timeout_graceful_shutdown=5,
    )

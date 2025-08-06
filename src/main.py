import markdown2
import uvicorn
from fastapi import FastAPI
from fastapi.responses import HTMLResponse

from src._version import version
from src.config.settings import AppConfig
from src.core.lifespan import lifespan
from src.core.middleware import setup_middlewares
from src.dependencies.dep_settings import AppConfigDep, get_app_config

app = FastAPI(
    debug=get_app_config().debug,
    lifespan=lifespan,
    title="modkit-parser",
    description="dari pada ribet parsing json panjang, pake ini aja biar tenang",
    version=version,
    summary="middleware service antara otomax client dan APi Provider.",
    terms_of_service="/terms",
)
setup_middlewares(app=app)
# app.include_router(api_router)


@app.get("/")
async def root():
    """Root endpoint for health check."""
    return {"message": "OK"}


@app.get("/info")
async def info(app_config: AppConfigDep) -> AppConfig:
    """Get information about the current application configuration.

    This endpoint provides details about the current environment settings.

    Args:
        app_config (AppConfigDep): The application configuration dependency.

    Returns:
        AppConfig: The application configuration.
    """
    return app_config


@app.get("/terms", response_class=HTMLResponse)
async def terms():
    """Get terms of service page.

    Returns:
        HTMLResponse: Terms of service in HTML format.
    """
    md = """
# Terms of Service

_Not for commercial use, and don't deploy this service to production without proper security measures._

- You may not use this for commercial purposes.
- ... (tambahkan markdown lain sesuai kebutuhan)
"""
    return markdown2.markdown(md)


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
